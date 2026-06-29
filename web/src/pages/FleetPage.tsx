import { Activity, Gauge, Plus, RefreshCcw, Save, Truck, Wrench } from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  Vehicle,
  VehicleStatus,
  createVehicle,
  listVehicles,
  scrapVehicleSale,
  updateVehicle,
} from "../api";

const vehicleTypes = [
  "Sikistirmali Cop Kamyonu",
  "Konteyner Yikama Araci",
  "Geri Donusum Kamyonu",
  "Konteyner Tasiyici",
  "Yol Supurme Araci",
  "Tibbi Atik Araci",
  "Vakumlu Arac",
];
const statuses: VehicleStatus[] = ["Aktif", "Bakimda", "Pasif", "Hurda"];

type FormState = {
  plaka: string;
  tip: string;
  kapasite_kg: string;
};

export function FleetPage({ token }: { token: string }) {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("Tum Tipler");
  const [statusFilter, setStatusFilter] = useState("Tum Durumlar");
  const [form, setForm] = useState<FormState>({
    plaka: "",
    tip: vehicleTypes[0],
    kapasite_kg: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [scrapVehicleId, setScrapVehicleId] = useState<number | null>(null);
  const [scrapAmount, setScrapAmount] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadVehicles() {
    setError("");
    setLoading(true);
    try {
      setVehicles(await listVehicles(token));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Arac listesi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadVehicles();
  }, []);

  const filteredVehicles = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("tr-TR");
    return vehicles.filter((vehicle) => {
      const matchesSearch =
        !needle ||
        vehicle.plaka.toLocaleLowerCase("tr-TR").includes(needle) ||
        vehicle.tip.toLocaleLowerCase("tr-TR").includes(needle);
      const matchesType = typeFilter === "Tum Tipler" || vehicle.tip === typeFilter;
      const matchesStatus = statusFilter === "Tum Durumlar" || vehicle.durum === statusFilter;
      return matchesSearch && matchesType && matchesStatus;
    });
  }, [vehicles, search, typeFilter, statusFilter]);

  const types = useMemo(
    () => ["Tum Tipler", ...Array.from(new Set(vehicles.map((vehicle) => vehicle.tip)))],
    [vehicles],
  );

  const activeCount = vehicles.filter((vehicle) => vehicle.durum === "Aktif").length;
  const maintenanceCount = vehicles.filter((vehicle) => vehicle.durum === "Bakimda").length;
  const passiveCount = vehicles.filter((vehicle) => vehicle.durum === "Pasif").length;
  const totalCapacity = vehicles.reduce((sum, vehicle) => sum + vehicle.kapasite_kg, 0);
  const activeCapacity = vehicles
    .filter((vehicle) => vehicle.durum === "Aktif")
    .reduce((sum, vehicle) => sum + vehicle.kapasite_kg, 0);
  const operationalRatio = vehicles.length > 0 ? Math.round((activeCount / vehicles.length) * 100) : 0;
  const typeDensity = useMemo(() => {
    return Array.from(new Set(vehicles.map((vehicle) => vehicle.tip))).map((type) => {
      const typedVehicles = vehicles.filter((vehicle) => vehicle.tip === type);
      return {
        type,
        count: typedVehicles.length,
        active: typedVehicles.filter((vehicle) => vehicle.durum === "Aktif").length,
      };
    });
  }, [vehicles]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const capacity = Number(form.kapasite_kg);
    if (!form.plaka.trim() || !Number.isFinite(capacity) || capacity <= 0) {
      setError("Plaka ve pozitif kapasite zorunludur.");
      return;
    }

    setSaving(true);
    try {
      await createVehicle(token, {
        plaka: form.plaka.trim(),
        tip: form.tip,
        kapasite_kg: capacity,
      });
      setForm({ plaka: "", tip: vehicleTypes[0], kapasite_kg: "" });
      setMessage("Yeni arac kaydi olusturuldu.");
      await loadVehicles();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Arac olusturulamadi.");
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(vehicle: Vehicle, durum: VehicleStatus) {
    if (durum === "Hurda") {
      setScrapVehicleId(vehicle.id);
      setScrapAmount("");
      return;
    }
    setError("");
    setMessage("");
    try {
      const updated = await updateVehicle(token, vehicle.id, { durum });
      setVehicles((current) =>
        current.map((item) => (item.id === vehicle.id ? updated : item)),
      );
      setMessage(`${vehicle.plaka} durumu guncellendi.`);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Arac durumu guncellenemedi.");
    }
  }

  async function handleScrapSale(vehicle: Vehicle) {
    const amount = Number(scrapAmount);
    if (!Number.isFinite(amount) || amount < 0) {
      setError("Hurda satis tutari 0 veya pozitif olmalidir.");
      return;
    }
    setError("");
    setMessage("");
    setSaving(true);
    try {
      const response = await scrapVehicleSale(token, vehicle.id, {
        satis_tutari: amount.toFixed(2),
        aciklama: `${vehicle.plaka} hurda arac satis geliri`,
      });
      setVehicles((current) => current.map((item) => (item.id === vehicle.id ? response.arac : item)));
      setMessage(response.mesaj);
      setScrapVehicleId(null);
      setScrapAmount("");
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Arac hurda satisi yapilamadi.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <div>
          <p>FILO KONTROL</p>
          <h1>Arac ve Filo Yonetimi</h1>
          <span>
            Belediye filosundaki araclari yonetin, plaka ve kapasite bilgilerini takip edin,
            aktif / pasif / bakimda durumlarini kontrol edin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <Truck size={34} />
          <strong>{activeCount}</strong>
          <span>Operasyonel Arac</span>
          <small>{maintenanceCount} arac bakimda</small>
        </div>
      </section>

      <section className="admin-summary-row" aria-label="Filo ozetleri">
        <article>
          <span>Toplam Arac</span>
          <strong>{vehicles.length}</strong>
        </article>
        <article>
          <span>Aktif</span>
          <strong>{activeCount}</strong>
        </article>
        <article>
          <span>Bakimda</span>
          <strong>{maintenanceCount}</strong>
        </article>
        <article>
          <span>Pasif</span>
          <strong>{passiveCount}</strong>
        </article>
      </section>

      <section className="fleet-command-grid">
        <article className="fleet-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Operasyon Hazirligi</h3>
              <p>Aktif filo orani ve toplam kapasite</p>
            </div>
            <Activity size={20} />
          </div>
          <div className="fill-pulse">
            <strong>{operationalRatio}%</strong>
            <span>aktif filo</span>
            <i><b style={{ width: `${operationalRatio}%` }} /></i>
            <small>{activeCapacity.toLocaleString("tr-TR")} / {totalCapacity.toLocaleString("tr-TR")} kg kapasite aktif</small>
          </div>
        </article>

        <article className="fleet-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Arac Tipi Dagilimi</h3>
              <p>Operasyon kapasitesi tip bazinda</p>
            </div>
            <Gauge size={20} />
          </div>
          <div className="density-list">
            {typeDensity.map((item) => {
              const percent = vehicles.length > 0 ? Math.round((item.count / vehicles.length) * 100) : 0;
              return (
                <div key={item.type}>
                  <span>{item.type}</span>
                  <strong>{item.count}</strong>
                  <i><b style={{ width: `${percent}%` }} /></i>
                  <small>{item.active} aktif / %{percent}</small>
                </div>
              );
            })}
          </div>
        </article>

        <article className="fleet-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Servis Sinyali</h3>
              <p>Bakim ve pasif arac takibi</p>
            </div>
            <Wrench size={20} />
          </div>
          <div className="fleet-signal-list">
            <button type="button" onClick={() => setStatusFilter("Bakimda")}>
              <strong>{maintenanceCount}</strong>
              <span>Bakimda</span>
            </button>
            <button type="button" onClick={() => setStatusFilter("Pasif")}>
              <strong>{passiveCount}</strong>
              <span>Pasif</span>
            </button>
          </div>
        </article>
      </section>

      <section className="form-panel action-panel">
        <div className="panel-heading">
          <div>
            <h3>Yeni Arac Ekle</h3>
            <p>Plaka, tip ve kapasite girerek filoya yeni arac tanimlayin.</p>
          </div>
          <button className="icon-button" onClick={loadVehicles} type="button" title="Yenile">
            <RefreshCcw size={18} />
          </button>
        </div>

        <form className="vehicle-form" onSubmit={handleCreate}>
          <label>
            Plaka
            <input
              value={form.plaka}
              onChange={(event) => setForm({ ...form, plaka: event.target.value })}
              placeholder="34 ABC 123"
            />
          </label>
          <label>
            Arac Tipi
            <select value={form.tip} onChange={(event) => setForm({ ...form, tip: event.target.value })}>
              {vehicleTypes.map((type) => (
                <option key={type}>{type}</option>
              ))}
            </select>
          </label>
          <label>
            Kapasite kg
            <input
              value={form.kapasite_kg}
              onChange={(event) => setForm({ ...form, kapasite_kg: event.target.value })}
              inputMode="numeric"
              placeholder="12000"
            />
          </label>
          <button className="primary-action" disabled={saving || !form.plaka.trim()} type="submit">
            <Save size={18} />
            {saving ? "Kaydediliyor" : "Kaydet"}
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
            placeholder="Plaka veya tip ile ara..."
          />
        </label>
        <label>
          Arac Tipi
          <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
            {types.map((type) => (
              <option key={type}>{type}</option>
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

      <section className="list-context-bar" aria-label="Filo filtre ozeti">
        <div>
          <strong>{filteredVehicles.length}</strong>
          <span>gosterilen arac</span>
        </div>
        <div>
          <strong>{typeFilter}</strong>
          <span>tip filtresi</span>
        </div>
        <div>
          <strong>{statusFilter}</strong>
          <span>durum filtresi</span>
        </div>
        <button
          className="ghost-button"
          disabled={!search && typeFilter === "Tum Tipler" && statusFilter === "Tum Durumlar"}
          onClick={() => {
            setSearch("");
            setTypeFilter("Tum Tipler");
            setStatusFilter("Tum Durumlar");
          }}
          type="button"
        >
          Filtreleri Temizle
        </button>
      </section>

      <section className="data-panel">
        <div className="table-title">
          <strong>Arac Listesi</strong>
          <span>
            {loading
              ? "Yukleniyor"
              : `Toplam ${vehicles.length} aractan ${filteredVehicles.length} kayit gosteriliyor`}
          </span>
        </div>

        <div className="fleet-table" role="table">
          <div className="fleet-row fleet-head" role="row">
            <span>Plaka / Arac</span>
            <span>Kapasite</span>
            <span>Durum</span>
            <span>Islem</span>
          </div>

          {filteredVehicles.map((vehicle) => (
            <div className="fleet-row" key={vehicle.id} role="row">
              <span>
                <strong>{vehicle.plaka}</strong>
                <small>{vehicle.tip}</small>
              </span>
              <span>{vehicle.kapasite_kg.toLocaleString("tr-TR")} kg</span>
              <span>
                <b className={`status-pill ${vehicle.durum.toLowerCase()}`}>{vehicle.durum}</b>
              </span>
              <span>
                <div className="row-control">
                  <small>Durum degistir</small>
                  <select
                    value={vehicle.durum}
                    onChange={(event) =>
                      handleStatusChange(vehicle, event.target.value as VehicleStatus)
                    }
                  >
                    {statuses.map((status) => (
                      <option key={status}>{status}</option>
                    ))}
                  </select>
                  {scrapVehicleId === vehicle.id && (
                    <div className="scrap-sale-control">
                      <input
                        inputMode="decimal"
                        value={scrapAmount}
                        onChange={(event) => setScrapAmount(event.target.value.replace(/[^\d.,]/g, "").replace(",", "."))}
                        placeholder="Hurda satis TL"
                      />
                      <button className="row-action" disabled={saving} onClick={() => handleScrapSale(vehicle)} type="button">
                        Sat
                      </button>
                    </div>
                  )}
                </div>
              </span>
            </div>
          ))}

          {!loading && filteredVehicles.length === 0 && (
            <div className="empty-state">
              <Plus size={22} />
              Kayit bulunamadi.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
