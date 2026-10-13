from app.database import Base, SessionLocal, engine
from app.scrapers.municipal import fetch_html, import_events


def main():
    Base.metadata.create_all(bind=engine)
    html = fetch_html()
    with SessionLocal() as db:
        created, skipped = import_events(db, html)
    print(f"Conector municipal finalizado: {created} eventos nuevos pendientes; {skipped} ya existían.")


if __name__ == "__main__":
    main()
