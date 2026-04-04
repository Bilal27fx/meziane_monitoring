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


def test_parse_sessions_extracts_date_from_slug_when_page_only_contains_audience_time():
    html = """
    <html>
      <body>
        <h1>Ventes judiciaires immobilieres - TJ Bobigny</h1>
        <p>Audience a 11h30 - 3 annonces</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    sessions = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/tj-bobigny/mardi-07-avril-2026.html",
    )

    assert len(sessions) == 1
    assert sessions[0].tribunal == "TJ Bobigny"
    assert sessions[0].session_datetime == datetime(2026, 4, 7, 11, 30)
    assert sessions[0].announced_listing_count == 3


def test_parse_sessions_prioritizes_audience_date_over_other_dates_in_page():
    html = """
    <html>
      <body>
        <h1>Ventes judiciaires immobilieres - TJ Paris - jeudi 19 mars 2026</h1>
        <p>Audience a 14h</p>
        <p>Visite sur place le mardi 10 mars 2026 a 09h</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    sessions = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html",
    )

    assert sessions[0].session_datetime == datetime(2026, 3, 19, 14, 0)


def test_parse_sessions_extracts_header_block_with_tribunal_judiciaire_label():
    html = """
    <html>
      <body>
        <h1>Tribunal Judiciaire de Paris</h1>
        <p>Vente aux enchères publiques en un lot de vente</p>
        <p>jeudi 21 mai 2026 à 14h</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    sessions = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/paris/vente.html",
    )

    assert len(sessions) == 1
    assert sessions[0].tribunal == "TJ Paris"
    assert sessions[0].session_datetime == datetime(2026, 5, 21, 14, 0)


def test_parse_sessions_extracts_annexe_tribunal_judiciaire_header():
    html = """
    <html>
      <body>
        <h1>À l'annexe du Tribunal Judiciaire de Nanterre (Hauts de Seine)</h1>
        <p>Vente aux enchères publiques en deux lots</p>
        <p>jeudi 16 avril 2026 à 14h30</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    sessions = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/nanterre/vente.html",
    )

    assert len(sessions) == 1
    assert sessions[0].tribunal == "TJ Nanterre"
    assert sessions[0].session_datetime == datetime(2026, 4, 16, 14, 30)


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


def test_parse_listing_cards_extracts_non_paris_city_from_card_text():
    html = """
    <html>
      <body>
        <a href="/annonce/108033.html">
          Un appartement - Mise a prix 60 000 EUR - 25,57 m² - Villeneuve-Saint-Georges 94190
        </a>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = RawSession(
        external_id="tj-creteil-2026-04-16-0930",
        tribunal="TJ Créteil",
        city="Créteil",
        session_datetime=datetime(2026, 4, 16, 9, 30),
        source_url="https://www.licitor.com/ventes-judiciaires-immobilieres/creteil/vente.html",
        announced_listing_count=1,
    )

    listings = adapter.parse_listing_cards(html, session.source_url, session)

    assert len(listings) == 1
    assert listings[0].city == "Villeneuve-Saint-Georges"
    assert listings[0].postal_code == "94190"


def test_parse_listing_detail_extracts_documents_and_contact_facts():
    html = """
    <html>
      <body>
        <h1>Un appartement a Paris 17eme</h1>
        <p>Mise a prix : 380 000 EUR</p>
        <p>Surface : 103,70 m²</p>
        <p>Appartement de 4 pieces avec 2 chambres au 3eme etage avec ascenseur, balcon, cave et parking</p>
        <p>Bien occupe</p>
        <p>Visites : mardi 10 mars 2026 de 14h a 15h au 12 rue des Fleurs, 75017 Paris</p>
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
    assert detail.facts["visit_dates"] == ["mardi 10 mars 2026 de 14h a 15h"]
    assert detail.facts["property_details"]["room_count"] == 4
    assert detail.facts["property_details"]["amenities"]["ascenseur"] is True
    assert detail.facts["property_details"]["visit"]["location"] == "12 rue des Fleurs, 75017 Paris"


def test_parse_listing_detail_extracts_realistic_floor_labels():
    html = """
    <html>
      <body>
        <h1>Studio Paris 15eme</h1>
        <p>Bien situe au 6eme etage avec ascenseur</p>
        <p>Surface : 18,2 m²</p>
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
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-15eme/paris/107346.html">
          Un appartement - Mise a prix 150 000 EUR - 18,20 m² - Paris 15eme 75015
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-15eme/paris/107346.html",
        listing,
    )

    assert detail.facts["etage"] == 6
    assert detail.facts["type_etage"] == "etage"
    assert detail.facts["ascenseur"] is True


def test_parse_listing_detail_extracts_exact_address_without_explicit_label():
    html = """
    <html>
      <body>
        <h1>Appartement Paris 20eme</h1>
        <p>Dans un ensemble immobilier sis 24 boulevard de Menilmontant 75020 Paris</p>
        <p>Surface : 27,4 m²</p>
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
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-20eme/paris/107348.html">
          Un appartement - Mise a prix 210 000 EUR - 27,40 m² - Paris 20eme 75020
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-20eme/paris/107348.html",
        listing,
    )

    assert detail.facts["address"] == "24 boulevard de Menilmontant 75020 Paris"


def test_parse_listing_detail_extracts_multiline_visit_dates_and_specific_visit_location():
    html = """
    <html>
      <body>
        <h1>Appartement Pantin</h1>
        <p>Adresse : 5 rue Jules Auffret, 93500 Pantin</p>
        <p>Visites sur place et sur rendez-vous</p>
        <p>Lundi 4 mai 2026 de 10h a 11h</p>
        <p>Mercredi 6 mai 2026 de 14h a 15h</p>
        <p>Rendez-vous au 17 avenue Jean Lolive, 93500 Pantin</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = RawSession(
        external_id="tj-bobigny-2026-05-12-1330",
        tribunal="TJ Bobigny",
        city="Pantin",
        session_datetime=datetime(2026, 5, 12, 13, 30),
        source_url="https://www.licitor.com/ventes-judiciaires-immobilieres/tj-bobigny/mardi-12-mai-2026.html",
        announced_listing_count=1,
    )
    listing = adapter.parse_listing_cards(
        """
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/pantin/seine-saint-denis/107350.html">
          Un appartement - Mise a prix 185 000 EUR - 42,00 m² - Pantin 93500
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/10/73/44/vente-aux-encheres/un-appartement/pantin/seine-saint-denis/107350.html",
        listing,
    )

    assert detail.facts["address"] == "5 rue Jules Auffret, 93500 Pantin"
    assert detail.facts["visit_dates"] == [
        "Lundi 4 mai 2026 de 10h a 11h",
        "Mercredi 6 mai 2026 de 14h a 15h",
    ]
    assert detail.facts["property_details"]["visit"]["location"] == "17 avenue Jean Lolive, 93500 Pantin"


def test_parse_listing_detail_does_not_confuse_visit_address_with_property_address():
    html = """
    <html>
      <body>
        <h1>Appartement Saint-Ouen</h1>
        <p>Adresse : 22 rue des Rosiers, 93400 Saint-Ouen-sur-Seine</p>
        <p>Visite : mardi 2 juin 2026 de 11h a 12h au 88 avenue Michelet, 93400 Saint-Ouen-sur-Seine</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = RawSession(
        external_id="tj-bobigny-2026-06-09-1330",
        tribunal="TJ Bobigny",
        city="Saint-Ouen-sur-Seine",
        session_datetime=datetime(2026, 6, 9, 13, 30),
        source_url="https://www.licitor.com/ventes-judiciaires-immobilieres/tj-bobigny/mardi-09-juin-2026.html",
        announced_listing_count=1,
    )
    listing = adapter.parse_listing_cards(
        """
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/saint-ouen/seine-saint-denis/107351.html">
          Un appartement - Mise a prix 210 000 EUR - 38,00 m² - Saint-Ouen-sur-Seine 93400
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/10/73/44/vente-aux-encheres/un-appartement/saint-ouen/seine-saint-denis/107351.html",
        listing,
    )

    assert detail.facts["address"] == "22 rue des Rosiers, 93400 Saint-Ouen-sur-Seine"
    assert detail.facts["property_details"]["visit"]["location"] == "88 avenue Michelet, 93400 Saint-Ouen-sur-Seine"


def test_parse_listing_detail_extracts_real_page_without_using_lawyer_address():
    html = """
    <html>
      <body>
        <h1>Tribunal Judiciaire de Paris</h1>
        <p>Vente aux enchères publiques en un lot</p>
        <p>jeudi 7 mai 2026 à 14h</p>
        <p>UN APPARTEMENT</p>
        <p>de 55 m² (Loi Carrez), au rez-de-chaussée, de deux pièces principales</p>
        <p>Une cave</p>
        <p>Inoccupé</p>
        <p>Mise à prix : 140 000 €</p>
        <p>(Outre les charges)</p>
        <p>Consignation pour enchérir : chèque de banque à l'ordre de M. le Bâtonnier Séquestre représentant 10% du montant de la mise à prix</p>
        <p>Paris 16ème</p>
        <p>22, square de l'Alboni</p>
        <p>Afficher le plan</p>
        <p>(exactitude non garantie)</p>
        <p>Visite sur place lundi 27 avril 2026 de 12h à 13h</p>
        <p>Maître Florence Renault, Avocat</p>
        <p>22, rue Breguet - 75011 Paris</p>
        <p>Tél.: 01 42 21 06 01</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/paris/vente.html",
    )[0]
    listing = adapter.parse_listing_cards(
        """
        <a href="/annonce/67128.html">
          Un appartement - Mise a prix 140 000 EUR - 55,00 m² - Paris 16eme 75016
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/67128.html",
        listing,
    )

    assert session.tribunal == "TJ Paris"
    assert session.session_datetime == datetime(2026, 5, 7, 14, 0)
    assert detail.facts["nb_pieces"] == 2
    assert detail.facts["address"] == "Paris 16ème\n22, square de l'Alboni"
    assert detail.facts["visit_dates"] == ["lundi 27 avril 2026 de 12h à 13h"]
    assert detail.facts["property_details"]["visit"]["location"] == "Paris 16ème\n22, square de l'Alboni"
    assert "Breguet" not in detail.facts["address"]


def test_parse_listing_detail_keeps_visit_hour_and_does_not_take_lawyer_postal_code():
    html = """
    <html>
      <body>
        <h1>Tribunal Judiciaire de Paris</h1>
        <p>Vente aux enchères publiques en un lot de vente</p>
        <p>jeudi 21 mai 2026 à 14h</p>
        <p>UN STUDIO</p>
        <p>de 12,46 m², au rez-de-chaussée</p>
        <p>Le bien est loué</p>
        <p>Mise à prix : 40 000 €</p>
        <p>Paris 18ème</p>
        <p>10, impasse du Curé</p>
        <p>Afficher le plan</p>
        <p>(exactitude non garantie)</p>
        <p>Visite sur place lundi 11 mai 2026 à 14h</p>
        <p>Maître Éric Assouline, du Cabinet Ethic All, Avocat</p>
        <p>15, bd Richard Lenoir - 75011 Paris</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = adapter.parse_sessions(
        html,
        "https://www.licitor.com/ventes-judiciaires-immobilieres/paris/vente.html",
    )[0]
    listing = adapter.parse_listing_cards(
        """
        <a href="/annonce/108146.html">
          Annonce n°108146 : un studio à Paris 18eme, mise a prix : 40 000 EUR - 12,46 m² - Paris 18eme 75018
        </a>
        """,
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/108146.html",
        listing,
    )

    assert detail.facts["address"] == "Paris 18ème\n10, impasse du Curé"
    assert detail.facts["postal_code"] == "75018"
    assert detail.facts["visit_dates"] == ["lundi 11 mai 2026 à 14h"]
    assert detail.facts["property_details"]["visit"]["location"] == "Paris 18ème\n10, impasse du Curé"


# ── Nouveaux cas — bugs fixés ──────────────────────────────────────────────


def test_parse_sessions_returns_none_datetime_when_date_not_found():
    """Bug 2 : _extract_session_datetime ne doit plus lever d'exception."""
    html = "<html><body><p>Audience TJ Paris - pas de date lisible ici.</p></body></html>"

    adapter = LicitorAuctionAdapter()
    sessions = adapter.parse_sessions(html, "https://www.licitor.com/ventes/tj-paris/vente.html")

    assert len(sessions) == 1
    assert sessions[0].session_datetime is None


def test_extract_postal_code_works_outside_idf():
    """Bug 6 : postal_code ne doit pas être limité à l'IDF."""
    adapter = LicitorAuctionAdapter()

    assert adapter._extract_postal_code("Appartement situé à Lyon, 69003") == "69003"
    assert adapter._extract_postal_code("Maison à Bordeaux 33000") == "33000"
    assert adapter._extract_postal_code("Bien à Marseille 13001") == "13001"


def test_extract_visit_details_location_without_idf_postal_code():
    """Bug 3a : lieu de visite extrait même sans CP IDF."""
    adapter = LicitorAuctionAdapter()
    text = "Visite sur place au 45 rue de la Paix, 69003 Lyon\nle 12 mai 2026 de 10h a 11h"

    result = adapter._extract_visit_details(text, None)

    assert result["location"] is not None
    assert "45 rue de la Paix" in result["location"]


def test_extract_visit_blocks_not_stopped_by_meme_or_mise():
    """Bug 3b : le mot 'même' ou 'mise' ne doit pas couper le bloc de visite."""
    adapter = LicitorAuctionAdapter()
    lines = [
        "Visite du bien",
        "le 14 avril 2026 de 10h à 11h",
        "même en cas de pluie",
        "au 5 rue Victor Hugo, 75015 Paris",
    ]
    blocks = adapter._extract_visit_blocks(lines)

    assert len(blocks) == 1
    # Les 4 lignes doivent être dans le bloc
    full_block = " ".join(blocks[0])
    assert "même en cas de pluie" in full_block
    assert "5 rue Victor Hugo" in full_block


def test_extract_visit_blocks_stops_on_avocat_pattern():
    """Bug 3b : le pattern Me. Nom doit bien arrêter le bloc."""
    adapter = LicitorAuctionAdapter()
    lines = [
        "Visite : 10 avril 2026 de 14h à 15h",
        "au 12 avenue Foch, 75016 Paris",
        "Me. Dupont, avocat au barreau de Paris",
        "Cahier des conditions de vente disponible",
    ]
    blocks = adapter._extract_visit_blocks(lines)

    assert len(blocks) == 1
    full_block = " ".join(blocks[0])
    assert "12 avenue Foch" in full_block
    assert "Me. Dupont" not in full_block


def test_parse_listing_detail_extracts_address_with_appartement_keyword():
    """Bug 5 : une ligne contenant 'appartement' ne doit plus être ignorée si c'est une adresse."""
    html = """
    <html>
      <body>
        <h1>Appartement Paris 11eme</h1>
        <p>Appartement situe au 8 rue de la Roquette, 75011 Paris</p>
        <p>Surface : 45 m²</p>
      </body>
    </html>
    """

    adapter = LicitorAuctionAdapter()
    session = RawSession(
        external_id="tj-paris-2026-04-10-1400",
        tribunal="TJ Paris",
        city="Paris",
        session_datetime=datetime(2026, 4, 10, 14, 0),
        source_url="https://www.licitor.com/ventes/tj-paris/vente.html",
        announced_listing_count=1,
    )
    listing = adapter.parse_listing_cards(
        '<a href="/annonce/1/2/3/vente/appartement/paris-11/107999.html">Appartement 75011</a>',
        session.source_url,
        session,
    )[0]

    detail = adapter.parse_listing_detail(
        html,
        "https://www.licitor.com/annonce/1/2/3/vente/appartement/paris-11/107999.html",
        listing,
    )

    assert detail.facts["address"] is not None
    assert "8 rue de la Roquette" in detail.facts["address"]
