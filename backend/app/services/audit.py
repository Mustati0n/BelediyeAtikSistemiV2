from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models.entities import IslemLog, Personel


def log_action(
    db: Session,
    *,
    actor: Personel | None,
    islem_tipi: str,
    aciklama: str,
    varlik_tipi: str,
    varlik_id: int | None = None,
    commit: bool = False,
) -> IslemLog:
    log = IslemLog(
        islem_tarihi=datetime.now(UTC),
        islem_tipi=islem_tipi,
        aciklama=aciklama,
        varlik_tipi=varlik_tipi,
        varlik_id=varlik_id,
        islemi_yapan=actor,
    )
    db.add(log)
    if commit:
        db.commit()
        db.refresh(log)
    return log

