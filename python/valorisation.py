# IMPORTATIONS

import numpy as np

from nettoyage import df, df_boursier  # isort: skip

# DONNEES

df_derniere_annee = df.sort_values(["ticker", "annee"], ascending= [True, False]).groupby("ticker").head(1).reset_index(drop=True)

df_dcf = df_derniere_annee[["ticker", "annee", "Charges d'Interets", "Dette Fi. long", "Dette Fi. court" ,"Tréso", "Flux de Trésorerie Disponible"]]

df_boursier = df_boursier.reset_index()

df_dcf = df_dcf.merge(df_boursier, on="ticker", how="left")

# HYPOTHESES

hyp = {"Rf":0.045,"E(Rm)":0.10,"IS":0.25, "Croissance FCF":0.05, "g":0.01, "nb an":5}

# CALCUL DU WACC

def calcul_wacc(df_dcf, hyp):

    df_dcf["Dette financière totale"] = df_dcf["Dette Fi. long"].fillna(0) + df_dcf["Dette Fi. court"].fillna(0)

    df_dcf["part_dette"] = df_dcf["Dette financière totale"] / (df_dcf["Dette financière totale"] + df_dcf["Capit. boursière"])
    df_dcf["part_capitaux"] = df_dcf["Capit. boursière"] / (df_dcf["Dette financière totale"] + df_dcf["Capit. boursière"])

    df_dcf["Ke"] = hyp["Rf"] + df_dcf["Beta"] * (hyp["E(Rm)"] - hyp["Rf"])

    df_dcf["Kd"] = abs(df_dcf["Charges d'Interets"])/df_dcf["Dette financière totale"]
    df_dcf["Kdnet"] = df_dcf["Kd"] * (1 - hyp["IS"])
    
    df_dcf["WACC"] = (df_dcf["part_capitaux"] * df_dcf["Ke"]) + (df_dcf["part_dette"] * df_dcf["Kdnet"])
    
    return df_dcf

# CALCUL FCF ACTUALISE

def calcul_dcf(df_dcf, hyp):
    
    df_dcf["Rf"] = hyp["Rf"]
    df_dcf["E(Rm)"] = hyp["E(Rm)"]
    df_dcf["IS"] = hyp["IS"]
    df_dcf["Croissance FCF"] = hyp["Croissance FCF"]
    df_dcf["g"] = hyp["g"]
    df_dcf["nb an"] = hyp["nb an"]

    df_dcf["FCF de départ"] = df_dcf["Flux de Trésorerie Disponible"]        

    df_dcf["FCF1"] = df_dcf["FCF de départ"] * (1 + hyp["Croissance FCF"])
    df_dcf["FCF2"] = df_dcf["FCF1"] * (1 + hyp["Croissance FCF"])
    df_dcf["FCF3"] = df_dcf["FCF2"] * (1 + hyp["Croissance FCF"])
    df_dcf["FCF4"] = df_dcf["FCF3"] * (1 + hyp["Croissance FCF"])
    df_dcf["FCF5"] = df_dcf["FCF4"] * (1 + hyp["Croissance FCF"])


    df_dcf["FCF1 actualisé"] = df_dcf["FCF1"] / (1 + df_dcf["WACC"])**1
    df_dcf["FCF2 actualisé"] = df_dcf["FCF2"] / (1 + df_dcf["WACC"])**2
    df_dcf["FCF3 actualisé"] = df_dcf["FCF3"] / (1 + df_dcf["WACC"])**3
    df_dcf["FCF4 actualisé"] = df_dcf["FCF4"] / (1 + df_dcf["WACC"])**4
    df_dcf["FCF5 actualisé"] = df_dcf["FCF5"] / (1 + df_dcf["WACC"])**5

    df_dcf["Somme des FCF actualisé"] = df_dcf["FCF1 actualisé"] + df_dcf["FCF2 actualisé"] + df_dcf["FCF3 actualisé"] + df_dcf["FCF4 actualisé"] + df_dcf["FCF5 actualisé"]

    df_dcf["VT"] = (df_dcf["FCF5"] * (1+hyp["g"])) / (df_dcf["WACC"] - hyp["g"])
    df_dcf["VT actualisée"] = df_dcf["VT"] / (1 + df_dcf["WACC"])**hyp["nb an"]
    
    df_dcf["Valeur entreprise"] = df_dcf["Somme des FCF actualisé"] + df_dcf["VT actualisée"]

    df_dcf["Valeur des capitaux propres"] = df_dcf["Valeur entreprise"] - df_dcf["Dette financière totale"] + df_dcf["Tréso"]

    df_dcf["Valeur théorique d'une action"] = df_dcf["Valeur des capitaux propres"] / df_dcf["Nb d'actions"]

    df_dcf["Potentiel"] = (df_dcf["Valeur théorique d'une action"]/ df_dcf["Prix actuel"]) - 1

    df_dcf["Statut DCF"] = np.where(df_dcf["WACC"].isna(),"Données insuffisantes","Calculé")

    return df_dcf

wacc = calcul_wacc(df_dcf, hyp)

dcf = calcul_dcf(df_dcf, hyp)

print(df_dcf)
