-- 1) Nombre de de patients par genre
SELECT genre, COUNT(*) AS nb_patients
FROM Patients
GROUP BY genre;

-- 2) Nombre de médicaments par forme pharmaceutique
SELECT forme, COUNT(*) AS nb_medicaments
FROM Medicaments
GROUP BY forme
ORDER BY nb_medicaments DESC
LIMIT 5;

-- 3) Top 5 des médicaments les plus prescrits
SELECT idfMedic, COUNT(*) AS nb_prescriptions
FROM Prescrire
GROUP BY idfMedic
ORDER BY nb_prescriptions DESC
LIMIT 5;

-- 4) Top 10 des substances les plus utilisées
SELECT 
    s.denomination AS substance_active,
    COUNT(c.idfMedic) AS nb_medicaments_associes
FROM Substances s
JOIN Composer c ON s.idfSubstance = c.idfSubstance
GROUP BY s.idfSubstance, s.denomination
ORDER BY nb_medicaments_associes DESC
LIMIT 10;

-- 5) Nombre de prescriptions par tranche d'âge
SELECT 
    CASE 
        WHEN p.age < 25 THEN 'Moins de 25 ans'
        WHEN p.age BETWEEN 25 AND 50 THEN '25-50 ans'
        WHEN p.age BETWEEN 51 AND 75 THEN '51-75 ans'
        ELSE 'Plus de 75 ans'
    END AS tranche_age,
    COUNT(*) AS nb_prescriptions,
    ROUND(AVG(pr.posologie), 2) AS posologie_moyenne
FROM Prescrire pr
JOIN Patients p ON pr.idfPatient = p.idfPatient
GROUP BY tranche_age
ORDER BY nb_prescriptions DESC;

-- 6) Top 10 des médicamments contenant le plus de substances
SELECT 
    m.idfMedic,
    m.denomination,
    COUNT(c.idfSubstance) AS nb_substances
FROM Medicaments m
JOIN Composer c ON m.idfMedic = c.idfMedic
GROUP BY m.idfMedic, m.denomination
ORDER BY nb_substances DESC
LIMIT 10;

-- 7) Prix le plus bas, le plus haut et moyen
SELECT 
    MIN(prixPublic) AS prix_min,
    MAX(prixPublic) AS prix_max,
    ROUND(AVG(prixPublic), 2) AS prix_moyen
FROM Presentations
WHERE prixPublic IS NOT NULL;

-- 8) Nombre total de prescriptions
SELECT COUNT(*) AS total_prescriptions
FROM Prescrire;

-- 9) Durée minimale, maximale et moyenne d'une prescription
SELECT 
    MIN(duree) AS duree_min,
    MAX(duree) AS duree_max,
    ROUND(AVG(duree), 1) AS duree_moyenne
FROM Prescrire;

-- 10) Taux de remboursement moyen sur l'ensemble des boîtes
SELECT ROUND(AVG(tauxRembt), 2) AS taux_moyen_remboursement
FROM Presentations
WHERE tauxRembt IS NOT NULL;