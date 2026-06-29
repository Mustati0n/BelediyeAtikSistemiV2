import { BarChart3, History, RefreshCcw, Wallet } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { AdminDashboardSummary, ApiError, RecentAuditLog, getAdminDashboard } from "../api";

const moneyFormatter = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  maximumFractionDigits: 0,
});

export function AdminFinanceOverviewPage({ token }: { token: string }) {
  const [summary, setSummary] = useState<AdminDashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    setLoading(true);
    try {
      setSummary(await getAdminDashboard(token));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Finans ozeti alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const financeLogs = useMemo(() => {
    if (!summary) return [];
    return summary.son_islemler.filter(isFinanceLog).slice(0, 6);
  }, [summary]);

  if (loading && !summary) return <div className="state-box">Finans denetim ozeti yukleniyor</div>;

  if (error && !summary) {
    return (
      <div className="state-box danger">
        <strong>Finans ozeti acilamadi</strong>
        <span>{error}</span>
        <button onClick={load} type="button">
          <RefreshCcw size={16} />
          Tekrar dene
        </button>
      </div>
    );
  }

  if (!summary) return null;

  const income = Number(summary.finans.onayli_gelir_toplami);
  const expense = Number(summary.finans.onayli_gider_toplami);
  const net = Number(summary.finans.net_sonuc);
  const pending = summary.finans.bekleyen_gelir_sayisi + summary.finans.bekleyen_gider_sayisi;
  const max = Math.max(income, expense, Math.abs(net), 1);

  return (
    <div className="page-stack">
      <section className="page-hero">
        <div>
          <p>ADMIN FINANS DENETIMI</p>
          <h1>Finans Genel Ozeti</h1>
          <span>
            Muhasebe islemlerine mudahale etmeden gelir, gider, net sonuc ve son finans hareketlerini
            denetim seviyesinde takip edin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <Wallet size={34} />
          <strong>{moneyFormatter.format(net)}</strong>
          <span>Genel Net</span>
          <small>{pending} bekleyen muhasebe kaydi</small>
        </div>
      </section>

      <section className="admin-summary-row" aria-label="Admin finans ozetleri">
        <article>
          <span>Onayli Gelir</span>
          <strong>{moneyFormatter.format(income)}</strong>
        </article>
        <article>
          <span>Onayli Gider</span>
          <strong>{moneyFormatter.format(expense)}</strong>
        </article>
        <article>
          <span>Net Sonuc</span>
          <strong>{moneyFormatter.format(net)}</strong>
        </article>
        <article>
          <span>Bekleyen</span>
          <strong>{pending}</strong>
        </article>
      </section>

      <section className="admin-finance-dashboard">
        <article className="command-panel">
          <div className="panel-heading">
            <div>
              <h3>Genel Kar / Zarar</h3>
              <p>Onaylanmis gelir ve gider dengesinden hesaplanir</p>
            </div>
            <BarChart3 size={20} />
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
        </article>

        <article className="command-panel">
          <div className="panel-heading">
            <div>
              <h3>Son Finans Hareketleri</h3>
              <p>Muhasebe ve tesis kaynakli son hareketler</p>
            </div>
            <History size={20} />
          </div>
          <div className="command-timeline">
            {financeLogs.length === 0 ? (
              <div className="empty-row">Son finans hareketi yok.</div>
            ) : (
              financeLogs.map((log) => (
                <button key={log.id} type="button">
                  <span />
                  <strong>{log.islem_tipi}</strong>
                  <small>{log.aciklama}</small>
                  <em>{log.yapan || "Sistem"}</em>
                </button>
              ))
            )}
          </div>
        </article>
      </section>
    </div>
  );
}

function isFinanceLog(log: RecentAuditLog): boolean {
  const text = `${log.islem_tipi} ${log.aciklama} ${log.varlik_tipi}`.toLocaleLowerCase("tr-TR");
  return ["gelir", "gider", "maas", "finans", "satis", "muhasebe"].some((word) =>
    text.includes(word),
  );
}
