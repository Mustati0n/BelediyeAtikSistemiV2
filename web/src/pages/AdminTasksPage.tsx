import { ClipboardList, Eye, ImageOff, MapPinned, RefreshCcw, Route, Send, Trash2, UserCheck, Workflow, X } from "lucide-react";
import L from "leaflet";
import type { FormEvent } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  DriverTask,
  Personnel,
  Vehicle,
  assignOperationTask,
  createAdminReportTask,
  deleteOperationTask,
  listOperationTasks,
  listPersonnel,
  listVehicles,
} from "../api";

type AssignmentForm = {
  task_id: string;
  sofor_id: string;
  arac_id: string;
  planlanan_tarih: string;
  sira_no: string;
};

type NewTaskForm = {
  aciklama: string;
  enlem: string;
  boylam: string;
};

const emptyForm: AssignmentForm = {
  task_id: "",
  sofor_id: "",
  arac_id: "",
  planlanan_tarih: "",
  sira_no: "",
};

const emptyNewTaskForm: NewTaskForm = {
  aciklama: "",
  enlem: "",
  boylam: "",
};
const GAZIANTEP_CENTER: [number, number] = [37.0662, 37.3833];
const GAZIANTEP_BOUNDS = L.latLngBounds([36.45, 36.55], [37.65, 38.45]);

function formatTaskOption(task: DriverTask): string {
  const description =
    task.kaynak.aciklama.length > 58
      ? `${task.kaynak.aciklama.slice(0, 58)}...`
      : task.kaynak.aciklama;
  return `#${task.id} / ${task.kaynak.tip} / ${description}`;
}

export function AdminTasksPage({ token }: { token: string }) {
  const [tasks, setTasks] = useState<DriverTask[]>([]);
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [form, setForm] = useState<AssignmentForm>(emptyForm);
  const [newTaskForm, setNewTaskForm] = useState<NewTaskForm>(emptyNewTaskForm);
  const [statusFilter, setStatusFilter] = useState("Tum Durumlar");
  const [typeFilter, setTypeFilter] = useState("Tum Tipler");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [creatingTask, setCreatingTask] = useState(false);
  const [selectedTask, setSelectedTask] = useState<DriverTask | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);
    try {
      const [taskData, personnelData, vehicleData] = await Promise.all([
        listOperationTasks(token),
        listPersonnel(token),
        listVehicles(token),
      ]);
      setTasks(taskData);
      setPersonnel(personnelData);
      setVehicles(vehicleData);
      setForm((current) => ({
        ...current,
        task_id: current.task_id || String(taskData[0]?.id || ""),
        sofor_id:
          current.sofor_id ||
          String(personnelData.find((person) => person.rol.ad === "Sofor" && person.aktif_mi)?.id || ""),
        arac_id:
          current.arac_id ||
          String(vehicleData.find((vehicle) => vehicle.durum === "Aktif")?.id || ""),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Gorev havuzu alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const drivers = useMemo(
    () => personnel.filter((person) => person.rol.ad === "Sofor" && person.aktif_mi),
    [personnel],
  );
  const activeVehicles = useMemo(
    () => vehicles.filter((vehicle) => vehicle.durum === "Aktif"),
    [vehicles],
  );

  const assignableTasks = useMemo(
    () => tasks.filter((task) => task.durum === "Bekliyor" || task.durum === "Atandi"),
    [tasks],
  );

  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const matchesStatus = statusFilter === "Tum Durumlar" || task.durum === statusFilter;
      const matchesType = typeFilter === "Tum Tipler" || task.kaynak.tip === typeFilter;
      return matchesStatus && matchesType;
    });
  }, [tasks, statusFilter, typeFilter]);

  const waitingCount = tasks.filter((task) => task.durum === "Bekliyor").length;
  const assignedCount = tasks.filter((task) => task.durum === "Atandi").length;
  const inProgressCount = tasks.filter((task) => task.durum === "Islemde").length;
  const taskTypes = useMemo(() => {
    return ["Ihbar", "Konteyner"].map((type) => ({
      type,
      count: tasks.filter((task) => task.kaynak.tip === type).length,
      waiting: tasks.filter((task) => task.kaynak.tip === type && task.durum === "Bekliyor").length,
    }));
  }, [tasks]);
  const driverLoad = useMemo(() => {
    return drivers
      .map((driver) => ({
        id: driver.id,
        name: driver.ad_soyad,
        assigned: 0,
      }))
      .sort((a, b) => a.assigned - b.assigned)
      .slice(0, 5);
  }, [drivers]);
  const nextSuggestedOrder = useMemo(() => {
    const usedOrders = tasks
      .map((task) => task.sira_no)
      .filter((order): order is number => typeof order === "number" && Number.isFinite(order));
    return usedOrders.length > 0 ? Math.max(...usedOrders) + 1 : 1;
  }, [tasks]);

  async function handleAssign(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const taskId = Number(form.task_id);
    const driverId = Number(form.sofor_id);
    const vehicleId = Number(form.arac_id);
    const order = form.sira_no ? Number(form.sira_no) : null;

    if (!taskId || !driverId) {
      setError("Gorev ve sofor secimi zorunludur.");
      return;
    }

    setSaving(true);
    try {
      await assignOperationTask(token, taskId, {
        sofor_id: driverId,
        arac_id: vehicleId || null,
        planlanan_tarih: form.planlanan_tarih
          ? new Date(form.planlanan_tarih).toISOString()
          : null,
        sira_no: order,
      });
      setMessage(`${taskId} numarali gorev sofore atandi.`);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Gorev atanamadi.");
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const lat = Number(newTaskForm.enlem);
    const lng = Number(newTaskForm.boylam);
    if (!newTaskForm.aciklama.trim() || newTaskForm.aciklama.trim().length < 5) {
      setError("Yeni gorev aciklamasi en az 5 karakter olmalidir.");
      return;
    }
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      setError("Haritadan bir nokta secin veya gecerli koordinat girin.");
      return;
    }

    setCreatingTask(true);
    try {
      const response = await createAdminReportTask(token, {
        aciklama: newTaskForm.aciklama.trim(),
        enlem: lat.toFixed(7),
        boylam: lng.toFixed(7),
        fotograf_url: null,
      });
      setMessage(`#${response.gorev_id} numarali yeni gorev havuza eklendi.`);
      setNewTaskForm(emptyNewTaskForm);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Yeni gorev olusturulamadi.");
    } finally {
      setCreatingTask(false);
    }
  }

  async function handleDeleteTask(task: DriverTask) {
    if (!window.confirm(`#${task.id} numarali gorev havuzdan silinsin mi?`)) return;
    setError("");
    setMessage("");
    setSaving(true);
    try {
      await deleteOperationTask(token, task.id);
      setMessage(`#${task.id} numarali gorev silindi.`);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Gorev silinemedi.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <div>
          <p>GOREV HAVUZU</p>
          <h1>Gorev Atama ve Operasyon Planlama</h1>
          <span>
            Bekleyen ihbar ve kritik konteyner gorevlerini aktif soforlere ve araclara atayin.
            Atanan gorevler sofor paneline otomatik duser.
          </span>
        </div>

        <div className="fleet-stat-card">
          <ClipboardList size={34} />
          <strong>{waitingCount}</strong>
          <span>Bekleyen Gorev</span>
          <small>{assignedCount} gorev atanmis</small>
        </div>
      </section>

      <section className="admin-summary-row" aria-label="Gorev ozetleri">
        <article>
          <span>Acik Gorev</span>
          <strong>{tasks.length}</strong>
        </article>
        <article>
          <span>Bekleyen</span>
          <strong>{waitingCount}</strong>
        </article>
        <article>
          <span>Atanmis</span>
          <strong>{assignedCount}</strong>
        </article>
        <article>
          <span>Islemde</span>
          <strong>{inProgressCount}</strong>
        </article>
      </section>

      <section className="task-map-planner">
        <div className="task-map-card">
          <div className="panel-heading">
            <div>
              <h3>Haritadan Yeni Gorev Olustur</h3>
              <p>
                Haritada bir noktaya tiklayin; koordinatlar otomatik dolsun ve gorev havuzuna
                yeni ihbar gorevi acilsin.
              </p>
            </div>
            <span className="map-count-pill">{tasks.length} acik gorev</span>
          </div>
          <AdminTaskPickerMap
            tasks={tasks}
            selected={
              newTaskForm.enlem && newTaskForm.boylam
                ? { lat: Number(newTaskForm.enlem), lng: Number(newTaskForm.boylam) }
                : null
            }
            onPick={(lat, lng) =>
              setNewTaskForm((current) => ({
                ...current,
                enlem: lat.toFixed(7),
                boylam: lng.toFixed(7),
              }))
            }
          />
        </div>

        <form className="new-task-form" onSubmit={handleCreateTask}>
          <strong>Yeni Gorev Bilgisi</strong>
          <label>
            Aciklama
            <textarea
              value={newTaskForm.aciklama}
              onChange={(event) =>
                setNewTaskForm({ ...newTaskForm, aciklama: event.target.value })
              }
              placeholder="Atik birikmesi, tasma, cevre kirliligi..."
            />
          </label>
          <div className="geo-grid">
            <label>
              Enlem
              <input
                inputMode="decimal"
                value={newTaskForm.enlem}
                onChange={(event) =>
                  setNewTaskForm({ ...newTaskForm, enlem: event.target.value })
                }
                placeholder="Haritadan secin"
              />
            </label>
            <label>
              Boylam
              <input
                inputMode="decimal"
                value={newTaskForm.boylam}
                onChange={(event) =>
                  setNewTaskForm({ ...newTaskForm, boylam: event.target.value })
                }
                placeholder="Haritadan secin"
              />
            </label>
          </div>
          <button
            className="primary-action"
            disabled={creatingTask || !newTaskForm.aciklama.trim() || !newTaskForm.enlem}
            type="submit"
          >
            <Send size={18} />
            {creatingTask ? "Olusturuluyor" : "Gorev Olustur"}
          </button>
        </form>
      </section>

      <section className="ops-planning-grid">
        <article className="ops-planning-panel">
          <div className="panel-heading">
            <div>
              <h3>Gorev Dagilimi</h3>
              <p>Kaynak tipine gore havuz yogunlugu</p>
            </div>
            <Workflow size={20} />
          </div>
          <div className="density-list">
            {taskTypes.map((item) => {
              const percent = tasks.length > 0 ? Math.round((item.count / tasks.length) * 100) : 0;
              return (
                <div key={item.type}>
                  <span>{item.type}</span>
                  <strong>{item.count}</strong>
                  <i><b style={{ width: `${percent}%` }} /></i>
                  <small>{item.waiting} bekleyen / %{percent}</small>
                </div>
              );
            })}
          </div>
        </article>

        <article className="ops-planning-panel">
          <div className="panel-heading">
            <div>
              <h3>Sofor Uygunlugu</h3>
              <p>Atama formuna hizli aktarim</p>
            </div>
            <UserCheck size={20} />
          </div>
          <div className="driver-load-list">
            {driverLoad.map((driver) => (
              <button
                key={driver.id}
                type="button"
                onClick={() => setForm((current) => ({ ...current, sofor_id: String(driver.id) }))}
              >
                <strong>{driver.name}</strong>
                <span>aktif ve atanabilir</span>
              </button>
            ))}
          </div>
        </article>
      </section>

      <section className="form-panel action-panel">
        <div className="panel-heading">
          <div>
            <h3>Gorev Ata</h3>
            <p>Atama icin aktif sofor ve istenirse aktif arac secin.</p>
          </div>
          <button className="icon-button" onClick={loadData} type="button" title="Yenile">
            <RefreshCcw size={18} />
          </button>
        </div>

        <form className="assignment-form" onSubmit={handleAssign}>
          <label>
            Gorev
            <select value={form.task_id} onChange={(event) => setForm({ ...form, task_id: event.target.value })}>
              <option value="">Gorev secin</option>
              {assignableTasks.map((task) => (
                <option key={task.id} value={task.id}>
                  {formatTaskOption(task)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sofor
            <select value={form.sofor_id} onChange={(event) => setForm({ ...form, sofor_id: event.target.value })}>
              <option value="">Sofor secin</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.ad_soyad}
                </option>
              ))}
            </select>
          </label>
          <label>
            Arac
            <select value={form.arac_id} onChange={(event) => setForm({ ...form, arac_id: event.target.value })}>
              <option value="">Aracsiz ata</option>
              {activeVehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.plaka} / {vehicle.tip}
                </option>
              ))}
            </select>
          </label>
          <label>
            Plan Tarihi
            <input
              type="datetime-local"
              value={form.planlanan_tarih}
              onChange={(event) => setForm({ ...form, planlanan_tarih: event.target.value })}
            />
          </label>
          <label>
            Sira
            <input
              inputMode="numeric"
              value={form.sira_no}
              onChange={(event) => setForm({ ...form, sira_no: event.target.value })}
              placeholder="1"
            />
          </label>
          <div className="assignment-actions">
            <button
              className="row-action"
              onClick={() => setForm({ ...form, sira_no: String(nextSuggestedOrder) })}
              type="button"
            >
              Sira Oner
            </button>
            <button className="primary-action" disabled={saving || assignableTasks.length === 0} type="submit">
              <Send size={18} />
              {saving ? "Ataniyor" : "Ata"}
            </button>
          </div>
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
          Gorev Tipi
          <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
            <option>Tum Tipler</option>
            <option>Ihbar</option>
            <option>Konteyner</option>
          </select>
        </label>
        <label>
          Durum
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option>Tum Durumlar</option>
            <option>Bekliyor</option>
            <option>Atandi</option>
            <option>Islemde</option>
          </select>
        </label>
      </section>

      <section className="data-panel">
        <div className="table-title">
          <strong>Acik Gorevler</strong>
          <span>{loading ? "Yukleniyor" : `${filteredTasks.length} kayit gosteriliyor`}</span>
        </div>

        <div className="task-list">
          {filteredTasks.map((task) => (
            <article className="task-card" key={task.id}>
              <div className="task-main">
                <div>
                  <strong>
                    #{task.id} / {task.kaynak.tip}
                  </strong>
                  <span>
                    {shortText(task.kaynak.aciklama, 92)}
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
                <button className="row-action" onClick={() => setSelectedTask(task)} type="button">
                  <Eye size={16} />
                  Detay
                </button>
                <button
                  className="row-action danger"
                  disabled={saving || task.durum === "Islemde"}
                  onClick={() => handleDeleteTask(task)}
                  type="button"
                >
                  <Trash2 size={16} />
                  Sil
                </button>
              </div>
            </article>
          ))}

          {!loading && filteredTasks.length === 0 && (
            <div className="empty-state">
              <ClipboardList size={22} />
              Acik gorev bulunamadi.
            </div>
          )}
        </div>
      </section>

      <TaskDetailDialog task={selectedTask} onClose={() => setSelectedTask(null)} />
    </div>
  );
}

function TaskDetailDialog({ task, onClose }: { task: DriverTask | null; onClose: () => void }) {
  if (!task) return null;

  const hasPhoto = Boolean(task.kaynak.fotograf_url);

  return (
    <div className="dialog-backdrop" onMouseDown={onClose} role="presentation">
      <section
        className={`task-detail-dialog ${hasPhoto ? "with-photo" : ""}`}
        onMouseDown={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <button className="dialog-close" onClick={onClose} type="button" aria-label="Kapat">
          <X size={18} />
        </button>
        <div className="task-detail-heading">
          <span>{task.kaynak.tip} Detayi</span>
          <h3>#{task.id} numarali gorev</h3>
          <b className={`status-pill ${task.durum.toLowerCase()}`}>{task.durum}</b>
        </div>

        <div className="task-detail-body">
          {hasPhoto ? (
            <figure className="task-report-photo">
              <img alt={`#${task.id} ihbar fotografi`} src={task.kaynak.fotograf_url || ""} />
            </figure>
          ) : (
            <div className="task-report-photo empty">
              <ImageOff size={34} />
              <strong>Fotograf yok</strong>
              <span>Ihbar fotograf eklenmeden gonderilmis.</span>
            </div>
          )}

          <div className="task-report-info">
            <div>
              <span>Aciklama</span>
              <p>{task.kaynak.aciklama}</p>
            </div>
            <div className="task-report-facts">
              <div>
                <span>Kaynak</span>
                <strong>{task.kaynak.tip} #{task.kaynak.id}</strong>
              </div>
              <div>
                <span>Kaynak Durumu</span>
                <strong>{task.kaynak.durum}</strong>
              </div>
              <div>
                <span>Oncelik</span>
                <strong>{task.oncelik}</strong>
              </div>
              <div>
                <span>Sira</span>
                <strong>{task.sira_no || "-"}</strong>
              </div>
              <div>
                <span>Koordinat</span>
                <strong>{task.kaynak.enlem}, {task.kaynak.boylam}</strong>
              </div>
              <div>
                <span>Arac</span>
                <strong>
                  {task.kullanilan_arac
                    ? `${task.kullanilan_arac.plaka} / ${task.kullanilan_arac.tip}`
                    : "Atanmadi"}
                </strong>
              </div>
              {task.kaynak.doluluk_orani !== null && task.kaynak.doluluk_orani !== undefined && (
                <div>
                  <span>Doluluk</span>
                  <strong>{task.kaynak.doluluk_orani}%</strong>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function shortText(value: string, maxLength: number): string {
  return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value;
}

function AdminTaskPickerMap({
  tasks,
  selected,
  onPick,
}: {
  tasks: DriverTask[];
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
    }).setView(GAZIANTEP_CENTER, 12);
    map.setMaxBounds(GAZIANTEP_BOUNDS);
    map.setMinZoom(9);
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap",
    }).addTo(map);
    const markerLayer = L.layerGroup().addTo(map);
    map.on("click", (event) => {
      if (!GAZIANTEP_BOUNDS.contains(event.latlng)) return;
      onPick(event.latlng.lat, event.latlng.lng);
    });

    mapRef.current = map;
    markerLayerRef.current = markerLayer;
    window.setTimeout(() => map.invalidateSize(), 150);

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
    const bounds: L.LatLngTuple[] = [GAZIANTEP_CENTER];

    tasks.forEach((task) => {
      const lat = Number(task.kaynak.enlem);
      const lng = Number(task.kaynak.boylam);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
      if (!GAZIANTEP_BOUNDS.contains([lat, lng])) return;
      bounds.push([lat, lng]);
      L.marker([lat, lng], {
        icon: L.divIcon({
          className: `task-map-marker ${task.durum.toLowerCase()}`,
          html: `<span>${task.id}</span><small>${task.kaynak.tip}</small>`,
          iconSize: [66, 48],
          iconAnchor: [33, 44],
          popupAnchor: [0, -38],
        }),
      })
        .bindPopup(`<strong>#${task.id}</strong><br />${task.kaynak.aciklama}<br />${task.durum}`)
        .addTo(markerLayer);
    });

    if (selected && Number.isFinite(selected.lat) && Number.isFinite(selected.lng)) {
      bounds.push([selected.lat, selected.lng]);
      L.marker([selected.lat, selected.lng], {
        icon: L.divIcon({
          className: "task-map-marker selected",
          html: "<span>+</span><small>Yeni</small>",
          iconSize: [66, 48],
          iconAnchor: [33, 44],
        }),
      }).addTo(markerLayer);
    }

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    } else {
      map.setView(GAZIANTEP_CENTER, 12);
    }
    window.setTimeout(() => map.invalidateSize(), 80);
  }, [tasks, selected]);

  return <div className="admin-task-picker-map" ref={mapElementRef} aria-label="Gorev konumu secim haritasi" />;
}
