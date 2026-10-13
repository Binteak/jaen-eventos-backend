from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Event


def seed_demo_events(db: Session) -> None:
    if db.scalar(select(Event.id).limit(1)) is not None:
        return
    now = datetime.now().astimezone().replace(minute=0, second=0, microsecond=0)
    examples = [
        {"title": "Paseo cultural por el casco histórico", "description": "Ejemplo de evento para validar la agenda. Sustituir por datos confirmados de una fuente autorizada.", "category": "cultura", "starts_at": now + timedelta(hours=3), "venue": "Centro histórico", "address": "Centro, Jaén", "latitude": 37.765, "longitude": -3.790, "price_text": "Consultar", "source_name": "Datos de demostración", "source_key": "demo", "source_url": "https://www.aytojaen.es/", "status": "published"},
        {"title": "Concierto de ejemplo", "description": "Registro ficticio: no representa un evento real anunciado.", "category": "musica", "starts_at": now + timedelta(days=1, hours=2), "venue": "Recinto por confirmar", "address": "Jaén, España", "latitude": 37.770, "longitude": -3.790, "price_text": "Por confirmar", "source_name": "Datos de demostración", "source_key": "demo", "source_url": "https://www.aytojaen.es/", "status": "published"},
        {"title": "Actividad familiar de ejemplo", "description": "Contenido de demostración. No publicar como evento real.", "category": "familia", "starts_at": now + timedelta(days=2, hours=4), "venue": "Espacio por confirmar", "address": "Jaén, España", "latitude": 37.775, "longitude": -3.785, "price_text": "Consultar", "source_name": "Datos de demostración", "source_key": "demo", "source_url": "https://www.aytojaen.es/", "status": "published"},
    ]
    db.add_all(Event(**item) for item in examples)
    db.commit()
