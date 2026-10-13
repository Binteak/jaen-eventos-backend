"""Extractor HTML experimental para la agenda del Ayuntamiento de Jaén.

No elude controles. Antes de programarlo en producción, verificar permisos,
condiciones de uso, robots.txt, frecuencia admisible y atribución.
"""
from datetime import datetime, time
from urllib.parse import urljoin, quote
from zoneinfo import ZoneInfo
import re
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Event

SOURCE_KEY = "ayuntamiento-jaen"
SOURCE_NAME = "Ayuntamiento de Jaén"
SOURCE_URL = "https://www.aytojaen.es/portal/p_138_contenedoragenda.jsp?codResi=1&codbusqueda=546&language=es&layout=p_138_contenedoragenda.jsp&seccion=s_lact_d11_v1.jsp"
MADRID = ZoneInfo("Europe/Madrid")


def category_for(text: str) -> str:
    value = text.casefold()
    if any(word in value for word in ("concierto", "música", "musica", "festival", "banda")):
        return "musica"
    if any(word in value for word in ("teatro", "zarzuela", "danza", "baile", "exposición", "exposicion", "cultura")):
        return "cultura"
    if any(word in value for word in ("deporte", "carrera", "partido", "torneo")):
        return "deporte"
    if any(word in value for word in ("infancia", "infantil", "familia", "niños", "ninos")):
        return "familia"
    return "otros"


def parse_spanish_date(text: str) -> datetime | None:
    text = re.sub(r"\s+", " ", text).strip()
    # El portal suele presentar rangos dd mes aaaa - dd mes aaaa; extraemos la fecha inicial.
    match = re.search(r"(\d{1,2}\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ.]+\s+\d{4})", text)
    if not match:
        return None
    try:
        parsed = date_parser.parse(match.group(1), dayfirst=True, fuzzy=True)
        return datetime.combine(parsed.date(), time(20, 0), tzinfo=MADRID)
    except (ValueError, OverflowError):
        return None


def extract_events(html: str, base_url: str = SOURCE_URL) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict] = []
    seen: set[tuple[str, str]] = set()
    # Parser tolerante: busca filas de tablas y elementos con enlaces a detalles.
    for row in soup.select("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        title_link = row.find("a", href=True)
        title = (title_link.get_text(" ", strip=True) if title_link else cells[1].get_text(" ", strip=True))
        if not title or len(title) < 4 or title.casefold() in {"título", "titulo", "agenda"}:
            continue
        row_text = row.get_text(" ", strip=True)
        starts_at = parse_spanish_date(row_text)
        if starts_at is None:
            continue
        source_url = urljoin(base_url, title_link["href"]) if title_link else f"{base_url}#evento-{quote(title[:80])}-{starts_at.date().isoformat()}"
        key = (title.casefold(), starts_at.date().isoformat())
        if key in seen:
            continue
        seen.add(key)
        image = row.find("img", src=True)
        price = None
        for cell in cells:
            value = cell.get_text(" ", strip=True)
            if re.search(r"€|gratuit|gratis|precio", value, re.I):
                price = value[:120]
                break
        results.append({
            "title": title[:240], "description": None, "category": category_for(title),
            "starts_at": starts_at, "ends_at": None, "venue": None, "address": "Jaén, España",
            "latitude": None, "longitude": None, "price_text": price,
            # Solo guardamos URL de imagen para referencia; no descargamos ni republicamos imágenes.
            "image_url": urljoin(base_url, image["src"]) if image else None,
            "source_name": SOURCE_NAME, "source_key": SOURCE_KEY, "source_url": source_url,
        })
    return results


def fetch_html() -> str:
    headers = {"User-Agent": settings.scraper_user_agent, "Accept": "text/html,application/xhtml+xml"}
    with httpx.Client(headers=headers, timeout=20, follow_redirects=True) as client:
        response = client.get(SOURCE_URL)
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", "").lower():
            raise ValueError("La fuente no ha devuelto HTML")
        return response.text


def import_events(db: Session, html: str) -> tuple[int, int]:
    parsed = extract_events(html)
    created = 0
    skipped = 0
    for item in parsed:
        exists = db.scalar(select(Event.id).where(Event.source_key == SOURCE_KEY, Event.source_url == item["source_url"]))
        if exists:
            skipped += 1
            continue
        db.add(Event(**item, status="pending"))
        created += 1
    db.commit()
    return created, skipped
