
from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventOut, ReviewIn


MADRID = ZoneInfo("Europe/Madrid")



# ============================================================
# CONFIGURACIÓN: MODO MOCK
# ============================================================

# True: los eventos se generan en memoria y no necesitan PostgreSQL.
# False: la API utiliza la base de datos para listar eventos.
MOCK_MODE = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    # En modo mock no creamos tablas ni conectamos con PostgreSQL.
    if not MOCK_MODE:
        from app.database import Base, engine, SessionLocal
        from app.seed import seed_demo_events

        Base.metadata.create_all(bind=engine)

        if settings.seed_demo:
            with SessionLocal() as db:
                seed_demo_events(db)

    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de agenda de eventos para Jaén",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4204",
        "http://127.0.0.1:4204",
        "https://jaen-eventos-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================
# EVENTOS DE PRUEBA
# ============================================================

def build_mock_events():
    now = datetime.now(MADRID).replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    def event_time(days: int, hours: int):
        return (now + timedelta(days=days, hours=hours)).isoformat()

    return [
        {
            "id": 1,
            "title": "Concierto de música en directo",
            "description": (
                "Disfruta de una noche de música en directo "
                "con artistas locales en el centro de Jaén."
            ),
            "category": "musica",
            "starts_at": event_time(0, 1),
            "ends_at": event_time(0, 3),
            "venue": "Plaza de Santa María",
            "address": "Plaza de Santa María, Jaén",
            "latitude": 37.7650,
            "longitude": -3.7880,
            "price_text": "Entrada gratuita",
            "image_url": (
                "https://images.unsplash.com/photo-1501386761578-eac5c94b800a"
                "?auto=format&fit=crop&w=900&q=80"
            ),
            "source_name": "Jaén Eventos Demo",
            "source_key": "demo",
            "source_url": "https://www.jaen.es/",
            "instagram_url": None,
            "status": "published",
            "is_sponsored": False,
        },
        {
            "id": 2,
            "title": "Exposición de arte y fotografía",
            "description": (
                "Descubre una selección de obras artísticas "
                "y fotografías en esta exposición de prueba."
            ),
            "category": "cultura",
            "starts_at": event_time(0, 2),
            "ends_at": event_time(0, 4),
            "venue": "Centro cultural",
            "address": "Centro de Jaén",
            "latitude": 37.7670,
            "longitude": -3.7900,
            "price_text": "Entrada gratuita",
            "image_url": (
                "https://images.unsplash.com/photo-1577083552431-6e5fd01aa342"
                "?auto=format&fit=crop&w=900&q=80"
            ),
            "source_name": "Jaén Eventos Demo",
            "source_key": "demo",
            "source_url": "https://www.jaen.es/",
            "instagram_url": None,
            "status": "published",
            "is_sponsored": False,
        },
        {
            "id": 3,
            "title": "Actividad deportiva al aire libre",
            "description": (
                "Una propuesta deportiva para disfrutar "
                "del aire libre y mantenerse activo."
            ),
            "category": "deporte",
            "starts_at": event_time(0, 3),
            "ends_at": event_time(0, 5),
            "venue": "Parque del Seminario",
            "address": "Jaén",
            "latitude": 37.7710,
            "longitude": -3.7850,
            "price_text": "Gratis",
            "image_url": (
                "https://images.unsplash.com/photo-1552674605-db6ffd4facb5"
                "?auto=format&fit=crop&w=900&q=80"
            ),
            "source_name": "Jaén Eventos Demo",
            "source_key": "demo",
            "source_url": "https://www.jaen.es/",
            "instagram_url": None,
            "status": "published",
            "is_sponsored": False,
        },
        {
            "id": 4,
            "title": "Taller creativo para familias",
            "description": (
                "Un taller de manualidades para compartir "
                "una experiencia creativa en familia."
            ),
            "category": "familia",
            "starts_at": event_time(0, 4),
            "ends_at": event_time(0, 6),
            "venue": "Espacio cultural",
            "address": "Jaén",
            "latitude": 37.7630,
            "longitude": -3.7920,
            "price_text": "Consultar disponibilidad",
            "image_url": (
                "https://images.unsplash.com/photo-1513364776144-60967b0f800f"
                "?auto=format&fit=crop&w=900&q=80"
            ),
            "source_name": "Jaén Eventos Demo",
            "source_key": "demo",
            "source_url": "https://www.jaen.es/",
            "instagram_url": None,
            "status": "published",
            "is_sponsored": False,
        },
        {
            "id": 5,
            "title": "Visita cultural por Jaén",
            "description": (
                "Descubre el patrimonio y los rincones "
                "más interesantes del casco histórico."
            ),
            "category": "cultura",
            "starts_at": event_time(1, 2),
            "ends_at": event_time(1, 4),
            "venue": "Catedral de Jaén",
            "address": "Plaza de Santa María, Jaén",
            "latitude": 37.7653,
            "longitude": -3.7877,
            "price_text": "Consultar precio",
            "image_url": (
                "https://images.unsplash.com/photo-1569949381669-ecf31ae8e613"
                "?auto=format&fit=crop&w=900&q=80"
            ),
            "source_name": "Jaén Eventos Demo",
            "source_key": "demo",
            "source_url": "https://www.jaen.es/",
            "instagram_url": None,
            "status": "published",
            "is_sponsored": False,
        },
    ]


# ============================================================
# SALUD DE LA API
# ============================================================

@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "service": "jaen-eventos-api",
        "mode": "mock" if MOCK_MODE else "database",
    }


# ============================================================
# LISTADO DE EVENTOS
# ============================================================

@app.get("/api/v1/events")
def list_events(
    date_filter: date | None = Query(default=None, alias="date"),
    from_date: date | None = None,
    to_date: date | None = None,
    category: str | None = None,
    q: str | None = Query(default=None, max_length=100),
    db: Session | None = Depends(
        lambda: None if MOCK_MODE else next(get_db())
    ),
):
    # MODO MOCK: no se consulta la base de datos.
    if MOCK_MODE:
        events = build_mock_events()

        start_date = date_filter or from_date

        if start_date:
            events = [
                event for event in events
                if date.fromisoformat(event["starts_at"][:10]) >= start_date
            ]

        if date_filter:
            events = [
                event for event in events
                if date.fromisoformat(event["starts_at"][:10]) == date_filter
            ]
        elif to_date:
            events = [
                event for event in events
                if date.fromisoformat(event["starts_at"][:10]) <= to_date
            ]

        if category and category.lower() != "todos":
            events = [
                event for event in events
                if event["category"] == category.lower()
            ]

        if q and q.strip():
            search_text = q.strip().casefold()

            events = [
                event for event in events
                if search_text in event["title"].casefold()
                or search_text in event["description"].casefold()
                or search_text in event["venue"].casefold()
                or search_text in event["address"].casefold()
            ]

        return sorted(events, key=lambda event: event["starts_at"])[:300]

    # MODO BASE DE DATOS: conserva el comportamiento original.
    if db is None:
        raise HTTPException(
            status_code=500,
            detail="No se pudo obtener la sesión de base de datos",
        )

    stmt = select(Event).where(Event.status == "published")
    start_date = date_filter or from_date

    if start_date:
        start_dt = datetime.combine(
            start_date, time.min, tzinfo=MADRID
        )
        stmt = stmt.where(Event.starts_at >= start_dt)

    if date_filter:
        end_dt = datetime.combine(
            date_filter + timedelta(days=1),
            time.min,
            tzinfo=MADRID,
        )
        stmt = stmt.where(Event.starts_at < end_dt)
    elif to_date:
        end_dt = datetime.combine(
            to_date + timedelta(days=1),
            time.min,
            tzinfo=MADRID,
        )
        stmt = stmt.where(Event.starts_at < end_dt)

    if category and category.lower() != "todos":
        stmt = stmt.where(Event.category == category.lower())

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Event.title.ilike(like),
                Event.description.ilike(like),
                Event.venue.ilike(like),
                Event.address.ilike(like),
            )
        )

    stmt = stmt.order_by(Event.starts_at.asc()).limit(300)
    return list(db.scalars(stmt).all())


# ============================================================
# DETALLE DE EVENTO
# Estos endpoints siguen necesitando PostgreSQL.
# ============================================================

@app.get("/api/v1/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)

    if not event or event.status != "published":
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado",
        )

    return event


# ============================================================
# ADMINISTRACIÓN
# Estos endpoints siguen necesitando PostgreSQL.
# ============================================================

@app.get(
    "/api/v1/admin/events",
    response_model=list[EventOut],
)
def admin_events(
    status: str = Query(
        default="pending",
        pattern="^(pending|published|rejected)$",
    ),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Event)
            .where(Event.status == status)
            .order_by(Event.captured_at.desc())
            .limit(500)
        ).all()
    )


@app.patch(
    "/api/v1/admin/events/{event_id}/review",
    response_model=EventOut,
)
def review_event(
    event_id: int,
    payload: ReviewIn,
    db: Session = Depends(get_db),
):
    event = db.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado",
        )

    event.status = payload.status
    db.commit()
    db.refresh(event)

    return event


@app.post(
    "/api/v1/admin/events",
    response_model=EventOut,
    status_code=201,
)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
):
    event = Event(
        **payload.model_dump(),
        status="pending",
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event