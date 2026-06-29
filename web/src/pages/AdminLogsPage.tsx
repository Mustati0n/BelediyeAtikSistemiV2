import { Download, FileSearch, RefreshCcw, Search, ScrollText } from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import { ApiError, RecentAuditLog, listAdminLogs } from "../api";

type LogFilters = {
  query: string;
  islem_tipi: string;
  varlik_tipi: string;
  yapan: string;
  date_from: string;
  date_to: string;
};

const defaultFilters: LogFilters = {
  query: "",
  islem_tipi: "",
  varlik_tipi: "",
  yapan: "",
  date_from: "",
  date_to: "",
};
const pageSizeOptions = [15, 30, 50, 100];

export function AdminLogsPage({ token }: { token: string }) {
  const [filters, setFilters] = useState<LogFilters>(defaultFilters);
  const [logs, setLogs] = useState<RecentAuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadLogs(nextFilters = filters, nextPage = page, nextPageSize = pageSize) {
    setError("");
    setLoading(true);
    try {
      const data = await listAdminLogs(token, {
        ...nextFilters,
        limit: nextPageSize,
        offset: (nextPage - 1) * nextPageSize,
        date_from: nextFilters.date_from ? `${nextFilters.date_from}T00:00:00` : undefined,
        date_to: nextFilters.date_to ? `${nextFilters.date_to}T23:59:59` : undefined,
      });
      setLogs(data.loglar);
      setTotal(data.toplam);
      setPage(nextPage);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Log kayitlari alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLogs(defaultFilters, 1);
  }, []);

  const typeCount = useMemo(() => new Set(logs.map((log) => log.islem_tipi)).size, [logs]);
  const actorCount = useMemo(
    () => new Set(logs.map((log) => log.yapan || "Sistem")).size,
    [logs],
  );

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    loadLogs(filters, 1);
  }

  function clearFilters() {
    setFilters(defaultFilters);
    loadLogs(defaultFilters, 1);
  }

  function handlePageSizeChange(nextValue: string) {
    const nextPageSize = Number(nextValue);
    setPageSize(nextPageSize);
    loadLogs(filters, 1, nextPageSize);
  }

  function exportCsv() {
    const rows = [
      ["ID", "Tarih", "Islem Tipi", "Aciklama", "Varlik Tipi", "Varlik ID", "Yapan"],
      ...logs.map((log) => [
        String(log.id),
        log.islem_tarihi,
        log.islem_tipi,
        log.aciklama,
        log.varlik_tipi,
        log.varlik_id ? String(log.varlik_id) : "",
        log.yapan || "Sistem",
      ]),
    ];
    const csv = rows.map((row) => row.map(csvCell).join(";")).join("\n");
    const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `atik-sistemi-loglari-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="page-stack">
      <section className="page-hero audit-hero">
        <div>
          <p>DENETIM GECMISI</p>
          <h1>Log Kayitlari</h1>
          <span>
            Sistem icindeki gorev, bakim, muhasebe, tesis ve kullanici hareketlerini tek yerden
            izleyin; arama ve filtrelerle olay gecmisini daraltin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <ScrollText size={34} />
          <strong>{total}</strong>
          <span>Toplam Eslesen</span>
          <small>{loading ? "Guncelleniyor" : `${logs.length} kayit listede`}</small>
        </div>
      </section>

      <section className="admin-summary-row" aria-label="Log ozetleri">
        <article>
          <span>Listelenen</span>
          <strong>{logs.length}</strong>
        </article>
        <article>
          <span>Islem Turu</span>
          <strong>{typeCount}</strong>
        </article>
        <article>
          <span>Kullanici</span>
          <strong>{actorCount}</strong>
        </article>
        <article>
          <span>Sayfa</span>
          <strong>
            {page}/{totalPages}
          </strong>
        </article>
      </section>

      <section className="filter-panel audit-filter-panel">
        <form onSubmit={handleSubmit}>
          <label>
            Genel Arama
            <input
              value={filters.query}
              onChange={(event) => setFilters({ ...filters, query: event.target.value })}
              placeholder="Aciklama, islem veya varlik ara..."
            />
          </label>
          <label>
            Islem Tipi
            <input
              value={filters.islem_tipi}
              onChange={(event) => setFilters({ ...filters, islem_tipi: event.target.value })}
              placeholder="GorevAtama"
            />
          </label>
          <label>
            Varlik Tipi
            <input
              value={filters.varlik_tipi}
              onChange={(event) => setFilters({ ...filters, varlik_tipi: event.target.value })}
              placeholder="Gorev, Konteyner..."
            />
          </label>
          <label>
            Yapan
            <input
              value={filters.yapan}
              onChange={(event) => setFilters({ ...filters, yapan: event.target.value })}
              placeholder="Kullanici adi veya e-posta"
            />
          </label>
          <label>
            Baslangic
            <input
              type="date"
              value={filters.date_from}
              onChange={(event) => setFilters({ ...filters, date_from: event.target.value })}
            />
          </label>
          <label>
            Bitis
            <input
              type="date"
              value={filters.date_to}
              onChange={(event) => setFilters({ ...filters, date_to: event.target.value })}
            />
          </label>
          <label>
            Sayfada
            <select
              value={pageSize}
              onChange={(event) => handlePageSizeChange(event.target.value)}
            >
              {pageSizeOptions.map((option) => (
                <option key={option} value={option}>
                  {option} kayit
                </option>
              ))}
            </select>
          </label>
          <div className="filter-actions">
            <button className="secondary-action" onClick={clearFilters} type="button">
              <RefreshCcw size={17} />
              Temizle
            </button>
            <button className="primary-action" disabled={loading} type="submit">
              <Search size={17} />
              {loading ? "Araniyor" : "Filtrele"}
            </button>
          </div>
        </form>
      </section>

      <InlineNotice message={error} type="error" onClose={() => setError("")} />

      <section className="data-panel audit-log-panel">
        <div className="table-title">
          <strong>Islem Gecmisi</strong>
          <span>{loading ? "Yukleniyor" : `${total} eslesme icinden ${logs.length} kayit`}</span>
          <button className="row-action" disabled={logs.length === 0} onClick={exportCsv} type="button">
            <Download size={16} />
            CSV Aktar
          </button>
        </div>

        <div className="audit-log-list">
          {logs.map((log) => (
            <article key={log.id}>
              <div className="audit-log-icon">
                <FileSearch size={20} />
              </div>
              <div>
                <strong>{log.islem_tipi}</strong>
                <p>{log.aciklama}</p>
                <small>
                  {log.varlik_tipi}
                  {log.varlik_id ? ` #${log.varlik_id}` : ""} / {log.yapan || "Sistem"}
                </small>
              </div>
              <time>{formatDateTime(log.islem_tarihi)}</time>
            </article>
          ))}

          {!loading && logs.length === 0 && (
            <div className="empty-state">
              <ScrollText size={24} />
              <strong>Eslesen log kaydi yok.</strong>
              <span>Filtreleri genisletip tekrar deneyin.</span>
            </div>
          )}
        </div>

        <Pagination
          page={page}
          totalPages={totalPages}
          onPageChange={(nextPage) => loadLogs(filters, nextPage)}
        />
      </section>
    </div>
  );
}

function Pagination({
  page,
  totalPages,
  onPageChange,
}: {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  const pages = Array.from({ length: totalPages }, (_, index) => index + 1);
  return (
    <nav className="pagination-bar" aria-label="Log sayfalari">
      {pages.map((item) => (
        <button
          className={item === page ? "active" : ""}
          key={item}
          onClick={() => onPageChange(item)}
          type="button"
        >
          {item}
        </button>
      ))}
      <button disabled={page >= totalPages} onClick={() => onPageChange(page + 1)} type="button">
        Ileri
      </button>
      <button disabled={page >= totalPages} onClick={() => onPageChange(totalPages)} type="button">
        Son
      </button>
    </nav>
  );
}

function csvCell(value: string): string {
  return `"${value.replaceAll('"', '""')}"`;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("tr-TR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
