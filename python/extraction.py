# IMPORTATIONS

import numpy as np
import yfinance as yf

# FONCTIONS 

def extraire_donnees(ticker):
    stock = yf.Ticker(ticker)
    
    bl = stock.balance_sheet
    cr = stock.financials
    cf = stock.cashflow

    info = stock.info

    nom_societe = info.get('shortName', np.nan)
    cap_bours = info.get('marketCap', np.nan)
    nb_act = info.get('sharesOutstanding', np.nan)
    p_actuel = info.get('currentPrice', np.nan)
    beta = info.get('beta', np.nan)

    info_societe = {"ticker": ticker, 
    "nom_societe": nom_societe, 
    "cap_bours": cap_bours, 
    "nb_act": nb_act, 
    "p_actuel": p_actuel, 
    "beta": beta
    }
    
    return bl, cr, cf, info_societe

def verif_donnees(df, nom_poste):
    if nom_poste in df.index:
        return df.loc[nom_poste], True
    else:
        return np.nan, False

def extraction_bilan(bl):
    donnees_bilan = {}
    donnees_bilan_manquantes = []

    postes_bilan = {"Capitaux Propres": "Stockholders Equity",
    "Total Actif": "Total Assets",
    "Actif Circulant": "Current Assets",
    "Inventaire": "Inventory",
    "Passif Circulant": "Current Liabilities",
    "Dette Totale": "Total Debt",
    "Dette Fi. long": "Long Term Debt",
    "Dette Fi. court": "Current Debt",
    "Tréso": "Cash Cash Equivalents And Short Term Investments"}

    for nom_poste, nom_yahoo in postes_bilan.items():
        valeur, existe = verif_donnees(bl, nom_yahoo)
        if existe:
            donnees_bilan[nom_poste] = valeur
        else:
            donnees_bilan_manquantes.append(nom_poste)

    return donnees_bilan, donnees_bilan_manquantes

def extraction_compte_resultat(cr):
    donnees_cr = {}
    donnees_cr_manquantes = []

    postes_cr = {"CA":"Total Revenue",
    "Resultat Net": "Net Income",
    "EBITDA": "EBITDA", 
    "Charges d'Interets": "Interest Expense", 
    "Resultat Avant Impot": "Income Before Tax", 
    "Impots": "Income Tax Expense"
    }

    for nom_poste, nom_yahoo in postes_cr.items():
        valeur, existe = verif_donnees(cr, nom_yahoo)
        if existe:
            donnees_cr[nom_poste] = valeur
        else:
            donnees_cr_manquantes.append(nom_poste)

    return donnees_cr, donnees_cr_manquantes

def extraction_flux_tresorerie(cf):
    donnees_cf = {}
    donnees_cf_manquantes = []

    postes_cf = {"Flux de Trésorerie Opérationnel": "Operating Cash Flow", 
    "Capex": "Capital Expenditures", 
    "Flux de Trésorerie Disponible": "Free Cash Flow"
    }

    for nom_poste, nom_yahoo in postes_cf.items():
        valeur, existe = verif_donnees(cf, nom_yahoo)
        if existe:
            donnees_cf[nom_poste] = valeur
        else:
            donnees_cf_manquantes.append(nom_poste)

    return donnees_cf, donnees_cf_manquantes

def regroupements_donnees():
    societes = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ADBE", "ORCL", "CRM", "IBM"] 

    donnees_financieres = {}
    donnees_boursiers = {}
    donnees_manquantes = {}

    for societe in societes:
        bl, cr, cf, info_societe = extraire_donnees(societe)
    
        donnees_bilan, donnees_bilan_manquantes = extraction_bilan(bl)
        donnees_cr, donnees_cr_manquantes = extraction_compte_resultat(cr)
        donnees_cf, donnees_cf_manquantes = extraction_flux_tresorerie(cf)

        donnees_financieres[societe] = {**donnees_bilan, **donnees_cr, **donnees_cf}
        donnees_boursiers[societe] = {**info_societe}

        donnees_m = {
            "Bilan": donnees_bilan_manquantes,
            "Compte de Résultat": donnees_cr_manquantes,
            "Flux de Trésorerie": donnees_cf_manquantes
        }
    
        if any(donnees_m.values()):
            donnees_manquantes[societe] = donnees_m

    return donnees_financieres, donnees_boursiers, donnees_manquantes