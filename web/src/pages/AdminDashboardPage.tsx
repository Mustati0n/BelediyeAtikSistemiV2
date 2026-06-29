import {
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  ClipboardList,
  Factory,
  Gauge,
  History,
  MapPinned,
  RefreshCcw,
  ShieldCheck,
  SlidersHorizontal,
  Truck,
  Users,
  Wallet,
  Wrench,
} from "lucide-react";
import L from "leaflet";
import type { CSSProperties } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import {
  AdminDashboardSummary,
  ApiError,
  Container,
  CountByStatus,
  DriverTask,
  getAdminDashboard,
  listContainers,
  listOperationTasks,
} from "../api";

type Props = {
  token: string;
  onNavigate: (path: string) => void;
};

const moneyFormatter = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat("tr-TR", {
  maximumFractionDigits: 1,
});

export function AdminDashboardPage({ token, onNavigate }: Props) {
  const [summary, setSummary] = useState<AdminDashboardSummary | null>(null);
  const [containers, setContainers] = useState<Container[]>([]);
  const [tasks, setTasks] = useState<DriverTask[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setError("");
    setLoading(true);
    try {
      const [dashboardData, containerData, taskData] = await Promise.all([
        getAdminDashboard(token),
        listContainers(token),
        listOperationTasks(token),
      ]);
      setSummary(dashboardData);
      setContainers(containerData);
      setTasks(taskData);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Admin ozeti yuklenemedi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [token]);

  const attentionCount = useMemo(() => {
    if (!summary) return 0;
    return (
      findStatus(summary.konteynerler.durumlar, "Kritik") +
      summary.gorevler.bekleyen +
      findStatus(summary.bakim.durumlar, "Acildi") +
      summary.finans.bekleyen_gider_sayisi +
      summary.finans.bekleyen_gelir_sayisi +
      findStatus(summary.tesis_teslimleri.durumlar, "Beklemede")
    );
  }, [summary]);

  if (loading && !summary) {
    return <div className="state-box">Admin denetim merkezi yukleniyor</div>;
  }

  if (error && !summary) {
    return (
      <div className="state-box danger">
        <strong>Denetim merkezi acilamadi</strong>
        <span>{error}</span>
        <button onClick={load} type="button">
          <RefreshCcw size={16} />
          Tekrar dene
        </button>
      </div>
    );
  }

  if (!summary) return null;

  const activeVehicles = findStatus(summary.araclar.durumlar, "Aktif");
  const criticalContainers = findStatus(summary.konteynerler.durumlar, "Kritik");
  const watchedContainers = findStatus(summary.konteynerler.durumlar, "Izleniyor");
  const openTasks = summary.gorevler.bekleyen + summary.gorevler.atanmis + summary.gorevler.islemde;
  const pendingDeliveries = findStatus(summary.tesis_teslimleri.durumlar, "Beklemede");
  const pendingFinance =
    summary.finans.bekleyen_gider_sayisi + summary.finans.bekleyen_gelir_sayisi;
  const maintenanceOpen = findStatus(summary.bakim.durumlar, "Acildi");
  const totalSignal =
    summary.konteynerler.toplam + summary.gorevler.toplam + summary.araclar.toplam + summary.personel.toplam;
  const healthScore = Math.max(42, Math.min(98, 100 - attentionCount * 6));
  const recentLogs = summary.son_islemler.slice(0, 10);

  return (
    <div className="admin-command-dashboard">
      <section className="command-hero">
        <div className="command-hero-copy">
          <div className="command-eyebrow">
            <ShieldCheck size={18} />
            <span>Canli Denetim Merkezi</span>
          </div>
          <h1>Akilli sehir atik operasyonu tek ekranda.</h1>
          <p>
            Filo, konteyner, gorev, bakim, tesis, finans ve audit loglari ayni merkezden izlenir;
            riskli alanlar hizli aksiyon kartlariyla yonetilir.
          </p>
          <div className="command-hero-actions">
            <span className="command-hero-note">
              <ClipboardList size={18} />
              Gorev havuzu operator ekraninda yonetilir
            </span>
            <button onClick={() => onNavigate("/admin/konteynerler")} type="button">
              <MapPinned size={18} />
              Haritayi Ac
            </button>
          </div>
        </div>

        <div className="command-status-card">
          <div
            className="health-ring"
            style={{ "--score": `${healthScore}%` } as CSSProperties}
          >
            <strong>{healthScore}</strong>
            <span>skor</span>
          </div>
          <div>
            <span>Operasyon Sagligi</span>
            <strong>{attentionCount} takip kaydi</strong>
            <small>{totalSignal} toplam sinyal sistemde izleniyor</small>
          </div>
        </div>
      </section>

      <section className="command-kpi-grid" aria-label="Ana denetim metrikleri">
        <CommandKpi
          icon={Truck}
          title="Filo"
          value={summary.araclar.toplam}
          note={`${activeVehicles} aktif arac`}
          tone="green"
          onClick={() => onNavigate("/admin/filo")}
        />
        <CommandKpi
          icon={Users}
          title="Personel"
          value={summary.personel.toplam}
          note="rol bazli ekip"
          tone="blue"
          onClick={() => onNavigate("/admin/personel")}
        />
        <CommandKpi
          icon={MapPinned}
          title="Konteyner"
          value={summary.konteynerler.toplam}
          note={`${criticalContainers} kritik, ${watchedContainers} izleniyor`}
          tone="red"
          onClick={() => onNavigate("/admin/konteynerler")}
        />
        <CommandKpi
          icon={ClipboardList}
          title="Acik Gorev"
          value={openTasks}
          note={`${summary.gorevler.bekleyen} bekleyen, ${summary.gorevler.islemde} islemde`}
          tone="amber"
        />
        <CommandKpi
          icon={Wallet}
          title="Finans"
          value={pendingFinance}
          note="bekleyen onay"
          tone="blue"
          onClick={() => onNavigate("/admin/finans")}
        />
        <CommandKpi
          icon={Wrench}
          title="Bakim"
          value={maintenanceOpen}
          note="acik servis kaydi"
          tone="amber"
          onClick={() => onNavigate("/maintenance/bakim")}
        />
        <CommandKpi
          icon={SlidersHorizontal}
          title="Parametreler"
          value="9"
          note="sistem esikleri"
          tone="green"
          onClick={() => onNavigate("/admin/parametreler")}
        />
        <CommandKpi
          icon={History}
          title="Log Kayitlari"
          value={summary.son_islemler.length}
          note="son denetim kaydi"
          tone="blue"
          onClick={() => onNavigate("/admin/loglar")}
        />
      </section>

      <section className="command-grid">
        <div className="command-main">
          <section className="operations-visual">
            <div className="panel-heading">
              <div>
                <h3>Operasyon Haritasi</h3>
                <p>Kritik konteyner, bekleyen gorev ve saha akislarinin anlik ozeti</p>
              </div>
              <button className="ghost-button" onClick={() => onNavigate("/admin/konteynerler")} type="button">
                Haritaya git
                <ArrowUpRight size={16} />
              </button>
            </div>
            <DashboardOperationMap containers={containers} tasks={tasks} />
            <div className="ops-strip">
              <span>
                <AlertTriangle size={16} />
                {criticalContainers} kritik konteyner
              </span>
              <span>
                <ClipboardList size={16} />
                {summary.gorevler.atanmis} atanmis gorev
              </span>
              <span>
                <Wrench size={16} />
                {maintenanceOpen} acik bakim
              </span>
            </div>
          </section>

          <section className="command-insight-grid">
            <OperationDensityPanel
              activeVehicles={activeVehicles}
              totalVehicles={summary.araclar.toplam}
              criticalContainers={criticalContainers}
              totalContainers={summary.konteynerler.toplam}
              activePersonnel={findStatus(summary.personel.durumlar, "Sofor")}
              totalPersonnel={summary.personel.toplam}
              completedTasks={findStatus(summary.gorevler.durumlar, "Tamamlandi")}
              totalTasks={summary.gorevler.toplam}
            />
            <CriticalAlertsPanel
              alerts={[
                {
                  title: "Bekleyen gorev",
                  value: summary.gorevler.bekleyen,
                  note: "Sofor ve arac atamasi operator tarafinda bekliyor.",
                  action: "Operator takipte",
                },
                {
                  title: "Kritik konteyner",
                  value: criticalContainers,
                  note: "Doluluk esigi ustundeki saha noktalari.",
                  action: "Haritayi ac",
                  onClick: () => onNavigate("/admin/konteynerler"),
                },
                {
                  title: "Bakim plani",
                  value: maintenanceOpen,
                  note: "Teknik takip gerektiren bakim kayitlari.",
                  action: "Bakimi ac",
                  onClick: () => onNavigate("/maintenance/bakim"),
                },
                {
                  title: "Finans onayi",
                  value: pendingFinance,
                  note: "Gelir ve gider kayitlari onay bekliyor.",
                  action: "Finans ozeti",
                  onClick: () => onNavigate("/admin/finans"),
                },
              ]}
            />
          </section>

          <section className="command-chart-grid">
            <StatusPanel
              icon={ClipboardList}
              title="Gorev Akisi"
              subtitle={`${summary.gorevler.toplam} toplam gorev`}
              statuses={summary.gorevler.durumlar}
            />
            <StatusPanel
              icon={MapPinned}
              title="Konteyner Durumlari"
              subtitle={`${summary.konteynerler.toplam} saha noktasi`}
              statuses={summary.konteynerler.durumlar}
            />
            <FinancePanel
              income={Number(summary.finans.onayli_gelir_toplami)}
              expense={Number(summary.finans.onayli_gider_toplami)}
              net={Number(summary.finans.net_sonuc)}
              pending={pendingFinance}
              onClick={() => onNavigate("/admin/finans")}
            />
            <StatusPanel
              icon={Factory}
              title="Tesis Teslimleri"
              subtitle={`${pendingDeliveries} bekleyen teslim`}
              statuses={summary.tesis_teslimleri.durumlar}
            />
          </section>
        </div>

        <aside className="command-side">
          <section className="command-panel command-priority-panel">
            <div className="panel-heading">
              <div>
                <h3>Oncelikli Aksiyonlar</h3>
                <p>Bugun kontrol edilmesi gereken basliklar</p>
              </div>
              <Gauge size={20} />
            </div>
            <div className="priority-list">
              <PriorityItem
                title="Bekleyen gorevleri ata"
                value={summary.gorevler.bekleyen}
                note="Operator gorev havuzunda planlar"
              />
              <PriorityItem
                title="Kritik konteynerleri incele"
                value={criticalContainers}
                note="Harita ve doluluk kontrolu"
                onClick={() => onNavigate("/admin/konteynerler")}
              />
              <PriorityItem
                title="Finans onay kuyrugu"
                value={pendingFinance}
                note="Gider ve gelir kayitlari"
                onClick={() => onNavigate("/admin/finans")}
              />
            </div>
          </section>

          <section className="command-panel command-log-panel">
            <div className="panel-heading">
              <div>
                <h3>Son Log Kayitlari</h3>
                <p>Sistemdeki son hareketler</p>
              </div>
              <History size={20} />
            </div>
            <div className="command-timeline">
              {recentLogs.length === 0 ? (
                <div className="empty-row">Henuz islem kaydi yok.</div>
              ) : (
                recentLogs.map((log) => (
                  <button key={log.id} onClick={() => onNavigate("/admin/loglar")} type="button">
                    <span />
                    <strong>{log.islem_tipi}</strong>
                    <small>{log.aciklama}</small>
                    <em>{log.yapan || "Sistem"}</em>
                  </button>
                ))
              )}
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}

function OperationDensityPanel({
  activeVehicles,
  totalVehicles,
  criticalContainers,
  totalContainers,
  activePersonnel,
  totalPersonnel,
  completedTasks,
  totalTasks,
}: {
  activeVehicles: number;
  totalVehicles: number;
  criticalContainers: number;
  totalContainers: number;
  activePersonnel: number;
  totalPersonnel: number;
  completedTasks: number;
  totalTasks: number;
}) {
  const rows = [
    {
      label: "Aktif arac kullanimi",
      value: activeVehicles,
      total: totalVehicles,
      tone: "green",
    },
    {
      label: "Kritik konteyner yuklenmesi",
      value: criticalContainers,
      total: totalContainers,
      tone: "red",
    },
    {
      label: "Aktif personel kapsama",
      value: activePersonnel,
      total: totalPersonnel,
      tone: "blue",
    },
    {
      label: "Gorev tamamlama kapsami",
      value: completedTasks,
      total: totalTasks,
      tone: "green",
    },
  ];

  return (
    <article className="command-panel density-panel">
      <div className="panel-heading">
        <div>
          <h3>Operasyon Yogunlugu</h3>
          <p>Canli backend verisinden uretilen kapasite ve risk dengesi</p>
        </div>
        <Gauge size={20} />
      </div>
      <div className="density-list">
        {rows.map((row) => {
          const percent = row.total > 0 ? Math.round((row.value / row.total) * 100) : 0;
          return (
            <div className={`density-row ${row.tone}`} key={row.label}>
              <div>
                <span>{row.label}</span>
                <strong>
                  {row.value}/{row.total} (%{percent})
                </strong>
              </div>
              <i>
                <b style={{ width: `${Math.max(4, percent)}%` }} />
              </i>
            </div>
          );
        })}
      </div>
    </article>
  );
}

function CriticalAlertsPanel({
  alerts,
}: {
  alerts: Array<{
    title: string;
    value: number;
    note: string;
    action: string;
    onClick?: () => void;
  }>;
}) {
  return (
    <article className="command-panel critical-alert-panel">
      <div className="panel-heading">
        <div>
          <h3>Kritik Sistem Uyarilari</h3>
          <p>Saha ve sistem loglarindan derlenen dikkat noktalari</p>
        </div>
        <AlertTriangle size={20} />
      </div>
      <div className="critical-alert-list">
        {alerts.map((alert) => (
          <div className="critical-alert-row" key={alert.title}>
            <div>
              <strong>{alert.title}</strong>
              <span>{alert.note}</span>
            </div>
            <b>{alert.value}</b>
            {alert.onClick ? (
              <button onClick={alert.onClick} type="button">
                {alert.action}
              </button>
            ) : (
              <span className="static-action-label">{alert.action}</span>
            )}
          </div>
        ))}
      </div>
    </article>
  );
}

function CommandKpi({
  icon: Icon,
  title,
  value,
  note,
  tone,
  onClick,
}: {
  icon: typeof Truck;
  title: string;
  value: number | string;
  note: string;
  tone: "green" | "red" | "amber" | "blue";
  onClick?: () => void;
}) {
  const content = (
    <>
      <div>
        <Icon size={20} />
        <span>{title}</span>
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </>
  );

  return onClick ? (
    <button className={`command-kpi ${tone}`} onClick={onClick} type="button">
      {content}
    </button>
  ) : (
    <article className={`command-kpi ${tone} static`}>{content}</article>
  );
}

function StatusPanel({
  icon: Icon,
  title,
  subtitle,
  statuses,
}: {
  icon: typeof Truck;
  title: string;
  subtitle: string;
  statuses: CountByStatus[];
}) {
  const total = statuses.reduce((sum, item) => sum + item.sayi, 0);
  return (
    <article className="command-panel">
      <div className="panel-heading">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <Icon size={20} />
      </div>
      <div className="status-bars">
        {statuses.length === 0 ? (
          <div className="empty-row">Veri yok.</div>
        ) : (
          statuses.map((item) => (
            <div className="status-bar-row" key={item.durum}>
              <div>
                <span>{item.durum}</span>
                <strong>{item.sayi}</strong>
              </div>
              <i>
                <b style={{ width: `${total ? Math.max(8, (item.sayi / total) * 100) : 0}%` }} />
              </i>
            </div>
          ))
        )}
      </div>
    </article>
  );
}

function FinancePanel({
  income,
  expense,
  net,
  pending,
  onClick,
}: {
  income: number;
  expense: number;
  net: number;
  pending: number;
  onClick: () => void;
}) {
  const max = Math.max(income, expense, Math.abs(net), 1);
  return (
    <article className="command-panel finance-command-panel">
      <div className="panel-heading">
        <div>
          <h3>Finans Dengesi</h3>
          <p>{pending} bekleyen onay</p>
        </div>
        <BarChart3 size={20} />
      </div>
      <div className="finance-gauge">
        <strong>{moneyFormatter.format(net)}</strong>
        <span>net sonuc</span>
      </div>
      <div className="finance-meter-list">
        <div>
          <span>Gelir</span>
          <strong>{moneyFormatter.format(income)}</strong>
          <i>
            <b style={{ width: `${Math.max(8, (income / max) * 100)}%` }} />
          </i>
        </div>
        <div>
          <span>Gider</span>
          <strong>{moneyFormatter.format(expense)}</strong>
          <i>
            <b style={{ width: `${Math.max(8, (expense / max) * 100)}%` }} />
          </i>
        </div>
      </div>
      <button className="ghost-button" onClick={onClick} type="button">
        Muhasebeyi ac
        <ArrowUpRight size={16} />
      </button>
    </article>
  );
}

function PriorityItem({
  title,
  value,
  note,
  onClick,
}: {
  title: string;
  value: number;
  note: string;
  onClick?: () => void;
}) {
  const content = (
    <>
      <strong>{value}</strong>
      <span>{title}</span>
      <small>{note}</small>
      {onClick ? <ArrowUpRight size={16} /> : <i>Bilgi</i>}
    </>
  );

  return onClick ? (
    <button className="priority-item" onClick={onClick} type="button">
      {content}
    </button>
  ) : (
    <div className="priority-item static">{content}</div>
  );
}

function DashboardOperationMap({
  containers,
  tasks,
}: {
  containers: Container[];
  tasks: DriverTask[];
}) {
  const mapElementRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerLayerRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapElementRef.current || mapRef.current) return;

    const map = L.map(mapElementRef.current, {
      zoomControl: false,
      attributionControl: false,
      dragging: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      boxZoom: false,
      keyboard: false,
    }).setView([37.0662, 37.3833], 12);
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap",
    }).addTo(map);

    const markerLayer = L.layerGroup().addTo(map);
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
    const bounds: L.LatLngTuple[] = [];

    containers.forEach((container) => {
      const lat = Number(container.enlem);
      const lng = Number(container.boylam);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

      bounds.push([lat, lng]);
      L.marker([lat, lng], {
        icon: L.divIcon({
          className: `dashboard-map-marker container ${dashboardContainerTone(container)}`,
          html: `<span>${container.doluluk_orani}%</span>`,
          iconSize: [46, 34],
          iconAnchor: [23, 30],
          popupAnchor: [0, -28],
        }),
      })
        .bindPopup(`<strong>${container.kod}</strong><br />${container.bolge.ad}<br />${container.durum}`)
        .addTo(markerLayer);
    });

    tasks.forEach((task) => {
      const lat = Number(task.kaynak.enlem);
      const lng = Number(task.kaynak.boylam);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

      bounds.push([lat, lng]);
      L.marker([lat, lng], {
        icon: L.divIcon({
          className: `dashboard-map-marker task ${task.durum.toLowerCase()}`,
          html: `<span>#${task.id}</span>`,
          iconSize: [46, 34],
          iconAnchor: [23, 30],
          popupAnchor: [0, -28],
        }),
      })
        .bindPopup(`<strong>Gorev #${task.id}</strong><br />${task.kaynak.aciklama}<br />${task.durum}`)
        .addTo(markerLayer);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [24, 24], maxZoom: 13 });
    } else {
      map.setView([37.0662, 37.3833], 12);
    }
  }, [containers, tasks]);

  return <div className="dashboard-operation-map" ref={mapElementRef} aria-label="Canli operasyon haritasi" />;
}

function dashboardContainerTone(container: Container): string {
  if (container.durum === "Kritik" || container.doluluk_orani >= 85) return "critical";
  if (container.durum === "GoreveAtandi") return "assigned";
  if (container.doluluk_orani >= 70) return "watch";
  return "normal";
}

function findStatus(statuses: { durum: string; sayi: number }[], status: string): number {
  return statuses.find((item) => item.durum === status)?.sayi || 0;
}
