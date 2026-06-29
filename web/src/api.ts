export type Role =
  | "Sistem Yoneticisi"
  | "Sofor"
  | "Bakim Teknisyeni"
  | "Muhasebe Personeli"
  | "Geri Donusum Operatoru";

export type CurrentUser = {
  id: number;
  ad_soyad: string;
  email: string;
  tc_no: string;
  aktif_mi: boolean;
  rol: Role;
};

export type VehicleStatus = "Aktif" | "Pasif" | "Bakimda" | "Hurda";

export type Vehicle = {
  id: number;
  plaka: string;
  tip: string;
  kapasite_kg: number;
  durum: VehicleStatus;
};

export type VehicleCreate = {
  plaka: string;
  tip: string;
  kapasite_kg: number;
};

export type VehicleUpdate = {
  tip?: string;
  kapasite_kg?: number;
  durum?: VehicleStatus;
};

export type RoleRecord = {
  id: number;
  ad: Role;
  aciklama?: string | null;
};

export type Personnel = {
  id: number;
  tc_no: string;
  ad_soyad: string;
  email: string;
  telefon?: string | null;
  taban_maas: string;
  cocuk_sayisi: number;
  aktif_mi: boolean;
  rol: RoleRecord;
};

export type PersonnelCreate = {
  tc_no: string;
  ad_soyad: string;
  email: string;
  telefon?: string | null;
  taban_maas: string;
  cocuk_sayisi: number;
  rol_id: number;
  password: string;
};

export type PersonnelUpdate = Partial<
  Omit<PersonnelCreate, "tc_no" | "password"> & {
    aktif_mi: boolean;
    password: string;
  }
>;

export type ContainerStatus =
  | "Normal"
  | "Izleniyor"
  | "Kritik"
  | "GoreveAtandi"
  | "Bosaltildi";

export type Region = {
  id: number;
  ad: string;
  aciklama?: string | null;
};

export type Container = {
  id: number;
  kod: string;
  enlem: string;
  boylam: string;
  doluluk_orani: number;
  durum: ContainerStatus;
  bolge: Region;
};

export type RegionCreate = {
  ad: string;
  aciklama?: string | null;
};

export type ContainerCreate = {
  kod: string;
  enlem: string;
  boylam: string;
  doluluk_orani: number;
  durum: ContainerStatus;
  bolge_id: number;
};

export type ContainerUpdate = Partial<ContainerCreate>;

export type TaskStatus = "Bekliyor" | "Atandi" | "Islemde" | "Tamamlandi" | "Basarisiz";
export type TaskResult =
  | "Tamamlandi"
  | "Ulasilamadi"
  | "YanlisIhbar"
  | "TekrarKontrolGerekli";
export type TaskType = "Ihbar" | "KritikKonteyner";

export type DriverTaskSource = {
  tip: string;
  id: number;
  aciklama: string;
  enlem: string;
  boylam: string;
  durum: string;
  doluluk_orani?: number | null;
  fotograf_url?: string | null;
};

export type DriverTaskVehicle = {
  id: number;
  plaka: string;
  tip: string;
  kapasite_kg: number;
  durum: string;
};

export type DriverTask = {
  id: number;
  tip: TaskType;
  durum: TaskStatus;
  oncelik: number;
  planlanan_tarih?: string | null;
  sira_no?: number | null;
  aciklama?: string | null;
  kullanilan_arac_id?: number | null;
  kullanilan_arac?: DriverTaskVehicle | null;
  kaynak: DriverTaskSource;
};

export type TaskActionResponse = {
  gorev_id: number;
  durum: TaskStatus;
  mesaj: string;
};

export type ContainerFillUpdateResponse = {
  konteyner_id: number;
  doluluk_orani: number;
  durum: ContainerStatus;
  gorev_olusturuldu: boolean;
  gorev_id?: number | null;
};

export type ContainerFillSimulationItem = {
  konteyner_id: number;
  kod: string;
  eski_doluluk_orani: number;
  yeni_doluluk_orani: number;
  artis_orani: number;
  durum: ContainerStatus;
  gorev_olusturuldu: boolean;
  gorev_id?: number | null;
};

export type ContainerFillSimulationResponse = {
  toplam_konteyner: number;
  guncellenen_konteyner: number;
  olusan_gorev_sayisi: number;
  sonuclar: ContainerFillSimulationItem[];
};

export type MaintenanceStatus = "Acildi" | "Incelemede" | "Tamamlandi" | "Iptal";
export type ApprovalStatus = "Beklemede" | "Onaylandi" | "Reddedildi";

export type MaintenanceRecord = {
  id: number;
  arac_id: number;
  arac_plaka: string;
  tarih: string;
  aciklama: string;
  bakim_turu?: string | null;
  oncelik?: string | null;
  maliyet_tl: string;
  parca_maliyeti_tl?: string | null;
  iscilik_maliyeti_tl?: string | null;
  tedarikci?: string | null;
  kilometre?: number | null;
  planlanan_tarih?: string | null;
  durum: MaintenanceStatus;
  teknik_tamamlanma_tarihi?: string | null;
  arac_durumu: VehicleStatus;
  gider_kaydi_id?: number | null;
  gider_durumu?: ApprovalStatus | null;
};

export type MaintenanceCreate = {
  arac_id: number;
  aciklama: string;
  maliyet_tl: string;
  tarih?: string | null;
  bakim_turu?: string | null;
  oncelik?: string | null;
  parca_maliyeti_tl?: string | null;
  iscilik_maliyeti_tl?: string | null;
  tedarikci?: string | null;
  kilometre?: number | null;
  planlanan_tarih?: string | null;
};

export type PendingExpense = {
  id: number;
  tarih: string;
  tutar: string;
  aciklama: string;
  durum: ApprovalStatus;
  bakim_kaydi_id?: number | null;
  arac_plaka?: string | null;
};

export type PendingRevenue = {
  id: number;
  tarih: string;
  tutar: string;
  aciklama: string;
  durum: ApprovalStatus;
  satis_id?: number | null;
};

export type DecisionResponse = {
  gider_id?: number;
  gelir_id?: number;
  durum: ApprovalStatus;
  mesaj: string;
};

export type ProfitLossSummary = {
  onayli_gelir_toplami: string;
  onayli_gider_toplami: string;
  net_sonuc: string;
  bekleyen_gider_sayisi: number;
  bekleyen_gelir_sayisi: number;
};

export type PaymentType = "Avans" | "Tekli" | "Toplu";
export type PaymentStatus = "Bekliyor" | "Odendi" | "Iptal";

export type SalaryCalculation = {
  personel_id: number;
  ad_soyad: string;
  taban_maas: string;
  cocuk_sayisi: number;
  cocuk_destegi: string;
  toplam_hesaplanan_maas: string;
};

export type SalaryPayment = {
  id: number;
  personel_id: number;
  ad_soyad: string;
  tutar: string;
  aciklama?: string | null;
  odeme_tipi: PaymentType;
  durum: PaymentStatus;
  donem_ay: number;
  donem_yil: number;
  odeme_tarihi: string;
};

export type BatchSalaryResponse = {
  toplam_odeme: string;
  kayit_sayisi: number;
  odemeler: SalaryPayment[];
};

export type WasteType = "Plastik" | "Cam" | "Metal" | "Kagit" | "Organik" | "Diger";

export type Delivery = {
  id: number;
  tarih: string;
  toplam_kg: string;
  atik_tipi?: WasteType | null;
  aciklama?: string | null;
  onaylandi_mi: boolean;
  onay_tarihi?: string | null;
  teslim_eden_sofor_id: number;
  teslim_alan_operator_id?: number | null;
};

export type Stock = {
  id: number;
  atik_tipi: WasteType;
  toplam_miktar_kg: string;
};

export type SortingItem = {
  atik_tipi: WasteType;
  miktar_kg: string;
  aciklama?: string | null;
};

export type SortingResponse = {
  teslim_id: number;
  hareket_sayisi: number;
};

export type StockMovement = {
  id: number;
  tarih: string;
  atik_tipi: WasteType;
  miktar_kg: string;
  aciklama?: string | null;
  stok_id: number;
  tesis_teslim_id: number;
};

export type SaleResponse = {
  satis_id: number;
  tarih: string;
  stok_id: number;
  atik_tipi: WasteType;
  miktar_kg: string;
  birim_fiyat: string;
  toplam_tutar: string;
  alici_firma?: string | null;
  belge_no?: string | null;
  durum: ApprovalStatus;
  gelir_kaydi_id?: number | null;
  gelir_durumu?: ApprovalStatus | null;
};

export type CitizenReportResponse = {
  ihbar_id: number;
  gorev_id: number;
  durum: string;
  mesaj: string;
};

export type CitizenPhotoUploadResponse = {
  fotograf_url: string;
  dosya_adi: string;
  boyut: number;
};

export type CitizenReportStatus = {
  ihbar_id: number;
  durum: string;
  aciklama: string;
  enlem: string;
  boylam: string;
  olusturma_tarihi: string;
  gorev_id?: number | null;
  gorev_durumu?: string | null;
};

export type CountByStatus = {
  durum: string;
  sayi: number;
};

export type AdminModuleSnapshot = {
  toplam: number;
  durumlar: CountByStatus[];
};

export type AdminTaskSnapshot = AdminModuleSnapshot & {
  bekleyen: number;
  atanmis: number;
  islemde: number;
};

export type RecentAuditLog = {
  id: number;
  islem_tipi: string;
  aciklama: string;
  varlik_tipi: string;
  varlik_id?: number | null;
  islem_tarihi: string;
  yapan?: string | null;
};

export type AdminDashboardSummary = {
  araclar: AdminModuleSnapshot;
  personel: AdminModuleSnapshot;
  konteynerler: AdminModuleSnapshot;
  gorevler: AdminTaskSnapshot;
  bakim: AdminModuleSnapshot;
  tesis_teslimleri: AdminModuleSnapshot;
  stok_toplam_kg: string;
  finans: ProfitLossSummary;
  son_islemler: RecentAuditLog[];
};

export type AdminLogFilters = {
  query?: string;
  islem_tipi?: string;
  varlik_tipi?: string;
  yapan?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
};

export type AdminLogListResponse = {
  toplam: number;
  loglar: RecentAuditLog[];
};

export type SystemParameter = {
  id: number;
  anahtar: string;
  deger: string;
  veri_tipi: string;
  kategori?: string | null;
  aciklama?: string | null;
};

export type SystemParameterListResponse = {
  toplam: number;
  parametreler: SystemParameter[];
};

type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_at: string;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ||
  (window.location.protocol === "https:"
    ? `${window.location.origin}/api/v1`
    : "http://77.83.37.48:8000/api/v1");

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const detail = data?.detail || response.statusText || "Beklenmeyen hata olustu.";
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => item?.msg || item?.message || String(item))
        .filter(Boolean);
      throw new ApiError(messages.join(" ") || "Beklenmeyen hata olustu.");
    }
    throw new ApiError(String(detail));
  }

  return data as T;
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  return parseResponse<TokenResponse>(response);
}

export async function createCitizenReport(payload: {
  aciklama: string;
  enlem: string;
  boylam: string;
  fotograf_url?: string | null;
}): Promise<CitizenReportResponse> {
  const response = await fetch(`${API_BASE_URL}/public/ihbarlar`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseResponse<CitizenReportResponse>(response);
}

export async function uploadCitizenReportPhoto(file: File): Promise<CitizenPhotoUploadResponse> {
  const body = new FormData();
  body.set("file", file);
  const response = await fetch(`${API_BASE_URL}/public/ihbarlar/fotograf`, {
    method: "POST",
    body,
  });
  return parseResponse<CitizenPhotoUploadResponse>(response);
}

export async function getCitizenReportStatus(ihbarId: number): Promise<CitizenReportStatus> {
  const response = await fetch(`${API_BASE_URL}/public/ihbarlar/${ihbarId}`);
  return parseResponse<CitizenReportStatus>(response);
}

export async function createAdminReportTask(
  token: string,
  payload: {
    aciklama: string;
    enlem: string;
    boylam: string;
    fotograf_url?: string | null;
  },
): Promise<CitizenReportResponse> {
  return apiRequest<CitizenReportResponse>(token, "/operations/ihbarlar", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCurrentUser(token: string): Promise<CurrentUser> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return parseResponse<CurrentUser>(response);
}

export async function apiRequest<T>(
  token: string,
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  return parseResponse<T>(response);
}

export async function getAdminDashboard(token: string): Promise<AdminDashboardSummary> {
  return apiRequest<AdminDashboardSummary>(token, "/admin/dashboard");
}

export async function listAdminLogs(
  token: string,
  filters: AdminLogFilters = {},
): Promise<AdminLogListResponse> {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      params.set(key, String(value));
    }
  });

  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiRequest<AdminLogListResponse>(token, `/admin/logs${suffix}`);
}

export async function listSystemParameters(token: string): Promise<SystemParameter[]> {
  const data = await apiRequest<SystemParameterListResponse>(token, "/settings/parameters");
  return data.parametreler;
}

export async function updateSystemParameter(
  token: string,
  parameterId: number,
  value: string,
): Promise<SystemParameter> {
  return apiRequest<SystemParameter>(token, `/settings/parameters/${parameterId}`, {
    method: "PATCH",
    body: JSON.stringify({ deger: value }),
  });
}

export async function listVehicles(token: string): Promise<Vehicle[]> {
  const data = await apiRequest<{ toplam: number; araclar: Vehicle[] }>(token, "/fleet/araclar");
  return data.araclar;
}

export async function createVehicle(token: string, payload: VehicleCreate): Promise<Vehicle> {
  return apiRequest<Vehicle>(token, "/fleet/araclar", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateVehicle(
  token: string,
  vehicleId: number,
  payload: VehicleUpdate,
): Promise<Vehicle> {
  return apiRequest<Vehicle>(token, `/fleet/araclar/${vehicleId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function scrapVehicleSale(
  token: string,
  vehicleId: number,
  payload: { satis_tutari: string; aciklama?: string | null },
): Promise<{ arac: Vehicle; gelir_kaydi_id: number; mesaj: string }> {
  return apiRequest<{ arac: Vehicle; gelir_kaydi_id: number; mesaj: string }>(
    token,
    `/fleet/araclar/${vehicleId}/hurda-satis`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function listRoles(token: string): Promise<RoleRecord[]> {
  return apiRequest<RoleRecord[]>(token, "/personnel/roles");
}

export async function listPersonnel(token: string): Promise<Personnel[]> {
  const data = await apiRequest<{ toplam: number; personeller: Personnel[] }>(
    token,
    "/personnel",
  );
  return data.personeller;
}

export async function createPersonnel(
  token: string,
  payload: PersonnelCreate,
): Promise<Personnel> {
  return apiRequest<Personnel>(token, "/personnel", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePersonnel(
  token: string,
  personelId: number,
  payload: PersonnelUpdate,
): Promise<Personnel> {
  return apiRequest<Personnel>(token, `/personnel/${personelId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function listRegions(token: string): Promise<Region[]> {
  return apiRequest<Region[]>(token, "/containers/regions");
}

export async function createRegion(token: string, payload: RegionCreate): Promise<Region> {
  return apiRequest<Region>(token, "/containers/regions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listContainers(token: string): Promise<Container[]> {
  const data = await apiRequest<{ toplam: number; konteynerler: Container[] }>(
    token,
    "/containers",
  );
  return data.konteynerler;
}

export async function createContainer(
  token: string,
  payload: ContainerCreate,
): Promise<Container> {
  return apiRequest<Container>(token, "/containers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateContainer(
  token: string,
  containerId: number,
  payload: ContainerUpdate,
): Promise<Container> {
  return apiRequest<Container>(token, `/containers/${containerId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteContainer(token: string, containerId: number): Promise<void> {
  await apiRequest<void>(token, `/containers/${containerId}`, {
    method: "DELETE",
  });
}

export async function updateContainerFill(
  token: string,
  containerId: number,
  doluluk_orani: number,
): Promise<ContainerFillUpdateResponse> {
  return apiRequest<ContainerFillUpdateResponse>(
    token,
    `/operations/konteynerler/${containerId}/doluluk`,
    {
      method: "POST",
      body: JSON.stringify({ doluluk_orani }),
    },
  );
}

export async function simulateContainerFill(
  token: string,
): Promise<ContainerFillSimulationResponse> {
  return apiRequest<ContainerFillSimulationResponse>(
    token,
    "/operations/konteynerler/doluluk-simulasyon",
    {
      method: "POST",
    },
  );
}

export async function listDriverTasks(token: string): Promise<DriverTask[]> {
  const data = await apiRequest<{ toplam: number; gorevler: DriverTask[] }>(
    token,
    "/operations/sofor/gorevler/gunluk",
  );
  return data.gorevler;
}

export async function listOperationTasks(token: string): Promise<DriverTask[]> {
  const data = await apiRequest<{ toplam: number; gorevler: DriverTask[] }>(
    token,
    "/operations/gorevler",
  );
  return data.gorevler;
}

export async function assignOperationTask(
  token: string,
  taskId: number,
  payload: {
    sofor_id: number;
    arac_id?: number | null;
    planlanan_tarih?: string | null;
    sira_no?: number | null;
  },
): Promise<TaskActionResponse> {
  return apiRequest<TaskActionResponse>(token, `/operations/gorevler/${taskId}/ata`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deleteOperationTask(token: string, taskId: number): Promise<void> {
  await apiRequest<null>(token, `/operations/gorevler/${taskId}`, {
    method: "DELETE",
  });
}

export async function listMaintenanceRecords(token: string): Promise<MaintenanceRecord[]> {
  return apiRequest<MaintenanceRecord[]>(token, "/maintenance/bakim-kayitlari");
}

export async function createMaintenanceRecord(
  token: string,
  payload: MaintenanceCreate,
): Promise<MaintenanceRecord> {
  return apiRequest<MaintenanceRecord>(token, "/maintenance/bakim-kayitlari", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function completeMaintenanceTechnical(
  token: string,
  maintenanceId: number,
): Promise<MaintenanceRecord> {
  return apiRequest<MaintenanceRecord>(
    token,
    `/maintenance/bakim-kayitlari/${maintenanceId}/teknik-tamamla`,
    {
      method: "POST",
    },
  );
}

export async function listPendingExpenses(token: string): Promise<PendingExpense[]> {
  return apiRequest<PendingExpense[]>(token, "/finance/giderler/bekleyen");
}

export async function approveExpense(token: string, expenseId: number): Promise<DecisionResponse> {
  return apiRequest<DecisionResponse>(token, `/finance/giderler/${expenseId}/onayla`, {
    method: "POST",
  });
}

export async function rejectExpense(token: string, expenseId: number): Promise<DecisionResponse> {
  return apiRequest<DecisionResponse>(token, `/finance/giderler/${expenseId}/reddet`, {
    method: "POST",
  });
}

export async function listPendingRevenues(token: string): Promise<PendingRevenue[]> {
  return apiRequest<PendingRevenue[]>(token, "/recycling/gelirler/bekleyen");
}

export async function approveRevenue(token: string, revenueId: number): Promise<DecisionResponse> {
  return apiRequest<DecisionResponse>(token, `/recycling/gelirler/${revenueId}/onayla`, {
    method: "POST",
  });
}

export async function rejectRevenue(token: string, revenueId: number): Promise<DecisionResponse> {
  return apiRequest<DecisionResponse>(token, `/recycling/gelirler/${revenueId}/reddet`, {
    method: "POST",
  });
}

export async function getProfitLossSummary(token: string): Promise<ProfitLossSummary> {
  return apiRequest<ProfitLossSummary>(token, "/finance/raporlar/kar-zarar");
}

export async function calculateSalary(
  token: string,
  personelId: number,
): Promise<SalaryCalculation> {
  return apiRequest<SalaryCalculation>(token, `/finance/maas/personeller/${personelId}/hesapla`);
}

export async function createSingleSalaryPayment(
  token: string,
  payload: {
    personel_id: number;
    donem_ay: number;
    donem_yil: number;
    odeme_tarihi: string;
    tutar: string;
    odeme_tipi: Exclude<PaymentType, "Toplu">;
    aciklama?: string | null;
  },
): Promise<SalaryPayment> {
  return apiRequest<SalaryPayment>(token, "/finance/maas/tekli", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createBatchSalaryPayment(
  token: string,
  payload: { donem_ay: number; donem_yil: number; odeme_tarihi: string },
): Promise<BatchSalaryResponse> {
  return apiRequest<BatchSalaryResponse>(token, "/finance/maas/toplu", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listDeliveries(token: string): Promise<Delivery[]> {
  return apiRequest<Delivery[]>(token, "/recycling/teslimler");
}

export async function createDelivery(
  token: string,
  payload: { toplam_kg: string; atik_tipi?: WasteType | null; aciklama?: string | null },
): Promise<Delivery> {
  return apiRequest<Delivery>(token, "/recycling/teslimler", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function approveDelivery(
  token: string,
  deliveryId: number,
): Promise<{ teslim_id: number; onaylandi_mi: boolean; mesaj: string }> {
  return apiRequest<{ teslim_id: number; onaylandi_mi: boolean; mesaj: string }>(
    token,
    `/recycling/teslimler/${deliveryId}/onayla`,
    { method: "POST" },
  );
}

export async function applySorting(
  token: string,
  deliveryId: number,
  hareketler: SortingItem[],
): Promise<SortingResponse> {
  return apiRequest<SortingResponse>(token, `/recycling/teslimler/${deliveryId}/ayristir`, {
    method: "POST",
    body: JSON.stringify({ hareketler }),
  });
}

export async function listStocks(token: string): Promise<Stock[]> {
  return apiRequest<Stock[]>(token, "/recycling/stoklar");
}

export async function listStockMovements(token: string): Promise<StockMovement[]> {
  return apiRequest<StockMovement[]>(token, "/recycling/stok-hareketleri");
}

export async function createManualStockMovement(
  token: string,
  payload: { atik_tipi: WasteType; miktar_kg: string; aciklama?: string | null },
): Promise<StockMovement> {
  return apiRequest<StockMovement>(token, "/recycling/stoklar/manuel", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listSales(token: string): Promise<SaleResponse[]> {
  return apiRequest<SaleResponse[]>(token, "/recycling/satislar");
}

export async function createSale(
  token: string,
  payload: {
    atik_tipi: WasteType;
    miktar_kg: string;
    birim_fiyat: string;
    alici_firma?: string | null;
    belge_no?: string | null;
  },
): Promise<SaleResponse> {
  return apiRequest<SaleResponse>(token, "/recycling/satislar", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function startDriverTask(
  token: string,
  taskId: number,
): Promise<TaskActionResponse> {
  return apiRequest<TaskActionResponse>(token, `/operations/gorevler/${taskId}/baslat`, {
    method: "POST",
  });
}

export async function completeDriverTask(
  token: string,
  taskId: number,
  payload: { sonuc: TaskResult; aciklama?: string | null },
): Promise<TaskActionResponse> {
  return apiRequest<TaskActionResponse>(token, `/operations/gorevler/${taskId}/sonuclandir`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export function apiBaseUrl(): string {
  return API_BASE_URL;
}
