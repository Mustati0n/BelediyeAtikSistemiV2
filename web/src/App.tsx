import {
  BarChart3,
  ClipboardList,
  Factory,
  LayoutDashboard,
  LogOut,
  MapPinned,
  ScrollText,
  ShieldCheck,
  SlidersHorizontal,
  Truck,
  UserCog,
  Users,
  Wrench,
  Wallet,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ApiError, CurrentUser, apiBaseUrl, getCurrentUser, healthCheck, login } from "./api";
import { clearSession, loadToken, loadUser, saveSession } from "./auth";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { AdminFinanceOverviewPage } from "./pages/AdminFinanceOverviewPage";
import { AdminLogsPage } from "./pages/AdminLogsPage";
import { AdminParametersPage } from "./pages/AdminParametersPage";
import { AdminTasksPage } from "./pages/AdminTasksPage";
import { CitizenReportPage } from "./pages/CitizenReportPage";
import { ContainersPage } from "./pages/ContainersPage";
import { DriverTasksPage } from "./pages/DriverTasksPage";
import { FleetPage } from "./pages/FleetPage";
import { FinancePage } from "./pages/FinancePage";
import { MaintenancePage } from "./pages/MaintenancePage";
import { PersonnelPage } from "./pages/PersonnelPage";
import { RecyclingPage } from "./pages/RecyclingPage";
import { Section, roleHome, sectionFromPath, sectionLabels } from "./routes";

type AuthState = {
  token: string | null;
  user: CurrentUser | null;
};

const adminViewSections: Section[] = ["admin", "maintenance", "finance", "recycling"];
const sectionDefaultPaths: Record<Section, string> = {
  admin: "/admin",
  driver: "/driver/gorevler",
  maintenance: "/maintenance/bakim",
  finance: "/finance/muhasebe",
  recycling: "/recycling/gorevler",
};

function navigate(path: string): void {
  window.history.pushState(null, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function allowedSectionsFor(user: CurrentUser): Section[] {
  if (user.rol === "Sistem Yoneticisi") return adminViewSections;
  return [roleHome[user.rol].slice(1) as Section];
}

function visibleSectionsFor(user: CurrentUser): Section[] {
  if (user.rol === "Sistem Yoneticisi") return ["admin"];
  return allowedSectionsFor(user);
}

function isAdminReadOnly(user: CurrentUser, section: Section): boolean {
  return user.rol === "Sistem Yoneticisi" && section !== "admin";
}

function homePathFor(user: CurrentUser): string {
  const homeSection = roleHome[user.rol].slice(1) as Section;
  return sectionDefaultPaths[homeSection];
}

export function App() {
  const [auth, setAuth] = useState<AuthState>(() => ({
    token: loadToken(),
    user: loadUser(),
  }));
  const [path, setPath] = useState(window.location.pathname);
  const [checking, setChecking] = useState(Boolean(loadToken()));

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    const token = loadToken();
    if (!token) {
      setChecking(false);
      return;
    }

    getCurrentUser(token)
      .then((user) => {
        saveSession(token, user);
        setAuth({ token, user });
      })
      .catch(() => {
        clearSession();
        setAuth({ token: null, user: null });
      })
      .finally(() => setChecking(false));
  }, []);

  const section = useMemo(() => sectionFromPath(path), [path]);

  if (checking) {
    return <Splash />;
  }

  if (
    path === "/ihbar" ||
    path.startsWith("/ihbar/") ||
    path === "/vatandas" ||
    path.startsWith("/vatandas/")
  ) {
    return <CitizenReportPage />;
  }

  if (!auth.token || !auth.user || path === "/login" || path === "/") {
    return (
      <LoginPage
        onLogin={(token, user) => {
          saveSession(token, user);
          setAuth({ token, user });
          navigate(homePathFor(user));
        }}
      />
    );
  }

  if (!section) {
    navigate(homePathFor(auth.user));
    return <Splash />;
  }

  if (!allowedSectionsFor(auth.user).includes(section)) {
    navigate(homePathFor(auth.user));
    return <Splash />;
  }

  if (section !== "admin" && path === `/${section}`) {
    navigate(sectionDefaultPaths[section]);
    return <Splash />;
  }

  return (
    <PanelShell
      path={path}
      section={section}
      token={auth.token}
      user={auth.user}
      onNavigate={navigate}
      onLogout={() => {
        clearSession();
        setAuth({ token: null, user: null });
        navigate("/login");
      }}
    />
  );
}

function Splash() {
  return (
    <main className="splash">
      <div className="brand-mark">S</div>
      <p>Sistem yukleniyor</p>
    </main>
  );
}

function LoginPage({ onLogin }: { onLogin: (token: string, user: CurrentUser) => void }) {
  const [username, setUsername] = useState("admin@belediye.local");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [apiReady, setApiReady] = useState<boolean | null>(null);
  const demoAccounts = [
    { label: "Admin", username: "admin@belediye.local", password: "Admin123!" },
    { label: "Sofor", username: "sofor@belediye.local", password: "Sofor123!" },
    { label: "Bakim", username: "bakim@belediye.local", password: "Bakim123!" },
    { label: "Muhasebe", username: "muhasebe@belediye.local", password: "Muhasebe123!" },
    { label: "Tesis", username: "operator@belediye.local", password: "Operator123!" },
  ];

  useEffect(() => {
    healthCheck().then(setApiReady);
  }, []);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);

    try {
      const tokenResponse = await login(username.trim(), password);
      const user = await getCurrentUser(tokenResponse.access_token);
      onLogin(tokenResponse.access_token, user);
    } catch (exc) {
      if (exc instanceof ApiError) {
        setError(exc.message);
      } else {
        setError(`Backend servisine baglanilamadi: ${apiBaseUrl()}`);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel" aria-label="Personel girisi">
        <div className="login-brand">
          <div className="brand-mark">S</div>
          <h1>AKILLI SEHIR ATIK YONETIMI SISTEMI</h1>
          <p>SURDURULEBILIR KENT OPERASYONLARI PORTALI</p>
        </div>

        <form className="login-card" onSubmit={submit}>
          <div className="api-status" data-ready={apiReady === true}>
            <span />
            {apiReady === null
              ? "Backend kontrol ediliyor"
              : apiReady
                ? "Backend baglantisi hazir"
                : "Backend baglantisi yok"}
          </div>

          <label>
            KULLANICI ADI VEYA E-POSTA
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="adiniz@kurum.gov.tr"
              autoComplete="username"
            />
          </label>

          <label>
            SIFRE
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Sifre"
              type="password"
              autoComplete="current-password"
            />
          </label>

          {error && (
            <div className="error-box" role="alert">
              <strong>!</strong>
              <span>{error}</span>
            </div>
          )}

          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Giris yapiliyor" : "Portala Giris Yap"}
          </button>

          <div className="demo-users">
            <strong>Demo hesaplar</strong>
            <div>
              {demoAccounts.map((account) => (
                <button
                  key={account.username}
                  onClick={() => {
                    setUsername(account.username);
                    setPassword(account.password);
                  }}
                  type="button"
                >
                  {account.label}
                </button>
              ))}
            </div>
          </div>
        </form>
      </section>
    </main>
  );
}

function PanelShell({
  path,
  section,
  token,
  user,
  onNavigate,
  onLogout,
}: {
  path: string;
  section: Section;
  token: string;
  user: CurrentUser;
  onNavigate: (path: string) => void;
  onLogout: () => void;
}) {
  const menu = [
    { section: "admin" as const, icon: UserCog, label: "Yonetim" },
    { section: "driver" as const, icon: Truck, label: "Sofor" },
    { section: "maintenance" as const, icon: Wrench, label: "Bakim" },
    { section: "finance" as const, icon: BarChart3, label: "Muhasebe" },
    { section: "recycling" as const, icon: Factory, label: "Tesis" },
  ];
  const visibleMenu = menu.filter((item) => visibleSectionsFor(user).includes(item.section));
  const sectionLinks: Record<Section, Array<{ path: string; label: string; icon: typeof LayoutDashboard }>> = {
    admin: [
      { path: "/admin", label: "Denetim", icon: LayoutDashboard },
      { path: "/admin/filo", label: "Filo", icon: Truck },
      { path: "/admin/personel", label: "Personel", icon: Users },
      { path: "/admin/konteynerler", label: "Konteyner", icon: MapPinned },
      { path: "/admin/finans", label: "Finans", icon: Wallet },
      { path: "/admin/parametreler", label: "Parametreler", icon: SlidersHorizontal },
      { path: "/admin/loglar", label: "Log Kayitlari", icon: ScrollText },
    ],
    driver: [
      { path: "/driver/gorevler", label: "Gunluk Gorev", icon: ClipboardList },
    ],
    maintenance: [
      { path: "/maintenance/bakim", label: "Bakim Kayitlari", icon: Wrench },
    ],
    finance: [
      { path: "/finance/muhasebe", label: "Muhasebe", icon: BarChart3 },
    ],
    recycling: [
      { path: "/recycling/gorevler", label: "Gorev Havuzu", icon: ClipboardList },
      { path: "/recycling/tesis", label: "Tesis Islemleri", icon: Factory },
    ],
  };
  const isAdminShell = user.rol === "Sistem Yoneticisi";

  return (
    <main className={isAdminShell ? "app-shell admin-shell" : "app-shell"}>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">S</div>
          <div>
            <strong>Atik Yonetim Sistemi</strong>
            <span>Operasyon Paneli</span>
          </div>
        </div>

        <nav>
          {visibleMenu.map((item) => {
            const Icon = item.icon;
            return (
              <div className="nav-group" key={item.section}>
                <button
                  className={item.section === section ? "active" : ""}
                  onClick={() => onNavigate(sectionDefaultPaths[item.section])}
                  type="button"
                >
                  <Icon size={18} />
                  {item.label}
                </button>
                {item.section === section && (
                  <div className="subnav">
                    {sectionLinks[item.section].length === 1 ? (
                      (() => {
                        const link = sectionLinks[item.section][0];
                        const LinkIcon = link.icon;
                        return (
                          <span className="subnav-title" key={link.path}>
                            <LinkIcon size={15} />
                            {link.label}
                          </span>
                        );
                      })()
                    ) : (
                    sectionLinks[item.section].map((link) => {
                      const LinkIcon = link.icon;
                      return (
                        <button
                          className={path === link.path ? "active" : ""}
                          key={link.path}
                          onClick={() => onNavigate(link.path)}
                          type="button"
                        >
                          <LinkIcon size={15} />
                          {link.label}
                        </button>
                      );
                    }))}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p>{user.rol}</p>
            <h2>{sectionLabels[section]}</h2>
          </div>
          <div className="user-chip">
            <ShieldCheck size={18} />
            <span>{user.ad_soyad}</span>
            <button onClick={onLogout} type="button" aria-label="Cikis yap">
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {section === "admin" && path === "/admin" ? (
          <AdminDashboardPage token={token} onNavigate={onNavigate} />
        ) : section === "admin" && path === "/admin/filo" ? (
          <FleetPage token={token} />
        ) : section === "admin" && path === "/admin/personel" ? (
          <PersonnelPage token={token} />
        ) : section === "admin" && path === "/admin/konteynerler" ? (
          <ContainersPage token={token} />
        ) : section === "admin" && path === "/admin/finans" ? (
          <AdminFinanceOverviewPage token={token} />
        ) : section === "admin" && path === "/admin/parametreler" ? (
          <AdminParametersPage token={token} />
        ) : section === "admin" && path === "/admin/loglar" ? (
          <AdminLogsPage token={token} />
        ) : section === "driver" && path === "/driver/gorevler" ? (
          <DriverTasksPage token={token} />
        ) : section === "maintenance" && path === "/maintenance/bakim" ? (
          <MaintenancePage token={token} readOnly={isAdminReadOnly(user, section)} />
        ) : section === "finance" && path === "/finance/muhasebe" ? (
          <FinancePage token={token} readOnly={isAdminReadOnly(user, section)} />
        ) : section === "recycling" && path === "/recycling/gorevler" ? (
          <AdminTasksPage token={token} />
        ) : section === "recycling" && path === "/recycling/tesis" ? (
          <RecyclingPage token={token} readOnly={isAdminReadOnly(user, section)} />
        ) : (
          <PanelHome section={section} />
        )}
      </section>
    </main>
  );
}

function PanelHome({ section }: { section: Section }) {
  const cards: Record<Section, Array<{ title: string; value: string; note: string }>> = {
    admin: [
      { title: "Filo", value: "Aktif", note: "Arac listeleme, ekleme ve durum guncelleme hazir." },
      { title: "Personel", value: "Aktif", note: "Rol listesi, personel ekleme ve aktif/pasif islemi hazir." },
      { title: "Konteyner", value: "Aktif", note: "Bolge, konteyner, doluluk ve durum yonetimi hazir." },
    ],
    driver: [
      { title: "Gunluk Gorev", value: "Canli API", note: "Gorev listeleme, baslatma ve kapatma." },
      { title: "Rota", value: "Harita", note: "Harita entegrasyonu sonraki adim." },
      { title: "Teslim", value: "Canli API", note: "Gun sonu tesis teslim kaydi." },
    ],
    maintenance: [
      { title: "Bakim Kaydi", value: "Aktif", note: "Arac sec, bakim ac ve teknik tamamla." },
      { title: "Araclar", value: "Aktif", note: "Bakim icin arac listesi canli API'den gelir." },
      { title: "Gecmis", value: "Aktif", note: "Bakim gecmisi ve gider durumu listelenir." },
    ],
    finance: [
      { title: "Gider Onay", value: "Aktif", note: "Bekleyen giderleri onayla veya reddet." },
      { title: "Gelir Onay", value: "Aktif", note: "Satis gelirlerini onayla veya reddet." },
      { title: "Maas", value: "Aktif", note: "Maas hesapla, tekli veya toplu odeme yap." },
      { title: "Rapor", value: "Aktif", note: "Kar-zarar ozetini takip et." },
    ],
    recycling: [
      { title: "Teslim Alma", value: "Aktif", note: "Sofor teslimlerini onayla." },
      { title: "Stok", value: "Aktif", note: "Atik turu bazli stoklari gor." },
      { title: "Satis", value: "Aktif", note: "Stoktan satis ve gelir kaydi olustur." },
      { title: "Ayristirma", value: "Aktif", note: "Teslimleri stok hareketine donustur." },
    ],
  };
  const sectionCards = cards[section];

  return (
    <div className={`dashboard-grid count-${sectionCards.length}`}>
      {sectionCards.map((card) => (
        <article
          className={
            (section === "admin" && ["Filo", "Personel", "Konteyner"].includes(card.title)) ||
            (section === "driver" && card.title === "Gunluk Gorev") ||
            (section === "maintenance" && ["Bakim Kaydi", "Araclar", "Gecmis"].includes(card.title)) ||
            (section === "finance" && ["Gider Onay", "Gelir Onay", "Maas", "Rapor"].includes(card.title)) ||
            (section === "recycling" && ["Teslim Alma", "Stok", "Satis", "Ayristirma"].includes(card.title))
              ? "summary-card clickable"
              : "summary-card"
          }
          key={card.title}
          onClick={() => {
            if (section === "admin" && card.title === "Filo") navigate("/admin/filo");
            if (section === "admin" && card.title === "Personel") navigate("/admin/personel");
            if (section === "admin" && card.title === "Konteyner") {
              navigate("/admin/konteynerler");
            }
            if (section === "driver" && card.title === "Gunluk Gorev") {
              navigate("/driver/gorevler");
            }
            if (section === "maintenance") navigate("/maintenance/bakim");
            if (section === "finance") navigate("/finance/muhasebe");
            if (section === "recycling") navigate("/recycling/tesis");
          }}
        >
          <div>
            <ClipboardList size={20} />
            <span>{card.title}</span>
          </div>
          <strong>{card.value}</strong>
          <p>{card.note}</p>
        </article>
      ))}
    </div>
  );
}
