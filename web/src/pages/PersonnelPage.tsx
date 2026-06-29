import { BriefcaseBusiness, RefreshCcw, Save, ShieldCheck, Users } from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  Personnel,
  RoleRecord,
  createPersonnel,
  listPersonnel,
  listRoles,
  updatePersonnel,
} from "../api";

type FormState = {
  tc_no: string;
  ad_soyad: string;
  email: string;
  telefon: string;
  taban_maas: string;
  cocuk_sayisi: string;
  rol_id: string;
  password: string;
};

const emptyForm: FormState = {
  tc_no: "",
  ad_soyad: "",
  email: "",
  telefon: "",
  taban_maas: "",
  cocuk_sayisi: "0",
  rol_id: "",
  password: "",
};

export function PersonnelPage({ token }: { token: string }) {
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [roles, setRoles] = useState<RoleRecord[]>([]);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("Tum Roller");
  const [statusFilter, setStatusFilter] = useState("Tum Durumlar");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingPersonnelId, setEditingPersonnelId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);
    try {
      const [rolesData, personnelData] = await Promise.all([
        listRoles(token),
        listPersonnel(token),
      ]);
      setRoles(rolesData);
      setPersonnel(personnelData);
      setForm((current) => ({
        ...current,
        rol_id: current.rol_id || String(rolesData[0]?.id || ""),
      }));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Personel verisi alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const filteredPersonnel = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("tr-TR");
    return personnel.filter((person) => {
      const matchesSearch =
        !needle ||
        person.ad_soyad.toLocaleLowerCase("tr-TR").includes(needle) ||
        person.email.toLocaleLowerCase("tr-TR").includes(needle) ||
        person.tc_no.includes(needle);
      const matchesRole = roleFilter === "Tum Roller" || person.rol.ad === roleFilter;
      const matchesStatus =
        statusFilter === "Tum Durumlar" ||
        (statusFilter === "Aktif" && person.aktif_mi) ||
        (statusFilter === "Pasif" && !person.aktif_mi);
      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [personnel, search, roleFilter, statusFilter]);

  const activeCount = personnel.filter((person) => person.aktif_mi).length;
  const passiveCount = personnel.length - activeCount;
  const roleCount = roles.length;
  const roleDensity = useMemo(() => {
    return roles.map((role) => {
      const rolePeople = personnel.filter((person) => person.rol.id === role.id);
      return {
        id: role.id,
        name: role.ad,
        count: rolePeople.length,
        active: rolePeople.filter((person) => person.aktif_mi).length,
      };
    });
  }, [personnel, roles]);
  const payrollTotal = personnel.reduce((sum, person) => sum + Number(person.taban_maas), 0);
  const activeRatio = personnel.length > 0 ? Math.round((activeCount / personnel.length) * 100) : 0;

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const salary = Number(form.taban_maas);
    const children = Number(form.cocuk_sayisi);
    const roleId = Number(form.rol_id);

    if (!/^\d{11}$/.test(form.tc_no.trim())) {
      setError("TC no 11 haneli ve sadece rakam olmalidir.");
      return;
    }
    if (/\d/.test(form.ad_soyad)) {
      setError("Ad soyad alanina rakam girilemez.");
      return;
    }
    if (form.telefon.trim() && !/^\d{10,11}$/.test(form.telefon.trim())) {
      setError("Telefon 10-11 haneli ve sadece rakam olmalidir.");
      return;
    }
    if (!Number.isFinite(salary) || salary < 0 || salary > 250000) {
      setError("Taban maas 0 ile 250.000 TL arasinda olmalidir.");
      return;
    }
    if (!Number.isInteger(children) || children < 0 || children > 10) {
      setError("Cocuk sayisi 0 ile 10 arasinda olmalidir.");
      return;
    }
    if (
      !form.ad_soyad.trim() ||
      !form.email.trim() ||
      (!editingPersonnelId && !form.password) ||
      !roleId
    ) {
      setError("TC no, ad soyad, e-posta, sifre, rol ve maas alanlari zorunludur.");
      return;
    }

    setSaving(true);
    try {
      if (editingPersonnelId) {
        await updatePersonnel(token, editingPersonnelId, {
          ad_soyad: form.ad_soyad.trim(),
          email: form.email.trim(),
          telefon: form.telefon.trim() || null,
          taban_maas: salary.toFixed(2),
          cocuk_sayisi: children,
          rol_id: roleId,
          ...(form.password ? { password: form.password } : {}),
        });
      } else {
        await createPersonnel(token, {
          tc_no: form.tc_no.trim(),
          ad_soyad: form.ad_soyad.trim(),
          email: form.email.trim(),
          telefon: form.telefon.trim() || null,
          taban_maas: salary.toFixed(2),
          cocuk_sayisi: children,
          rol_id: roleId,
          password: form.password,
        });
      }
      setForm({ ...emptyForm, rol_id: String(roles[0]?.id || "") });
      setEditingPersonnelId(null);
      setMessage(editingPersonnelId ? "Personel bilgileri guncellendi." : "Yeni personel kaydi olusturuldu.");
      await loadData();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Personel olusturulamadi.");
    } finally {
      setSaving(false);
    }
  }

  function startEdit(person: Personnel) {
    setEditingPersonnelId(person.id);
    setForm({
      tc_no: person.tc_no,
      ad_soyad: person.ad_soyad,
      email: person.email,
      telefon: person.telefon || "",
      taban_maas: String(Number(person.taban_maas)),
      cocuk_sayisi: String(person.cocuk_sayisi),
      rol_id: String(person.rol.id),
      password: "",
    });
    setError("");
    setMessage("Personel duzenleme modu acildi.");
  }

  async function toggleActive(person: Personnel) {
    setError("");
    setMessage("");
    try {
      const updated = await updatePersonnel(token, person.id, { aktif_mi: !person.aktif_mi });
      setPersonnel((current) => current.map((item) => (item.id === person.id ? updated : item)));
      setMessage(`${person.ad_soyad} durumu guncellendi.`);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Personel durumu guncellenemedi.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <div>
          <p>PERSONEL KONTROL</p>
          <h1>Personel ve Rol Yonetimi</h1>
          <span>
            Sistem kullanicilarini, rol atamalarini ve aktiflik durumlarini merkezi olarak
            yonetin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <Users size={34} />
          <strong>{activeCount}</strong>
          <span>Aktif Personel</span>
          <small>{passiveCount} pasif kayit</small>
        </div>
      </section>

      <section className="admin-summary-row" aria-label="Personel ozetleri">
        <article>
          <span>Toplam Personel</span>
          <strong>{personnel.length}</strong>
        </article>
        <article>
          <span>Aktif</span>
          <strong>{activeCount}</strong>
        </article>
        <article>
          <span>Pasif</span>
          <strong>{passiveCount}</strong>
        </article>
        <article>
          <span>Rol Sayisi</span>
          <strong>{roleCount}</strong>
        </article>
      </section>

      <section className="personnel-command-grid">
        <article className="personnel-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Kadro Sagligi</h3>
              <p>Aktiflik orani ve personel kapsami</p>
            </div>
            <ShieldCheck size={20} />
          </div>
          <div className="fill-pulse">
            <strong>{activeRatio}%</strong>
            <span>aktif personel</span>
            <i><b style={{ width: `${activeRatio}%` }} /></i>
            <small>{activeCount} aktif / {passiveCount} pasif</small>
          </div>
        </article>

        <article className="personnel-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Rol Dagilimi</h3>
              <p>Yetki gruplarina gore ekip yogunlugu</p>
            </div>
            <BriefcaseBusiness size={20} />
          </div>
          <div className="density-list">
            {roleDensity.map((role) => {
              const percent = personnel.length > 0 ? Math.round((role.count / personnel.length) * 100) : 0;
              return (
                <div key={role.id}>
                  <span>{role.name}</span>
                  <strong>{role.count}</strong>
                  <i><b style={{ width: `${percent}%` }} /></i>
                  <small>{role.active} aktif / %{percent}</small>
                </div>
              );
            })}
          </div>
        </article>

        <article className="personnel-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Maas Yuku</h3>
              <p>Personel taban maas toplam ozeti</p>
            </div>
            <Users size={20} />
          </div>
          <div className="finance-mini-total">
            <strong>{payrollTotal.toLocaleString("tr-TR", { style: "currency", currency: "TRY", maximumFractionDigits: 0 })}</strong>
            <span>{personnel.length} kayit icin taban maas</span>
          </div>
        </article>
      </section>

      <section className="form-panel action-panel">
        <div className="panel-heading">
          <div>
            <h3>{editingPersonnelId ? "Personel Bilgisi Guncelle" : "Yeni Personel Ekle"}</h3>
            <p>{editingPersonnelId ? "Secili personelin iletisim, rol ve maas bilgilerini guncelleyin." : "Temel bilgileri ve rolunu girerek yeni kullanici hesabi olusturun."}</p>
          </div>
          <button className="icon-button" onClick={loadData} type="button" title="Yenile">
            <RefreshCcw size={18} />
          </button>
        </div>

        <form className="personnel-form" onSubmit={handleCreate}>
          <label>
            TC No
            <input
              value={form.tc_no}
              disabled={Boolean(editingPersonnelId)}
              onChange={(event) => setForm({ ...form, tc_no: onlyDigits(event.target.value).slice(0, 11) })}
              inputMode="numeric"
              maxLength={11}
              placeholder="10000000000"
            />
          </label>
          <label>
            Ad Soyad
            <input
              value={form.ad_soyad}
              onChange={(event) => setForm({ ...form, ad_soyad: withoutDigits(event.target.value) })}
              placeholder="Ad Soyad"
            />
          </label>
          <label>
            E-posta
            <input
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              placeholder="personel@belediye.local"
            />
          </label>
          <label>
            Telefon
            <input
              value={form.telefon}
              onChange={(event) => setForm({ ...form, telefon: onlyDigits(event.target.value).slice(0, 11) })}
              inputMode="numeric"
              placeholder="5550000000"
            />
          </label>
          <label>
            Rol
            <select value={form.rol_id} onChange={(event) => setForm({ ...form, rol_id: event.target.value })}>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.ad}
                </option>
              ))}
            </select>
          </label>
          <label>
            Taban Maas
            <input
              value={form.taban_maas}
              onChange={(event) => setForm({ ...form, taban_maas: numericDecimal(event.target.value).slice(0, 9) })}
              inputMode="decimal"
              placeholder="35000"
            />
          </label>
          <label>
            Cocuk Sayisi
            <input
              value={form.cocuk_sayisi}
              onChange={(event) => setForm({ ...form, cocuk_sayisi: onlyDigits(event.target.value).slice(0, 2) })}
              inputMode="numeric"
            />
          </label>
          <label>
            Sifre
            <input
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              type="password"
              placeholder={editingPersonnelId ? "Bos birakilirsa degismez" : "En az 6 karakter"}
            />
          </label>
          {editingPersonnelId && (
            <button
              className="row-action"
              onClick={() => {
                setEditingPersonnelId(null);
                setForm({ ...emptyForm, rol_id: String(roles[0]?.id || "") });
              }}
              type="button"
            >
              Vazgec
            </button>
          )}
          <button
            className="primary-action"
            disabled={saving || !form.tc_no.trim() || !form.ad_soyad.trim() || !form.email.trim()}
            type="submit"
          >
            <Save size={18} />
            {saving ? "Kaydediliyor" : editingPersonnelId ? "Guncelle" : "Kaydet"}
          </button>
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
          Arama
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Ad, e-posta veya TC no ile ara..."
          />
        </label>
        <label>
          Rol
          <select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>
            <option>Tum Roller</option>
            {roles.map((role) => (
              <option key={role.id}>{role.ad}</option>
            ))}
          </select>
        </label>
        <label>
          Durum
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option>Tum Durumlar</option>
            <option>Aktif</option>
            <option>Pasif</option>
          </select>
        </label>
      </section>

      <section className="list-context-bar" aria-label="Personel filtre ozeti">
        <div>
          <strong>{filteredPersonnel.length}</strong>
          <span>gosterilen personel</span>
        </div>
        <div>
          <strong>{roleFilter}</strong>
          <span>rol filtresi</span>
        </div>
        <div>
          <strong>{statusFilter}</strong>
          <span>durum filtresi</span>
        </div>
        <button
          className="ghost-button"
          disabled={!search && roleFilter === "Tum Roller" && statusFilter === "Tum Durumlar"}
          onClick={() => {
            setSearch("");
            setRoleFilter("Tum Roller");
            setStatusFilter("Tum Durumlar");
          }}
          type="button"
        >
          Filtreleri Temizle
        </button>
      </section>

      <section className="data-panel">
        <div className="table-title">
          <strong>Personel Listesi</strong>
          <span>
            {loading
              ? "Yukleniyor"
              : `Toplam ${personnel.length} personelden ${filteredPersonnel.length} kayit gosteriliyor`}
          </span>
        </div>

        <div className="personnel-table" role="table">
          <div className="personnel-row personnel-head" role="row">
            <span>Personel</span>
            <span>Rol</span>
            <span>Maas</span>
            <span>Durum</span>
            <span>Islem</span>
          </div>

          {filteredPersonnel.map((person) => (
            <div className="personnel-row" key={person.id} role="row">
              <span>
                <strong>{person.ad_soyad}</strong>
                <small>{person.email} / {person.tc_no}</small>
              </span>
              <span>{person.rol.ad}</span>
              <span>
                {Number(person.taban_maas).toLocaleString("tr-TR", {
                  style: "currency",
                  currency: "TRY",
                })}
                <small>{person.cocuk_sayisi} cocuk</small>
              </span>
              <span>
                <b className={`status-pill ${person.aktif_mi ? "aktif" : "pasif"}`}>
                  {person.aktif_mi ? "Aktif" : "Pasif"}
                </b>
              </span>
              <span>
                <div className="row-control">
                  <small>Hesap durumu</small>
                  <button className="row-action" onClick={() => toggleActive(person)} type="button">
                    {person.aktif_mi ? "Pasife Al" : "Aktif Yap"}
                  </button>
                  <button className="row-action" onClick={() => startEdit(person)} type="button">
                    Duzenle
                  </button>
                </div>
              </span>
            </div>
          ))}

          {!loading && filteredPersonnel.length === 0 && (
            <div className="empty-state">
              <Users size={22} />
              Kayit bulunamadi.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function onlyDigits(value: string) {
  return value.replace(/\D/g, "");
}

function withoutDigits(value: string) {
  return value.replace(/\d/g, "");
}

function numericDecimal(value: string) {
  return value.replace(/[^\d.,]/g, "").replace(",", ".");
}
