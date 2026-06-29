import { LocateFixed, Search, Send, ShieldCheck, ImagePlus, XCircle } from "lucide-react";
import L from "leaflet";
import type { FormEvent } from "react";
import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  CitizenReportStatus,
  apiBaseUrl,
  createCitizenReport,
  getCitizenReportStatus,
  uploadCitizenReportPhoto,
} from "../api";

type ReportForm = {
  aciklama: string;
  enlem: string;
  boylam: string;
  fotograf_url: string;
};

const defaultForm: ReportForm = {
  aciklama: "",
  enlem: "",
  boylam: "",
  fotograf_url: "",
};

const gaziantepBounds = {
  minLat: 36.45,
  maxLat: 37.65,
  minLng: 36.55,
  maxLng: 38.45,
};

function isInsideGaziantep(lat: number, lng: number): boolean {
  return (
    lat >= gaziantepBounds.minLat &&
    lat <= gaziantepBounds.maxLat &&
    lng >= gaziantepBounds.minLng &&
    lng <= gaziantepBounds.maxLng
  );
}

export function CitizenReportPage() {
  const [form, setForm] = useState<ReportForm>(defaultForm);
  const [busy, setBusy] = useState(false);
  const [locating, setLocating] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [photoPreview, setPhotoPreview] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [locationStatus, setLocationStatus] = useState("");
  const [statusQuery, setStatusQuery] = useState("");
  const [statusResult, setStatusResult] = useState<CitizenReportStatus | null>(null);
  const [error, setError] = useState("");
  const [statusError, setStatusError] = useState("");
  const [success, setSuccess] = useState<{ ihbarId: number; gorevId: number; message: string } | null>(null);

  useEffect(() => {
    return () => {
      if (photoPreview) URL.revokeObjectURL(photoPreview);
    };
  }, [photoPreview]);

  function useLocation() {
    setError("");
    setLocationStatus("");
    setLocating(true);

    if (!navigator.geolocation) {
      setError("Tarayiciniz konum bilgisini desteklemiyor.");
      setLocating(false);
      return;
    }

    if (!window.isSecureContext) {
      setError(
        "Tarayici konum izni icin HTTPS ister. HTTPS adresini kullanabilir veya haritadan nokta secebilirsiniz.",
      );
      setLocating(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setForm((current) => ({
          ...current,
          enlem: position.coords.latitude.toFixed(7),
          boylam: position.coords.longitude.toFixed(7),
        }));
        setLocationStatus(
          `Konum alindi. Yaklasik hassasiyet ${Math.round(position.coords.accuracy)} metre.`,
        );
        setLocating(false);
      },
      (geoError) => {
        const reason =
          geoError.code === geoError.PERMISSION_DENIED
            ? "Konum izni reddedildi."
            : geoError.code === geoError.TIMEOUT
              ? "Konum istegi zaman asimina ugradi."
              : "Konum alinamadi.";
        setError(`${reason} Haritadan nokta secebilirsiniz.`);
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }

  async function handlePhotoFile(file: File | null) {
    if (!file) return;
    setError("");
    setUploadingPhoto(true);
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    const previewUrl = URL.createObjectURL(file);
    setPhotoPreview(previewUrl);
    try {
      const response = await uploadCitizenReportPhoto(file);
      const uploadedUrl = response.fotograf_url.startsWith("/")
        ? `${apiBaseUrl().replace(/\/api\/v1$/, "")}${response.fotograf_url}`
        : response.fotograf_url;
      setForm((current) => ({ ...current, fotograf_url: uploadedUrl }));
      setLocationStatus(`${response.dosya_adi} yuklendi ve ihbara eklendi.`);
    } catch (exc) {
      setPhotoPreview("");
      URL.revokeObjectURL(previewUrl);
      setError(exc instanceof ApiError ? exc.message : "Fotograf yuklenemedi.");
    } finally {
      setUploadingPhoto(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function clearPhoto() {
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    setPhotoPreview("");
    setForm((current) => ({ ...current, fotograf_url: "" }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess(null);

    const lat = Number(form.enlem);
    const lon = Number(form.boylam);
    if (!form.aciklama.trim() || form.aciklama.trim().length < 5) {
      setError("Ihbar aciklamasi en az 5 karakter olmalidir.");
      return;
    }
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      setError("Gecerli enlem ve boylam girin.");
      return;
    }
    if (!isInsideGaziantep(lat, lon)) {
      setError("Ihbar konumu Gaziantep il sinirlari icinde olmalidir.");
      return;
    }

    setBusy(true);
    try {
      const response = await createCitizenReport({
        aciklama: form.aciklama.trim(),
        enlem: lat.toFixed(7),
        boylam: lon.toFixed(7),
        fotograf_url: form.fotograf_url.trim() || null,
      });
      setSuccess({
        ihbarId: response.ihbar_id,
        gorevId: response.gorev_id,
        message: response.mesaj,
      });
      setStatusQuery(String(response.ihbar_id));
      setForm(defaultForm);
      clearPhoto();
      setLocationStatus("");
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Ihbar gonderilemedi.");
    } finally {
      setBusy(false);
    }
  }

  async function queryStatus() {
    setStatusError("");
    setStatusResult(null);
    const ihbarId = Number(statusQuery);
    if (!Number.isInteger(ihbarId) || ihbarId <= 0) {
      setStatusError("Gecerli bir ihbar numarasi girin.");
      return;
    }

    try {
      setStatusResult(await getCitizenReportStatus(ihbarId));
    } catch (exc) {
      setStatusError(exc instanceof ApiError ? exc.message : "Ihbar durumu alinamadi.");
    }
  }

  return (
    <main className="citizen-page">
      <section className="citizen-hero">
        <div className="citizen-copy">
          <div className="brand-mark">S</div>
          <p>VATANDAS IHBAR PORTALI</p>
          <h1>Atik, tasma veya cevre kirliligi ihbarini hizlica bildir.</h1>
          <span>
            Konum ve aciklama gonderildiginde ihbar belediye gorev havuzuna duserek operasyon
            ekibi tarafindan planlanir.
          </span>
        </div>

        <form className="citizen-form" onSubmit={submit}>
          <div className="citizen-form-head">
            <ShieldCheck size={22} />
            <div>
              <strong>Ihbar Bilgileri</strong>
              <span>Uyelik gerektirmez</span>
            </div>
          </div>

          <div className="citizen-report-grid">
            <div className="citizen-report-main">
              <label>
                Aciklama
                <textarea
                  value={form.aciklama}
                  onChange={(event) => setForm({ ...form, aciklama: event.target.value })}
                  placeholder="Konteyner tasiyor, atik yola dokulmus..."
                />
              </label>

              <div className="citizen-photo-panel">
                <div>
                  <strong>Fotograf</strong>
                  <span>Opsiyonel olarak cihazdan fotograf yukleyin veya link ekleyin</span>
                </div>
                <input
                  ref={fileInputRef}
                  accept="image/jpeg,image/png,image/webp"
                  capture="environment"
                  onChange={(event) => handlePhotoFile(event.target.files?.[0] || null)}
                  type="file"
                />
                <div className="citizen-photo-actions">
                  <button className="row-action" disabled={uploadingPhoto} onClick={() => fileInputRef.current?.click()} type="button">
                    <ImagePlus size={16} />
                    {uploadingPhoto ? "Yukleniyor" : "Fotograf Sec"}
                  </button>
                  {(form.fotograf_url || photoPreview) && (
                    <button className="row-action" onClick={clearPhoto} type="button">
                      <XCircle size={16} />
                      Kaldir
                    </button>
                  )}
                </div>
                {photoPreview && <img alt="Secilen ihbar fotografi" src={photoPreview} />}
                <label>
                  Fotograf URL
                  <input
                    value={form.fotograf_url}
                    onChange={(event) => setForm({ ...form, fotograf_url: event.target.value })}
                    placeholder="Opsiyonel link"
                  />
                </label>
              </div>
            </div>

            <div className="citizen-location-card">
              <CitizenLocationMap
                selected={
                  form.enlem && form.boylam
                    ? { lat: Number(form.enlem), lng: Number(form.boylam) }
                    : null
                }
                onPick={(lat, lng) => {
                  if (!isInsideGaziantep(lat, lng)) {
                    setError("Ihbar konumu Gaziantep il sinirlari icinde olmalidir.");
                    return;
                  }
                  setForm((current) => ({
                    ...current,
                    enlem: lat.toFixed(7),
                    boylam: lng.toFixed(7),
                  }));
                  setLocationStatus("Haritadan secilen koordinat forma eklendi.");
                  setError("");
                }}
              />
              <div className="geo-grid">
                <label>
                  Enlem
                  <input aria-readonly="true" readOnly value={form.enlem} placeholder="Haritadan secin" />
                </label>
                <label>
                  Boylam
                  <input aria-readonly="true" readOnly value={form.boylam} placeholder="Haritadan secin" />
                </label>
              </div>
              <button className="row-action location-button" onClick={useLocation} type="button">
                <LocateFixed size={18} />
                {locating ? "Konum aliniyor" : "Konumumu Kullan"}
              </button>
              <small className="geo-helper">
                Konum elle yazilmaz; haritadan nokta secin veya tarayici konumunu kullanin.
              </small>
            </div>
          </div>

          <InlineNotice
            message={locationStatus}
            type="success"
            onClose={() => setLocationStatus("")}
          />

          <InlineNotice message={error} type="error" onClose={() => setError("")} />

          <InlineNotice
            message={success ? `${success.message} Ihbar #${success.ihbarId}, gorev #${success.gorevId}.` : ""}
            type="success"
            onClose={() => setSuccess(null)}
          />

          <button className="primary-button" disabled={busy} type="submit">
            <Send size={18} />
            {busy ? "Gonderiliyor" : "Ihbari Gonder"}
          </button>

          <div className="citizen-status-panel">
            <strong>Ihbar Durumu Sorgula</strong>
            <div>
              <input
                inputMode="numeric"
                value={statusQuery}
                onChange={(event) => setStatusQuery(event.target.value)}
                placeholder="Ihbar no"
              />
              <button className="row-action" onClick={queryStatus} type="button">
                <Search size={16} />
                Sorgula
              </button>
            </div>
            <InlineNotice message={statusError} type="error" onClose={() => setStatusError("")} />
            {statusResult && (
              <div className="citizen-status-result">
                <span>Ihbar #{statusResult.ihbar_id}</span>
                <strong>{statusResult.durum}</strong>
                <small>
                  Gorev #{statusResult.gorev_id || "-"} / {statusResult.gorev_durumu || "Planlanmadi"}
                </small>
              </div>
            )}
          </div>
        </form>
      </section>
    </main>
  );
}

function CitizenLocationMap({
  selected,
  onPick,
}: {
  selected: { lat: number; lng: number } | null;
  onPick: (lat: number, lng: number) => void;
}) {
  const mapElementRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerLayerRef = useRef<L.LayerGroup | null>(null);

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
    map.on("click", (event) => onPick(event.latlng.lat, event.latlng.lng));

    mapRef.current = map;
    markerLayerRef.current = markerLayer;

    return () => {
      map.remove();
      mapRef.current = null;
      markerLayerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const markerLayer = markerLayerRef.current;
    if (!map || !markerLayer) return;

    markerLayer.clearLayers();

    if (selected && Number.isFinite(selected.lat) && Number.isFinite(selected.lng)) {
      L.marker([selected.lat, selected.lng], {
        icon: L.divIcon({
          className: "task-map-marker selected",
          html: "<span>+</span><small>Secim</small>",
          iconSize: [66, 48],
          iconAnchor: [33, 44],
        }),
      }).addTo(markerLayer);
      map.setView([selected.lat, selected.lng], 14);
    }
  }, [selected]);

  return (
    <div className="citizen-map-picker">
      <div ref={mapElementRef} aria-label="Ihbar konumu secim haritasi" />
      <span>Haritaya tiklayarak ihbar konumunu secebilirsiniz.</span>
    </div>
  );
}
