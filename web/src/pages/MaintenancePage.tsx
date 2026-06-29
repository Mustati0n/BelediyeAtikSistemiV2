import {
  AlertTriangle,
  BarChart3,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  Download,
  Gauge,
  RefreshCcw,
  Save,
  ShieldCheck,
  Truck,
  Wrench,
} from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  MaintenanceRecord,
  Vehicle,
  completeMaintenanceTechnical,
  createMaintenanceRecord,
  listMaintenanceRecords,
  listVehicles,
} from "../api";

const tabs = ["Ozet", "Yeni Bakim", "Acik Bakimlar", "Maliyetler", "Gecmis"] as const;
const maintenanceTypes = ["Periyodik", "Ariza", "Motor", "Fren", "Lastik", "Elektrik", "Yag Degisimi", "Kaporta"];
const priorityOptions = ["Dusuk", "Normal", "Kritik"];

type Tab = (typeof tabs)[number];

type FormState = {
  arac_id: string;
  aciklama: string;
  maliyet_tl: string;
  tarih: string;
  bakim_turu: string;
  oncelik: string;
  parca_maliyeti_tl: string;
  iscilik_maliyeti_tl: string;
  tedarikci: string;
  kilometre: string;
  planlanan_tarih: string;
};

const emptyForm: FormState = {
  arac_id: "",
  aciklama: "",
  maliyet_tl: "",
  tarih: "",
  bakim_turu: "Periyodik",
  oncelik: "Normal",
  parca_maliyeti_tl: "",
  iscilik_maliyeti_tl: "",
  tedarikci: "",
  kilometre: "",
  planlanan_tarih: "",
};

export function MaintenancePage({ token, readOnly = false }: { token: string; readOnly?: boolean }) {
  const [activeTab, setActiveTab] = useState<Tab>("Ozet");
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [records, setRecords] = useState<MaintenanceRecord[]>([]);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [vehicleFilter, setVehicleFilter] = useState("Tum Araclar");
  const [statusFilter, setStatusFilter] = useState("Tum Durumlar");
  const [priorityFilter, setPriorityFilter] = useState("Tum Oncelikler");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyRecordId, setBusyRecordId] = useState<number | null>(null);
  const [selectedCostRecordId, setSelectedCostRecordId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);
    try {
      const [vehicleData, recordData] = await Promise.all([
        listVehicles(token),
        listMaintenanceRecords(token),
      ]);
      setVehicles(vehicleData);
      setRecords(recordData);
      setForm((current) => ({
        ...current,
        arac_id: current.arac_id || String(vehicleData.find((vehicle) => vehicle.durum === "Aktif")?.id || ""),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Bakim verisi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const activeVehicles = useMemo(
    () => vehicles.filter((vehicle) => vehicle.durum === "Aktif"),
    [vehicles],
  );
  const openRecords = records.filter((record) => record.durum !== "Tamamlandi" && record.durum !== "Iptal");
  const completedRecords = records.filter((record) => record.durum === "Tamamlandi");
  const criticalRecords = openRecords.filter((record) => record.oncelik === "Kritik");
  const maintenanceVehicles = vehicles.filter((vehicle) => vehicle.durum === "Bakimda").length;
  const pendingExpenseTotal = records
    .filter((record) => (record.gider_durumu || "Beklemede") === "Beklemede")
    .reduce((sum, record) => sum + Number(record.maliyet_tl), 0);
  const totalCost = records.reduce((sum, record) => sum + Number(record.maliyet_tl), 0);
  const averageCost = records.length > 0 ? totalCost / records.length : 0;
  const topVehicle = useMemo(() => {
    const counts = new Map<string, number>();
    records.forEach((record) => counts.set(record.arac_plaka, (counts.get(record.arac_plaka) || 0) + 1));
    return [...counts.entries()].sort((a, b) => b[1] - a[1])[0];
  }, [records]);

  const filteredRecords = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("tr-TR");
    return records.filter((record) => {
      const matchesVehicle = vehicleFilter === "Tum Araclar" || record.arac_plaka === vehicleFilter;
      const matchesStatus = statusFilter === "Tum Durumlar" || record.durum === statusFilter;
      const matchesPriority = priorityFilter === "Tum Oncelikler" || (record.oncelik || "Normal") === priorityFilter;
      const haystack = [
        record.arac_plaka,
        record.aciklama,
        record.bakim_turu || "",
        record.tedarikci || "",
      ].join(" ").toLocaleLowerCase("tr-TR");
      return matchesVehicle && matchesStatus && matchesPriority && (!normalizedQuery || haystack.includes(normalizedQuery));
    });
  }, [records, vehicleFilter, statusFilter, priorityFilter, query]);

  useEffect(() => {
    if (activeTab !== "Maliyetler") return;
    if (filteredRecords.length === 0) {
      setSelectedCostRecordId(null);
      return;
    }
    if (!selectedCostRecordId || !filteredRecords.some((record) => record.id === selectedCostRecordId)) {
      setSelectedCostRecordId(filteredRecords[0].id);
    }
  }, [activeTab, filteredRecords, selectedCostRecordId]);

  const selectedCostRecord = filteredRecords.find((record) => record.id === selectedCostRecordId) || null;
  const accountingRecords = selectedCostRecord ? [selectedCostRecord] : filteredRecords;
  const calculatedMaintenanceTotal =
    Number(form.parca_maliyeti_tl || 0) + Number(form.iscilik_maliyeti_tl || 0);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (readOnly) return;
    setError("");
    setMessage("");

    const vehicleId = Number(form.arac_id);
    const parts = Number(form.parca_maliyeti_tl || 0);
    const labor = Number(form.iscilik_maliyeti_tl || 0);
    const total = parts + labor;
    const mileage = Number(form.kilometre || 0);

    if (!vehicleId || !form.aciklama.trim() || !Number.isFinite(total) || total < 0) {
      setError("Arac, aciklama ve gecerli maliyet zorunludur.");
      return;
    }

    setSaving(true);
    try {
      const created = await createMaintenanceRecord(token, {
        arac_id: vehicleId,
        aciklama: form.aciklama.trim(),
        maliyet_tl: total.toFixed(2),
        tarih: form.tarih ? new Date(form.tarih).toISOString() : null,
        bakim_turu: form.bakim_turu || null,
        oncelik: form.oncelik || null,
        parca_maliyeti_tl: form.parca_maliyeti_tl ? parts.toFixed(2) : null,
        iscilik_maliyeti_tl: form.iscilik_maliyeti_tl ? labor.toFixed(2) : null,
        tedarikci: form.tedarikci.trim() || null,
        kilometre: Number.isFinite(mileage) && mileage > 0 ? mileage : null,
        planlanan_tarih: form.planlanan_tarih ? new Date(form.planlanan_tarih).toISOString() : null,
      });
      setMessage(`${created.arac_plaka} icin ${created.bakim_turu || "bakim"} kaydi acildi ve muhasebeye gider dustu.`);
      setForm({ ...emptyForm, arac_id: String(activeVehicles[0]?.id || "") });
      setActiveTab("Acik Bakimlar");
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Bakim kaydi olusturulamadi.");
    } finally {
      setSaving(false);
    }
  }

  async function handleComplete(record: MaintenanceRecord) {
    if (readOnly) return;
    setBusyRecordId(record.id);
    setError("");
    setMessage("");
    try {
      const updated = await completeMaintenanceTechnical(token, record.id);
      setMessage(`${updated.arac_plaka} teknik bakimi tamamlandi ve arac aktif hale geldi.`);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Teknik bakim tamamlanamadi.");
    } finally {
      setBusyRecordId(null);
    }
  }

  function exportCsv() {
    const rows = [
      ["ID", "Arac", "Tarih", "Tur", "Oncelik", "Durum", "Gider", "Maliyet", "Tedarikci", "Aciklama"],
      ...filteredRecords.map((record) => [
        record.id,
        record.arac_plaka,
        record.tarih,
        record.bakim_turu || "-",
        record.oncelik || "Normal",
        record.durum,
        record.gider_durumu || "Beklemede",
        record.maliyet_tl,
        record.tedarikci || "-",
        record.aciklama,
      ]),
    ];
    const csv = rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(";")).join("\n");
    const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `bakim-raporu-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="page-stack maintenance-cockpit">
      <section className="page-hero">
        <div>
          <p>BAKIM OPERASYONU</p>
          <h1>Arac Sagligi ve Servis Yonetimi</h1>
          <span>
            Arac bakimlarini planlayin, kritik arizalari ayirin, parca/iscilik maliyetini izleyin
            ve muhasebeye dusen gider surecini tek ekrandan takip edin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <Wrench size={34} />
          <strong>{openRecords.length}</strong>
          <span>Acik Bakim</span>
          <small>{maintenanceVehicles} arac serviste</small>
        </div>
      </section>

      <section className="maintenance-kpi-grid">
        <MaintenanceMetric icon={ClipboardList} label="Acik Kayit" value={openRecords.length} note="bakim" />
        <MaintenanceMetric icon={AlertTriangle} label="Kritik" value={criticalRecords.length} note="oncelikli" danger={criticalRecords.length > 0} />
        <MaintenanceMetric icon={Gauge} label="Bekleyen Gider" value={formatCurrency(pendingExpenseTotal)} note="muhasebe" />
        <MaintenanceMetric icon={BarChart3} label="Ortalama Maliyet" value={formatCurrency(averageCost)} note="kayit basi" />
      </section>

      <nav className="facility-tabs" aria-label="Bakim sekmeleri">
        {tabs.map((tab) => (
          <button className={activeTab === tab ? "active" : ""} key={tab} onClick={() => setActiveTab(tab)} type="button">
            {tab}
          </button>
        ))}
      </nav>

      <InlineNotice
        message={error || message}
        type={error ? "error" : "success"}
        onClose={() => {
          setError("");
          setMessage("");
        }}
      />

      {activeTab === "Ozet" && (
        <section className="maintenance-overview">
          <div className="data-panel maintenance-health-panel">
            <div className="table-title">
              <strong>Arac Saglik Ozeti</strong>
              <span>{vehicles.length} arac</span>
            </div>
            <div className="maintenance-health-grid">
              <HealthCard label="Aktif Arac" value={vehicles.filter((vehicle) => vehicle.durum === "Aktif").length} />
              <HealthCard label="Serviste" value={maintenanceVehicles} tone="warning" />
              <HealthCard label="Tamamlanan" value={completedRecords.length} />
              <HealthCard label="En Cok Bakim" value={topVehicle ? topVehicle[0] : "-"} note={topVehicle ? `${topVehicle[1]} kayit` : "veri yok"} />
            </div>
          </div>

          <div className="data-panel">
            <div className="table-title">
              <strong>Oncelikli Bakim Kuyrugu</strong>
              <span>{openRecords.length} acik</span>
            </div>
            <MaintenanceCardList
              records={[...openRecords].sort(compareMaintenancePriority).slice(0, 4)}
              readOnly={readOnly}
              busyRecordId={busyRecordId}
              onComplete={handleComplete}
              emptyText="Acik bakim yok."
              compact
            />
          </div>
        </section>
      )}

      {activeTab === "Yeni Bakim" && (
        <section className="form-panel maintenance-work-order">
          <div className="panel-heading">
            <div>
              <h3>Bakim Is Emri Olustur</h3>
              <p>
                {readOnly
                  ? "Admin izleme modunda kayitlar goruntulenir; islem yapilamaz."
                  : "Parca ve iscilik girilirse toplam maliyet otomatik hesaplanir ve muhasebeye gider olarak duser."}
              </p>
            </div>
            <button className="icon-button" onClick={loadData} type="button" title="Yenile">
              <RefreshCcw size={18} />
            </button>
          </div>

          <form className="maintenance-form enhanced" onSubmit={handleCreate}>
            <label>
              Arac
              <select disabled={readOnly} value={form.arac_id} onChange={(event) => setForm({ ...form, arac_id: event.target.value })}>
                <option value="">Arac secin</option>
                {activeVehicles.map((vehicle) => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.plaka} / {vehicle.tip}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Bakim Turu
              <select disabled={readOnly} value={form.bakim_turu} onChange={(event) => setForm({ ...form, bakim_turu: event.target.value })}>
                {maintenanceTypes.map((type) => <option key={type}>{type}</option>)}
              </select>
            </label>
            <label>
              Oncelik
              <select disabled={readOnly} value={form.oncelik} onChange={(event) => setForm({ ...form, oncelik: event.target.value })}>
                {priorityOptions.map((priority) => <option key={priority}>{priority}</option>)}
              </select>
            </label>
            <label>
              Parca Maliyeti
              <input inputMode="decimal" value={form.parca_maliyeti_tl} disabled={readOnly} onChange={(event) => setForm({ ...form, parca_maliyeti_tl: event.target.value })} placeholder="9000" />
            </label>
            <label>
              Iscilik
              <input inputMode="decimal" value={form.iscilik_maliyeti_tl} disabled={readOnly} onChange={(event) => setForm({ ...form, iscilik_maliyeti_tl: event.target.value })} placeholder="3500" />
            </label>
            <label>
              Toplam Maliyet
              <input
                className="computed-cost-input"
                inputMode="decimal"
                value={calculatedMaintenanceTotal > 0 ? calculatedMaintenanceTotal.toFixed(2) : ""}
                readOnly
                placeholder="Otomatik hesaplanir"
              />
            </label>
            <label>
              Tedarikci
              <input value={form.tedarikci} disabled={readOnly} onChange={(event) => setForm({ ...form, tedarikci: event.target.value })} placeholder="Servis / firma" />
            </label>
            <label>
              Kilometre
              <input inputMode="numeric" value={form.kilometre} disabled={readOnly} onChange={(event) => setForm({ ...form, kilometre: event.target.value })} placeholder="182000" />
            </label>
            <label>
              Planlanan Tarih
              <input type="datetime-local" value={form.planlanan_tarih} disabled={readOnly} onChange={(event) => setForm({ ...form, planlanan_tarih: event.target.value })} />
            </label>
            <label>
              Kayit Tarihi
              <input type="datetime-local" value={form.tarih} disabled={readOnly} onChange={(event) => setForm({ ...form, tarih: event.target.value })} />
            </label>
            <label className="maintenance-description-field">
              Aciklama
              <textarea value={form.aciklama} disabled={readOnly} onChange={(event) => setForm({ ...form, aciklama: event.target.value })} placeholder="Ariza belirtisi, yapilacak islem, servis notu..." />
            </label>
            <button className="primary-action" disabled={saving || readOnly || activeVehicles.length === 0} type="submit">
              <Save size={18} />
              {saving ? "Kaydediliyor" : "Is Emri Ac"}
            </button>
          </form>
        </section>
      )}

      {activeTab === "Acik Bakimlar" && (
        <section className="data-panel">
          <MaintenanceToolbar
            vehicles={vehicles}
            vehicleFilter={vehicleFilter}
            statusFilter={statusFilter}
            priorityFilter={priorityFilter}
            query={query}
            onVehicleFilter={setVehicleFilter}
            onStatusFilter={setStatusFilter}
            onPriorityFilter={setPriorityFilter}
            onQuery={setQuery}
            onExport={exportCsv}
          />
          <MaintenanceCardList
            records={filteredRecords.filter((record) => record.durum !== "Tamamlandi")}
            readOnly={readOnly}
            busyRecordId={busyRecordId}
            onComplete={handleComplete}
            emptyText={loading ? "Yukleniyor..." : "Acik bakim kaydi bulunamadi."}
          />
        </section>
      )}

      {activeTab === "Maliyetler" && (
        <section className="maintenance-cost-workbench">
          <CostPanel title="Maliyet Ozeti" records={records} />
          <div className="maintenance-cost-detail-grid">
            <CostPanel
              title="Filtrelenen Kayitlar"
              records={filteredRecords}
              selectedId={selectedCostRecordId}
              onSelect={setSelectedCostRecordId}
              showRecords
              showSummary={false}
            />
            <div className="data-panel maintenance-expense-panel">
              <div className="table-title">
                <strong>Muhasebe Baglantisi</strong>
                <span>
                  {selectedCostRecord
                    ? `Secili kayit #${selectedCostRecord.id}`
                    : `${accountingRecords.filter((record) => record.gider_kaydi_id).length} gider`}
                </span>
              </div>
              <div className="history-list">
                {accountingRecords.slice(0, 8).map((record) => (
                  <button
                    className={record.id === selectedCostRecordId ? "selected" : ""}
                    key={record.id}
                    onClick={() => setSelectedCostRecordId(record.id)}
                    type="button"
                  >
                    <strong>{record.arac_plaka} / {formatCurrency(Number(record.maliyet_tl))}</strong>
                    <span>Gider #{record.gider_kaydi_id || "-"} / {record.gider_durumu || "Beklemede"}</span>
                    <small>{record.bakim_turu || "Bakim"} / {record.tedarikci || "Tedarikci yok"}</small>
                  </button>
                ))}
                {accountingRecords.length === 0 && <div className="empty-state">Filtreye uygun muhasebe kaydi yok.</div>}
              </div>
            </div>
          </div>
        </section>
      )}

      {activeTab === "Gecmis" && (
        <section className="data-panel">
          <MaintenanceToolbar
            vehicles={vehicles}
            vehicleFilter={vehicleFilter}
            statusFilter={statusFilter}
            priorityFilter={priorityFilter}
            query={query}
            onVehicleFilter={setVehicleFilter}
            onStatusFilter={setStatusFilter}
            onPriorityFilter={setPriorityFilter}
            onQuery={setQuery}
            onExport={exportCsv}
          />
          <MaintenanceTimeline records={filteredRecords} loading={loading} />
        </section>
      )}
    </div>
  );
}

function MaintenanceMetric({ icon: Icon, label, value, note, danger = false }: { icon: typeof Wrench; label: string; value: number | string; note: string; danger?: boolean }) {
  return (
    <article className={`maintenance-metric ${danger ? "danger" : ""}`}>
      <Icon size={22} />
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function HealthCard({ label, value, note, tone = "normal" }: { label: string; value: number | string; note?: string; tone?: "normal" | "warning" }) {
  return (
    <article className={`maintenance-health-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note || "anlik"}</small>
    </article>
  );
}

function MaintenanceToolbar({
  vehicles,
  vehicleFilter,
  statusFilter,
  priorityFilter,
  query,
  onVehicleFilter,
  onStatusFilter,
  onPriorityFilter,
  onQuery,
  onExport,
}: {
  vehicles: Vehicle[];
  vehicleFilter: string;
  statusFilter: string;
  priorityFilter: string;
  query: string;
  onVehicleFilter: (value: string) => void;
  onStatusFilter: (value: string) => void;
  onPriorityFilter: (value: string) => void;
  onQuery: (value: string) => void;
  onExport: () => void;
}) {
  return (
    <div className="maintenance-toolbar">
      <label>
        Arama
        <input value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Plaka, aciklama, servis..." />
      </label>
      <label>
        Arac
        <select value={vehicleFilter} onChange={(event) => onVehicleFilter(event.target.value)}>
          <option>Tum Araclar</option>
          {vehicles.map((vehicle) => (
            <option key={vehicle.id}>{vehicle.plaka}</option>
          ))}
        </select>
      </label>
      <label>
        Durum
        <select value={statusFilter} onChange={(event) => onStatusFilter(event.target.value)}>
          <option>Tum Durumlar</option>
          <option>Acildi</option>
          <option>Incelemede</option>
          <option>Tamamlandi</option>
          <option>Iptal</option>
        </select>
      </label>
      <label>
        Oncelik
        <select value={priorityFilter} onChange={(event) => onPriorityFilter(event.target.value)}>
          <option>Tum Oncelikler</option>
          {priorityOptions.map((priority) => <option key={priority}>{priority}</option>)}
        </select>
      </label>
      <button className="row-action" onClick={onExport} type="button">
        <Download size={16} />
        CSV
      </button>
    </div>
  );
}

function MaintenanceCardList({
  records,
  readOnly,
  busyRecordId,
  onComplete,
  emptyText,
  compact = false,
}: {
  records: MaintenanceRecord[];
  readOnly: boolean;
  busyRecordId: number | null;
  onComplete: (record: MaintenanceRecord) => void;
  emptyText: string;
  compact?: boolean;
}) {
  return (
    <div className={compact ? "maintenance-card-list compact" : "maintenance-card-list"}>
      {records.map((record) => (
        <article className="maintenance-card" key={record.id}>
          <div className="maintenance-card-main">
            <div className={`maintenance-priority ${priorityClass(record.oncelik)}`}>
              <ShieldCheck size={18} />
              <span>{record.oncelik || "Normal"}</span>
            </div>
            <div>
              <strong>{record.arac_plaka} / {record.bakim_turu || "Bakim"}</strong>
              <p>{record.aciklama}</p>
              <small>
                {new Date(record.tarih).toLocaleString("tr-TR")} / {record.tedarikci || "Tedarikci yok"}
              </small>
            </div>
          </div>
          <div className="maintenance-card-meta">
            <span>
              <b>{formatCurrency(Number(record.maliyet_tl))}</b>
              <small>Maliyet</small>
            </span>
            <span>
              <b>{record.kilometre ? `${record.kilometre.toLocaleString("tr-TR")} km` : "-"}</b>
              <small>Kilometre</small>
            </span>
            <span>
              <b className={`status-pill ${record.durum.toLowerCase()}`}>{record.durum}</b>
              <small>Gider: {record.gider_durumu || "Beklemede"}</small>
            </span>
          </div>
          <div className="maintenance-card-actions">
            {record.planlanan_tarih && (
              <span className="maintenance-date-pill">
                <CalendarClock size={15} />
                {new Date(record.planlanan_tarih).toLocaleDateString("tr-TR")}
              </span>
            )}
            <button
              className="row-action"
              disabled={readOnly || busyRecordId === record.id || record.durum === "Tamamlandi"}
              onClick={() => onComplete(record)}
              type="button"
            >
              <CheckCircle2 size={16} />
              Tamamla
            </button>
          </div>
        </article>
      ))}
      {records.length === 0 && (
        <div className="empty-state">
          <Truck size={22} />
          {emptyText}
        </div>
      )}
    </div>
  );
}

function CostPanel({
  title,
  records,
  selectedId,
  onSelect,
  showRecords = false,
  showSummary = true,
}: {
  title: string;
  records: MaintenanceRecord[];
  selectedId?: number | null;
  onSelect?: (id: number) => void;
  showRecords?: boolean;
  showSummary?: boolean;
}) {
  const parts = records.reduce((sum, record) => sum + Number(record.parca_maliyeti_tl || 0), 0);
  const labor = records.reduce((sum, record) => sum + Number(record.iscilik_maliyeti_tl || 0), 0);
  const total = records.reduce((sum, record) => sum + Number(record.maliyet_tl), 0);
  return (
    <div className="data-panel maintenance-cost-panel">
      <div className="table-title">
        <strong>{title}</strong>
        <span>{records.length} kayit</span>
      </div>
      {showSummary && (
        <div className="cost-breakdown">
          <div>
            <span>Parca</span>
            <strong>{formatCurrency(parts)}</strong>
          </div>
          <div>
            <span>Iscilik</span>
            <strong>{formatCurrency(labor)}</strong>
          </div>
          <div>
            <span>Toplam</span>
            <strong>{formatCurrency(total)}</strong>
          </div>
        </div>
      )}
      {showRecords && (
        <div className="cost-record-picker">
          {records.slice(0, 10).map((record) => (
            <button
              className={record.id === selectedId ? "selected" : ""}
              key={record.id}
              onClick={() => onSelect?.(record.id)}
              type="button"
            >
              <span>{record.arac_plaka}</span>
              <strong>{formatCurrency(Number(record.maliyet_tl))}</strong>
              <small>{record.bakim_turu || "Bakim"} / {record.gider_durumu || "Beklemede"}</small>
            </button>
          ))}
          {records.length === 0 && <div className="empty-state">Filtreye uygun maliyet kaydi yok.</div>}
        </div>
      )}
    </div>
  );
}

function MaintenanceTimeline({ records, loading }: { records: MaintenanceRecord[]; loading: boolean }) {
  return (
    <div className="maintenance-timeline">
      {records.map((record) => (
        <article key={record.id}>
          <span className={`timeline-dot ${priorityClass(record.oncelik)}`} />
          <div>
            <strong>#{record.id} / {record.arac_plaka} / {record.bakim_turu || "Bakim"}</strong>
            <p>{record.aciklama}</p>
            <small>
              {new Date(record.tarih).toLocaleString("tr-TR")} / {record.durum} / {formatCurrency(Number(record.maliyet_tl))}
            </small>
          </div>
        </article>
      ))}
      {!loading && records.length === 0 && (
        <div className="empty-state">
          <Truck size={22} />
          Bakim gecmisi bulunamadi.
        </div>
      )}
    </div>
  );
}

function compareMaintenancePriority(a: MaintenanceRecord, b: MaintenanceRecord) {
  const order: Record<string, number> = { Kritik: 0, Normal: 1, Dusuk: 2 };
  return (order[a.oncelik || "Normal"] ?? 1) - (order[b.oncelik || "Normal"] ?? 1);
}

function priorityClass(priority?: string | null) {
  if (priority === "Kritik") return "critical";
  if (priority === "Dusuk") return "low";
  return "normal";
}

function formatCurrency(value: number) {
  return value.toLocaleString("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0,
  });
}
