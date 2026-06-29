import { CheckCircle2, MapPinned, Play, RefreshCcw, Route } from "lucide-react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useMemo, useRef, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  DriverTask,
  TaskResult,
  WasteType,
  completeDriverTask,
  createDelivery,
  listDriverTasks,
  startDriverTask,
} from "../api";

const taskResults: Array<{ label: string; value: TaskResult }> = [
  { label: "Tamamlandi", value: "Tamamlandi" },
  { label: "Ulasilamadi", value: "Ulasilamadi" },
  { label: "Yanlis Ihbar", value: "YanlisIhbar" },
  { label: "Tekrar Kontrol", value: "TekrarKontrolGerekli" },
];

const GAZIANTEP_CENTER: [number, number] = [37.0662, 37.3833];
const wasteTypes: WasteType[] = ["Plastik", "Cam", "Metal", "Kagit", "Organik", "Diger"];

type RoadRouteState = {
  status: "idle" | "loading" | "ready" | "fallback" | "error";
  distanceKm: number;
  durationMin: number;
};

const emptyRoadRoute: RoadRouteState = {
  status: "idle",
  distanceKm: 0,
  durationMin: 0,
};

export function DriverTasksPage({ token }: { token: string }) {
  const [tasks, setTasks] = useState<DriverTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<DriverTask | null>(null);
  const [driverLocation, setDriverLocation] = useState<[number, number] | null>(null);
  const [roadRoute, setRoadRoute] = useState<RoadRouteState>(emptyRoadRoute);
  const [routeMode, setRouteMode] = useState<"manual" | "optimized">("manual");
  const [result, setResult] = useState<TaskResult>("Tamamlandi");
  const [note, setNote] = useState("");
  const [deliveryKg, setDeliveryKg] = useState("");
  const [deliveryWasteType, setDeliveryWasteType] = useState<WasteType>("Diger");
  const [loading, setLoading] = useState(true);
  const [busyTaskId, setBusyTaskId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadTasks() {
    setError("");
    setLoading(true);
    try {
      setTasks(await listDriverTasks(token));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Gorev listesi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  const manualSortedTasks = useMemo(
    () =>
      [...tasks].sort((a, b) => {
        const orderA = a.sira_no ?? 9999;
        const orderB = b.sira_no ?? 9999;
        return orderA - orderB || b.oncelik - a.oncelik || a.id - b.id;
      }),
    [tasks],
  );
  const sortedTasks = useMemo(() => {
    if (routeMode === "manual") return manualSortedTasks;
    return optimizeTaskOrder(manualSortedTasks, driverLocation ?? GAZIANTEP_CENTER);
  }, [driverLocation, manualSortedTasks, routeMode]);

  const inProgressCount = tasks.filter((task) => task.durum === "Islemde").length;
  const assignedCount = tasks.filter((task) => task.durum === "Atandi").length;
  const routePoints = useMemo(() => buildRoutePoints(sortedTasks), [sortedTasks]);
  const directDistanceKm = useMemo(() => calculateRouteDistance(routePoints), [routePoints]);
  const shownDistanceKm =
    roadRoute.status === "ready" && roadRoute.distanceKm > 0
      ? roadRoute.distanceKm
      : directDistanceKm;

  function requestLocation() {
    if (!navigator.geolocation) {
      setError("Tarayici konum destegi vermiyor.");
      return;
    }

    setError("");
    if (!window.isSecureContext) {
      setError(
        "Konum icin HTTPS gerekir. https://77.83.37.48 adresinden acin veya haritayi Gaziantep merkezli kullanin.",
      );
      setDriverLocation(GAZIANTEP_CENTER);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setDriverLocation([position.coords.latitude, position.coords.longitude]);
        setMessage("Sofor konumu haritaya eklendi.");
      },
      (geoError) => {
        const reason =
          geoError.code === geoError.PERMISSION_DENIED
            ? "Konum izni reddedildi."
            : geoError.code === geoError.TIMEOUT
              ? "Konum istegi zaman asimina ugradi."
              : "Tarayici konumu okuyamadi.";
        setDriverLocation(GAZIANTEP_CENTER);
        setError(`${reason} Harita Gaziantep merkezli gosteriliyor.`);
      },
      { enableHighAccuracy: true, timeout: 8000 },
    );
  }

  async function handleStart(task: DriverTask) {
    setBusyTaskId(task.id);
    setError("");
    setMessage("");
    try {
      await startDriverTask(token, task.id);
      setMessage(`${task.id} numarali gorev baslatildi.`);
      await loadTasks();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Gorev baslatilamadi.");
    } finally {
      setBusyTaskId(null);
    }
  }

  async function handleComplete() {
    if (!selectedTask) return;

    setBusyTaskId(selectedTask.id);
    setError("");
    setMessage("");
    const amount = Number(deliveryKg);
    if (result === "Tamamlandi" && (!Number.isFinite(amount) || amount <= 0)) {
      setError("Tamamlanan gorev icin aractaki atik kg bilgisi zorunludur.");
      setBusyTaskId(null);
      return;
    }
    try {
      await completeDriverTask(token, selectedTask.id, {
        sonuc: result,
        aciklama: note.trim() || null,
      });
      if (result === "Tamamlandi") {
        const delivery = await createDelivery(token, {
          toplam_kg: amount.toFixed(3),
          atik_tipi: deliveryWasteType,
          aciklama: `Gorev #${selectedTask.id} / ${selectedTask.kaynak.tip} / ${note.trim() || selectedTask.kaynak.aciklama}`,
        });
        setMessage(`${selectedTask.id} numarali gorev sonuclandirildi ve teslim #${delivery.id} tesise dustu.`);
      } else {
        setMessage(`${selectedTask.id} numarali gorev sonuclandirildi.`);
      }
      setSelectedTask(null);
      setNote("");
      setResult("Tamamlandi");
      setDeliveryKg("");
      setDeliveryWasteType("Diger");
      await loadTasks();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Gorev sonuclandirilamadi.");
    } finally {
      setBusyTaskId(null);
    }
  }

  return (
    <div className="page-stack driver-page">
      <section className="driver-hero">
        <div>
          <p>SOFOR OPERASYONU</p>
          <h1>Gunluk Gorev Kokpiti</h1>
          <span>
            Gaziantep icindeki atanmis duraklari haritadan takip edin, rotanizi gorun,
            gorevi baslatip saha sonucunu tek ekrandan kaydedin.
          </span>
        </div>

        <div className="driver-hero-actions">
          <button className="row-action" onClick={loadTasks} type="button">
            <RefreshCcw size={16} />
            Yenile
          </button>
          <button className="primary-action" onClick={requestLocation} type="button">
            <MapPinned size={16} />
            Konumumu Kullan
          </button>
          <button
            className="row-action"
            onClick={() => setRouteMode((mode) => (mode === "manual" ? "optimized" : "manual"))}
            type="button"
          >
            <Route size={16} />
            {routeMode === "manual" ? "Rota Optimize Et" : "Manuel Siraya Don"}
          </button>
        </div>
      </section>

      <section className="driver-stat-grid">
        <article>
          <Route size={22} />
          <span>Aktif Gorev</span>
          <strong>{tasks.length}</strong>
        </article>
        <article>
          <Play size={22} />
          <span>Atanan</span>
          <strong>{assignedCount}</strong>
        </article>
        <article>
          <CheckCircle2 size={22} />
          <span>Islemde</span>
          <strong>{inProgressCount}</strong>
        </article>
        <article>
          <MapPinned size={22} />
          <span>{roadRoute.status === "ready" ? "Yol Rotasi" : "Tahmini Rota"}</span>
          <strong>{shownDistanceKm.toFixed(1)} km</strong>
        </article>
      </section>

      <section className="driver-map-workspace">
        <div className="driver-map-card">
          <div className="map-toolbar">
            <div>
              <strong>Gaziantep Operasyon Haritasi</strong>
              <span>
                OpenStreetMap altligi, OSRM yol rotasi ve {routeMode === "manual" ? "admin sirasi" : "optimize sira"}
              </span>
            </div>
            <div className="map-toolbar-actions">
              <button className="row-action" onClick={loadTasks} type="button">
                <RefreshCcw size={16} />
                Gorevleri Yenile
              </button>
              <button className="row-action" onClick={requestLocation} type="button">
                <MapPinned size={16} />
                Konum
              </button>
              <button
                className="row-action"
                onClick={() => setRouteMode((mode) => (mode === "manual" ? "optimized" : "manual"))}
                type="button"
              >
                <Route size={16} />
                {routeMode === "manual" ? "Optimize" : "Manuel"}
              </button>
            </div>
          </div>

          <DriverRouteMap
            driverLocation={driverLocation}
            onRoadRouteChange={setRoadRoute}
            onTaskSelect={setSelectedTask}
            points={routePoints}
          />
        </div>

        <aside className="driver-route-board">
          <div>
            <p>ROTA PLANI</p>
            <h3>Siradaki Duraklar</h3>
            <span>
              {loading
                ? "Gorevler yukleniyor"
                : roadRoute.status === "ready"
                  ? `${sortedTasks.length} durak / ${roadRoute.durationMin.toFixed(0)} dk yol / ${
                      routeMode === "manual" ? "manuel sira" : "optimize sira"
                    }`
                  : `${sortedTasks.length} aktif durak / ${
                      routeMode === "manual" ? "manuel sira" : "optimize sira"
                    }`}
            </span>
          </div>

          <div className={`road-route-status ${roadRoute.status}`}>
            <Route size={18} />
            <div>
              <strong>
                {roadRoute.status === "loading"
                  ? "Yol rotasi hesaplaniyor"
                  : roadRoute.status === "ready"
                    ? "Yol rotasi hazir"
                    : roadRoute.status === "fallback"
                      ? "Kus bakisi yedek rota"
                      : roadRoute.status === "error"
                        ? "Yol rotasi alinamadi"
                        : "Rota bekleniyor"}
              </strong>
              <span>
                {roadRoute.status === "ready"
                  ? `${roadRoute.distanceKm.toFixed(1)} km / ${roadRoute.durationMin.toFixed(0)} dk`
                  : "OSRM yol motoru gorev sirasina gore rota cizer."}
              </span>
            </div>
          </div>

          <div className="route-strip">
          {sortedTasks.slice(0, 6).map((task, index) => (
            <div className="route-stop" key={task.id}>
              <strong>{task.sira_no ?? index + 1}</strong>
              <span>{task.kaynak.tip}</span>
              <small>
                {task.kaynak.aciklama}
                {task.kaynak.doluluk_orani != null ? ` / %${task.kaynak.doluluk_orani} dolu` : ""}
              </small>
            </div>
          ))}
          {!loading && sortedTasks.length === 0 && (
            <div className="empty-state">
              <MapPinned size={22} />
              Bugun icin atanmis gorev yok.
            </div>
          )}
          </div>

          <div className="route-board-footer">
            <div>
              <strong>{sortedTasks.filter((task) => task.kaynak.tip === "Konteyner").length}</strong>
              <span>Konteyner gorevi</span>
            </div>
            <div>
              <strong>{driverLocation ? "Aktif" : "Kapali"}</strong>
              <span>Sofor konumu</span>
            </div>
          </div>
        </aside>
      </section>

      <InlineNotice
        message={error || message}
        type={error ? "error" : "success"}
        onClose={() => {
          setError("");
          setMessage("");
        }}
      />

      <section className="data-panel driver-task-panel">
        <div className="table-title">
          <strong>Gorev Listesi</strong>
          <span>{loading ? "Yukleniyor" : `${sortedTasks.length} aktif gorev`}</span>
        </div>

        <div className="task-list">
          {sortedTasks.map((task) => (
            <article className="task-card" key={task.id}>
              <div className="task-main">
                <div>
                  <strong>
                    {task.sira_no ? `${task.sira_no}. ` : ""}
                    {task.kaynak.aciklama}
                  </strong>
                  <span>
                    {task.kaynak.tip} / {task.kaynak.durum} / Oncelik {task.oncelik}
                  </span>
                </div>
                <b className={`status-pill ${task.durum.toLowerCase()}`}>{task.durum}</b>
              </div>

              <div className="task-meta">
                <span>
                  <MapPinned size={16} />
                  {task.kaynak.enlem}, {task.kaynak.boylam}
                </span>
                <span>
                  <Route size={16} />
                  {task.kullanilan_arac
                    ? `${task.kullanilan_arac.plaka} / ${task.kullanilan_arac.tip}`
                    : "Arac atanmadi"}
                </span>
              </div>

              <div className="task-actions">
                <button
                  className="row-action"
                  disabled={busyTaskId === task.id || task.durum !== "Atandi"}
                  onClick={() => handleStart(task)}
                  type="button"
                >
                  <Play size={16} />
                  Baslat
                </button>
                <button
                  className="primary-action"
                  disabled={busyTaskId === task.id || task.durum !== "Islemde"}
                  onClick={() => setSelectedTask(task)}
                  type="button"
                >
                  <CheckCircle2 size={16} />
                  Sonuclandir
                </button>
              </div>
            </article>
          ))}

          {!loading && sortedTasks.length === 0 && (
            <div className="empty-state">
              <MapPinned size={22} />
              Kayit bulunamadi.
            </div>
          )}
        </div>
      </section>

      {selectedTask && (
        <div className="modal-backdrop" role="presentation" onClick={() => setSelectedTask(null)}>
          <section className="result-modal" role="dialog" onClick={(event) => event.stopPropagation()}>
            <div className="panel-heading">
              <div>
                <h3>{selectedTask.durum === "Atandi" ? "Gorev Detayi" : "Gorev Sonuclandir"}</h3>
                <p>
                  {selectedTask.kaynak.aciklama}
                  {selectedTask.kaynak.doluluk_orani != null
                    ? ` / %${selectedTask.kaynak.doluluk_orani} dolu`
                    : ""}
                </p>
              </div>
            </div>

            <div className="task-detail-grid">
              <div>
                <span>Durum</span>
                <strong>{selectedTask.durum}</strong>
              </div>
              <div>
                <span>Kaynak</span>
                <strong>{selectedTask.kaynak.tip}</strong>
              </div>
              <div>
                <span>Sira</span>
                <strong>{selectedTask.sira_no ?? "-"}</strong>
              </div>
              <div>
                <span>Oncelik</span>
                <strong>{selectedTask.oncelik}</strong>
              </div>
            </div>

            {selectedTask.durum === "Islemde" && (
              <>
                <label>
                  Sonuc
                  <select value={result} onChange={(event) => setResult(event.target.value as TaskResult)}>
                    {taskResults.map((item) => (
                      <option key={item.value} value={item.value}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Aciklama
                  <textarea
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="Opsiyonel saha notu"
                  />
                </label>
                {result === "Tamamlandi" && (
                  <div className="task-delivery-grid">
                    <label>
                      Aractaki Atik Kg
                      <input
                        inputMode="decimal"
                        value={deliveryKg}
                        onChange={(event) => setDeliveryKg(event.target.value.replace(/[^\d.,]/g, "").replace(",", "."))}
                        placeholder="120"
                      />
                    </label>
                    <label>
                      Atik Tipi
                      <select value={deliveryWasteType} onChange={(event) => setDeliveryWasteType(event.target.value as WasteType)}>
                        {wasteTypes.map((type) => <option key={type}>{type}</option>)}
                      </select>
                    </label>
                  </div>
                )}
              </>
            )}

            <div className="modal-actions">
              <button className="row-action" onClick={() => setSelectedTask(null)} type="button">
                Vazgec
              </button>
              {selectedTask.durum === "Atandi" ? (
                <button
                  className="primary-action"
                  disabled={busyTaskId === selectedTask.id}
                  onClick={async () => {
                    await handleStart(selectedTask);
                    setSelectedTask(null);
                  }}
                  type="button"
                >
                  <Play size={16} />
                  Gorevi Baslat
                </button>
              ) : (
                <button
                  className="primary-action"
                  disabled={busyTaskId === selectedTask.id || selectedTask.durum !== "Islemde"}
                  onClick={handleComplete}
                  type="button"
                >
                  Kaydet
                </button>
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

type RoutePoint = {
  task: DriverTask;
  lat: number;
  lng: number;
};

function buildRoutePoints(tasks: DriverTask[]): RoutePoint[] {
  return tasks
    .map((task) => ({
      task,
      lat: Number(task.kaynak.enlem),
      lng: Number(task.kaynak.boylam),
    }))
    .filter((point) => Number.isFinite(point.lat) && Number.isFinite(point.lng));
}

function calculateRouteDistance(points: RoutePoint[]): number {
  return points.slice(1).reduce((total, point, index) => {
    const previous = points[index];
    return total + haversineKm(previous.lat, previous.lng, point.lat, point.lng);
  }, 0);
}

function optimizeTaskOrder(tasks: DriverTask[], origin: [number, number]): DriverTask[] {
  const remaining = [...tasks];
  const ordered: DriverTask[] = [];
  let currentLat = origin[0];
  let currentLng = origin[1];

  while (remaining.length > 0) {
    let bestIndex = 0;
    let bestDistance = Number.POSITIVE_INFINITY;
    remaining.forEach((task, index) => {
      const lat = Number(task.kaynak.enlem);
      const lng = Number(task.kaynak.boylam);
      const distance = Number.isFinite(lat) && Number.isFinite(lng)
        ? haversineKm(currentLat, currentLng, lat, lng)
        : Number.POSITIVE_INFINITY;
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = index;
      }
    });

    const [nextTask] = remaining.splice(bestIndex, 1);
    ordered.push(nextTask);
    currentLat = Number(nextTask.kaynak.enlem);
    currentLng = Number(nextTask.kaynak.boylam);
  }

  return ordered;
}

function haversineKm(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const earthRadiusKm = 6371;
  const latDelta = toRadians(lat2 - lat1);
  const lngDelta = toRadians(lng2 - lng1);
  const a =
    Math.sin(latDelta / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(lngDelta / 2) ** 2;
  return 2 * earthRadiusKm * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function toRadians(value: number): number {
  return (value * Math.PI) / 180;
}

type OsrmRouteResponse = {
  routes?: Array<{
    distance: number;
    duration: number;
    geometry?: {
      coordinates?: Array<[number, number]>;
    };
  }>;
};

function DriverRouteMap({
  driverLocation,
  onRoadRouteChange,
  onTaskSelect,
  points,
}: {
  driverLocation: [number, number] | null;
  onRoadRouteChange: (route: RoadRouteState) => void;
  onTaskSelect: (task: DriverTask) => void;
  points: RoutePoint[];
}) {
  const mapElementRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.LayerGroup | null>(null);
  const [roadGeometry, setRoadGeometry] = useState<[number, number][]>([]);

  useEffect(() => {
    if (!mapElementRef.current || mapRef.current) return;

    mapRef.current = L.map(mapElementRef.current, {
      center: GAZIANTEP_CENTER,
      zoom: 12,
      zoomControl: true,
      attributionControl: true,
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap",
      maxZoom: 19,
    }).addTo(mapRef.current);
    layerRef.current = L.layerGroup().addTo(mapRef.current);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const waypointPoints = driverLocation
      ? [{ lat: driverLocation[0], lng: driverLocation[1] }, ...points]
      : points;

    if (waypointPoints.length < 2) {
      setRoadGeometry([]);
      onRoadRouteChange({
        ...emptyRoadRoute,
        status: waypointPoints.length === 1 ? "fallback" : "idle",
      });
      return;
    }

    async function fetchRoadRoute() {
      onRoadRouteChange({
        ...emptyRoadRoute,
        status: "loading",
      });

      const coordinateText = waypointPoints
        .map((point) => `${point.lng},${point.lat}`)
        .join(";");
      const url =
        `https://router.project-osrm.org/route/v1/driving/${coordinateText}` +
        "?overview=full&geometries=geojson&steps=false";

      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("OSRM route failed");
        const payload = (await response.json()) as OsrmRouteResponse;
        const route = payload.routes?.[0];
        if (!route?.geometry?.coordinates?.length) throw new Error("OSRM route empty");

        const geometry = route.geometry.coordinates.map(([lng, lat]) => [lat, lng] as [number, number]);
        if (cancelled) return;

        setRoadGeometry(geometry);
        onRoadRouteChange({
          status: "ready",
          distanceKm: route.distance / 1000,
          durationMin: route.duration / 60,
        });
      } catch {
        if (cancelled) return;
        setRoadGeometry([]);
        onRoadRouteChange({
          status: "fallback",
          distanceKm: calculateRouteDistance(points),
          durationMin: 0,
        });
      }
    }

    fetchRoadRoute();
    return () => {
      cancelled = true;
    };
  }, [driverLocation, onRoadRouteChange, points]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    const latLngs = points.map((point) => L.latLng(point.lat, point.lng));
    const roadLatLngs = roadGeometry.map(([lat, lng]) => L.latLng(lat, lng));
    if (roadLatLngs.length > 1) {
      L.polyline(roadLatLngs, {
        color: "#10752d",
        weight: 5,
        opacity: 0.86,
      }).addTo(layer);
    } else if (latLngs.length > 1) {
      L.polyline(latLngs, {
        color: "#8a5a04",
        dashArray: "8 8",
        weight: 4,
        opacity: 0.76,
      }).addTo(layer);
    }

    points.forEach((point, index) => {
      L.marker([point.lat, point.lng], {
        icon: createRouteIcon(point, index),
      })
        .bindPopup(
          `<strong>${point.task.kaynak.aciklama}</strong><br/>${point.task.kaynak.tip} / ${point.task.kaynak.durum}${
            point.task.kaynak.doluluk_orani != null
              ? `<br/>Doluluk: %${point.task.kaynak.doluluk_orani}`
              : ""
          }`,
        )
        .on("click", () => onTaskSelect(point.task))
        .addTo(layer);
    });

    if (driverLocation) {
      L.marker(driverLocation, { icon: createDriverIcon() })
        .bindPopup("<strong>Sofor konumu</strong>")
        .addTo(layer);
    }

    const boundsPoints = [
      ...(roadLatLngs.length > 0 ? roadLatLngs : latLngs),
      ...(driverLocation ? [L.latLng(driverLocation)] : []),
    ];
    if (boundsPoints.length > 0) {
      map.fitBounds(L.latLngBounds(boundsPoints), { padding: [42, 42], maxZoom: 14 });
    } else {
      map.setView(GAZIANTEP_CENTER, 12);
    }
  }, [driverLocation, onTaskSelect, points, roadGeometry]);

  return <div className="driver-leaflet-map" ref={mapElementRef} aria-label="Gaziantep rota haritasi" />;
}

function createRouteIcon(point: RoutePoint, index: number): L.DivIcon {
  const fill =
    point.task.kaynak.tip === "Konteyner" && point.task.kaynak.doluluk_orani != null
      ? `%${point.task.kaynak.doluluk_orani}`
      : point.task.kaynak.tip;
  return L.divIcon({
    className: "leaflet-route-marker",
    html: `<span>${point.task.sira_no ?? index + 1}</span><small>${fill}</small>`,
    iconSize: [64, 48],
    iconAnchor: [32, 42],
    popupAnchor: [0, -38],
  });
}

function createDriverIcon(): L.DivIcon {
  return L.divIcon({
    className: "leaflet-driver-marker",
    html: "<span>S</span><small>Konum</small>",
    iconSize: [64, 48],
    iconAnchor: [32, 42],
    popupAnchor: [0, -38],
  });
}
