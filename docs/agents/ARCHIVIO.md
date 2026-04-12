# ARCHIVIO — Agent Extraction PDF

**Rôle :** Téléchargement et extraction LLM des cahiers des charges PDF  
**LLM :** Oui — gpt-4o-mini  
**Position dans le graphe :** HERMES → ARCHIVIO (en parallèle avec MERCATO) → ORACLE

---

## Responsabilité

ARCHIVIO télécharge les PDFs détectés par HERMES (cahiers des charges, diagnostics, PV)
et en extrait les données structurées via LLM.

Il tourne en **fan-out** : un nœud ARCHIVIO par PDF, tous en parallèle.
Ses erreurs sont non-bloquantes — si un PDF échoue, le listing continue sans ces données.

---

## Ce qu'il reçoit (depuis le state via Send())

```python
# Une instance par PDF (fan-out via Send())
pdf_url: str
listing_url: str
```

---

## Ce qu'il produit (dans le state)

```python
pdf_extractions: dict[str, dict]
# pdf_url → {
#   "listing_url": "https://licitor.fr/annonce/456",
#   "surface_m2": 58.0,
#   "charges_annuelles": 2400.0,
#   "taxe_fonciere": 1200.0,
#   "syndic": "Cabinet Dupont",
#   "reglement_copropriete": true,
#   "nb_lots_copropriete": 24,
#   "procedure_syndicale": false,
#   "etat_general": "bon",         # "bon" | "moyen" | "dégradé" | null
#   "dpe_classe": "D",
#   "ges_classe": "E",
#   "amiante": false,
#   "plomb": null,
#   "termites": false,
#   "raw_text_excerpt": "...",     # premiers 500 chars pour audit
#   "extraction_model": "gpt-4o-mini"
# }
```

---

## Séquence interne

```
1. Télécharger le PDF (HTTP GET, timeout 30s)
2. Extraire le texte brut (pypdf ou pdfplumber)
3. Segmenter en sections (charges, diagnostics, règlement, etc.)
4. Appel LLM (gpt-4o-mini, json_object mode) avec le texte segmenté
5. Valider la réponse (Pydantic)
6. Retourner le résultat dans state.pdf_extractions[pdf_url]
```

---

## Fichiers

```
backend/app/agents/archivio/
├── __init__.py
├── agent.py        # archivio_node(state) — reçoit un seul pdf_url via Send()
├── downloader.py   # Téléchargement PDF avec retry
└── extractor.py    # Extraction texte + appel LLM + validation Pydantic
```

---

## Prompt LLM

**Modèle :** `gpt-4o-mini`  
**Mode :** `response_format={"type": "json_object"}`  
**Température :** `0.0`

Le prompt extrait depuis le texte brut du PDF :
- Surface, charges, taxe foncière
- État général du bien
- Informations copropriété (nb lots, syndic, procédure)
- Diagnostics (DPE, GES, amiante, plomb, termites)

**Règle stricte :** `null` si l'information n'est pas dans le texte — jamais de déduction.

---

## Fan-out LangGraph

```python
# Dans hermes_node, à la fin :
sends = []
for listing_url, pdf_urls in state["pdf_urls"].items():
    for pdf_url in pdf_urls:
        sends.append(Send("archivio", {"pdf_url": pdf_url, "listing_url": listing_url}))
return sends  # LangGraph dispatch en parallèle
```

Les résultats de toutes les instances sont fusionnés dans `state.pdf_extractions`
avant que ORACLE ne commence.

---

## Contraintes

- **Non-bloquant** : erreur sur un PDF → loggé dans `state.errors`, ORACLE reçoit `pdf_extractions[pdf_url] = None`
- **Timeout download** : 30s
- **Timeout LLM** : 30s
- **Taille max PDF** : 50 pages (au-delà, seules les 50 premières sont traitées)
- **Token limit** : prompt tronqué à 8000 tokens si le PDF est très long

---

## Erreurs dans le state

```python
{"node": "archivio", "detail": "PDF download failed: 404 https://.../cahier.pdf", "ts": "..."}
{"node": "archivio", "detail": "LLM extraction failed: json decode error", "ts": "..."}
```
