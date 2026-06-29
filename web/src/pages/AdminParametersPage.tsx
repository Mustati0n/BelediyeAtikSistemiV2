import { RefreshCcw, Save, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { InlineNotice } from "../components/InlineNotice";
import {
  ApiError,
  SystemParameter,
  listSystemParameters,
  updateSystemParameter,
} from "../api";

export function AdminParametersPage({ token }: { token: string }) {
  const [parameters, setParameters] = useState<SystemParameter[]>([]);
  const [drafts, setDrafts] = useState<Record<number, string>>({});
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("Tum Kategoriler");
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadParameters() {
    setError("");
    setLoading(true);
    try {
      const data = await listSystemParameters(token);
      setParameters(data);
      setDrafts(Object.fromEntries(data.map((parameter) => [parameter.id, parameter.deger])));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Parametreler alinamadi.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadParameters();
  }, []);

  const categories = useMemo(
    () => [
      "Tum Kategoriler",
      ...Array.from(new Set(parameters.map((parameter) => parameter.kategori || "Genel"))),
    ],
    [parameters],
  );

  const filteredParameters = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("tr-TR");
    return parameters.filter((parameter) => {
      const category = parameter.kategori || "Genel";
      const matchesCategory = categoryFilter === "Tum Kategoriler" || category === categoryFilter;
      const matchesSearch =
        !needle ||
        parameter.anahtar.toLocaleLowerCase("tr-TR").includes(needle) ||
        category.toLocaleLowerCase("tr-TR").includes(needle) ||
        (parameter.aciklama || "").toLocaleLowerCase("tr-TR").includes(needle);
      return matchesCategory && matchesSearch;
    });
  }, [categoryFilter, parameters, search]);

  const groupedParameters = useMemo(() => {
    return filteredParameters.reduce<Record<string, SystemParameter[]>>((groups, parameter) => {
      const category = parameter.kategori || "Genel";
      groups[category] = [...(groups[category] || []), parameter];
      return groups;
    }, {});
  }, [filteredParameters]);
  const changedCount = parameters.filter((parameter) => drafts[parameter.id] !== parameter.deger).length;

  async function saveParameter(parameter: SystemParameter) {
    setError("");
    setMessage("");
    setSavingId(parameter.id);
    try {
      const updated = await updateSystemParameter(token, parameter.id, drafts[parameter.id] || "");
      setParameters((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
      setDrafts((current) => ({ ...current, [updated.id]: updated.deger }));
      setMessage(`${updated.anahtar} guncellendi.`);
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "Parametre guncellenemedi.");
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <div>
          <p>SISTEM AYARLARI</p>
          <h1>Sistem Parametreleri</h1>
          <span>
            Kod degisikligi yapmadan kritik esikleri, simulasyon araliklarini, fiyatlari ve
            muhasebe katsayilarini yonetin.
          </span>
        </div>

        <div className="fleet-stat-card">
          <SlidersHorizontal size={34} />
          <strong>{parameters.length}</strong>
          <span>Aktif Parametre</span>
          <small>{categories.length - 1} kategori</small>
        </div>
      </section>

      <section className="filter-panel toolbar-panel">
        <label>
          Arama
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Parametre, kategori veya aciklama ara..."
          />
        </label>
        <label>
          Kategori
          <select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}>
            {categories.map((category) => (
              <option key={category}>{category}</option>
            ))}
          </select>
        </label>
        <button className="row-action" onClick={loadParameters} type="button">
          <RefreshCcw size={17} />
          Yenile
        </button>
      </section>

      <section className="settings-command-grid">
        <article className="settings-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Kategori Hizli Secim</h3>
              <p>Ayar gruplari arasinda hizli gecis</p>
            </div>
            <SlidersHorizontal size={20} />
          </div>
          <div className="settings-chip-row">
            {categories.slice(1).map((category) => (
              <button
                className={categoryFilter === category ? "active" : ""}
                key={category}
                onClick={() => setCategoryFilter(category)}
                type="button"
              >
                {category}
              </button>
            ))}
          </div>
        </article>

        <article className="settings-command-panel">
          <div className="panel-heading">
            <div>
              <h3>Degisiklik Ozeti</h3>
              <p>Kaydedilmeyi bekleyen alanlar</p>
            </div>
            <Save size={20} />
          </div>
          <div className="finance-mini-total">
            <strong>{changedCount}</strong>
            <span>kaydedilmemis degisiklik</span>
          </div>
        </article>
      </section>

      <InlineNotice
        message={error || message}
        type={error ? "error" : "success"}
        onClose={() => {
          setError("");
          setMessage("");
        }}
      />

      <section className="parameter-grid">
        {Object.entries(groupedParameters).map(([category, items]) => (
          <article className="parameter-panel" key={category}>
            <div className="panel-heading">
              <div>
                <h3>{category}</h3>
                <p>{items.length} yonetilebilir alan</p>
              </div>
              <SlidersHorizontal size={20} />
            </div>

            <div className="parameter-list">
              {items.map((parameter) => (
                <div className="parameter-row" key={parameter.id}>
                  <div>
                    <strong>{parameter.anahtar}</strong>
                    <span>{parameter.aciklama || "Aciklama yok"}</span>
                    <small>{parameter.veri_tipi}</small>
                  </div>
                  <input
                    value={drafts[parameter.id] ?? parameter.deger}
                    onChange={(event) =>
                      setDrafts((current) => ({
                        ...current,
                        [parameter.id]: event.target.value,
                      }))
                    }
                  />
                  <button
                    className="primary-action"
                    disabled={savingId === parameter.id || drafts[parameter.id] === parameter.deger}
                    onClick={() => saveParameter(parameter)}
                    type="button"
                  >
                    <Save size={16} />
                    {savingId === parameter.id ? "Kaydediliyor" : "Kaydet"}
                  </button>
                </div>
              ))}
            </div>
          </article>
        ))}

        {!loading && filteredParameters.length === 0 && (
          <div className="empty-state">
            <SlidersHorizontal size={24} />
            Parametre bulunamadi.
          </div>
        )}
      </section>
    </div>
  );
}
