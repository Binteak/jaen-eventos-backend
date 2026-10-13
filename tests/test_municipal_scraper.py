from app.scrapers.municipal import extract_events


def test_extract_events_from_simple_html():
    html = '''<table><tr><th>Imagen</th><th>Titulo</th><th>Fecha</th><th>Precio</th></tr>
    <tr><td></td><td><a href="/evento/123">Concierto de prueba</a></td><td>13 oct. 2026 - 13 oct. 2026</td><td>Actividad gratuita</td></tr></table>'''
    events = extract_events(html, "https://example.test/agenda")
    assert len(events) == 1
    assert events[0]["title"] == "Concierto de prueba"
    assert events[0]["category"] == "musica"
    assert events[0]["price_text"] == "Actividad gratuita"
    assert events[0]["source_url"] == "https://example.test/evento/123"


def test_empty_html_returns_no_events():
    assert extract_events("<html><body>Sin eventos</body></html>") == []
