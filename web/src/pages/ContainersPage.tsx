import { AlertTriangle, Gauge, Layers, MapPinned, Pencil, Plus, RefreshCcw, Save, Trash2, X } from "lucide-react";
import L from "leaflet";
import type { FormEvent } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  Container,
  ContainerStatus,
  Region,
  createContainer,
  createRegion,
  deleteContainer,
  listContainers,
  listRegions,
  simulateContainerFill,
  updateContainer,
  updateContainerFill,
} from "../api";

const statuses: ContainerStatus[] = [
  "Normal",
  "Izleniyor",
  "Kritik",
  "GoreveAtandi",
  "Bosaltildi",
];

type ContainerForm = {
  kod: string;
  enlem: string;
  boylam: string;
  doluluk_orani: string;
  durum: ContainerStatus;
  bolge_id: string;
};

const emptyContainerForm: ContainerForm = {
  kod: "",
  enlem: "",
  boylam: "",
  doluluk_orani: "0",
  durum: "Normal",
  bolge_id: "",
};

export function ContainersPage({ token }: { token: string }) {
  const [regions, setRegions] = useState<Region[]>([]);
  const [containers, setContainers] = useState<Container[]>([]);
  const [containerForm, setContainerForm] = useState<ContainerForm>(emptyContainerForm);
  const [regionName, setRegionName] = useState("");
  const [regionDescription, setRegionDescription] = useState("");
  const [search, setSearch] = useState("");
  const [regionFilter, setRegionFilter] = useState("Tum Bolgeler");
  const [statusFilter, setStatusFilter] = useState("Tum Durumlar");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [editingContainerId, setEditingContainerId] = useState<number | null>(null);
  const [deletingContainerId, setDeletingContainerId] = useState<number | null>(null);
  const [deleteCandidate, setDeleteCandidate] = useState<Container | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);
    try {
      const [regionData, containerData] = await Promise.all([
        listRegions(token),
        listContainers(token),
      ]);
      setRegions(regionData);
      setContainers(containerData);
      setContainerForm((current) => ({
        ...current,
        bolge_id: current.bolge_id || String(regionData[0]?.id || ""),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Konteyner verisi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const filteredContainers = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("tr-TR");
    return containers.filter((container) => {
      const matchesSearch =
        !needle ||
        container.kod.toLocaleLowerCase("tr-TR").includes(needle) ||
        container.bolge.ad.toLocaleLowerCase("tr-TR").includes(needle);
      const matchesRegion = regionFilter === "Tum Bolgeler" || container.bolge.ad === regionFilter;
      const matchesStatus = statusFilter === "Tum Durumlar" || container.durum === statusFilter;
      return matchesSearch && matchesRegion && matchesStatus;
    });
  }, [containers, search, regionFilter, statusFilter]);

  const criticalCount = containers.filter((container) => container.durum === "Kritik").length;
  const watchedCount = containers.filter((container) => container.doluluk_orani >= 70).length;
  const assignedCount = containers.filter((container) => container.durum === "GoreveAtandi").length;
  const averageFill = containers.length > 0
    ? Math.round(containers.reduce((sum, container) => sum + container.doluluk_orani, 0) / containers.length)
    : 0;
  const regionDensity = useMemo(() => {
    return regions
      .map((region) => {
        const regionContainers = containers.filter((container) => container.bolge.id === region.id);
        const average = regionContainers.length > 0
          ? Math.round(regionContainers.reduce((sum, container) => sum + container.doluluk_orani, 0) / regionContainers.length)
          : 0;
        return {
          id: region.id,
          name: region.ad,
          count: regionContainers.length,
          critical: regionContainers.filter((container) => container.durum === "Kritik").length,
          average,
        };
      })
      .sort((a, b) => b.average - a.average);
  }, [containers, regions]);
  const criticalContainers = containers
    .filter((container) => container.durum === "Kritik" || container.doluluk_orani >= 85)
    .sort((a, b) => b.doluluk_orani - a.doluluk_orani)
    .slice(0, 5);

  async function handleCreateRegion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    if (regionName.trim().length < 2) {
      setError("Bolge adi en az 2 karakter olmalidir.");
      return;
    }

    setSaving(true);
    try {
      const region = await createRegion(token, {
        ad: regionName.trim(),
        aciklama: regionDescription.trim() || null,
      });
      setRegions((current) => [...current, region].sort((a, b) => a.ad.localeCompare(b.ad)));
      setContainerForm((current) => ({ ...current, bolge_id: String(region.id) }));
      setRegionName("");
      setRegionDescription("");
      setMessage("Yeni bolge olusturuldu.");
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Bolge olusturulamadi.");
    } finally {
      setSaving(false);
    }
  }

  async function handleSubmitContainer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const fill = Number(containerForm.doluluk_orani);
    const regionId = Number(containerForm.bolge_id);

    if (
      !containerForm.kod.trim() ||
      !containerForm.enlem.trim() ||
      !containerForm.boylam.trim() ||
      !Number.isFinite(fill) ||
      fill < 0 ||
      fill > 100 ||
      !regionId
    ) {
      setError("Kod, bolge, koordinat ve 0-100 arasi doluluk zorunludur.");
      return;
    }

    setSaving(true);
    try {
      if (editingContainerId !== null) {
        const original = containers.find((container) => container.id === editingContainerId);
        const updated = await updateContainer(token, editingContainerId, {
          kod: containerForm.kod.trim(),
          enlem: containerForm.enlem.trim(),
          boylam: containerForm.boylam.trim(),
          durum: containerForm.durum,
          bolge_id: regionId,
        });

        if (original && original.doluluk_orani !== fill) {
          await updateContainerFill(token, editingContainerId, fill);
        }

        setMessage(`${updated.kod} konteyneri guncellendi.`);
        resetContainerForm(regionId);
        await loadData();
        return;
      }

      const created = await createContainer(token, {
        kod: containerForm.kod.trim(),
        enlem: containerForm.enlem.trim(),
        boylam: containerForm.boylam.trim(),
        doluluk_orani: fill,
        durum: containerForm.durum,
        bolge_id: regionId,
      });
      if (fill >= 85) {
        const fillUpdate = await updateContainerFill(token, created.id, fill);
        setMessage(
          fillUpdate.gorev_olusturuldu
            ? `Yeni konteyner kaydi olusturuldu ve #${fillUpdate.gorev_id} gorevi acildi.`
            : "Yeni konteyner kaydi olusturuldu; konteyner icin acik gorev zaten var.",
        );
      } else {
        setMessage("Yeni konteyner kaydi olusturuldu.");
      }
      resetContainerForm(regionId);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Konteyner kaydedilemedi.");
    } finally {
      setSaving(false);
    }
  }

  function resetContainerForm(fallbackRegionId?: number) {
    setEditingContainerId(null);
    setContainerForm({
      ...emptyContainerForm,
      bolge_id: String(fallbackRegionId || regions[0]?.id || ""),
    });
  }

  const startEditContainer = useCallback((container: Container) => {
    setError("");
    setMessage("");
    setEditingContainerId(container.id);
    setContainerForm({
      kod: container.kod,
      enlem: container.enlem,
      boylam: container.boylam,
      doluluk_orani: String(container.doluluk_orani),
      durum: container.durum,
      bolge_id: String(container.bolge.id),
    });
  }, []);

  const handleMapPick = useCallback((lat: number, lng: number) => {
    setError("");
    setMessage("");
    setContainerForm((current) => ({
      ...current,
      enlem: lat.toFixed(7),
      boylam: lng.toFixed(7),
    }));
  }, []);

  async function handleDeleteContainer(container: Container) {
    setError("");
    setMessage("");
    setDeletingContainerId(container.id);
    try {
      await deleteContainer(token, container.id);
      setContainers((current) => current.filter((item) => item.id !== container.id));
      if (editingContainerId === container.id) resetContainerForm();
      setDeleteCandidate(null);
      setMessage(`${container.kod} konteyneri silindi.`);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Konteyner silinemedi.");
    } finally {
      setDeletingContainerId(null);
    }
  }

  async function handleQuickUpdate(
    container: Container,
    payload: { durum?: ContainerStatus; doluluk_orani?: number },
  ) {
    setError("");
    setMessage("");

    try {
      if (payload.doluluk_orani !== undefined) {
        const fillUpdate = await updateContainerFill(token, container.id, payload.doluluk_orani);
        setMessage(
          fillUpdate.gorev_olusturuldu
            ? `${container.kod} kritik seviyeye ulasti ve #${fillUpdate.gorev_id} gorevi acildi.`
            : `${container.kod} doluluk orani guncellendi.`,
        );
        await loadData();
        return;
      }

      const updated = await updateContainer(token, container.id, payload);
      setContainers((current) =>
        current.map((item) => (item.id === container.id ? updated : item)),
      );
      setMessage(`${container.kod} guncellendi.`);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Konteyner guncellenemedi.");
    }
  }

  async function handleSimulateFill() {
    setError("");
    setMessage("");
    setSimulating(true);
    try {
      const result = await simulateContainerFill(token);
      setMessage(
        `${result.guncellenen_konteyner} konteyner icin sensor simulasyonu calisti; ${result.olusan_gorev_sayisi} yeni gorev olustu.`,
      );
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Doluluk simulasyonu calistirilamadi.");
    } finally {
      setSimulating(false);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <div>
          <p>KONTEYNER IZLEME</p>
          <h1>Bolge ve Konteyner Yonetimi</h1>
          <span>
            Bolge kayitlarini, konteyner koordinatlarini, doluluk oranlarini ve operasyon
            durumlarini web panelinden yonetin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <MapPinned size={34} />
          <strong>{criticalCount}</strong>
          <span>Kritik Konteyner</span>
          <small>{watchedCount} kayit %70 uzeri</small>
        </div>
      </section>

      <section className="admin-summary-row" aria-label="Konteyner ozetleri">
        <article>
          <span>Toplam Konteyner</span>
          <strong>{containers.length}</strong>
        </article>
        <article>
          <span>Kritik</span>
          <strong>{criticalCount}</strong>
        </article>
        <article>
          <span>Goreve Atandi</span>
          <strong>{assignedCount}</strong>
        </article>
        <article>
          <span>Bolge</span>
          <strong>{regions.length}</strong>
        </article>
      </section>

      <section className="simulation-panel">
        <div>
          <Gauge size={24} />
          <div>
            <strong>Sensor Doluluk Simulasyonu</strong>
            <span>
              Konteyner doluluklarini rastgele artirir; kritik seviyeye gelen kayitlar icin
              otomatik gorev havuzu olusturur.
            </span>
          </div>
        </div>
        <button
          className="primary-action"
          disabled={simulating || containers.length === 0}
          onClick={handleSimulateFill}
          type="button"
        >
          <Gauge size={18} />
          {simulating ? "Calisiyor" : "Simulasyonu Calistir"}
        </button>
      </section>

      <section className="city-ops-grid">
        <article className="city-ops-panel">
          <div className="panel-heading">
            <div>
              <h3>Bolge Yogunlugu</h3>
              <p>Doluluk ortalamasina gore ilk bolgeler</p>
            </div>
            <Layers size={20} />
          </div>
          <div className="density-list">
            {regionDensity.slice(0, 4).map((region) => (
              <div key={region.id}>
                <span>{region.name}</span>
                <strong>{region.average}%</strong>
                <i><b style={{ width: `${region.average}%` }} /></i>
                <small>{region.count} konteyner / {region.critical} kritik</small>
              </div>
            ))}
          </div>
        </article>

        <article className="city-ops-panel">
          <div className="panel-heading">
            <div>
              <h3>Kritik Noktalar</h3>
              <p>Once bosaltilmasi gereken konteynerler</p>
            </div>
            <AlertTriangle size={20} />
          </div>
          <div className="critical-mini-list">
            {criticalContainers.map((container) => (
              <button
                key={container.id}
                type="button"
                onClick={() => {
                  setSearch(container.kod);
                  setStatusFilter("Tum Durumlar");
                }}
              >
                <strong>{container.kod}</strong>
                <span>{container.bolge.ad}</span>
                <b>{container.doluluk_orani}%</b>
              </button>
            ))}
            {criticalContainers.length === 0 && <div className="empty-state">Kritik konteyner yok.</div>}
          </div>
        </article>

        <article className="city-ops-panel">
          <div className="panel-heading">
            <div>
              <h3>Doluluk Nabzi</h3>
              <p>Genel seviye ve operasyon sinyali</p>
            </div>
            <Gauge size={20} />
          </div>
          <div className="fill-pulse">
            <strong>{averageFill}%</strong>
            <span>ortalama doluluk</span>
            <i><b style={{ width: `${averageFill}%` }} /></i>
            <small>{watchedCount} nokta izleme esiginde</small>
          </div>
        </article>
      </section>

      <section className="container-map-panel">
        <div className="panel-heading">
          <div>
            <h3>Tum Konteyner Haritasi</h3>
            <p>
              Gaziantep icindeki konteynerleri doluluk, bolge ve operasyon durumuna gore harita
              uzerinden izleyin.
            </p>
          </div>
          <span className="map-count-pill">{filteredContainers.length} nokta</span>
        </div>
        <AdminContainerMap
          containers={filteredContainers}
          selectedContainerId={editingContainerId}
          selectedPosition={
            containerForm.enlem && containerForm.boylam
              ? [Number(containerForm.enlem), Number(containerForm.boylam)]
              : null
          }
          onPick={handleMapPick}
          onSelect={startEditContainer}
        />
      </section>

      <section className="form-panel action-panel">
        <div className="panel-heading">
          <div>
            <h3>{editingContainerId ? "Konteyneri Duzenle" : "Yeni Konteyner Ekle"}</h3>
            <p>
              {editingContainerId
                ? "Secili konteynerin kod, bolge, konum, doluluk ve durum bilgisini guncelleyin."
                : "Kayitlar dogrudan backend API uzerinden olusturulur."}
            </p>
          </div>
          {editingContainerId && (
            <div className="container-edit-actions">
              <button
                className="row-action danger"
                disabled={deletingContainerId === editingContainerId}
                onClick={() => {
                  const container = containers.find((item) => item.id === editingContainerId);
                  if (container) setDeleteCandidate(container);
                }}
                type="button"
              >
                <Trash2 size={16} />
                Sil
              </button>
              <button className="row-action" onClick={() => resetContainerForm()} type="button">
                <X size={16} />
                Vazgec
              </button>
            </div>
          )}
        </div>

        <form className="container-form" onSubmit={handleSubmitContainer}>
          <label>
            Kod
            <input
              value={containerForm.kod}
              onChange={(event) =>
                setContainerForm({ ...containerForm, kod: event.target.value })
              }
              placeholder="KNT-001"
            />
          </label>
          <label>
            Bolge
            <select
              value={containerForm.bolge_id}
              onChange={(event) =>
                setContainerForm({ ...containerForm, bolge_id: event.target.value })
              }
            >
              <option value="">Bolge secin</option>
              {regions.map((region) => (
                <option key={region.id} value={region.id}>
                  {region.ad}
                </option>
              ))}
            </select>
          </label>
          <div className="map-picked-location">
            <span>Haritadan Secilen Konum</span>
            <strong>
              {containerForm.enlem && containerForm.boylam
                ? `${containerForm.enlem}, ${containerForm.boylam}`
                : "Haritadan nokta secin"}
            </strong>
            <small>Koordinat elle girilmez; haritaya tiklayarak otomatik doldurulur.</small>
          </div>
          <label>
            Doluluk
            <input
              value={containerForm.doluluk_orani}
              onChange={(event) =>
                setContainerForm({ ...containerForm, doluluk_orani: event.target.value })
              }
              inputMode="numeric"
              placeholder="0"
            />
          </label>
          <label>
            Durum
            <select
              value={containerForm.durum}
              onChange={(event) =>
                setContainerForm({
                  ...containerForm,
                  durum: event.target.value as ContainerStatus,
                })
              }
            >
              {statuses.map((status) => (
                <option key={status}>{status}</option>
              ))}
            </select>
          </label>
          <button
            className="primary-action"
            disabled={saving || !containerForm.kod.trim() || !containerForm.bolge_id}
            type="submit"
          >
            <Save size={18} />
            {saving ? "Kaydediliyor" : editingContainerId ? "Guncelle" : "Kaydet"}
          </button>
        </form>
      </section>

      <section className="form-panel action-panel">
        <div className="panel-heading">
          <div>
            <h3>Yeni Bolge Ekle</h3>
            <p>Konteynerler bir bolgeye bagli olarak takip edilir.</p>
          </div>
          <button className="icon-button" onClick={loadData} type="button" title="Yenile">
            <RefreshCcw size={18} />
          </button>
        </div>

        <form className="region-form" onSubmit={handleCreateRegion}>
          <label>
            Bolge Adi
            <input
              value={regionName}
              onChange={(event) => setRegionName(event.target.value)}
              placeholder="Merkez"
            />
          </label>
          <label>
            Aciklama
            <input
              value={regionDescription}
              onChange={(event) => setRegionDescription(event.target.value)}
              placeholder="Opsiyonel"
            />
          </label>
          <button className="primary-action" disabled={saving || !regionName.trim()} type="submit">
            <Plus size={18} />
            Bolge Ekle
          </button>
        </form>
      </section>

      <InlineNotice
        message={error || message}
        type={error ? "error" : "success"}
        onClose={() => {
          setError("");
          setMessage("");
        }}
      />

      <section className="filter-panel toolbar-panel">
        <label>
          Arama
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Kod veya bolge ile ara..."
          />
        </label>
        <label>
          Bolge
          <select value={regionFilter} onChange={(event) => setRegionFilter(event.target.value)}>
            <option>Tum Bolgeler</option>
            {regions.map((region) => (
              <option key={region.id}>{region.ad}</option>
            ))}
          </select>
        </label>
        <label>
          Durum
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option>Tum Durumlar</option>
            {statuses.map((status) => (
              <option key={status}>{status}</option>
            ))}
          </select>
        </label>
      </section>

      <section className="data-panel">
        <div className="table-title">
          <strong>Konteyner Listesi</strong>
          <span>
            {loading
              ? "Yukleniyor"
              : `Toplam ${containers.length} konteynerden ${filteredContainers.length} kayit gosteriliyor`}
          </span>
        </div>

        <div className="container-table" role="table">
          <div className="container-row container-head" role="row">
            <span>Kod / Bolge</span>
            <span>Koordinat</span>
            <span>Doluluk</span>
            <span>Durum</span>
            <span>Islem</span>
          </div>

          {filteredContainers.map((container) => (
            <div className="container-row" key={container.id} role="row">
              <span>
                <strong>{container.kod}</strong>
                <small>{container.bolge.ad}</small>
              </span>
              <span>
                {container.enlem}
                <small>{container.boylam}</small>
              </span>
              <span>
                <div className="fill-meter" aria-label={`Doluluk ${container.doluluk_orani}`}>
                  <span style={{ width: `${container.doluluk_orani}%` }} />
                </div>
                <small>{container.doluluk_orani}% dolu</small>
              </span>
              <span>
                <b className={`status-pill ${container.durum.toLowerCase()}`}>
                  {container.durum}
                </b>
              </span>
              <span className="quick-actions">
                <input
                  value={container.doluluk_orani}
                  onChange={(event) =>
                    handleQuickUpdate(container, {
                      doluluk_orani: Math.min(100, Math.max(0, Number(event.target.value))),
                    })
                  }
                  inputMode="numeric"
                />
                <select
                  value={container.durum}
                  onChange={(event) =>
                    handleQuickUpdate(container, {
                      durum: event.target.value as ContainerStatus,
                    })
                  }
                >
                  {statuses.map((status) => (
                    <option key={status}>{status}</option>
                  ))}
                </select>
                <button className="row-action" onClick={() => startEditContainer(container)} type="button">
                  <Pencil size={15} />
                  Duzenle
                </button>
                <button
                  className="row-action danger"
                  disabled={deletingContainerId === container.id}
                  onClick={() => handleDeleteContainer(container)}
                  type="button"
                >
                  <Trash2 size={15} />
                  {deletingContainerId === container.id ? "Siliniyor" : "Sil"}
                </button>
              </span>
            </div>
          ))}

          {!loading && filteredContainers.length === 0 && (
            <div className="empty-state">
              <Plus size={22} />
              Kayit bulunamadi.
            </div>
          )}
        </div>
      </section>
      <ConfirmDialog
        open={deleteCandidate !== null}
        title="Konteyner silinsin mi?"
        message={
          deleteCandidate
            ? `${deleteCandidate.kod} konteyneri silinecek. Acik gorevi varsa sistem islemi reddeder.`
            : ""
        }
        confirmLabel="Sil"
        danger
        busy={deleteCandidate !== null && deletingContainerId === deleteCandidate.id}
        onCancel={() => setDeleteCandidate(null)}
        onConfirm={() => {
          if (deleteCandidate) handleDeleteContainer(deleteCandidate);
        }}
      />
    </div>
  );
}

function AdminContainerMap({
  containers,
  selectedContainerId,
  selectedPosition,
  onPick,
  onSelect,
}: {
  containers: Container[];
  selectedContainerId: number | null;
  selectedPosition: [number, number] | null;
  onPick: (lat: number, lng: number) => void;
  onSelect: (container: Container) => void;
}) {
  const mapElementRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerLayerRef = useRef<L.LayerGroup | null>(null);
  const selectedLayerRef = useRef<L.LayerGroup | null>(null);
  const fittedContainerKeyRef = useRef("");

  useEffect(() => {
    if (!mapElementRef.current || mapRef.current) return;

    const map = L.map(mapElementRef.current, {
      zoomControl: false,
      attributionControl: false,
    }).setView([37.0662, 37.3833], 12);
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap",
    }).addTo(map);

    const markerLayer = L.layerGroup().addTo(map);
    const selectedLayer = L.layerGroup().addTo(map);
    map.on("click", (event) => {
      onPick(event.latlng.lat, event.latlng.lng);
    });
    mapRef.current = map;
    markerLayerRef.current = markerLayer;
    selectedLayerRef.current = selectedLayer;

    return () => {
      map.off("click");
      map.remove();
      mapRef.current = null;
      markerLayerRef.current = null;
      selectedLayerRef.current = null;
    };
  }, [onPick]);

  useEffect(() => {
    const map = mapRef.current;
    const markerLayer = markerLayerRef.current;
    if (!map || !markerLayer) return;

    markerLayer.clearLayers();
    const bounds: L.LatLngTuple[] = [];

    containers.forEach((container) => {
      const lat = Number(container.enlem);
      const lng = Number(container.boylam);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

      bounds.push([lat, lng]);
      const marker = L.marker([lat, lng], {
        icon: L.divIcon({
          className: `admin-container-marker ${containerMarkerTone(container)} ${container.id === selectedContainerId ? "selected" : ""}`,
          html: `<span>${container.doluluk_orani}%</span><small>${container.kod}</small>`,
          iconSize: [74, 50],
          iconAnchor: [37, 46],
          popupAnchor: [0, -40],
        }),
      })
        .bindPopup(
          `<strong>${container.kod}</strong><br />${container.bolge.ad}<br />Doluluk: ${container.doluluk_orani}%<br />Durum: ${container.durum}<br />Duzenlemek icin marker'a tiklayin.`,
        )
        .addTo(markerLayer);
      marker.on("click", () => onSelect(container));
    });

    const containerKey = containers
      .map((container) => `${container.id}:${container.enlem}:${container.boylam}`)
      .join("|");
    if (containerKey !== fittedContainerKeyRef.current && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [36, 36], maxZoom: 14 });
      fittedContainerKeyRef.current = containerKey;
    } else if (containerKey !== fittedContainerKeyRef.current) {
      map.setView([37.0662, 37.3833], 12);
      fittedContainerKeyRef.current = containerKey;
    }
  }, [containers, onSelect, selectedContainerId]);

  useEffect(() => {
    const selectedLayer = selectedLayerRef.current;
    if (!selectedLayer) return;

    selectedLayer.clearLayers();
    if (
      selectedPosition &&
      Number.isFinite(selectedPosition[0]) &&
      Number.isFinite(selectedPosition[1])
    ) {
      L.marker(selectedPosition, {
        icon: L.divIcon({
          className: "admin-container-picked-marker",
          html: "<span>Secim</span>",
          iconSize: [70, 34],
          iconAnchor: [35, 30],
        }),
      }).addTo(selectedLayer);
    }
  }, [selectedPosition]);

  return <div className="admin-container-map" ref={mapElementRef} aria-label="Konteyner haritasi" />;
}

function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  danger = false,
  busy = false,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  danger?: boolean;
  busy?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  if (!open) return null;

  return (
    <div className="dialog-backdrop" onMouseDown={onCancel} role="presentation">
      <section className="confirm-dialog" onMouseDown={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
        <button className="dialog-close" onClick={onCancel} type="button" aria-label="Kapat">
          <X size={18} />
        </button>
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="dialog-actions">
          <button className="row-action" onClick={onCancel} type="button">
            Vazgec
          </button>
          <button className={danger ? "primary-action danger" : "primary-action"} disabled={busy} onClick={onConfirm} type="button">
            {busy ? "Isleniyor" : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}

function containerMarkerTone(container: Container): string {
  if (container.durum === "Kritik" || container.doluluk_orani >= 85) return "critical";
  if (container.durum === "GoreveAtandi") return "assigned";
  if (container.doluluk_orani >= 70) return "watch";
  return "normal";
}
