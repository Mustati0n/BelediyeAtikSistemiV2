import {
  BarChart3,
  CheckCircle2,
  Factory,
  History,
  PackageCheck,
  RefreshCcw,
  Save,
  Send,
  ShoppingCart,
} from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  Delivery,
  SaleResponse,
  Stock,
  StockMovement,
  SystemParameter,
  WasteType,
  applySorting,
  approveDelivery,
  createManualStockMovement,
  createSale,
  listDeliveries,
  listSales,
  listStockMovements,
  listStocks,
  listSystemParameters,
} from "../api";

const wasteTypes: WasteType[] = ["Plastik", "Cam", "Metal", "Kagit", "Organik", "Diger"];
const tabs = ["Ozet", "Teslimler", "Ayristirma", "Stok", "Satis", "Gecmis"] as const;

type Tab = (typeof tabs)[number];

type SortForm = {
  teslim_id: string;
  atik_tipi: WasteType;
  miktar_kg: string;
  aciklama: string;
};

type SaleForm = {
  atik_tipi: WasteType;
  miktar_kg: string;
  birim_fiyat: string;
  alici_firma: string;
  belge_no: string;
};

type ManualStockForm = {
  atik_tipi: WasteType;
  miktar_kg: string;
  aciklama: string;
};

type DeliveryStatusFilter = "Tum Durumlar" | "Bekleyen" | "Onaylandi" | "Ayristirildi";
type DeliverySort = "date-desc" | "date-asc" | "kg-desc" | "kg-asc";

const emptySortForm: SortForm = {
  teslim_id: "",
  atik_tipi: "Plastik",
  miktar_kg: "",
  aciklama: "",
};

const emptySaleForm: SaleForm = {
  atik_tipi: "Plastik",
  miktar_kg: "",
  birim_fiyat: "",
  alici_firma: "",
  belge_no: "",
};

const emptyManualStockForm: ManualStockForm = {
  atik_tipi: "Plastik",
  miktar_kg: "",
  aciklama: "",
};

export function RecyclingPage({ token, readOnly = false }: { token: string; readOnly?: boolean }) {
  const [activeTab, setActiveTab] = useState<Tab>("Ozet");
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [sales, setSales] = useState<SaleResponse[]>([]);
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [parameters, setParameters] = useState<SystemParameter[]>([]);
  const [sortForm, setSortForm] = useState<SortForm>(emptySortForm);
  const [saleForm, setSaleForm] = useState<SaleForm>(emptySaleForm);
  const [manualStockForm, setManualStockForm] = useState<ManualStockForm>(emptyManualStockForm);
  const [deliveryStatusFilter, setDeliveryStatusFilter] = useState<DeliveryStatusFilter>("Tum Durumlar");
  const [deliveryWasteFilter, setDeliveryWasteFilter] = useState<"Tum Atiklar" | WasteType>("Tum Atiklar");
  const [deliverySort, setDeliverySort] = useState<DeliverySort>("date-desc");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyKey, setBusyKey] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);
    try {
      const [deliveryData, stockData, saleData, movementData] = await Promise.all([
        listDeliveries(token),
        listStocks(token),
        listSales(token),
        listStockMovements(token),
      ]);
      setDeliveries(deliveryData);
      setStocks(stockData);
      setSales(saleData);
      setMovements(movementData);
      setSortForm((current) => ({
        ...current,
        teslim_id: current.teslim_id || String(deliveryData.find((item) => item.onaylandi_mi)?.id || ""),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Tesis verisi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    async function loadPriceParameters() {
      try {
        const data = await listSystemParameters(token);
        setParameters(data);
      } catch {
        setParameters([]);
      }
    }
    loadPriceParameters();
  }, [token]);

  useEffect(() => {
    setError("");
    setMessage("");
  }, [activeTab]);

  useEffect(() => {
    if (!error && !message) return;
    const timeout = window.setTimeout(() => {
      setError("");
      setMessage("");
    }, 6000);
    return () => window.clearTimeout(timeout);
  }, [error, message]);

  const sortedDeliveryIds = useMemo(() => new Set(movements.map((movement) => movement.tesis_teslim_id)), [movements]);
  const pendingDeliveries = useMemo(
    () => sortDeliveries(deliveries.filter((delivery) => !delivery.onaylandi_mi), "date-desc"),
    [deliveries],
  );
  const approvedDeliveries = useMemo(
    () => sortDeliveries(deliveries.filter((delivery) => delivery.onaylandi_mi), "date-desc"),
    [deliveries],
  );
  const sortableDeliveries = approvedDeliveries.filter((delivery) => !sortedDeliveryIds.has(delivery.id));
  const filteredDeliveries = useMemo(() => {
    return sortDeliveries(
      deliveries.filter((delivery) => {
        const isSorted = sortedDeliveryIds.has(delivery.id);
        const matchesStatus =
          deliveryStatusFilter === "Tum Durumlar" ||
          (deliveryStatusFilter === "Bekleyen" && !delivery.onaylandi_mi) ||
          (deliveryStatusFilter === "Onaylandi" && delivery.onaylandi_mi && !isSorted) ||
          (deliveryStatusFilter === "Ayristirildi" && isSorted);
        const matchesWaste =
          deliveryWasteFilter === "Tum Atiklar" || delivery.atik_tipi === deliveryWasteFilter;
        return matchesStatus && matchesWaste;
      }),
      deliverySort,
    );
  }, [deliveries, deliverySort, deliveryStatusFilter, deliveryWasteFilter, sortedDeliveryIds]);
  const totalStockKg = stocks.reduce((sum, stock) => sum + Number(stock.toplam_miktar_kg), 0);
  const today = new Date().toLocaleDateString("tr-TR");
  const todayDeliveries = deliveries.filter((delivery) => new Date(delivery.tarih).toLocaleDateString("tr-TR") === today);
  const todayMovementsKg = movements
    .filter((movement) => new Date(movement.tarih).toLocaleDateString("tr-TR") === today)
    .reduce((sum, movement) => sum + Number(movement.miktar_kg), 0);
  const todaySales = sales.filter((sale) => new Date(sale.tarih).toLocaleDateString("tr-TR") === today);
  const stockByType = useMemo(() => Object.fromEntries(stocks.map((stock) => [stock.atik_tipi, Number(stock.toplam_miktar_kg)])), [stocks]);
  const unitPrices = useMemo(() => buildWasteUnitPrices(parameters), [parameters]);

  useEffect(() => {
    const suggestedPrice = unitPrices[saleForm.atik_tipi];
    if (!suggestedPrice) return;
    setSaleForm((current) => (
      current.birim_fiyat === "" || Object.values(unitPrices).includes(current.birim_fiyat)
        ? { ...current, birim_fiyat: suggestedPrice }
        : current
    ));
  }, [saleForm.atik_tipi, unitPrices]);

  async function handleApprove(delivery: Delivery) {
    if (readOnly) return;
    setBusyKey(`delivery-${delivery.id}`);
    setError("");
    setMessage("");
    try {
      await approveDelivery(token, delivery.id);
      setMessage(
        delivery.atik_tipi
          ? `#${delivery.id} teslimi onaylandi ve ${delivery.atik_tipi} stoguna eklendi.`
          : `#${delivery.id} numarali teslim onaylandi.`,
      );
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Teslim onaylanamadi.");
    } finally {
      setBusyKey("");
    }
  }

  async function handleSort(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (readOnly) return;
    setError("");
    setMessage("");

    const deliveryId = Number(sortForm.teslim_id);
    const amount = Number(sortForm.miktar_kg);
    if (!deliveryId || !Number.isFinite(amount) || amount <= 0) {
      setError("Ayristirma icin teslim ve pozitif kg zorunludur.");
      return;
    }

    setSaving(true);
    try {
      const response = await applySorting(token, deliveryId, [
        {
          atik_tipi: sortForm.atik_tipi,
          miktar_kg: amount.toFixed(3),
          aciklama: sortForm.aciklama.trim() || null,
        },
      ]);
      setMessage(`#${response.teslim_id} teslimi icin ${response.hareket_sayisi} stok hareketi olustu.`);
      setSortForm({ ...emptySortForm, teslim_id: String(sortableDeliveries[0]?.id || "") });
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Ayristirma kaydedilemedi.");
    } finally {
      setSaving(false);
    }
  }

  async function handleSale(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (readOnly) return;
    setError("");
    setMessage("");

    const amount = Number(saleForm.miktar_kg);
    const price = Number(saleForm.birim_fiyat);
    if (!Number.isFinite(amount) || amount <= 0 || !Number.isFinite(price) || price <= 0) {
      setError("Satis icin pozitif kg ve birim fiyat zorunludur.");
      return;
    }
    if ((stockByType[saleForm.atik_tipi] || 0) < amount) {
      setError(`${saleForm.atik_tipi} stogu bu satis icin yeterli degil.`);
      return;
    }

    setSaving(true);
    try {
      const sale = await createSale(token, {
        atik_tipi: saleForm.atik_tipi,
        miktar_kg: amount.toFixed(3),
        birim_fiyat: price.toFixed(2),
        alici_firma: saleForm.alici_firma.trim() || null,
        belge_no: saleForm.belge_no.trim() || null,
      });
      setMessage(`#${sale.satis_id} satisi olustu ve muhasebeye bekleyen gelir dustu.`);
      setSaleForm(emptySaleForm);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Satis olusturulamadi.");
    } finally {
      setSaving(false);
    }
  }

  async function handleManualStock(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (readOnly) return;
    setError("");
    setMessage("");
    const amount = Number(manualStockForm.miktar_kg);
    if (!Number.isFinite(amount) || amount <= 0) {
      setError("Manuel stok icin pozitif kg zorunludur.");
      return;
    }
    setSaving(true);
    try {
      const movement = await createManualStockMovement(token, {
        atik_tipi: manualStockForm.atik_tipi,
        miktar_kg: amount.toFixed(3),
        aciklama: manualStockForm.aciklama.trim() || null,
      });
      setMessage(`${movement.atik_tipi} icin ${Number(movement.miktar_kg).toLocaleString("tr-TR")} kg manuel stok eklendi.`);
      setManualStockForm(emptyManualStockForm);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Manuel stok eklenemedi.");
    } finally {
      setSaving(false);
    }
  }

  function exportHistoryCsv() {
    const rows = [
      ["Tur", "Tarih", "Atik Tipi", "Kg", "Tutar/Aciklama", "Durum"],
      ...movements.map((movement) => [
        "Stok Hareketi",
        movement.tarih,
        movement.atik_tipi,
        movement.miktar_kg,
        movement.aciklama || "",
        `Teslim #${movement.tesis_teslim_id}`,
      ]),
      ...sales.map((sale) => [
        "Satis",
        sale.tarih,
        sale.atik_tipi,
        sale.miktar_kg,
        `${sale.toplam_tutar} / ${sale.alici_firma || "-"}`,
        sale.durum,
      ]),
    ];
    const csv = rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(";")).join("\n");
    const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `tesis-gecmisi-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="page-stack recycling-cockpit">
      <section className="page-hero">
        <div>
          <p>TESIS OPERASYONU</p>
          <h1>Teslim, Ayristirma, Stok ve Satis</h1>
          <span>
            Sofor teslimlerini onaylayin, atiklari stok turlerine ayristirin, stoktan satis
            olusturun ve tum tesis gecmisini izleyin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <Factory size={34} />
          <strong>{pendingDeliveries.length}</strong>
          <span>Bekleyen Teslim</span>
          <small>{totalStockKg.toLocaleString("tr-TR")} kg stok</small>
        </div>
      </section>

      <section className="facility-kpi-grid">
        <Metric icon={PackageCheck} label="Bugun Teslim" value={todayDeliveries.length} note="kayit" />
        <Metric icon={BarChart3} label="Bugun Ayristirma" value={todayMovementsKg.toLocaleString("tr-TR")} note="kg" />
        <Metric icon={ShoppingCart} label="Bugun Satis" value={todaySales.length} note="kayit" />
        <Metric icon={Factory} label="Toplam Stok" value={totalStockKg.toLocaleString("tr-TR")} note="kg" />
      </section>

      <nav className="facility-tabs" aria-label="Tesis sekmeleri">
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
        <section className="facility-overview">
          <StockCards stocks={stocks} />
          <QueuePanel pendingDeliveries={pendingDeliveries} onApprove={handleApprove} readOnly={readOnly} busyKey={busyKey} />
        </section>
      )}

      {activeTab === "Teslimler" && (
        <DeliveryList
          deliveries={filteredDeliveries}
          loading={loading}
          readOnly={readOnly}
          busyKey={busyKey}
          onApprove={handleApprove}
          sortedDeliveryIds={sortedDeliveryIds}
          statusFilter={deliveryStatusFilter}
          wasteFilter={deliveryWasteFilter}
          sort={deliverySort}
          onStatusFilterChange={setDeliveryStatusFilter}
          onWasteFilterChange={setDeliveryWasteFilter}
          onSortChange={setDeliverySort}
        />
      )}

      {activeTab === "Ayristirma" && (
        <section className="form-panel">
          <PanelTitle title="Ayristirma Kaydi" note={readOnly ? "Admin izleme modunda islem yapilamaz." : "Onaylanmis ve henuz ayristirilmamis teslimleri stoga isleyin."} onRefresh={loadData} />
          <form className="recycling-form enhanced" onSubmit={handleSort}>
            <label>
              Teslim
              <select value={sortForm.teslim_id} disabled={readOnly} onChange={(event) => setSortForm({ ...sortForm, teslim_id: event.target.value })}>
                <option value="">Teslim secin</option>
                {sortableDeliveries.map((delivery) => (
                  <option key={delivery.id} value={delivery.id}>
                    #{delivery.id} / {Number(delivery.toplam_kg).toLocaleString("tr-TR")} kg
                  </option>
                ))}
              </select>
            </label>
            <label>
              Atik Tipi
              <select value={sortForm.atik_tipi} disabled={readOnly} onChange={(event) => setSortForm({ ...sortForm, atik_tipi: event.target.value as WasteType })}>
                {wasteTypes.map((type) => <option key={type}>{type}</option>)}
              </select>
            </label>
            <label>
              Kg
              <input inputMode="decimal" value={sortForm.miktar_kg} disabled={readOnly} onChange={(event) => setSortForm({ ...sortForm, miktar_kg: event.target.value })} placeholder="50" />
            </label>
            <label>
              Aciklama
              <input value={sortForm.aciklama} disabled={readOnly} onChange={(event) => setSortForm({ ...sortForm, aciklama: event.target.value })} placeholder="Opsiyonel" />
            </label>
            <button className="primary-action" disabled={saving || readOnly || sortableDeliveries.length === 0} type="submit">
              <Save size={18} />
              Kaydet
            </button>
          </form>
        </section>
      )}

      {activeTab === "Stok" && (
        <section className="facility-stock-workspace">
          <form className="form-panel manual-stock-form" onSubmit={handleManualStock}>
            <PanelTitle
              title="Manuel Stok Girisi"
              note={readOnly ? "Admin izleme modunda islem yapilamaz." : "Operator tesiste tartilan ek stoklari elle girebilir."}
              onRefresh={loadData}
            />
            <div className="recycling-form enhanced">
              <label>
                Atik Tipi
                <select
                  disabled={readOnly}
                  value={manualStockForm.atik_tipi}
                  onChange={(event) => setManualStockForm({ ...manualStockForm, atik_tipi: event.target.value as WasteType })}
                >
                  {wasteTypes.map((type) => <option key={type}>{type}</option>)}
                </select>
              </label>
              <label>
                Kg
                <input
                  disabled={readOnly}
                  inputMode="decimal"
                  value={manualStockForm.miktar_kg}
                  onChange={(event) => setManualStockForm({ ...manualStockForm, miktar_kg: event.target.value.replace(/[^\d.,]/g, "").replace(",", ".") })}
                  placeholder="75"
                />
              </label>
              <label>
                Aciklama
                <input
                  disabled={readOnly}
                  value={manualStockForm.aciklama}
                  onChange={(event) => setManualStockForm({ ...manualStockForm, aciklama: event.target.value })}
                  placeholder="Tartim fis no, kaynak..."
                />
              </label>
              <button className="primary-action" disabled={saving || readOnly} type="submit">
                <Save size={18} />
                Stok Ekle
              </button>
            </div>
          </form>
          <StockCards stocks={stocks} detailed />
        </section>
      )}

      {activeTab === "Satis" && (
        <section className="form-panel">
          <PanelTitle title="Stoktan Satis" note={readOnly ? "Admin izleme modunda islem yapilamaz." : "Satis stoktan duser ve muhasebeye bekleyen gelir kaydi olusturur."} />
          <form className="sale-form enhanced" onSubmit={handleSale}>
            <label>
              Atik Tipi
              <select
                value={saleForm.atik_tipi}
                disabled={readOnly}
                onChange={(event) => {
                  const atik_tipi = event.target.value as WasteType;
                  setSaleForm({
                    ...saleForm,
                    atik_tipi,
                    birim_fiyat: unitPrices[atik_tipi] || saleForm.birim_fiyat,
                  });
                }}
              >
                {wasteTypes.map((type) => <option key={type}>{type}</option>)}
              </select>
            </label>
            <label>
              Kg
              <input inputMode="decimal" value={saleForm.miktar_kg} disabled={readOnly} onChange={(event) => setSaleForm({ ...saleForm, miktar_kg: event.target.value })} placeholder="25" />
            </label>
            <label>
              Birim Fiyat
              <input inputMode="decimal" value={saleForm.birim_fiyat} disabled={readOnly} onChange={(event) => setSaleForm({ ...saleForm, birim_fiyat: event.target.value })} placeholder="12.50" />
            </label>
            <label>
              Alici Firma
              <input value={saleForm.alici_firma} disabled={readOnly} onChange={(event) => setSaleForm({ ...saleForm, alici_firma: event.target.value })} placeholder="Firma adi" />
            </label>
            <label>
              Belge No
              <input value={saleForm.belge_no} disabled={readOnly} onChange={(event) => setSaleForm({ ...saleForm, belge_no: event.target.value })} placeholder="Fatura / fis no" />
            </label>
            <button className="primary-action" disabled={saving || readOnly || stocks.length === 0} type="submit">
              <Send size={18} />
              Satis
            </button>
          </form>
          <SaleHistory sales={sales} />
        </section>
      )}

      {activeTab === "Gecmis" && (
        <section className="facility-history">
          <button className="row-action" onClick={exportHistoryCsv} type="button">
            <History size={16} />
            CSV Aktar
          </button>
          <MovementHistory movements={movements} />
          <SaleHistory sales={sales} />
        </section>
      )}
    </div>
  );
}

function Metric({ icon: Icon, label, value, note }: { icon: typeof Factory; label: string; value: number | string; note: string }) {
  return (
    <article className="facility-metric">
      <Icon size={22} />
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function PanelTitle({ title, note, onRefresh }: { title: string; note: string; onRefresh?: () => void }) {
  return (
    <div className="panel-heading">
      <div>
        <h3>{title}</h3>
        <p>{note}</p>
      </div>
      {onRefresh && (
        <button className="icon-button" onClick={onRefresh} type="button" title="Yenile">
          <RefreshCcw size={18} />
        </button>
      )}
    </div>
  );
}

function QueuePanel({ pendingDeliveries, onApprove, readOnly, busyKey }: { pendingDeliveries: Delivery[]; onApprove: (delivery: Delivery) => void; readOnly: boolean; busyKey: string }) {
  return (
    <section className="data-panel">
      <div className="table-title">
        <strong>Bekleyen Teslim Kuyrugu</strong>
        <span>{pendingDeliveries.length} kayit</span>
      </div>
      <div className="approval-list compact">
        {pendingDeliveries.slice(0, 5).map((delivery) => (
          <article className="approval-card" key={delivery.id}>
            <div>
              <strong>#{delivery.id} / {Number(delivery.toplam_kg).toLocaleString("tr-TR")} kg</strong>
              <span>{new Date(delivery.tarih).toLocaleString("tr-TR")}</span>
              <small>{delivery.atik_tipi || "Atik tipi yok"} / {delivery.aciklama || "Aciklama yok"}</small>
            </div>
            <button className="primary-action" disabled={readOnly || busyKey === `delivery-${delivery.id}`} onClick={() => onApprove(delivery)} type="button">
              <CheckCircle2 size={16} />
              Onayla
            </button>
          </article>
        ))}
        {pendingDeliveries.length === 0 && <div className="empty-state">Bekleyen teslim yok.</div>}
      </div>
    </section>
  );
}

function DeliveryList({
  deliveries,
  loading,
  readOnly,
  busyKey,
  onApprove,
  sortedDeliveryIds,
  statusFilter,
  wasteFilter,
  sort,
  onStatusFilterChange,
  onWasteFilterChange,
  onSortChange,
}: {
  deliveries: Delivery[];
  loading: boolean;
  readOnly: boolean;
  busyKey: string;
  onApprove: (delivery: Delivery) => void;
  sortedDeliveryIds: Set<number>;
  statusFilter: DeliveryStatusFilter;
  wasteFilter: "Tum Atiklar" | WasteType;
  sort: DeliverySort;
  onStatusFilterChange: (value: DeliveryStatusFilter) => void;
  onWasteFilterChange: (value: "Tum Atiklar" | WasteType) => void;
  onSortChange: (value: DeliverySort) => void;
}) {
  return (
    <section className="data-panel">
      <div className="table-title">
        <strong>Teslimler</strong>
        <span>{loading ? "Yukleniyor" : `${deliveries.length} kayit`}</span>
      </div>
      <div className="facility-list-toolbar">
        <label>
          Durum
          <select value={statusFilter} onChange={(event) => onStatusFilterChange(event.target.value as DeliveryStatusFilter)}>
            <option>Tum Durumlar</option>
            <option>Bekleyen</option>
            <option>Onaylandi</option>
            <option>Ayristirildi</option>
          </select>
        </label>
        <label>
          Atik Tipi
          <select value={wasteFilter} onChange={(event) => onWasteFilterChange(event.target.value as "Tum Atiklar" | WasteType)}>
            <option>Tum Atiklar</option>
            {wasteTypes.map((type) => <option key={type}>{type}</option>)}
          </select>
        </label>
        <label>
          Siralama
          <select value={sort} onChange={(event) => onSortChange(event.target.value as DeliverySort)}>
            <option value="date-desc">En yeni ilk</option>
            <option value="date-asc">En eski ilk</option>
            <option value="kg-desc">Kg buyukten kucuge</option>
            <option value="kg-asc">Kg kucukten buyuge</option>
          </select>
        </label>
      </div>
      <div className="approval-list">
        {deliveries.map((delivery) => (
          <article className="approval-card" key={delivery.id}>
            <div>
              <strong>#{delivery.id} / {Number(delivery.toplam_kg).toLocaleString("tr-TR")} kg</strong>
              <span>{new Date(delivery.tarih).toLocaleString("tr-TR")}</span>
              <small>{delivery.atik_tipi || "Atik tipi yok"} / {delivery.aciklama || "Aciklama yok"}</small>
            </div>
            <div className="approval-actions">
              <b className={`status-pill ${delivery.onaylandi_mi ? "onaylandi" : "beklemede"}`}>
                {sortedDeliveryIds.has(delivery.id) ? "Ayristirildi" : delivery.onaylandi_mi ? "Onaylandi" : "Beklemede"}
              </b>
              <button className="primary-action" disabled={readOnly || delivery.onaylandi_mi || busyKey === `delivery-${delivery.id}`} onClick={() => onApprove(delivery)} type="button">
                <CheckCircle2 size={16} />
                Onayla
              </button>
            </div>
          </article>
        ))}
        {!loading && deliveries.length === 0 && <div className="empty-state">Teslim kaydi bulunamadi.</div>}
      </div>
    </section>
  );
}

function sortDeliveries(deliveries: Delivery[], sort: DeliverySort): Delivery[] {
  const sortable = [...deliveries];
  return sortable.sort((a, b) => {
    if (sort === "date-asc") {
      return new Date(a.tarih).getTime() - new Date(b.tarih).getTime();
    }
    if (sort === "kg-desc") {
      return Number(b.toplam_kg) - Number(a.toplam_kg);
    }
    if (sort === "kg-asc") {
      return Number(a.toplam_kg) - Number(b.toplam_kg);
    }
    return new Date(b.tarih).getTime() - new Date(a.tarih).getTime();
  });
}

function StockCards({ stocks, detailed = false }: { stocks: Stock[]; detailed?: boolean }) {
  const max = Math.max(...stocks.map((stock) => Number(stock.toplam_miktar_kg)), 1);
  return (
    <section className={detailed ? "stock-grid detailed" : "stock-grid"}>
      {stocks.map((stock) => {
        const amount = Number(stock.toplam_miktar_kg);
        return (
          <article className="stock-card" key={stock.id}>
            <span>{stock.atik_tipi}</span>
            <strong>{amount.toLocaleString("tr-TR")} kg</strong>
            <i><b style={{ width: `${Math.max(6, (amount / max) * 100)}%` }} /></i>
            <small>{amount < 25 ? "Dusuk stok" : amount > 100 ? "Yuksek stok" : "Normal stok"}</small>
          </article>
        );
      })}
      {stocks.length === 0 && <div className="empty-state">Stok kaydi bulunamadi.</div>}
    </section>
  );
}

function MovementHistory({ movements }: { movements: StockMovement[] }) {
  return (
    <section className="data-panel">
      <div className="table-title">
        <strong>Stok Hareket Gecmisi</strong>
        <span>{movements.length} hareket</span>
      </div>
      <div className="history-list">
        {movements.map((movement) => (
          <article key={movement.id}>
            <strong>{movement.atik_tipi} / {Number(movement.miktar_kg).toLocaleString("tr-TR")} kg</strong>
            <span>{new Date(movement.tarih).toLocaleString("tr-TR")} / Teslim #{movement.tesis_teslim_id}</span>
            <small>{movement.aciklama || "Aciklama yok"}</small>
          </article>
        ))}
        {movements.length === 0 && <div className="empty-state">Stok hareketi yok.</div>}
      </div>
    </section>
  );
}

function SaleHistory({ sales }: { sales: SaleResponse[] }) {
  return (
    <section className="data-panel">
      <div className="table-title">
        <strong>Satis Gecmisi</strong>
        <span>{sales.length} satis</span>
      </div>
      <div className="history-list">
        {sales.map((sale) => (
          <article key={sale.satis_id}>
            <strong>#{sale.satis_id} / {sale.atik_tipi} / {Number(sale.miktar_kg).toLocaleString("tr-TR")} kg</strong>
            <span>{new Date(sale.tarih).toLocaleString("tr-TR")} / {Number(sale.toplam_tutar).toLocaleString("tr-TR")} TL / {sale.alici_firma || "Alici yok"}</span>
            <small>{sale.belge_no || "Belge no yok"} / {sale.durum}</small>
          </article>
        ))}
        {sales.length === 0 && <div className="empty-state">Satis kaydi yok.</div>}
      </div>
    </section>
  );
}

function buildWasteUnitPrices(parameters: SystemParameter[]): Record<WasteType, string> {
  const fallback: Record<WasteType, string> = {
    Plastik: "12.50",
    Cam: "4.10",
    Metal: "16.75",
    Kagit: "5.60",
    Organik: "2.20",
    Diger: "1.25",
  };
  const keyByType: Record<WasteType, string> = {
    Plastik: "plastik_birim_fiyat",
    Cam: "cam_birim_fiyat",
    Metal: "metal_birim_fiyat",
    Kagit: "kagit_birim_fiyat",
    Organik: "organik_birim_fiyat",
    Diger: "diger_birim_fiyat",
  };

  return wasteTypes.reduce<Record<WasteType, string>>((prices, type) => {
    const parameter = parameters.find((item) => item.anahtar === keyByType[type]);
    prices[type] = parameter?.deger || fallback[type];
    return prices;
  }, { ...fallback });
}
