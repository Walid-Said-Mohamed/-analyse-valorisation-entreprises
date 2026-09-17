# Analyse et Valorisation d'Entreprises — Stock Screener Sectoriel

Pipeline complet **Python → PostgreSQL → Power BI** permettant d'extraire, nettoyer, analyser et valoriser un panel d'entreprises cotées d'un même secteur, à partir de leurs états financiers publics.

## Objectif

Automatiser l'analyse financière comparative d'un portefeuille d'entreprises : calcul des ratios de rentabilité, de structure financière et de croissance, valorisation par la méthode des flux de trésorerie actualisés (DCF), et restitution sous forme de screener classant les sociétés par score composite.

Le projet reproduit, de façon automatisée et reproductible, une démarche qu'un analyste financier mène habituellement à la main sous Excel.

## Panel étudié

10 sociétés du secteur technologique (US) : `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `META`, `NVDA`, `ADBE`, `ORCL`, `CRM`, `IBM`.

## Stack technique

| Outil | Rôle |
|---|---|
| **Python** (pandas, numpy, yfinance) | Extraction des données, nettoyage, calcul des ratios et du DCF |
| **PostgreSQL** (SQLAlchemy) | Stockage structuré des ratios, du CAGR et de la valorisation |
| **SQL** | Requêtes d'agrégation, scoring, vues (screener) |
| **Power BI** | Dashboard de restitution (classement, comparaison, valorisation) |

## Architecture du pipeline

```
extraction.py   →   nettoyage.py   →   ratio.py   →   valorisation.py   →   sql.py   →   PostgreSQL   →   Power BI
   (yfinance)         (pandas)        (ratios)         (DCF)          (SQLAlchemy)
```

Chaque script est indépendant et importe les résultats du précédent, ce qui permet de relancer uniquement l'étape nécessaire (ex. recalculer les ratios sans re-télécharger les données).

## Structure du repo

```
├── extraction.py       # Récupération des données brutes via l'API yfinance
├── nettoyage.py        # Mise en forme, pivot et nettoyage des données financières
├── ratio.py             # Calcul des ratios financiers et du CAGR
├── valorisation.py      # Calcul du WACC et valorisation DCF
├── sql.py                # Connexion PostgreSQL et transfert des DataFrames
├── requetes.sql          # Requêtes d'exploration, scoring et vues SQL
├── Analyse financière et valorisation.pbix        # Dashboard Power BI (screener + comparatif)
├── .env.example           # Modèle des variables de connexion à la base (à dupliquer en .env)
├── .gitignore              # Exclut .env, __pycache__/ et *.pyc du versionnement
└── README.md
```

## Détail des étapes

### 1. Extraction (`extraction.py`)

- Récupération, pour chaque ticker, du bilan (`balance_sheet`), du compte de résultat (`financials`), du tableau de flux de trésorerie (`cashflow`) et des données de marché (`info`) via `yfinance`.
- Les postes comptables sont mappés depuis la nomenclature Yahoo Finance vers des libellés français standardisés (ex. `Total Assets` → `Total Actif`).
- Une fonction de vérification (`verif_donnees`) trace les postes manquants par société, pour identifier les données incomplètes sans faire échouer le script.

**Postes extraits :**
- Bilan : Capitaux Propres, Total Actif, Actif/Passif Circulant, Inventaire, Dette Totale, Dette Fi. long/court, Trésorerie
- Compte de résultat : CA, Résultat Net, EBITDA, Charges d'Intérêts, Résultat Avant Impôt, Impôts
- Flux de trésorerie : Flux Opérationnel, Capex, Flux de Trésorerie Disponible (FCF)

### 2. Nettoyage (`nettoyage.py`)

- Transformation des données brutes (structure imbriquée par ticker/poste/date) en deux tables exploitables :
  - `df_boursier` : une ligne par société (nom, capitalisation, nombre d'actions, prix, bêta)
  - `df` : une ligne par société/date, colonnes = postes financiers (pivot table)
- Suppression des lignes où tous les postes clés (CA, EBITDA, Résultat Net, Total Actif, Capitaux Propres) sont manquants.
- Ajout d'une colonne `annee` extraite de la date, tri par ticker et date.

### 3. Calcul des ratios (`ratio.py`)

| Ratio | Formule |
|---|---|
| Marge nette | Résultat Net / CA |
| Marge EBITDA | EBITDA / CA |
| ROA | Résultat Net / Total Actif |
| ROE | Résultat Net / Capitaux Propres |
| Dette / EBITDA | Dette Totale / EBITDA |
| Dette / Actifs | Dette Totale / Total Actif |
| Gearing | Dette Totale / Capitaux Propres |
| Croissance CA / RN | Variation en % par rapport à l'année précédente (`pct_change`) |
| CAGR du CA | Taux de croissance annuel moyen sur la période disponible |

### 4. Valorisation DCF (`valorisation.py`)

Valorisation par les flux de trésorerie disponibles actualisés, sur la dernière année disponible pour chaque société.

**Hypothèses retenues :**

| Paramètre | Valeur |
|---|---|
| Taux sans risque (Rf) | 4,5 % |
| Rendement de marché attendu (E(Rm)) | 10 % |
| Taux d'imposition (IS) | 25 % |
| Croissance du FCF (5 ans) | 5 % / an |
| Taux de croissance à l'infini (g) | 1 % |
| Horizon de projection | 5 ans |

**Étapes du calcul :**
1. **Coût des fonds propres (Ke)** via le MEDAF : `Rf + Bêta × (E(Rm) − Rf)`
2. **Coût de la dette net d'impôt (Kd net)** : Charges d'intérêts / Dette financière totale, ajusté de l'IS
3. **WACC** : moyenne pondérée de Ke et Kd net par les poids dette/capitaux propres (valeur de marché)
4. **Projection du FCF** sur 5 ans à taux de croissance constant, puis actualisation au WACC
5. **Valeur terminale** (modèle de croissance perpétuelle de Gordon-Shapiro), actualisée
6. **Valeur d'entreprise** = somme des FCF actualisés + valeur terminale actualisée
7. **Valeur des capitaux propres** = Valeur d'entreprise − Dette financière + Trésorerie
8. **Valeur théorique de l'action** = Valeur des capitaux propres / Nombre d'actions
9. **Potentiel** = (Valeur théorique / Prix actuel) − 1

Un statut (`Calculé` / `Données insuffisantes`) est attribué à chaque société selon la disponibilité du WACC.

### 5. Chargement en base (`sql.py`)

- Connexion à PostgreSQL via SQLAlchemy, identifiants gérés par variables d'environnement (`.env`, non versionné).
- Trois tables chargées : `ratios_financiers`, `cagr_ca`, `valorisation_societes`.

### 6. Requêtes SQL (`requetes.sql`)

- **Exploration** : classement des ROE sur l'année la plus récente, ROE moyen par société, filtrage multi-critères (`HAVING`).
- **Scoring** : attribution d'un point par critère dépassé (ROE > 15 %, marge nette > 10 %, dette/actifs < 30 %, ROA > 10 %), score composite et classement (`DENSE_RANK`).
- **Vues** : `derniere_annee` (dernière année disponible par société), `tableau_financier` (scoring sur la dernière année), `screener_societes` (jointure du scoring avec la valorisation DCF) — vue finale consommée par Power BI.

### 7. Dashboard Power BI (`Analyse financière et valorisation.pbix`)

Connecté à la vue `screener_societes`. Contient :
- Un classement des sociétés par score et par rang
- Une comparaison prix de marché vs valeur théorique (potentiel de hausse/baisse)
- Une vue détaillée des ratios par société

#### Page 1 - Vue d'ensemble

![Mon image](Vue-d'ensemble.png)

#### Page 2 - Analyse financière

![Mon image](Analyse-financière.png)

#### Page 3 - Valorisation DCF

![Mon image](Valorisation-DCF.png)

## Limites et améliorations possibles

- Le WACC utilise un bêta et des hypothèses de marché simplifiés (Rf, E(Rm) fixes pour toutes les sociétés) plutôt qu'un bêta sectoriel désendetté/réendetté
- La croissance du FCF est supposée constante sur 5 ans, sans scénario haut/bas
- Le panel est limité à un seul secteur ; une extension multi-sectorielle nécessiterait de pondérer les seuils du score par secteur
- Automatisation possible via une tâche planifiée pour rafraîchir les données à fréquence régulière

## Lancer le projet

```bash
pip install pandas numpy yfinance sqlalchemy psycopg2-binary python-dotenv

# Dupliquer .env.example en .env et renseigner les identifiants PostgreSQL
cp .env.example .env

python extraction.py
python nettoyage.py
python ratio.py
python valorisation.py
python sql.py
```

Puis exécuter `requetes.sql` sur la base pour créer les vues, et ouvrir `Analyse financière et valorisation.pbix` en le connectant à la vue `screener_societes`.
