from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import ModelBase, money_column, quantity_column
from backend.app.models.enums import (
    AracDurumu,
    AtikTipi,
    BakimDurumu,
    GorevDurumu,
    GorevSonucu,
    GorevTipi,
    IhbarDurumu,
    KonteynerDurumu,
    OdemeDurumu,
    OdemeTipi,
    OnayDurumu,
)


class Rol(ModelBase):
    ad: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    aciklama: Mapped[str | None] = mapped_column(Text())

    personeller: Mapped[list[Personel]] = relationship(back_populates="rol")


class Personel(ModelBase):
    tc_no: Mapped[str] = mapped_column(String(11), unique=True, index=True)
    sifre_hash: Mapped[str] = mapped_column(String(255))
    ad_soyad: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telefon: Mapped[str | None] = mapped_column(String(30))
    taban_maas: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    cocuk_sayisi: Mapped[int] = mapped_column(Integer, default=0)
    aktif_mi: Mapped[bool] = mapped_column(Boolean, default=True)

    rol_id: Mapped[int] = mapped_column(ForeignKey("rol.id", ondelete="RESTRICT"), index=True)

    rol: Mapped[Rol] = relationship(back_populates="personeller")
    atanan_gorevler: Mapped[list[Gorev]] = relationship(
        back_populates="atanan_sofor",
        foreign_keys="Gorev.atanan_sofor_id",
    )
    olusturulan_bakimlar: Mapped[list[BakimKaydi]] = relationship(
        back_populates="olusturan_personel"
    )
    maas_odemeleri: Mapped[list[MaasOdeme]] = relationship(back_populates="personel")
    teslim_ettigi_kayitlar: Mapped[list[TesisTeslim]] = relationship(
        back_populates="teslim_eden_sofor",
        foreign_keys="TesisTeslim.teslim_eden_sofor_id",
    )
    teslim_aldigi_kayitlar: Mapped[list[TesisTeslim]] = relationship(
        back_populates="teslim_alan_operator",
        foreign_keys="TesisTeslim.teslim_alan_operator_id",
    )
    islem_loglari: Mapped[list[IslemLog]] = relationship(back_populates="islemi_yapan")


class Bolge(ModelBase):
    ad: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    aciklama: Mapped[str | None] = mapped_column(Text())

    konteynerler: Mapped[list[Konteyner]] = relationship(back_populates="bolge")


class Konteyner(ModelBase):
    __table_args__ = (
        CheckConstraint("doluluk_orani >= 0 AND doluluk_orani <= 100", name="doluluk_orani_range"),
    )

    kod: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    enlem: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    boylam: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    doluluk_orani: Mapped[int] = mapped_column(Integer, default=0)
    durum: Mapped[KonteynerDurumu] = mapped_column(
        Enum(KonteynerDurumu, name="konteyner_durumu_enum"),
        default=KonteynerDurumu.NORMAL,
    )

    bolge_id: Mapped[int] = mapped_column(ForeignKey("bolge.id", ondelete="RESTRICT"), index=True)

    bolge: Mapped[Bolge] = relationship(back_populates="konteynerler")
    gorevler: Mapped[list[Gorev]] = relationship(back_populates="konteyner")


class Ihbar(ModelBase):
    aciklama: Mapped[str] = mapped_column(Text())
    enlem: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    boylam: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    fotograf_url: Mapped[str | None] = mapped_column(String(500))
    durum: Mapped[IhbarDurumu] = mapped_column(
        Enum(IhbarDurumu, name="ihbar_durumu_enum"),
        default=IhbarDurumu.BEKLIYOR,
    )
    olusturma_tarihi: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    gorevler: Mapped[list[Gorev]] = relationship(back_populates="ihbar")


class Arac(ModelBase):
    plaka: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    tip: Mapped[str] = mapped_column(String(100))
    kapasite_kg: Mapped[int] = mapped_column(Integer)
    durum: Mapped[AracDurumu] = mapped_column(
        Enum(AracDurumu, name="arac_durumu_enum"),
        default=AracDurumu.AKTIF,
    )

    gorevler: Mapped[list[Gorev]] = relationship(back_populates="kullanilan_arac")
    bakim_kayitlari: Mapped[list[BakimKaydi]] = relationship(back_populates="arac")


class Gorev(ModelBase):
    __table_args__ = (
        CheckConstraint(
            "(ihbar_id IS NOT NULL AND konteyner_id IS NULL) OR "
            "(ihbar_id IS NULL AND konteyner_id IS NOT NULL)",
            name="gorev_tek_kaynak",
        ),
        Index("ix_gorev_kritik_konteyner_acik", "konteyner_id", "durum"),
    )

    tip: Mapped[GorevTipi] = mapped_column(Enum(GorevTipi, name="gorev_tipi_enum"))
    oncelik: Mapped[int] = mapped_column(Integer, default=0)
    durum: Mapped[GorevDurumu] = mapped_column(
        Enum(GorevDurumu, name="gorev_durumu_enum"),
        default=GorevDurumu.BEKLIYOR,
    )
    sonuc: Mapped[GorevSonucu | None] = mapped_column(
        Enum(GorevSonucu, name="gorev_sonucu_enum"),
        nullable=True,
    )
    planlanan_tarih: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tamamlanma_tarihi: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sira_no: Mapped[int | None] = mapped_column(Integer)
    aciklama: Mapped[str | None] = mapped_column(Text())

    ihbar_id: Mapped[int | None] = mapped_column(
        ForeignKey("ihbar.id", ondelete="CASCADE"),
        index=True,
    )
    konteyner_id: Mapped[int | None] = mapped_column(
        ForeignKey("konteyner.id", ondelete="CASCADE"),
        index=True,
    )
    atanan_sofor_id: Mapped[int | None] = mapped_column(
        ForeignKey("personel.id", ondelete="SET NULL"),
        index=True,
    )
    kullanilan_arac_id: Mapped[int | None] = mapped_column(
        ForeignKey("arac.id", ondelete="SET NULL"),
        index=True,
    )

    ihbar: Mapped[Ihbar | None] = relationship(back_populates="gorevler")
    konteyner: Mapped[Konteyner | None] = relationship(back_populates="gorevler")
    atanan_sofor: Mapped[Personel | None] = relationship(
        back_populates="atanan_gorevler",
        foreign_keys=[atanan_sofor_id],
    )
    kullanilan_arac: Mapped[Arac | None] = relationship(back_populates="gorevler")


class BakimKaydi(ModelBase):
    tarih: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    aciklama: Mapped[str] = mapped_column(Text())
    maliyet_tl: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    durum: Mapped[BakimDurumu] = mapped_column(
        Enum(BakimDurumu, name="bakim_durumu_enum"),
        default=BakimDurumu.ACILDI,
    )
    teknik_tamamlanma_tarihi: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    arac_id: Mapped[int] = mapped_column(ForeignKey("arac.id", ondelete="RESTRICT"), index=True)
    olusturan_personel_id: Mapped[int] = mapped_column(
        ForeignKey("personel.id", ondelete="RESTRICT"),
        index=True,
    )

    arac: Mapped[Arac] = relationship(back_populates="bakim_kayitlari")
    olusturan_personel: Mapped[Personel] = relationship(back_populates="olusturulan_bakimlar")
    gider_kaydi: Mapped[GiderKaydi | None] = relationship(
        back_populates="bakim_kaydi",
        uselist=False,
    )


class GiderKaydi(ModelBase):
    tarih: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tutar: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    aciklama: Mapped[str] = mapped_column(Text())
    durum: Mapped[OnayDurumu] = mapped_column(
        Enum(OnayDurumu, name="onay_durumu_enum"),
        default=OnayDurumu.BEKLEMEDE,
    )

    bakim_kaydi_id: Mapped[int | None] = mapped_column(
        ForeignKey("bakimkaydi.id", ondelete="SET NULL"),
        unique=True,
    )

    bakim_kaydi: Mapped[BakimKaydi | None] = relationship(back_populates="gider_kaydi")


class TesisTeslim(ModelBase):
    tarih: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    toplam_kg: Mapped[Decimal] = quantity_column(default=Decimal("0.000"))
    aciklama: Mapped[str | None] = mapped_column(Text())
    onaylandi_mi: Mapped[bool] = mapped_column(Boolean, default=False)
    onay_tarihi: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    teslim_eden_sofor_id: Mapped[int] = mapped_column(
        ForeignKey("personel.id", ondelete="RESTRICT"),
        index=True,
    )
    teslim_alan_operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("personel.id", ondelete="SET NULL"),
        index=True,
    )

    teslim_eden_sofor: Mapped[Personel] = relationship(
        back_populates="teslim_ettigi_kayitlar",
        foreign_keys=[teslim_eden_sofor_id],
    )
    teslim_alan_operator: Mapped[Personel | None] = relationship(
        back_populates="teslim_aldigi_kayitlar",
        foreign_keys=[teslim_alan_operator_id],
    )
    stok_hareketleri: Mapped[list[StokHareketi]] = relationship(back_populates="tesis_teslim")


class Stok(ModelBase):
    atik_tipi: Mapped[AtikTipi] = mapped_column(Enum(AtikTipi, name="atik_tipi_enum"), unique=True)
    toplam_miktar_kg: Mapped[Decimal] = quantity_column(default=Decimal("0.000"))

    stok_hareketleri: Mapped[list[StokHareketi]] = relationship(back_populates="stok")
    satislar: Mapped[list[Satis]] = relationship(back_populates="stok")


class StokHareketi(ModelBase):
    tarih: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    atik_tipi: Mapped[AtikTipi] = mapped_column(Enum(AtikTipi, name="stok_hareketi_atik_tipi_enum"))
    miktar_kg: Mapped[Decimal] = quantity_column(default=Decimal("0.000"))
    aciklama: Mapped[str | None] = mapped_column(Text())

    tesis_teslim_id: Mapped[int] = mapped_column(
        ForeignKey("tesisteslim.id", ondelete="CASCADE"),
        index=True,
    )
    stok_id: Mapped[int] = mapped_column(ForeignKey("stok.id", ondelete="CASCADE"), index=True)

    tesis_teslim: Mapped[TesisTeslim] = relationship(back_populates="stok_hareketleri")
    stok: Mapped[Stok] = relationship(back_populates="stok_hareketleri")


class Satis(ModelBase):
    tarih: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    miktar_kg: Mapped[Decimal] = quantity_column(default=Decimal("0.000"))
    birim_fiyat: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    toplam_tutar: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    durum: Mapped[OnayDurumu] = mapped_column(
        Enum(OnayDurumu, name="satis_onay_durumu_enum"),
        default=OnayDurumu.BEKLEMEDE,
    )

    stok_id: Mapped[int] = mapped_column(ForeignKey("stok.id", ondelete="RESTRICT"), index=True)

    stok: Mapped[Stok] = relationship(back_populates="satislar")
    gelir_kaydi: Mapped[GelirKaydi | None] = relationship(
        back_populates="satis",
        uselist=False,
    )


class GelirKaydi(ModelBase):
    tarih: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tutar: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    aciklama: Mapped[str] = mapped_column(Text())
    durum: Mapped[OnayDurumu] = mapped_column(
        Enum(OnayDurumu, name="gelir_onay_durumu_enum"),
        default=OnayDurumu.BEKLEMEDE,
    )

    satis_id: Mapped[int | None] = mapped_column(
        ForeignKey("satis.id", ondelete="SET NULL"),
        unique=True,
    )

    satis: Mapped[Satis | None] = relationship(back_populates="gelir_kaydi")


class MaasOdeme(ModelBase):
    __table_args__ = (
        UniqueConstraint(
            "personel_id",
            "donem_ay",
            "donem_yil",
            "odeme_tipi",
            name="uq_maasodeme_donem_tip",
        ),
    )

    donem_ay: Mapped[int] = mapped_column(Integer)
    donem_yil: Mapped[int] = mapped_column(Integer)
    odeme_tarihi: Mapped[date] = mapped_column(Date)
    tutar: Mapped[Decimal] = money_column(default=Decimal("0.00"))
    odeme_tipi: Mapped[OdemeTipi] = mapped_column(Enum(OdemeTipi, name="odeme_tipi_enum"))
    durum: Mapped[OdemeDurumu] = mapped_column(
        Enum(OdemeDurumu, name="odeme_durumu_enum"),
        default=OdemeDurumu.BEKLIYOR,
    )

    personel_id: Mapped[int] = mapped_column(
        ForeignKey("personel.id", ondelete="RESTRICT"),
        index=True,
    )

    personel: Mapped[Personel] = relationship(back_populates="maas_odemeleri")


class IslemLog(ModelBase):
    islem_tarihi: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    islem_tipi: Mapped[str] = mapped_column(String(120), index=True)
    aciklama: Mapped[str] = mapped_column(Text())
    varlik_tipi: Mapped[str] = mapped_column(String(120), index=True)
    varlik_id: Mapped[int | None] = mapped_column(Integer)

    islemi_yapan_id: Mapped[int | None] = mapped_column(
        ForeignKey("personel.id", ondelete="SET NULL"),
        index=True,
    )

    islemi_yapan: Mapped[Personel | None] = relationship(back_populates="islem_loglari")


class SistemParametresi(ModelBase):
    anahtar: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    deger: Mapped[str] = mapped_column(String(500))
    veri_tipi: Mapped[str] = mapped_column(String(50))
    kategori: Mapped[str | None] = mapped_column(String(100))
    aciklama: Mapped[str | None] = mapped_column(Text())
