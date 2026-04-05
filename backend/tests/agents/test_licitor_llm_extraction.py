"""Tests du service d'extraction LLM Licitor (OpenAI mocké)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.agents.auction.licitor_llm_extraction_service import (
    LicitorLLMUnavailableError,
    LicitorPageExtraction,
    extract_page,
)
from app.agents.auction.licitor_text_segmenter import LicitorPageSections


def _make_sections(**kwargs) -> LicitorPageSections:
    defaults = {
        "header": "À l'annexe du Tribunal Judiciaire de Nanterre",
        "auction_block": "Vente aux enchères jeudi 16 avril 2026 à 14h30",
        "lots": [
            "1er lot de la vente\nUN STUDIO\nde 31,57 m²\nMise à prix : 57 000 €",
            "2nd lot de la vente\nUN APPARTEMENT\nde 103,40 m²\nMise à prix : 194 000 €",
        ],
        "address_block": "Courbevoie\n6, rue Kléber\n92400",
        "visit_block": "Visite sur place mercredi 8 avril 2026 de 11h30 à 12h30",
        "lawyer_block": "",
        "raw_text": "texte complet",
    }
    defaults.update(kwargs)
    return LicitorPageSections(**defaults)


def _mock_openai_response(payload: dict) -> MagicMock:
    """Construit un mock de réponse OpenAI à partir d'un dict payload."""
    msg = MagicMock()
    msg.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_mock_client(payload: dict) -> MagicMock:
    """Retourne un client OpenAI mocké qui retourne le payload donné."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
    return mock_client


_VALID_LLM_RESPONSE = {
    "tribunal": "TJ Nanterre",
    "city": "Nanterre",
    "auction_date": "2026-04-16",
    "auction_time": "14:30",
    "lots": [
        {
            "lot_number": 1,
            "type_bien": "STUDIO",
            "surface_m2": 31.57,
            "surface_balcon_m2": 3.50,
            "surface_terrasse_m2": None,
            "etage": 2,
            "nb_pieces": 1,
            "nb_chambres": None,
            "description": "UN STUDIO de 31,57 m²",
            "amenities": {"cave": True, "parking": True, "box": None, "jardin": None, "ascenseur": None, "balcon": True, "terrasse": None},
            "mise_a_prix": 57000.0,
            "extras": ["emplacement de voiture"],
        },
        {
            "lot_number": 2,
            "type_bien": "APPARTEMENT",
            "surface_m2": 103.40,
            "surface_balcon_m2": None,
            "surface_terrasse_m2": 69.08,
            "etage": 7,
            "nb_pieces": None,
            "nb_chambres": 4,
            "description": "UN APPARTEMENT de 103,40 m²",
            "amenities": {"cave": True, "parking": True, "box": None, "jardin": None, "ascenseur": None, "balcon": None, "terrasse": True},
            "mise_a_prix": 194000.0,
            "extras": ["débarras", "deux emplacements de voiture"],
        },
    ],
    "address": "6, rue Kléber, 92400 Courbevoie",
    "postal_code": "92400",
    "visit_dates": ["mercredi 8 avril 2026 de 11h30 à 12h30"],
    "visit_location": "sur place",
    "occupancy_status": None,
    "lawyer_name": None,
    "lawyer_phone": None,
}


class TestExtractPageSuccess:
    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_retourne_licitor_page_extraction(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_openai_cls.return_value = _make_mock_client(_VALID_LLM_RESPONSE)

        result = extract_page(_make_sections())
        assert isinstance(result, LicitorPageExtraction)

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_tribunal_extrait(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_openai_cls.return_value = _make_mock_client(_VALID_LLM_RESPONSE)

        result = extract_page(_make_sections())
        assert result.tribunal == "TJ Nanterre"

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_deux_lots_extraits(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_openai_cls.return_value = _make_mock_client(_VALID_LLM_RESPONSE)

        result = extract_page(_make_sections())
        assert len(result.lots) == 2

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_lot_1_surface_et_prix(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_openai_cls.return_value = _make_mock_client(_VALID_LLM_RESPONSE)

        result = extract_page(_make_sections())
        lot1 = result.lots[0]
        assert lot1.surface_m2 == 31.57
        assert lot1.mise_a_prix == 57000.0

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_visit_dates_extraites(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_openai_cls.return_value = _make_mock_client(_VALID_LLM_RESPONSE)

        result = extract_page(_make_sections())
        assert len(result.visit_dates) == 1
        assert "8 avril" in result.visit_dates[0]

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_postal_code_extrait(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_openai_cls.return_value = _make_mock_client(_VALID_LLM_RESPONSE)

        result = extract_page(_make_sections())
        assert result.postal_code == "92400"


class TestExtractPageErrors:
    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    def test_leve_erreur_si_pas_de_cle(self, mock_settings):
        mock_settings.OPENAI_API_KEY = None
        with pytest.raises(LicitorLLMUnavailableError, match="OPENAI_API_KEY"):
            extract_page(_make_sections())

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_leve_erreur_si_json_invalide(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        msg = MagicMock()
        msg.content = "pas du json {"
        choice = MagicMock()
        choice.message = msg
        response = MagicMock()
        response.choices = [choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = response
        mock_openai_cls.return_value = mock_client

        with pytest.raises(LicitorLLMUnavailableError):
            extract_page(_make_sections())

    @patch("app.agents.auction.licitor_llm_extraction_service.settings")
    @patch("openai.OpenAI")
    def test_leve_erreur_si_openai_timeout(self, mock_openai_cls, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("timeout")
        mock_openai_cls.return_value = mock_client

        with pytest.raises(LicitorLLMUnavailableError, match="timeout"):
            extract_page(_make_sections())
