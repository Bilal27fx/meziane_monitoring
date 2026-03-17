# 🏦 Configuration Bridge API - Guide Setup

**Date :** 15 mars 2026
**Service :** Connecteur bancaire automatique

---

## 📋 Prérequis

Bridge API permet de connecter automatiquement tes comptes bancaires et récupérer les transactions.

- **Site officiel :** https://bridgeapi.io
- **Documentation :** https://docs.bridgeapi.io
- **Alternative :** Budget Insight (https://www.budget-insight.com)

---

## 🔑 Obtenir les credentials Bridge

### Étape 1 : Créer un compte Bridge

1. Aller sur https://dashboard.bridgeapi.io/signup
2. Créer un compte développeur
3. Vérifier email

### Étape 2 : Créer une application

1. Dans le dashboard Bridge : **Create Application**
2. Nom : `Meziane Monitoring`
3. Type : `Server-to-Server`
4. Redirect URL : `http://localhost:8000/api/banking/callback`

### Étape 3 : Récupérer les credentials

Tu vas obtenir :
- **Client ID** : `client_xxx`
- **Client Secret** : `secret_xxx`

⚠️ **IMPORTANT** : Ne JAMAIS commit ces secrets dans Git !

---

## ⚙️ Configuration dans le projet

### 1. Mettre à jour `.env`

Ouvre `/Users/bilalmeziane/Desktop/Meziane_Monitoring/.env` et remplis :

```bash
# Bridge API
BRIDGE_CLIENT_ID=ton_client_id_ici
BRIDGE_CLIENT_SECRET=ton_client_secret_ici
```

### 2. Redémarrer le serveur

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

---

## 🧪 Tester la connexion

### 1. Lister les banques disponibles

```bash
curl http://localhost:8000/api/banking/banks
```

Réponse attendue :
```json
{
  "banks": [
    {"id": 1, "name": "BNP Paribas", "logo_url": "..."},
    {"id": 2, "name": "Crédit Agricole", "logo_url": "..."},
    ...
  ],
  "total": 150
}
```

### 2. Connecter une banque

```bash
curl -X POST http://localhost:8000/api/banking/items \
  -H "Content-Type: application/json" \
  -d '{
    "bank_id": 1,
    "redirect_url": "http://localhost:8000/api/banking/callback"
  }'
```

Réponse :
```json
{
  "item_id": 12345,
  "redirect_url": "https://connect.bridgeapi.io/...",
  "message": "Item créé avec succès"
}
```

### 3. Importer les transactions

Une fois la banque connectée et `user_uuid` obtenu :

```bash
curl -X POST http://localhost:8000/api/banking/import \
  -H "Content-Type: application/json" \
  -d '{
    "sci_id": 1,
    "account_id": 789456,
    "since": "2026-01-01",
    "until": "2026-03-15"
  }'
```

Réponse :
```json
{
  "imported": 45,
  "duplicates": 2,
  "errors": 0,
  "total": 47,
  "message": "45 transactions importées avec succès"
}
```

---

## 🔄 Flux complet

```
1. Utilisateur → Connecte sa banque via Bridge
   ↓
2. Bridge → Récupère transactions automatiquement
   ↓
3. Backend → Importe transactions dans PostgreSQL
   ↓
4. IA (GPT-4) → Catégorise automatiquement
   ↓
5. Dashboard → Affiche cashflow en temps réel
```

---

## 📊 Endpoints disponibles

### Liste banques
```
GET /api/banking/banks
```

### Liste comptes utilisateur
```
GET /api/banking/accounts/{user_uuid}
```

### Import transactions
```
POST /api/banking/import
Body: { sci_id, account_id, since, until }
```

### Synchroniser compte
```
POST /api/banking/sync
Body: { account_id }
```

### Récupérer transactions brutes
```
GET /api/banking/transactions/{account_id}?since=2026-01-01&limit=100
```

---

## 🛡️ Sécurité

### Variables sensibles
- ✅ `.env` dans `.gitignore` (déjà fait)
- ✅ Credentials jamais hardcodés dans le code
- ✅ HTTPS en production (pas en dev local)

### Mode Production
En production, utiliser :
- Variables d'environnement système (pas .env)
- Secrets Manager (AWS Secrets, etc.)
- HTTPS uniquement

---

## 💰 Tarification Bridge

**Sandbox (gratuit) :**
- Accès complet API
- Données de test
- Pas de vraies banques

**Production :**
- ~5€/utilisateur/mois
- Accès 500+ banques EU
- Support prioritaire

**Alternative gratuite :** Nordigen (OpenBanking EU)

---

## 🔧 Troubleshooting

### Erreur "Impossible de se connecter à Bridge API"
- Vérifier `BRIDGE_CLIENT_ID` et `BRIDGE_CLIENT_SECRET` dans `.env`
- Vérifier connexion internet
- Tester : `curl https://api.bridgeapi.io/v2/status`

### Erreur "Invalid credentials"
- Regénérer credentials dans Bridge dashboard
- Copier/coller soigneusement (pas d'espaces)

### Pas de transactions importées
- Vérifier date `since` (pas trop loin dans le passé)
- Vérifier que le compte a des transactions
- Check logs : `tail -f backend/logs/app.log`

---

## 📚 Ressources

- **Doc officielle :** https://docs.bridgeapi.io
- **API Reference :** https://docs.bridgeapi.io/reference
- **Swagger live :** https://api.bridgeapi.io/docs

---

**Status :** Implémentation terminée ✅
**Prochaine étape :** Remplir credentials et tester avec vraies banques
