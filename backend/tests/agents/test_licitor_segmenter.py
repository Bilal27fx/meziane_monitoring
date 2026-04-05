"""Tests unitaires du segmenteur de texte Licitor."""

import pytest

from app.agents.auction.licitor_text_segmenter import segment_licitor_page

# Texte réel extrait d'une page Licitor (exemple fourni par Bilal)
SAMPLE_MULTI_LOT = """\
À l'annexe du Tribunal Judiciaire de Nanterre (Hauts de Seine)
Vente aux enchères publiques en deux lots
jeudi 16 avril 2026 à 14h30
1er lot de la vente

UN STUDIO
de 31,57 m² (hors balcon de 3,50 m²), escalier numéro 6, au 2ème étage
Une cave
Un emplacement de voiture
Mise à prix : 57 000 €
2nd lot de la vente

UN APPARTEMENT
de 103,40 m² (hors terrasses), escalier numéro 6, au 7ème étage, comprenant :
entrée, séjour, quatre chambres, cuisine, dégagement, salle de bain, salle d'eau, deux wc, deux terrasses (24,38 m² et 44,70 m²)
Un débarras
Une cave
Deux emplacements de voiture
Mise à prix : 194 000 €
Courbevoie
ZAC Charas Nord
6, rue Kléber
Visite sur place mercredi 8 avril 2026 de 11h30 à 12h30
"""

SAMPLE_SINGLE_LOT = """\
À l'annexe du Tribunal Judiciaire de Paris
Vente aux enchères publiques
mardi 22 avril 2026 à 10h00
1er lot de la vente

UN APPARTEMENT
de 45 m², au 3ème étage
Cave
Mise à prix : 85 000 €
Paris 15
75015
Visite sur place lundi 14 avril 2026 de 10h00 à 11h00
Me. Martin - 01 45 67 89 00
"""

SAMPLE_NO_LOTS = """\
Tribunal Judiciaire de Lyon
Vente judiciaire
vendredi 10 avril 2026 à 09h30
Maison de 120 m² à Lyon
Mise à prix : 120 000 €
69003 Lyon
Visite le 5 avril 2026
"""


class TestSegmentMultiLot:
    def setup_method(self):
        self.sections = segment_licitor_page(SAMPLE_MULTI_LOT)

    def test_header_contient_tribunal(self):
        assert "Nanterre" in self.sections.header

    def test_auction_block_contient_date(self):
        assert "16 avril 2026" in self.sections.auction_block

    def test_deux_lots_detectes(self):
        assert len(self.sections.lots) == 2

    def test_lot_1_contient_studio(self):
        assert "STUDIO" in self.sections.lots[0]

    def test_lot_1_contient_mise_a_prix(self):
        assert "57 000" in self.sections.lots[0]

    def test_lot_2_contient_appartement(self):
        assert "APPARTEMENT" in self.sections.lots[1]

    def test_lot_2_contient_mise_a_prix(self):
        assert "194 000" in self.sections.lots[1]

    def test_address_block_contient_ville(self):
        assert "Courbevoie" in self.sections.address_block

    def test_address_block_contient_rue(self):
        assert "Kléber" in self.sections.address_block or "Kleber" in self.sections.address_block

    def test_visit_block_contient_date_visite(self):
        assert "8 avril 2026" in self.sections.visit_block

    def test_visit_block_contient_horaires(self):
        assert "11h30" in self.sections.visit_block

    def test_raw_text_preserve(self):
        assert "STUDIO" in self.sections.raw_text
        assert "APPARTEMENT" in self.sections.raw_text


class TestSegmentSingleLot:
    def setup_method(self):
        self.sections = segment_licitor_page(SAMPLE_SINGLE_LOT)

    def test_un_lot_detecte(self):
        assert len(self.sections.lots) == 1

    def test_lot_contient_appartement(self):
        assert "APPARTEMENT" in self.sections.lots[0]

    def test_lawyer_block_detecte(self):
        assert "Martin" in self.sections.lawyer_block

    def test_visit_block_detecte(self):
        assert "14 avril 2026" in self.sections.visit_block


class TestSegmentNoLots:
    def setup_method(self):
        self.sections = segment_licitor_page(SAMPLE_NO_LOTS)

    def test_pas_de_crash_sans_lots(self):
        # Le segmenteur ne doit pas lever d'exception
        assert self.sections is not None

    def test_raw_text_toujours_present(self):
        assert "Lyon" in self.sections.raw_text

    def test_visit_detecte(self):
        assert "5 avril" in self.sections.visit_block


class TestSegmentEdgeCases:
    def test_texte_vide(self):
        sections = segment_licitor_page("")
        assert sections.header == ""
        assert sections.lots == []

    def test_texte_minimal(self):
        sections = segment_licitor_page("Tribunal de Paris\nMise à prix : 50 000 €")
        assert sections.raw_text != ""
