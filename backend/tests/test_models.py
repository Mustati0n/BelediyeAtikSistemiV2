from backend.app.db.base import Base
from backend.app.models import entities  # noqa: F401


def test_expected_tables_are_registered_in_metadata() -> None:
    expected_tables = {
        "rol",
        "personel",
        "bolge",
        "konteyner",
        "ihbar",
        "gorev",
        "arac",
        "bakimkaydi",
        "giderkaydi",
        "tesisteslim",
        "stok",
        "stokhareketi",
        "satis",
        "gelirkaydi",
        "maasodeme",
        "islemlog",
        "sistemparametresi",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_gorev_table_has_single_source_constraint() -> None:
    gorev_table = Base.metadata.tables["gorev"]
    constraint_names = {constraint.name for constraint in gorev_table.constraints}

    assert "ck_gorev_gorev_tek_kaynak" in constraint_names


def test_personel_table_has_role_foreign_key() -> None:
    personel_table = Base.metadata.tables["personel"]
    foreign_key_targets = {fk.target_fullname for fk in personel_table.foreign_keys}

    assert "rol.id" in foreign_key_targets
