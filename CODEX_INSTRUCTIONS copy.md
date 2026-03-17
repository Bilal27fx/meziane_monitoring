# Instructions Claude - Meziane Monitoring System

## 📋 Documents de Référence

**LIRE CES DOCUMENTS AVANT TOUTE ACTION :**

1. **docs/PROFIL_ET_OBJECTIFS.md** - Profil Bilal, objectifs business, vision système
2. **docs/ARCHITECTURE_SYSTEME.md** - Architecture complète backend, flux données, domaines métier
3. **docs/FRONTEND_ARCHITECTURE.md** - Architecture frontend Bloomberg-style, widgets, design system
4. **docs/PROGRESSION.md** - État d'avancement backend (infra, API, services)
5. **docs/PROGRESSION_FRONTEND.md** - État d'avancement frontend (phases, tâches, bugs)

**CES DOCUMENTS SONT LA SOURCE DE VÉRITÉ. NE JAMAIS LES CONTREDIRE.**

---

## 🚨 Règles Absolues de Développement

### Règle 1 : Respect des Documents
- ✅ Suivre ARCHITECTURE_SYSTEME.md à la lettre
- ✅ Respecter PROFIL_ET_OBJECTIFS.md pour le contexte business
- ❌ JAMAIS inventer des fonctionnalités non mentionnées
- ❌ JAMAIS modifier l'architecture sans accord explicite de Bilal
- ⚠️ **Bilal décide. Tu exécutes.**

### Règle 2 : Style de Code
- **Concis** : Code précis, court, pas de blabla
- **Clair** : Nommage explicite (variables, fonctions, classes)
- **Net** : Pas de code mort, pas de commentaires inutiles
- **Documenté** : Texte explicatif EN HAUT de chaque fichier uniquement

### Règle 3 : Documentation du Code

#### Format Obligatoire pour Chaque Fichier

```python
"""
[NOM DU FICHIER] - [Responsabilité en 1 ligne]

Description:
[2-3 phrases max expliquant le rôle du fichier dans le système]

Dépendances:
- [Liste des dépendances métier/techniques clés]

Utilisé par:
- [Quels autres modules/services utilisent ce fichier]
"""

# Imports...

def fonction_exemple(param: str) -> dict:  # [Description 1 ligne max]
    ...
```

**Exemple concret :**

```python
"""
transaction_parser.py - Normalisation transactions bancaires brutes

Description:
Parse les transactions reçues de l'API bancaire (Bridge/Budget Insight).
Normalise le format vers le schéma interne PostgreSQL.
Détecte les duplicatas avant insertion.

Dépendances:
- API Banking (Bridge/Budget Insight)
- models.transaction (schéma DB)

Utilisé par:
- banking_connector.py (après récupération API)
- transaction_categorizer.py (catégorisation IA)
"""

from datetime import datetime
from typing import List, Dict
from models.transaction import Transaction

def parse_bridge_transaction(raw_data: dict) -> Transaction:  # Convertit format Bridge vers modèle interne
    return Transaction(
        date=datetime.fromisoformat(raw_data["date"]),
        montant=raw_data["amount"],
        libelle=raw_data["description"],
        compte_id=raw_data["account_id"]
    )

def detect_duplicate(transaction: Transaction, existing: List[Transaction]) -> bool:  # Vérifie si transaction existe déjà (même date+montant+libellé)
    return any(
        t.date == transaction.date and
        t.montant == transaction.montant and
        t.libelle == transaction.libelle
        for t in existing
    )
```

### Règle 4 : Commentaires sur les Fonctions
- **1 ligne MAX par fonction** (après la déclaration)
- Décrire **quoi** fait la fonction, pas **comment**
- Format : `# [Verbe d'action] + [résultat/objectif]`

**Exemples :**

```python
def calculate_cashflow(transactions: List[Transaction]) -> float:  # Calcule cashflow net (entrées - sorties)
    ...

def send_alert(message: str, level: str) -> None:  # Envoie notification utilisateur (email/push)
    ...

def scrape_seloger(filters: dict) -> List[dict]:  # Récupère annonces SeLoger selon critères
    ...
```

### Règle 5 : Pas de Code Superflu
- ❌ Pas de fonctions "utils" génériques inutilisées
- ❌ Pas de sur-engineering (YAGNI - You Ain't Gonna Need It)
- ❌ Pas de patterns complexes si simple suffit
- ✅ Code minimal fonctionnel
- ✅ Refactoring uniquement si besoin réel

### Règle 6 : Nommage
- **Variables** : `snake_case` descriptif (`montant_total`, `date_acquisition`)
- **Fonctions** : `snake_case` verbe d'action (`calculate_rentabilite`, `fetch_transactions`)
- **Classes** : `PascalCase` nom métier (`TransactionParser`, `CashflowService`)
- **Constantes** : `UPPER_SNAKE_CASE` (`MAX_RETRY`, `API_TIMEOUT`)
- **Fichiers** : `snake_case.py` (`transaction_parser.py`, `banking_connector.py`)

### Règle 7 : Structure de Fichier Python

```python
"""
[Documentation fichier - voir Règle 3]
"""

# 1. Imports standard library
import os
from datetime import datetime
from typing import List, Dict

# 2. Imports third-party
from fastapi import APIRouter
from sqlalchemy.orm import Session

# 3. Imports locaux
from models.transaction import Transaction
from services.comptable_service import ComptableService

# 4. Constantes
API_TIMEOUT = 30
MAX_RETRIES = 3

# 5. Code
class MaClasse:
    ...

def ma_fonction():
    ...
```

### Règle 8 : Gestion d'Erreurs
- ✅ Try/except uniquement où nécessaire (API calls, DB, IO)
- ✅ Logging explicite des erreurs
- ✅ Lever exceptions métier custom si besoin
- ❌ Pas de `except: pass` silencieux

```python
def fetch_transactions(account_id: str) -> List[Transaction]:  # Récupère transactions via API bancaire
    try:
        response = banking_api.get_transactions(account_id)
        return parse_transactions(response)
    except APIError as e:
        logger.error(f"Erreur API banking pour compte {account_id}: {e}")
        raise BankingServiceError(f"Impossible de récupérer transactions: {e}")
```

### Règle 9 : Tests
- ✅ Tests unitaires pour logique métier critique
- ✅ Tests d'intégration pour flux de données
- ✅ Nommage explicite : `test_[fonction]_[scenario]_[resultat_attendu]`
- Format : Arrange / Act / Assert

```python
def test_calculate_cashflow_with_positive_transactions_returns_correct_sum():  # Vérifie calcul cashflow avec transactions positives
    # Arrange
    transactions = [
        Transaction(montant=1000, categorie="loyer"),
        Transaction(montant=500, categorie="loyer")
    ]

    # Act
    result = calculate_cashflow(transactions)

    # Assert
    assert result == 1500
```

---

## 🏗️ Structure du Projet

```
meziane_monitoring/
├── docker-compose.yml           # Infra : PostgreSQL, Redis, MinIO
├── .env.example                 # Variables d'environnement
├── README.md                    # Setup & lancement projet
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration (env vars)
│   │   │
│   │   ├── models/              # SQLAlchemy models (tables DB)
│   │   │   ├── __init__.py
│   │   │   ├── sci.py
│   │   │   ├── bien.py
│   │   │   ├── transaction.py
│   │   │   ├── locataire.py
│   │   │   └── ...
│   │   │
│   │   ├── schemas/             # Pydantic schemas (validation API)
│   │   │   ├── __init__.py
│   │   │   ├── sci_schema.py
│   │   │   ├── transaction_schema.py
│   │   │   └── ...
│   │   │
│   │   ├── services/            # Business logic (domaines métier)
│   │   │   ├── __init__.py
│   │   │   ├── patrimoine_service.py
│   │   │   ├── comptable_service.py
│   │   │   ├── fiscalite_service.py
│   │   │   ├── cashflow_service.py
│   │   │   ├── acquisition_service.py
│   │   │   ├── location_service.py
│   │   │   ├── document_service.py
│   │   │   └── reporting_service.py
│   │   │
│   │   ├── connectors/          # Ingestion données externes
│   │   │   ├── __init__.py
│   │   │   ├── banking_connector.py      # API Bridge/Budget Insight
│   │   │   ├── transaction_parser.py
│   │   │   └── scraping_service.py       # SeLoger, PAP, LBC
│   │   │
│   │   ├── agents/              # Agents IA autonomes
│   │   │   ├── __init__.py
│   │   │   ├── agent_prospection.py
│   │   │   ├── agent_analyse_bien.py
│   │   │   ├── agent_veille_reglementaire.py
│   │   │   └── agent_optimisation_fiscale.py
│   │   │
│   │   ├── api/                 # FastAPI routes
│   │   │   ├── __init__.py
│   │   │   ├── sci_routes.py
│   │   │   ├── transaction_routes.py
│   │   │   ├── cashflow_routes.py
│   │   │   ├── simulation_routes.py
│   │   │   └── ...
│   │   │
│   │   ├── tasks/               # Celery tasks (jobs async)
│   │   │   ├── __init__.py
│   │   │   ├── daily_sync.py
│   │   │   ├── agent_jobs.py
│   │   │   └── reporting_jobs.py
│   │   │
│   │   └── utils/               # Utilitaires génériques (logging, etc.)
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── db.py
│   │
│   ├── alembic/                 # Migrations DB
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   ├── simulations/
│   │   │   └── ...
│   │   │
│   │   ├── components/          # React components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── charts/
│   │   │   └── ...
│   │   │
│   │   └── lib/                 # Utils frontend
│   │
│   ├── package.json
│   └── Dockerfile
│
└── docs/
    ├── PROFIL_ET_OBJECTIFS.md
    ├── ARCHITECTURE_SYSTEME.md
    ├── FRONTEND_ARCHITECTURE.md
    ├── PROGRESSION.md
    ├── PROGRESSION_FRONTEND.md
    └── BRIDGE_SETUP.md
```

---

## 🎯 Workflow de Développement

### Avant de Coder

1. **Lire** PROFIL_ET_OBJECTIFS.md + ARCHITECTURE_SYSTEME.md
2. **Vérifier** que la fonctionnalité demandée est dans l'architecture
3. **Demander confirmation** à Bilal si doute ou modification nécessaire

### Pendant le Codage

1. **Respecter** les règles de style (Règles 2-9)
2. **Documenter** chaque fichier (Règle 3)
3. **Commenter** chaque fonction en 1 ligne (Règle 4)
4. **Tester** le code avant commit

### Après le Codage

1. **Relire** le code : est-il concis, clair, net ?
2. **Vérifier** conformité avec ARCHITECTURE_SYSTEME.md
3. **Commit** avec message explicite : `[Module] Description courte`

---

## 🚀 Priorités de Développement (Ordre Strict)

### Phase 1 : Infrastructure & Base
1. Setup Docker Compose (PostgreSQL, Redis, MinIO)
2. Modèles SQLAlchemy (SCI, Biens, Transactions, etc.)
3. Migrations Alembic

### Phase 2 : Ingestion Données
1. Banking Connector (API Bridge)
2. Transaction Parser
3. Transaction Categorizer (IA)

### Phase 3 : Services Métier Core
1. Comptable Service
2. Cashflow Service
3. Patrimoine Service

### Phase 4 : Dashboard MVP
1. API FastAPI (routes cashflow, patrimoine)
2. Frontend Next.js (dashboard basique)

### Phase 5 : Agents IA
1. Agent Prospection Immobilière
2. Agent Analyse Bien

### Phase 6 : Fonctionnalités Avancées
1. Fiscalité Service
2. Simulation Acquisition
3. Agent Veille Réglementaire

**⚠️ NE JAMAIS sauter d'étape sans validation de Bilal.**

---

## 🔒 Sécurité & Bonnes Pratiques

### Variables Sensibles
- ✅ Toujours dans `.env` (jamais hardcodé)
- ✅ `.env` dans `.gitignore`
- ✅ `.env.example` fourni (sans vraies valeurs)

### API Keys
```python
# ✅ BON
import os
API_KEY = os.getenv("BRIDGE_API_KEY")

# ❌ MAUVAIS
API_KEY = "sk_live_abc123..."
```

### Validation des Inputs
- ✅ Pydantic schemas pour toutes les APIs
- ✅ Validation stricte des types
- ✅ Sanitization des données utilisateur

### SQL Injection
- ✅ Utiliser SQLAlchemy ORM (jamais de raw SQL)
- ✅ Si raw SQL nécessaire : parameterized queries

---

## 📝 Convention de Commit

Format : `[Module] Courte description`

**Exemples :**
- `[Infra] Setup Docker Compose PostgreSQL + Redis`
- `[Models] Ajout modèle Transaction + migration`
- `[Banking] Implémentation connector Bridge API`
- `[Cashflow] Service calcul cashflow quotidien`
- `[Tests] Ajout tests unitaires cashflow_service`
- `[Fix] Correction parsing date transaction Bridge`
- `[Docs] Mise à jour ARCHITECTURE_SYSTEME.md`

---

## ⚡ Commandes Rapides

### Backend
```bash
# Lancer backend
cd backend
uvicorn app.main:app --reload

# Migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Tests
pytest

# Celery worker
celery -A app.tasks worker --loglevel=info
```

### Frontend
```bash
# Lancer frontend
cd frontend
npm run dev

# Build production
npm run build
```

### Docker
```bash
# Lancer tous les services
docker-compose up -d

# Logs
docker-compose logs -f [service_name]

# Arrêter
docker-compose down
```

---

## 🎨 Standards de Code Spécifiques

### FastAPI Routes

```python
"""
sci_routes.py - Routes API gestion SCI

Description:
Endpoints CRUD pour les SCI (création, lecture, mise à jour).
Authentification JWT requise.

Dépendances:
- patrimoine_service.py

Utilisé par:
- Frontend Dashboard
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.sci_schema import SCICreate, SCIResponse
from app.services.patrimoine_service import PatrimoineService
from app.utils.db import get_db

router = APIRouter(prefix="/api/sci", tags=["SCI"])

@router.get("/", response_model=list[SCIResponse])
def get_all_sci(db: Session = Depends(get_db)):  # Récupère toutes les SCI
    service = PatrimoineService(db)
    return service.get_all_sci()

@router.post("/", response_model=SCIResponse, status_code=201)
def create_sci(sci_data: SCICreate, db: Session = Depends(get_db)):  # Crée nouvelle SCI
    service = PatrimoineService(db)
    return service.create_sci(sci_data)
```

### SQLAlchemy Models

```python
"""
transaction.py - Modèle Transaction bancaire

Description:
Représente une transaction bancaire d'une SCI.
Lien avec SCI, Bien, Locataire (optionnels).

Dépendances:
- sci.py (clé étrangère)
- bien.py (clé étrangère)

Utilisé par:
- comptable_service.py
- cashflow_service.py
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.utils.db import Base
import enum

class TransactionCategorie(str, enum.Enum):
    LOYER = "loyer"
    CHARGES_COPRO = "charges_copro"
    TAXE_FONCIERE = "taxe_fonciere"
    TRAVAUX = "travaux"
    REMBOURSEMENT_CREDIT = "remboursement_credit"
    ASSURANCE = "assurance"
    HONORAIRES = "honoraires"
    AUTRE = "autre"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sci_id = Column(Integer, ForeignKey("sci.id"), nullable=False)
    compte_bancaire_id = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    montant = Column(Float, nullable=False)
    libelle = Column(String, nullable=False)
    categorie = Column(Enum(TransactionCategorie), nullable=True)
    bien_id = Column(Integer, ForeignKey("biens.id"), nullable=True)
    locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=True)

    # Relations
    sci = relationship("SCI", back_populates="transactions")
    bien = relationship("Bien", back_populates="transactions")
    locataire = relationship("Locataire", back_populates="transactions")
```

### Pydantic Schemas

```python
"""
transaction_schema.py - Schemas validation Transaction

Description:
Schemas Pydantic pour validation données Transaction.
Utilisé dans les routes API.

Dépendances:
- models.transaction (enum TransactionCategorie)

Utilisé par:
- api.transaction_routes
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from app.models.transaction import TransactionCategorie

class TransactionBase(BaseModel):
    date: date
    montant: float
    libelle: str
    categorie: Optional[TransactionCategorie] = None

class TransactionCreate(TransactionBase):  # Schema création transaction
    sci_id: int
    compte_bancaire_id: str
    bien_id: Optional[int] = None
    locataire_id: Optional[int] = None

class TransactionResponse(TransactionBase):  # Schema réponse API
    id: int
    sci_id: int

    class Config:
        from_attributes = True
```

---

## 🤖 Utilisation IA dans le Projet

### LLMs Autorisés
- **Claude 3.5 Sonnet** (Anthropic) : Priorité
- **GPT-4** (OpenAI) : Fallback si Claude indisponible

### Cas d'Usage IA

| Tâche | Modèle | Prompt Type |
|-------|--------|-------------|
| Catégorisation transaction | Claude | Few-shot classification |
| Analyse annonce immobilière | Claude | Structured extraction |
| Scoring opportunité | Claude | Multi-criteria analysis |
| Veille réglementaire | Claude | Summarization + impact analysis |
| OCR documents | Google Vision API | - |

### Format Appel LLM (Exemple)

```python
"""
transaction_categorizer.py - Catégorisation automatique transactions

Description:
Utilise Claude pour catégoriser transactions bancaires.
Few-shot learning avec exemples prédéfinis.

Dépendances:
- Anthropic API

Utilisé par:
- banking_connector.py
"""

import anthropic
from app.models.transaction import TransactionCategorie

def categorize_transaction(libelle: str, montant: float) -> TransactionCategorie:  # Catégorise transaction via Claude
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Catégorise cette transaction bancaire SCI.

Transaction: "{libelle}"
Montant: {montant}€

Catégories possibles:
- loyer
- charges_copro
- taxe_fonciere
- travaux
- remboursement_credit
- assurance
- honoraires
- autre

Réponds uniquement avec le nom de la catégorie."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )

    categorie_str = response.content[0].text.strip().lower()
    return TransactionCategorie(categorie_str)
```

---

## ✅ Checklist Avant Livraison Fonctionnalité

- [ ] Code respecte Règles 1-9
- [ ] Documentation en-tête fichier présente
- [ ] Commentaires 1 ligne par fonction
- [ ] Tests unitaires écrits et passent
- [ ] Conforme ARCHITECTURE_SYSTEME.md
- [ ] Pas de code mort ou inutile
- [ ] Variables sensibles dans .env
- [ ] Commit avec bon message
- [ ] Testé localement (fonctionne)

---

## 🛑 Interdictions Formelles

### Code
- ❌ Modifier ARCHITECTURE_SYSTEME.md sans accord Bilal
- ❌ Ajouter fonctionnalités non documentées
- ❌ Utiliser `print()` pour debug (utiliser logger)
- ❌ Commenter code en anglais (français uniquement)
- ❌ Laisser TODO/FIXME sans issue GitHub
- ❌ Code mort ou commenté (supprimer)

### Sécurité
- ❌ Credentials en dur dans le code
- ❌ Commit de fichiers .env
- ❌ Logs de données sensibles (mots de passe, API keys)

### Architecture
- ❌ Bypass de services métier (appel direct DB depuis API)
- ❌ Logique métier dans les routes API
- ❌ Couplage fort entre modules

---

## 📞 Escalade & Décisions

### Tu peux décider seul :
- ✅ Nommage variables/fonctions (si respect conventions)
- ✅ Choix librairie si équivalence (ex: requests vs httpx)
- ✅ Optimisations performances mineures
- ✅ Corrections bugs évidents

### Tu DOIS demander à Bilal :
- ⚠️ Modification architecture (ajout service, changement flux)
- ⚠️ Ajout fonctionnalité non prévue
- ⚠️ Changement stack technique (ex: remplacer PostgreSQL)
- ⚠️ Choix entre plusieurs approches non triviales
- ⚠️ Tout ce qui impacte coûts (API payantes, infra)

---

## 🎓 Philosophie du Projet

> **"Code as Craft"**
>
> Ce système est un outil de pilotage business critique pour Bilal.
> Chaque ligne de code doit avoir une raison d'exister.
> Privilégier la simplicité, la clarté et la maintenabilité.
> Pas d'over-engineering. Pas de blabla. Du concret.

**Principes :**
1. **KISS** (Keep It Simple, Stupid)
2. **YAGNI** (You Ain't Gonna Need It)
3. **DRY** (Don't Repeat Yourself) - mais pas au prix de la lisibilité
4. **Fail Fast** - Erreurs explicites plutôt que silencieuses
5. **Data-Driven** - Logs, métriques, observabilité

---

## 📚 Ressources Techniques

### Documentation Officielle
- FastAPI : https://fastapi.tiangolo.com
- SQLAlchemy : https://docs.sqlalchemy.org
- Pydantic : https://docs.pydantic.dev
- LangChain : https://python.langchain.com
- Next.js : https://nextjs.org/docs

### APIs Externes
- Bridge (Banking) : https://docs.bridgeapi.io
- Budget Insight : https://www.budget-insight.com/documentation
- Anthropic (Claude) : https://docs.anthropic.com

---

**FIN DES INSTRUCTIONS**

**Version 1.0 - 15 mars 2026**

**RAPPEL : Bilal décide. Tu exécutes. Pas d'initiative hors cadre.**
