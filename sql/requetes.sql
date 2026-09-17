-- EXPLORATION

-- Classement des ROE année récente

SELECT ticker, annee, "ROE"
FROM ratios_financiers
WHERE annee = (SELECT MAX(annee)
from ratios_financiers)
ORDER BY "ROE" DESC
LIMIT 5;

-- ROE moyen

SELECT ticker, AVG("ROE") AS roe_moyen
FROM ratios_financiers
GROUP BY ticker
ORDER BY roe_moyen DESC;

-- Seuils avec Having

SELECT ticker, 
AVG("ROE") AS roe_moyen,
AVG("Marge nette") AS marge_nette_moyenne,
AVG("Dette / Actifs") AS dette_sur_actif_moyen,
AVG("ROA") AS roa_moyen
FROM ratios_financiers
GROUP BY ticker
HAVING AVG("ROE") > 15 
AND AVG("Marge nette") > 10
AND AVG("Dette / Actifs") < 30
AND AVG("ROA") > 10
ORDER BY roe_moyen DESC;

-- DERNIERE ANNEE

-- View des années les plus récentes

CREATE VIEW derniere_annee AS
SELECT ticker, MAX(annee) AS an
FROM ratios_financiers
GROUP BY ticker;

-- Screener récupérant les données de l'année la plus récente

SELECT resultat.ticker, resultat.annee, roe_moyen, marge_nette_moyenne, dette_sur_actif_moyen, roa_moyen, point_roe + point_marge + point_dette + point_roa AS score,
DENSE_RANK() OVER (ORDER BY point_roe + point_marge + point_dette + point_roa DESC, roe_moyen DESC) AS rang
FROM (SELECT ticker, annee, 
	AVG("ROE") AS roe_moyen,
	AVG("Marge nette") AS marge_nette_moyenne,
	AVG("Dette / Actifs") AS dette_sur_actif_moyen,
	AVG("ROA") AS roa_moyen,
	(CASE WHEN AVG("ROE") > 15  THEN 1 ELSE 0 END) AS point_roe,
	(CASE WHEN AVG("Marge nette") > 10 THEN 1 ELSE 0 END) AS point_marge,
	(CASE WHEN AVG("Dette / Actifs") < 30 THEN 1 ELSE 0 END) AS point_dette,
	(CASE WHEN AVG("ROA") > 10 THEN 1 ELSE 0 END) AS point_roa
	FROM ratios_financiers
	GROUP BY ticker, annee) AS resultat
INNER JOIN derniere_annee ON derniere_annee.ticker = resultat.ticker AND derniere_annee.an = resultat.annee

-- SCREENER

-- Calcul d'un socre par rapport aux seuils + classement

SELECT ticker, roe_moyen, marge_nette_moyenne, dette_sur_actif_moyen, roa_moyen, point_roe + point_marge + point_dette + point_roa AS score,
DENSE_RANK() OVER (ORDER BY point_roe + point_marge + point_dette + point_roa DESC, roe_moyen DESC) AS rang
FROM (SELECT ticker, 
	AVG("ROE") AS roe_moyen,
	AVG("Marge nette") AS marge_nette_moyenne,
	AVG("Dette / Actifs") AS dette_sur_actif_moyen,
	AVG("ROA") AS roa_moyen,
	(CASE WHEN AVG("ROE") > 15  THEN 1 ELSE 0 END) AS point_roe,
	(CASE WHEN AVG("Marge nette") > 10 THEN 1 ELSE 0 END) AS point_marge,
	(CASE WHEN AVG("Dette / Actifs") < 30 THEN 1 ELSE 0 END) AS point_dette,
	(CASE WHEN AVG("ROA") > 10 THEN 1 ELSE 0 END) AS point_roa
	FROM ratios_financiers
	GROUP BY ticker) AS resultat

-- VIEWS

-- View du résultat de l'analyse des sociétes par rapport aux indicateurs

CREATE VIEW tableau_financier AS

SELECT resultat.ticker, resultat.annee, roe_moyen, marge_nette_moyenne, dette_sur_actif_moyen, roa_moyen, point_roe + point_marge + point_dette + point_roa AS score,
DENSE_RANK() OVER (ORDER BY point_roe + point_marge + point_dette + point_roa DESC, roe_moyen DESC) AS rang
FROM (SELECT ticker, annee, 
	AVG("ROE") AS roe_moyen,
	AVG("Marge nette") AS marge_nette_moyenne,
	AVG("Dette / Actifs") AS dette_sur_actif_moyen,
	AVG("ROA") AS roa_moyen,
	(CASE WHEN AVG("ROE") > 15  THEN 1 ELSE 0 END) AS point_roe,
	(CASE WHEN AVG("Marge nette") > 10 THEN 1 ELSE 0 END) AS point_marge,
	(CASE WHEN AVG("Dette / Actifs") < 30 THEN 1 ELSE 0 END) AS point_dette,
	(CASE WHEN AVG("ROA") > 10 THEN 1 ELSE 0 END) AS point_roa
	FROM ratios_financiers
	GROUP BY ticker, annee) AS resultat
INNER JOIN derniere_annee ON derniere_annee.ticker = resultat.ticker AND derniere_annee.an = resultat.annee;

-- View tableau financier + données de valorisation 

CREATE VIEW screener_societes AS

SELECT valorisation_societes.ticker, 
"Nom", 
valorisation_societes.annee, 
"Valeur théorique d'une action", 
"Prix actuel", 
"Potentiel",
score,
rang
FROM valorisation_societes
LEFT JOIN tableau_financier ON valorisation_societes.ticker = tableau_financier.ticker
AND valorisation_societes.annee = tableau_financier.annee

-- FINAL POWER BI 

-- Tableau final

SELECT *
FROM screener_societes
ORDER BY rang;