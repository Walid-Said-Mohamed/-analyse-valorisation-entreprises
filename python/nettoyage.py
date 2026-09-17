# IMPORTATION 

import pandas as pd

from extraction import regroupements_donnees

# IMPORTATION EXTRACTION

donnees_financieres = {}
donnees_boursier = {}
donnees_manquantes = {}

donnees_financieres, donnees_boursier, donnees_manquantes = regroupements_donnees()

# FONCTIONS

def tableau_boursier(donnees_boursier):
    df_boursier = pd.DataFrame(donnees_boursier)

    df_boursier.columns = df_boursier.iloc[0]
    df_boursier = df_boursier[1:].reset_index(drop=True).T.rename(columns={0:"Nom", 1:"Capit. boursière", 2:"Nb d'actions", 3:"Prix actuel", 4:"Beta"})


    return df_boursier

def tableau_financier(donnees_financieres):
    lignes = []

    for ticker, postes in donnees_financieres.items():
        for poste, serie in postes.items():
            for date, montant in serie.items():
                lignes.append({"ticker":ticker, 
                "date":date, 
                "poste":poste, 
                "montant":montant})

    df_financier = pd.DataFrame(lignes)

    df_financier["date"] = pd.to_datetime(df_financier["date"])

    df_financier_complet = df_financier.pivot_table(
        index=["ticker", "date"],
        columns="poste",
        values="montant").reset_index()

    return df_financier_complet

df = tableau_financier(donnees_financieres)
df_boursier = tableau_boursier(donnees_boursier)

postes_importants = [
    "CA",
    "EBITDA",
    "Resultat Net",
    "Total Actif",
    "Capitaux Propres"]

lignes_a_supprimer = df[df[postes_importants].isna().all(axis=1)]

df = df.drop(lignes_a_supprimer.index).reset_index(drop=True)

df["annee"] = df["date"].dt.year

df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

print("\nDataframe boursier final :")

print(df_boursier)


print("\nDataframe financier final :")

print(df)

