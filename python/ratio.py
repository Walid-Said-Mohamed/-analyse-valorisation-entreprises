# IMPORTATIONS

from nettoyage import df

# FONCTIONS

df_ratios = df.copy()

df_ratios["Marge nette"] = (
    df_ratios["Resultat Net"]
    / df_ratios["CA"]
) * 100

df_ratios["Marge EBITDA"] = (
    df_ratios["EBITDA"]
    / df_ratios["CA"]
) * 100

df_ratios["ROA"] = (
    df_ratios["Resultat Net"]
    / df_ratios["Total Actif"]
) * 100

df_ratios["ROE"] = (
    df_ratios["Resultat Net"]
    / df_ratios["Capitaux Propres"]
) * 100


df_ratios["Dette / EBITDA"] = (
    df_ratios["Dette Totale"]
    / df_ratios["EBITDA"]
)

df_ratios["Dette / Actifs"] = (
    df_ratios["Dette Totale"]
    / df_ratios["Total Actif"]
) * 100

df_ratios["Gearing"] = (
    df_ratios["Dette Totale"]
    / df_ratios["Capitaux Propres"]
) * 100


df_ratios["Croissance CA"] = (
    df_ratios
    .groupby("ticker")["CA"]
    .pct_change()
    * 100
)

df_ratios["Croissance Résultat Net"] = (
    df_ratios
    .groupby("ticker")["Resultat Net"]
    .pct_change()
    * 100
)

def calcul_cagr(groupe):
    groupe = groupe.sort_values("annee")

    valeur_i = groupe["CA"].iloc[0]
    valeur_f = groupe["CA"].iloc[-1]

    nb_an = (groupe["annee"].iloc[-1] - groupe["annee"].iloc[0])

    if valeur_i <= 0 or nb_an == 0:
        return None

    variation = ((valeur_f / valeur_i) ** (1/nb_an) - 1) * 100

    return variation

colonnes_ratios = [
    "Marge nette",
    "Marge EBITDA",
    "ROA",
    "ROE",
    "Dette / EBITDA",
    "Dette / Actifs",
    "Gearing",
    "Croissance CA",
    "Croissance Résultat Net"
]

print("\nRatios calculés :")

print(df_ratios[["ticker", "annee"] + colonnes_ratios])

cagr_ca = (df_ratios.groupby("ticker").apply(calcul_cagr, include_groups=False).reset_index(name="CAGR CA"))

print("\nCAGR du chiffre d'affaires :")

print(cagr_ca)


