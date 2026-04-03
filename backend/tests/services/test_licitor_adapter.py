from datetime import datetime

from app.agents.auction.adapters.licitor import LicitorAuctionAdapter
from app.agents.auction.adapters.base import RawSession


def test_parse_sessions_extracts_tribunal_datetime_and_count():
    html = """
    <html>
      <body>
        <h1>Ventes judiciaires immobilieres - TJ Paris - jeudi 19 mars 2026</h1>
        <p>Audience a 14h - 7 annonces</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    sessions = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html",
    )

    assert len(sessions) == 1
    assert sessions[0].tribunal == "TJ Paris"
    assert sessions[0].session_datetime == datetime(2026, 3, 19, 14, 0)
    assert sessions[0].announced_listing_count == 7


def test_parse_listing_cards_extracts_detail_urls_and_basic_facts():
    html = """
    <html>
      <body>
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html">
          Un appartement - Mise a prix 380 000 EUR - 103,70 m² - Paris 17eme 75017
        </a>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = RawSession(
        external_id="tj-paris-2026-03-19-1400",
        tribunal="TJ Paris",
        city="Paris",
        session_datetime=datetime(2026, 3, 19, 14, 0),
        source_url="https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html",
        announced_listing_count=1,
    )

    listings = adapter.parse_listing_cards(html, session.source_url, session)

    assert len(listings) == 1
    assert listings[0].external_id == "10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344"
    assert listings[0].reserve_price == 380000
    assert listings[0].surface_m2 == 103.70
    assert listings[0].postal_code == "75017"


def test_parse_listing_detail_extracts_documents_and_contact_facts():
    html = """
    <html>
      <body>
        <h1>Un appartement a Paris 17eme</h1>
        <p>Mise a prix : 380 000 EUR</p>
        <p>Surface : 103,70 m²</p>
        <p>Appartement de 4 pieces avec 2 chambres au 3eme etage avec ascenseur, balcon, cave et parking</p>
        <p>Bien occupe</p>
        <p>Visites : mardi 10 mars 2026 de 14h a 15h</p>
        <p>Me Dupont - 01 40 00 00 00</p>
        <a href="/pdf/ccv.pdf">Cahier des conditions de vente</a>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = RawSession(
        external_id="tj-paris-2026-03-19-1400",
        tribunal="TJ Paris",
        city="Paris",
        session_datetime=datetime(2026, 3, 19, 14, 0),
        source_url="https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html",
        announced_listing_count=1,
    )
    listing = adapter.parse_listing_cards(
        """
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html">
          Un appartement - Mise a prix 380 000 EUR - 103,70 m² - Paris 17eme 75017
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html",
        listing,
    )

    assert detail.facts["title"] == "Un appartement a Paris 17eme"
    assert detail.facts["reserve_price"] == 380000
    assert detail.facts["surface_m2"] == 103.70
    assert detail.facts["nb_pieces"] == 4
    assert detail.facts["nb_chambres"] == 2
    assert detail.facts["etage"] == 3
    assert detail.facts["type_etage"] == "etage"
    assert detail.facts["ascenseur"] is True
    assert detail.facts["balcon"] is True
    assert detail.facts["cave"] is True
    assert detail.facts["parking"] is True
    assert detail.facts["occupancy_status"] == "occupe"
    assert detail.facts["lawyer_phone"] == "01 40 00 00 00"
    assert detail.facts["documents"] == ["https://www.licitor.com/pdf/ccv.pdf"]
    assert detail.facts["property_details"]["room_count"] == 4
    assert detail.facts["property_details"]["amenities"]["ascenseur"] is True
