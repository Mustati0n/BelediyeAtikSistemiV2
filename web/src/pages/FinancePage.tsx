import {
  Banknote,
  Calculator,
  CheckCircle2,
  ClipboardCheck,
  Download,
  FileText,
  PieChart,
  RefreshCcw,
  Send,
  TrendingDown,
  TrendingUp,
  Users,
  WalletCards,
  XCircle,
  Plus,
  Trash2,
} from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  PendingExpense,
  PendingRevenue,
  Personnel,
  ProfitLossSummary,
  SalaryCalculation,
  approveExpense,
  approveRevenue,
  calculateSalary,
  createBatchSalaryPayment,
  createSingleSalaryPayment,
  getProfitLossSummary,
  listPendingExpenses,
  listPendingRevenues,
  listPersonnel,
  rejectExpense,
  rejectRevenue,
} from "../api";

type SalaryForm = {
  personel_id: string;
  donem_ay: string;
  donem_yil: string;
  odeme_tarihi: string;
  tutar: string;
  odeme_tipi: "Tekli" | "Avans";
};

type AdjustmentType = "Mesai" | "Ozel Gun" | "Prim" | "Kesinti" | "Diger";

type PayrollAdjustment = {
  id: number;
  type: AdjustmentType;
  description: string;
  amount: string;
};

const financeTabs = ["Kokpit", "Onay Kuyrugu", "Personel Karti", "Bordro", "Raporlar"] as const;
type FinanceTab = (typeof financeTabs)[number];

const today = new Date().toISOString().slice(0, 10);

const emptySalaryForm: SalaryForm = {
  personel_id: "",
  donem_ay: String(new Date().getMonth() + 1),
  donem_yil: String(new Date().getFullYear()),
  odeme_tarihi: today,
  tutar: "",
  odeme_tipi: "Tekli",
};

export function FinancePage({ token, readOnly = false }: { token: string; readOnly?: boolean }) {
  const [activeTab, setActiveTab] = useState<FinanceTab>("Kokpit");
  const [expenses, setExpenses] = useState<PendingExpense[]>([]);
  const [revenues, setRevenues] = useState<PendingRevenue[]>([]);
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [summary, setSummary] = useState<ProfitLossSummary | null>(null);
  const [salary, setSalary] = useState<SalaryCalculation | null>(null);
  const [form, setForm] = useState<SalaryForm>(emptySalaryForm);
  const [adjustments, setAdjustments] = useState<PayrollAdjustment[]>([]);
  const [adjustmentDraft, setAdjustmentDraft] = useState<Omit<PayrollAdjustment, "id">>({
    type: "Mesai",
    description: "",
    amount: "",
  });
  const [approvalFilter, setApprovalFilter] = useState<"Tum Kayitlar" | "Gider" | "Gelir">("Tum Kayitlar");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyKey, setBusyKey] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);
    try {
      const [expenseData, revenueData, personnelData, summaryData] = await Promise.all([
        listPendingExpenses(token),
        listPendingRevenues(token),
        listPersonnel(token),
        getProfitLossSummary(token),
      ]);
      setExpenses(expenseData);
      setRevenues(revenueData);
      setPersonnel(personnelData);
      setSummary(summaryData);
      setForm((current) => ({
        ...current,
        personel_id: current.personel_id || String(personnelData.find((person) => person.aktif_mi)?.id || ""),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Muhasebe verisi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const activePersonnel = useMemo(
    () => personnel.filter((person) => person.aktif_mi),
    [personnel],
  );
  const pendingExpenseTotal = expenses.reduce((total, item) => total + Number(item.tutar), 0);
  const pendingRevenueTotal = revenues.reduce((total, item) => total + Number(item.tutar), 0);
  const pendingNetImpact = pendingRevenueTotal - pendingExpenseTotal;
  const approvedNet = summary ? Number(summary.net_sonuc) : 0;
  const projectedNet = approvedNet + pendingNetImpact;
  const payrollBase = activePersonnel.reduce((total, person) => total + Number(person.taban_maas), 0);
  const selectedPersonnel = personnel.find((person) => person.id === Number(form.personel_id)) || null;
  const selectedBaseSalary = selectedPersonnel ? Number(selectedPersonnel.taban_maas) : 0;
  const selectedChildSupport = selectedPersonnel ? selectedPersonnel.cocuk_sayisi * 1000 : 0;
  const selectedCalculatedSalary = salary ? Number(salary.toplam_hesaplanan_maas) : selectedBaseSalary + selectedChildSupport;
  const adjustmentTotal = adjustments.reduce((sum, item) => {
    const value = Number(item.amount || 0);
    return sum + (item.type === "Kesinti" ? -Math.abs(value) : Math.abs(value));
  }, 0);
  const personnelCardTotal = selectedCalculatedSalary + adjustmentTotal;
  const periodLabel = `${form.donem_ay.padStart(2, "0")}/${form.donem_yil}`;
  const totalPending = expenses.length + revenues.length;
  const approvalItems = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("tr-TR");
    const rows = [
      ...expenses.map((item) => ({ ...item, kind: "expense" as const })),
      ...revenues.map((item) => ({ ...item, kind: "revenue" as const })),
    ];
    return rows
      .filter((item) => {
        const kindMatch =
          approvalFilter === "Tum Kayitlar" ||
          (approvalFilter === "Gider" && item.kind === "expense") ||
          (approvalFilter === "Gelir" && item.kind === "revenue");
        const text = [
          item.aciklama,
          "arac_plaka" in item ? item.arac_plaka || "" : "",
          "satis_id" in item && item.satis_id ? `satis ${item.satis_id}` : "",
        ].join(" ").toLocaleLowerCase("tr-TR");
        return kindMatch && (!needle || text.includes(needle));
      })
      .sort((a, b) => Math.abs(Number(b.tutar)) - Math.abs(Number(a.tutar)));
  }, [approvalFilter, expenses, query, revenues]);

  async function handleDecision(
    kind: "expense" | "revenue",
    id: number,
    decision: "approve" | "reject",
  ) {
    if (readOnly) return;
    setBusyKey(`${kind}-${id}-${decision}`);
    setError("");
    setMessage("");
    try {
      if (kind === "expense" && decision === "approve") await approveExpense(token, id);
      if (kind === "expense" && decision === "reject") await rejectExpense(token, id);
      if (kind === "revenue" && decision === "approve") await approveRevenue(token, id);
      if (kind === "revenue" && decision === "reject") await rejectRevenue(token, id);
      setMessage(`${id} numarali ${kind === "expense" ? "gider" : "gelir"} kaydi islendi.`);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Onay islemi tamamlanamadi.");
    } finally {
      setBusyKey("");
    }
  }

  async function handleCalculate() {
    const personelId = Number(form.personel_id);
    if (!personelId) {
      setError("Maas hesaplamak icin personel secin.");
      return;
    }

    setError("");
    setMessage("");
    try {
      const data = await calculateSalary(token, personelId);
      setSalary(data);
      setForm((current) => ({
        ...current,
        tutar: current.tutar || Number(data.toplam_hesaplanan_maas).toFixed(2),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Maas hesaplanamadi.");
    }
  }

  async function handleSinglePayment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (readOnly) return;
    setError("");
    setMessage("");

    const personelId = Number(form.personel_id);
    const month = Number(form.donem_ay);
    const year = Number(form.donem_yil);
    const amount = Number(form.tutar);

    if (!personelId || month < 1 || month > 12 || !year || !Number.isFinite(amount) || amount <= 0) {
      setError("Personel, donem, tarih ve pozitif tutar zorunludur.");
      return;
    }

    setSaving(true);
    try {
      const payment = await createSingleSalaryPayment(token, {
        personel_id: personelId,
        donem_ay: month,
        donem_yil: year,
        odeme_tarihi: form.odeme_tarihi,
        tutar: amount.toFixed(2),
        odeme_tipi: form.odeme_tipi,
        aciklama: buildPayrollDescription(adjustments),
      });
      setMessage(`${payment.ad_soyad} icin ${payment.odeme_tipi} odemesi kaydedildi.`);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Maas odemesi kaydedilemedi.");
    } finally {
      setSaving(false);
    }
  }

  function addAdjustment() {
    const amount = Number(adjustmentDraft.amount);
    if (!adjustmentDraft.description.trim() || !Number.isFinite(amount) || amount <= 0) {
      setError("Ek kalem icin aciklama ve pozitif tutar girin.");
      return;
    }
    setError("");
    setAdjustments((current) => [
      ...current,
      {
        id: Date.now(),
        type: adjustmentDraft.type,
        description: adjustmentDraft.description.trim(),
        amount: amount.toFixed(2),
      },
    ]);
    setAdjustmentDraft({ type: "Mesai", description: "", amount: "" });
  }

  function applyPersonnelCardTotal() {
    setForm((current) => ({ ...current, tutar: personnelCardTotal.toFixed(2) }));
    setActiveTab("Bordro");
    setMessage("Personel karti toplam tutari bordro odeme formuna aktarildi.");
  }

  async function handleBatchPayment() {
    if (readOnly) return;
    setError("");
    setMessage("");
    const month = Number(form.donem_ay);
    const year = Number(form.donem_yil);

    if (month < 1 || month > 12 || !year || !form.odeme_tarihi) {
      setError("Toplu odeme icin donem ve tarih zorunludur.");
      return;
    }

    setSaving(true);
    try {
      const batch = await createBatchSalaryPayment(token, {
        donem_ay: month,
        donem_yil: year,
        odeme_tarihi: form.odeme_tarihi,
      });
      setMessage(`${batch.kayit_sayisi} personel icin toplu maas odemesi yapildi.`);
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Toplu maas odemesi yapilamadi.");
    } finally {
      setSaving(false);
    }
  }

  function exportFinanceCsv() {
    const rows = [
      ["Tip", "ID", "Tarih", "Aciklama", "Tutar", "Durum", "Kaynak"],
      ...expenses.map((item) => [
        "Gider",
        item.id,
        item.tarih,
        item.aciklama,
        item.tutar,
        item.durum,
        item.arac_plaka || `Bakim #${item.bakim_kaydi_id || "-"}`,
      ]),
      ...revenues.map((item) => [
        "Gelir",
        item.id,
        item.tarih,
        item.aciklama,
        item.tutar,
        item.durum,
        `Satis #${item.satis_id || "-"}`,
      ]),
    ];
    const csv = rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(";")).join("\n");
    const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `muhasebe-kuyrugu-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="page-stack finance-cockpit">
      <section className="page-hero finance-hero">
        <div>
          <p>FINANS OPERASYON MERKEZI</p>
          <h1>Muhasebe, Onay ve Bordro Kontrolu</h1>
          <span>
            Gelir-gider onaylarini yonetin, nakit etkisini izleyin, personel odemelerini donem
            bazli calistirin ve finansal raporlari tek kokpitten takip edin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <Banknote size={34} />
          <strong>{totalPending}</strong>
          <span>Onay Bekleyen</span>
          <small>{summary ? `${formatMoney(summary.net_sonuc)} net sonuc` : "Ozet yukleniyor"}</small>
        </div>
      </section>

      <section className="finance-ledger-grid">
        <FinanceMetric icon={TrendingUp} label="Onayli Gelir" value={formatMoney(summary?.onayli_gelir_toplami || 0)} note="kesinlesen" tone="income" />
        <FinanceMetric icon={TrendingDown} label="Onayli Gider" value={formatMoney(summary?.onayli_gider_toplami || 0)} note="kesinlesen" tone="expense" />
        <FinanceMetric icon={WalletCards} label="Bekleyen Net" value={formatMoney(pendingNetImpact)} note="onay etkisi" tone={pendingNetImpact >= 0 ? "income" : "expense"} />
        <FinanceMetric icon={PieChart} label="Projeksiyon" value={formatMoney(projectedNet)} note="net + bekleyen" tone={projectedNet >= 0 ? "income" : "expense"} />
      </section>

      <nav className="facility-tabs" aria-label="Muhasebe sekmeleri">
        {financeTabs.map((tab) => (
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

      {activeTab === "Kokpit" && (
        <section className="finance-dashboard-grid">
          <article className="finance-control-panel">
            <div className="panel-heading">
              <div>
                <h3>Nakit Akisi Gosterimi</h3>
                <p>Onayli sonuc ve bekleyen kayitlarin muhtemel etkisi</p>
              </div>
              <FileText size={22} />
            </div>
            <div className="cashflow-bars">
              <CashBar label="Onayli net" value={approvedNet} max={Math.max(Math.abs(approvedNet), Math.abs(projectedNet), 1)} />
              <CashBar label="Bekleyen gelir" value={pendingRevenueTotal} max={Math.max(pendingRevenueTotal, pendingExpenseTotal, 1)} />
              <CashBar label="Bekleyen gider" value={-pendingExpenseTotal} max={Math.max(pendingRevenueTotal, pendingExpenseTotal, 1)} />
              <CashBar label="Tahmini net" value={projectedNet} max={Math.max(Math.abs(approvedNet), Math.abs(projectedNet), 1)} />
            </div>
          </article>

          <article className="finance-control-panel">
            <div className="panel-heading">
              <div>
                <h3>Onay Onceligi</h3>
                <p>En yuksek tutarli bekleyen kayitlar</p>
              </div>
              <ClipboardCheck size={22} />
            </div>
            <div className="finance-priority-list">
              {approvalItems.slice(0, 5).map((item) => (
                <button key={`${item.kind}-${item.id}`} onClick={() => setActiveTab("Onay Kuyrugu")} type="button">
                  <span>{item.kind === "expense" ? "Gider" : "Gelir"} #{item.id}</span>
                  <strong>{formatMoney(item.tutar)}</strong>
                  <small>{item.aciklama}</small>
                </button>
              ))}
              {!loading && approvalItems.length === 0 && <div className="empty-state">Bekleyen onay yok.</div>}
            </div>
          </article>

          <article className="finance-control-panel">
            <div className="panel-heading">
              <div>
                <h3>Donem Kontrolu</h3>
                <p>{periodLabel} muhasebe hazirlik ozeti</p>
              </div>
              <Users size={22} />
            </div>
            <div className="finance-check-list enhanced">
              <div>
                <span>Aktif Personel</span>
                <strong>{activePersonnel.length}</strong>
                <small>{formatMoney(payrollBase)} taban bordro</small>
              </div>
              <div>
                <span>Bekleyen Gider</span>
                <strong>{expenses.length}</strong>
                <small>{formatMoney(pendingExpenseTotal)}</small>
              </div>
              <div>
                <span>Bekleyen Gelir</span>
                <strong>{revenues.length}</strong>
                <small>{formatMoney(pendingRevenueTotal)}</small>
              </div>
              <div>
                <span>Calisma Modu</span>
                <strong>{readOnly ? "Izleme" : "Yetkili"}</strong>
                <small>{readOnly ? "islem kapali" : "onay ve odeme acik"}</small>
              </div>
            </div>
          </article>
        </section>
      )}

      {activeTab === "Onay Kuyrugu" && (
        <section className="finance-approval-desk">
          <div className="finance-toolbar">
            <label>
              Arama
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Aciklama, arac, satis..." />
            </label>
            <label>
              Kayit Tipi
              <select value={approvalFilter} onChange={(event) => setApprovalFilter(event.target.value as typeof approvalFilter)}>
                <option>Tum Kayitlar</option>
                <option>Gider</option>
                <option>Gelir</option>
              </select>
            </label>
            <button className="row-action" onClick={exportFinanceCsv} type="button">
              <Download size={16} />
              CSV
            </button>
            <button className="row-action" onClick={loadData} type="button">
              <RefreshCcw size={16} />
              Yenile
            </button>
          </div>
          <ApprovalLedger
            busyKey={busyKey}
            items={approvalItems}
            loading={loading}
            readOnly={readOnly}
            onDecision={handleDecision}
          />
        </section>
      )}

      {activeTab === "Personel Karti" && (
        <section className="employee-payroll-grid">
          <article className="finance-control-panel employee-profile-card">
            <div className="panel-heading">
              <div>
                <h3>Personel Maas Bilgisi</h3>
                <p>Secilen personelin bordro temeli ve donem hesabi</p>
              </div>
              <Users size={22} />
            </div>
            <label>
              Personel
              <select
                value={form.personel_id}
                disabled={readOnly}
                onChange={(event) => {
                  setSalary(null);
                  setAdjustments([]);
                  setForm({ ...form, personel_id: event.target.value, tutar: "" });
                }}
              >
                <option value="">Personel secin</option>
                {activePersonnel.map((person) => (
                  <option key={person.id} value={person.id}>
                    {person.ad_soyad} / {person.rol.ad}
                  </option>
                ))}
              </select>
            </label>
            <div className="employee-salary-facts">
              <div>
                <span>Taban Maas</span>
                <strong>{formatMoney(selectedBaseSalary)}</strong>
              </div>
              <div>
                <span>Cocuk Destegi</span>
                <strong>{formatMoney(selectedChildSupport)}</strong>
              </div>
              <div>
                <span>Hesaplanan Maas</span>
                <strong>{formatMoney(selectedCalculatedSalary)}</strong>
              </div>
              <div>
                <span>Rol / Cocuk</span>
                <strong>{selectedPersonnel ? `${selectedPersonnel.rol.ad} / ${selectedPersonnel.cocuk_sayisi}` : "-"}</strong>
              </div>
            </div>
            <button className="row-action" disabled={readOnly || !form.personel_id} onClick={handleCalculate} type="button">
              <Calculator size={17} />
              Maas Bilgisini Yenile
            </button>
          </article>

          <article className="finance-control-panel employee-adjustment-card">
            <div className="panel-heading">
              <div>
                <h3>Ek Kalemler</h3>
                <p>Mesai, ozel gun, prim veya kesinti ekleyin</p>
              </div>
              <Plus size={22} />
            </div>
            <div className="adjustment-form">
              <label>
                Tip
                <select value={adjustmentDraft.type} disabled={readOnly} onChange={(event) => setAdjustmentDraft({ ...adjustmentDraft, type: event.target.value as AdjustmentType })}>
                  <option>Mesai</option>
                  <option>Ozel Gun</option>
                  <option>Prim</option>
                  <option>Kesinti</option>
                  <option>Diger</option>
                </select>
              </label>
              <label>
                Aciklama
                <input value={adjustmentDraft.description} disabled={readOnly} onChange={(event) => setAdjustmentDraft({ ...adjustmentDraft, description: event.target.value })} placeholder="Bayram mesaisi, gece vardiyasi..." />
              </label>
              <label>
                Tutar
                <input inputMode="decimal" value={adjustmentDraft.amount} disabled={readOnly} onChange={(event) => setAdjustmentDraft({ ...adjustmentDraft, amount: event.target.value })} placeholder="2500" />
              </label>
              <button className="primary-action" disabled={readOnly} onClick={addAdjustment} type="button">
                <Plus size={16} />
                Ekle
              </button>
            </div>
            <div className="adjustment-list">
              {adjustments.map((item) => (
                <div key={item.id}>
                  <span>{item.type}</span>
                  <strong>{item.description}</strong>
                  <b>{item.type === "Kesinti" ? "-" : "+"}{formatMoney(item.amount)}</b>
                  <button
                    className="icon-button"
                    disabled={readOnly}
                    onClick={() => setAdjustments((current) => current.filter((row) => row.id !== item.id))}
                    type="button"
                    title="Sil"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ))}
              {adjustments.length === 0 && <div className="empty-state">Ek kalem yok.</div>}
            </div>
          </article>

          <article className="finance-control-panel employee-total-card">
            <div className="panel-heading">
              <div>
                <h3>Personel Donem Toplami</h3>
                <p>{periodLabel} icin odemeye aktarilacak tutar</p>
              </div>
              <WalletCards size={22} />
            </div>
            <div className="employee-total">
              <span>Net odenecek</span>
              <strong>{formatMoney(personnelCardTotal)}</strong>
              <small>Ek kalem etkisi: {formatMoney(adjustmentTotal)}</small>
            </div>
            <button className="primary-action" disabled={readOnly || !selectedPersonnel} onClick={applyPersonnelCardTotal} type="button">
              <Send size={17} />
              Bordroya Aktar
            </button>
          </article>
        </section>
      )}

      {activeTab === "Bordro" && (
        <section className="finance-payroll-layout">
          <section className="form-panel action-panel finance-payroll-panel">
            <div className="panel-heading">
              <div>
                <h3>Maas ve Odeme Merkezi</h3>
                <p>
                  {readOnly
                    ? "Admin izleme modunda finans kayitlari goruntulenir; odeme/onay islemi yapilamaz."
                    : "Personel maasi hesaplayin, tekli/avans odeme yapin veya donem icin toplu maas calistirin."}
                </p>
              </div>
              <button className="icon-button" onClick={loadData} type="button" title="Yenile">
                <RefreshCcw size={18} />
              </button>
            </div>

            <form className="salary-form enhanced" onSubmit={handleSinglePayment}>
              <label>
                Personel
                <select
                  value={form.personel_id}
                  disabled={readOnly}
                  onChange={(event) => {
                    setSalary(null);
                    setForm({ ...form, personel_id: event.target.value, tutar: "" });
                  }}
                >
                  <option value="">Personel secin</option>
                  {activePersonnel.map((person) => (
                    <option key={person.id} value={person.id}>
                      {person.ad_soyad} / {person.rol.ad}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Ay
                <input disabled={readOnly} value={form.donem_ay} onChange={(event) => setForm({ ...form, donem_ay: event.target.value })} />
              </label>
              <label>
                Yil
                <input disabled={readOnly} value={form.donem_yil} onChange={(event) => setForm({ ...form, donem_yil: event.target.value })} />
              </label>
              <label>
                Tarih
                <input type="date" value={form.odeme_tarihi} disabled={readOnly} onChange={(event) => setForm({ ...form, odeme_tarihi: event.target.value })} />
              </label>
              <label>
                Tip
                <select value={form.odeme_tipi} disabled={readOnly} onChange={(event) => setForm({ ...form, odeme_tipi: event.target.value as "Tekli" | "Avans" })}>
                  <option>Tekli</option>
                  <option>Avans</option>
                </select>
              </label>
              <label>
                Tutar
                <input inputMode="decimal" value={form.tutar} disabled={readOnly} onChange={(event) => setForm({ ...form, tutar: event.target.value })} placeholder="35000" />
              </label>
              <div className="salary-form-actions">
                <button className="row-action" disabled={readOnly || !form.personel_id} onClick={handleCalculate} type="button">
                  <Calculator size={17} />
                  Hesapla
                </button>
                <button className="primary-action" disabled={saving || readOnly || !form.personel_id} type="submit">
                  <Send size={18} />
                  Tekli Ode
                </button>
              </div>
            </form>

            <div className="salary-actions">
              <span>
                {salary
                  ? `${salary.ad_soyad}: ${formatMoney(salary.toplam_hesaplanan_maas)} hesaplandi`
                  : "Maas hesaplamak icin personel secin."}
              </span>
              <button className="row-action" disabled={saving || readOnly || activePersonnel.length === 0} onClick={handleBatchPayment} type="button">
                Toplu Maas Ode
              </button>
            </div>
          </section>

          <aside className="finance-control-panel">
            <div className="panel-heading">
              <div>
                <h3>Bordro Ozeti</h3>
                <p>{periodLabel} donem hazirligi</p>
              </div>
              <Users size={22} />
            </div>
            <div className="finance-check-list enhanced">
              <div>
                <span>Aktif Personel</span>
                <strong>{activePersonnel.length}</strong>
              </div>
              <div>
                <span>Taban Bordro</span>
                <strong>{formatMoney(payrollBase)}</strong>
              </div>
              <div>
                <span>Ortalama Maas</span>
                <strong>{formatMoney(activePersonnel.length ? payrollBase / activePersonnel.length : 0)}</strong>
              </div>
              <div>
                <span>Odeme Tarihi</span>
                <strong>{new Date(form.odeme_tarihi).toLocaleDateString("tr-TR")}</strong>
              </div>
            </div>
          </aside>
        </section>
      )}

      {activeTab === "Raporlar" && (
        <section className="finance-report-grid">
          <ReportCard title="Kar / Zarar" value={formatMoney(summary?.net_sonuc || 0)} note="Onayli gelir - onayli gider" positive={approvedNet >= 0} />
          <ReportCard title="Bekleyen Tahsilat" value={formatMoney(pendingRevenueTotal)} note={`${revenues.length} gelir kaydi`} positive />
          <ReportCard title="Bekleyen Odeme" value={formatMoney(pendingExpenseTotal)} note={`${expenses.length} gider kaydi`} positive={false} />
          <ReportCard title="Tahmini Sonuc" value={formatMoney(projectedNet)} note="Onayli net + bekleyen etki" positive={projectedNet >= 0} />
        </section>
      )}
    </div>
  );
}

function FinanceMetric({ icon: Icon, label, value, note, tone }: { icon: typeof Banknote; label: string; value: string; note: string; tone: "income" | "expense" }) {
  return (
    <article className={`finance-ledger-card ${tone}`}>
      <Icon size={22} />
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function CashBar({ label, value, max }: { label: string; value: number; max: number }) {
  const width = Math.min(100, Math.round((Math.abs(value) / max) * 100));
  return (
    <div className={value >= 0 ? "cash-row income" : "cash-row expense"}>
      <span>{label}</span>
      <strong>{formatMoney(value)}</strong>
      <i><b style={{ width: `${Math.max(5, width)}%` }} /></i>
    </div>
  );
}

function ApprovalLedger({
  busyKey,
  items,
  loading,
  readOnly,
  onDecision,
}: {
  busyKey: string;
  items: Array<(PendingExpense | PendingRevenue) & { kind: "expense" | "revenue" }>;
  loading: boolean;
  readOnly: boolean;
  onDecision: (type: "expense" | "revenue", id: number, decision: "approve" | "reject") => void;
}) {
  return (
    <section className="data-panel">
      <div className="table-title">
        <strong>Onay Defteri</strong>
        <span>{loading ? "Yukleniyor" : `${items.length} kayit`}</span>
      </div>

      <div className="finance-ledger-list">
        {items.map((item) => (
          <article key={`${item.kind}-${item.id}`}>
            <div className={`ledger-kind ${item.kind}`}>
              {item.kind === "expense" ? "Gider" : "Gelir"}
            </div>
            <div>
              <strong>#{item.id} / {item.aciklama}</strong>
              <span>{new Date(item.tarih).toLocaleString("tr-TR")}</span>
              <small>
                {"arac_plaka" in item && item.arac_plaka ? `Arac: ${item.arac_plaka}` : ""}
                {"satis_id" in item && item.satis_id ? `Satis: #${item.satis_id}` : ""}
              </small>
            </div>
            <strong className="ledger-amount">{formatMoney(item.tutar)}</strong>
            <div className="approval-actions">
              <button className="row-action" disabled={readOnly || busyKey === `${item.kind}-${item.id}-reject`} onClick={() => onDecision(item.kind, item.id, "reject")} type="button">
                <XCircle size={16} />
                Reddet
              </button>
              <button className="primary-action" disabled={readOnly || busyKey === `${item.kind}-${item.id}-approve`} onClick={() => onDecision(item.kind, item.id, "approve")} type="button">
                <CheckCircle2 size={16} />
                Onayla
              </button>
            </div>
          </article>
        ))}

        {!loading && items.length === 0 && (
          <div className="empty-state">
            <Banknote size={22} />
            Bekleyen muhasebe kaydi yok.
          </div>
        )}
      </div>
    </section>
  );
}

function ReportCard({ title, value, note, positive }: { title: string; value: string; note: string; positive: boolean }) {
  return (
    <article className={`finance-report-card ${positive ? "positive" : "negative"}`}>
      <span>{title}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function buildPayrollDescription(adjustments: PayrollAdjustment[]): string | null {
  if (adjustments.length === 0) return null;
  return adjustments
    .map((item) => `${item.type}: ${item.description} (${item.type === "Kesinti" ? "-" : "+"}${Number(item.amount).toFixed(2)} TL)`)
    .join(" | ");
}

function formatMoney(value: string | number): string {
  return Number(value).toLocaleString("tr-TR", {
    style: "currency",
    currency: "TRY",
  });
}
