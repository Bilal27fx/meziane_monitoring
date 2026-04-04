# Plan — Fix extraction données Licitor (date, lieu enchère, visite)

**Date :** 2026-04-04  
**Statut :** Validé — en cours  
**Priorité :** Haute

---

## Contexte

L'adapter Licitor rate fréquemment l'extraction de la date d'enchère et du lieu de visite.
Diagnostic issu de la lecture complète de `licitor.py`, `auction_ingestion_service.py` et `auction_listing.py`.

---

## Bugs identifiés

### Bug 1 — Root cause : `auction_date` / `auction_location` uniquement depuis la session

`auction_date`, `auction_tribunal`, `auction_location` sont des `@property` sur `AuctionListing` qui lisent **exclusivement** depuis `self.session` (lignes 98-112 du modèle).

Si `parse_sessions` rate la date → **toutes les annonces de la session ont `auction_date=null`**.  
Aucun fallback depuis la page détail, alors que les pages détail Licitor répètent date + tribunal.

Problème supplémentaire : `auction_location` retourne `None` si `session.city` est absent, même quand `session.tribunal` est connu.

### Bug 2 — `_extract_session_datetime` crashe le run entier

`licitor.py:212` lève une `ValueError` quand la date ne peut pas être parsée.  
Cette exception remonte jusqu'au run → `status = FAILED` → toutes les annonces du run sont perdues.

### Bug 3 — `_extract_visit_details` : lieu de visite non extrait

**3a.** `explicit_location_pattern` (ligne 330) requiert un code postal IDF (`75xxx`, `92xxx`...).  
Toute adresse sans CP IDF → `visit_location = None`.

**3b.** `_extract_visit_blocks` (ligne 609) a `"me "` comme stop keyword.  
Coupe le bloc dès "même", "mise", ou un nom d'avocat → date/lieu tronqués.

**3c.** Fenêtre de capture limitée à 4 lignes après "visite" → trop courte sur certaines pages.

### Bug 4 — `_apply_listing_detail` n'applique jamais `auction_date` / `auction_location`

`ingestion_service.py:234-264` : aucune ligne ne set ces champs depuis les `facts` du détail.  
Même si `parse_listing_detail` les extrayait, ils seraient ignorés.

### Bug 5 — `_extract_address` exclut les lignes contenant "appartement"

`licitor.py:421` : "appartement" est dans les mots-clés d'exclusion.  
Une ligne du type "Appartement situé au 5 rue de la Paix, 75001 Paris" est entièrement ignorée.

### Bug 6 — `postal_code` et patterns location uniquement IDF

Codes postaux hardcodés `75xxx`, `77xxx`, `78xxx`, `91-95xxx`.  
Tout bien hors IDF → `postal_code = None`, `visit_location = None`.

---

## Fichiers touchés

| Fichier | Modifications |
|---|---|
| `backend/app/agents/auction/adapters/licitor.py` | Bugs 2, 3, 5, 6 + nouvelle méthode `_extract_auction_info_from_detail` |
| `backend/app/models/auction_listing.py` | Bug 1 — fix `@property auction_location`, ajout fallback `property_details` |
| `backend/app/services/auction_ingestion_service.py` | Bug 4 — `_apply_listing_detail` propage `auction_date` / `auction_location` |
| `backend/tests/services/test_licitor_adapter.py` | Nouveaux cas de test pour chaque bug |

---

## Ordre d'exécution

### Étape 1 — `licitor.py` : `_extract_session_datetime` ne crashe plus

Remplacer le `raise ValueError` par `return None`.  
Modifier `parse_sessions` : si `session_datetime is None` → retourner liste vide + logger.

### Étape 2 — `licitor.py` : extraire date + tribunal depuis la page détail

Nouvelle méthode `_extract_auction_info_from_detail(text: str) -> dict` :
- Réutilise `_extract_session_datetime` et `_extract_tribunal`
- Retourne `{ "auction_date": datetime|None, "auction_tribunal": str|None }`

L'appeler dans `parse_listing_detail`, ajouter les clés dans `facts`.

### Étape 3 — `models/auction_listing.py` : fallback + fix `auction_location`

Modifier les `@property` :

```python
@property
def auction_date(self):
    # Fallback sur le détail si la session n'a pas de date
    override = (self.property_details or {}).get("auction", {}).get("date")
    if override:
        return override
    return self.session.session_datetime if self.session else None

@property
def auction_location(self):
    # Fix : retourner le tribunal seul si city est absent
    if not self.session:
        return None
    tribunal = self.session.tribunal or ""
    city = self.session.city
    return f"{tribunal} · {city}" if city else (tribunal or None)
```

### Étape 4 — `ingestion_service.py` : propager les infos du détail

Dans `_apply_listing_detail`, si `facts` contient `auction_date` ou `auction_tribunal` :
- Les stocker dans `listing.property_details["auction"]`
- Uniquement si la session n'a pas déjà cette info

### Étape 5 — `licitor.py` : `_extract_visit_details` moins restrictive

- `explicit_location_pattern` : supprimer l'obligation du CP IDF — accepter tout texte après les mots-clés de lieu
- `_extract_visit_blocks` : remplacer stop keyword `"me "` par le pattern `r"\bMe\.\s+[A-Z]"`, augmenter fenêtre à 6 lignes

### Étape 6 — `licitor.py` : `_extract_address` + `postal_code` élargis

- Retirer `"appartement"` des exclusions dans `_extract_address`
- Élargir `_extract_postal_code` : accepter tout CP français 5 chiffres avec filtre `10000 <= int(cp) <= 97700`

### Étape 7 — Tests

Cas à couvrir dans `test_licitor_adapter.py` :
- Page détail avec date d'enchère → présente dans `facts`
- Visite sans CP IDF → `visit_location` quand même extrait
- Stop keyword `"me "` ne coupe plus un bloc valide
- `_extract_session_datetime` sans date → `None`, pas d'exception
- `auction_location` retourne le tribunal seul si `city` absent
- Adresse contenant "appartement" → correctement extraite

---

## Tests attendus post-livraison

```
backend/tests/services/test_licitor_adapter.py  — tous passent
```

Les compteurs `missing_auction_date` et `missing_visit_location` du `data_quality` doivent baisser significativement sur un vrai run.
