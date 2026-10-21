import datetime
import random
import sqlite3
import pandas as pd


NOM_BASE = "base_tp.sqlite"
FICHIER_PREUVE = "preuve_chargement_cible.txt"

connexion = sqlite3.connect(NOM_BASE)
curseur = connexion.cursor()


# 1. Chargement de la table 'Patients'

df_patients_raw = pd.read_sql_query(
    "SELECT * FROM brute_Healthcare_data", connexion
)

df_patients = pd.DataFrame(
    {
        "idfPatient": range(1, len(df_patients_raw) + 1),
        "prenom": df_patients_raw["first_name"].astype(str).str.strip(),
        "nom": df_patients_raw["last_name"].astype(str).str.strip(),
        "age": pd.to_numeric(df_patients_raw["age"], errors="coerce").fillna(0).astype(int),
        "genre": df_patients_raw["gender"].astype(str).str.strip(),
        "mail": df_patients_raw["email"].astype(str).str.strip(),
    }
)

df_patients.to_sql("Patients", connexion, if_exists="append", index=False)


# 2. Chargement de la table 'Groupes'

sql_groupes = """
INSERT OR IGNORE INTO Groupes (idfGroupe, libelle)
SELECT DISTINCT 
    CAST(idfGroupe AS INTEGER), 
    TRIM(libelle)
FROM brute_CIS_GENER
WHERE idfGroupe IS NOT NULL AND idfGroupe != '';
"""
curseur.execute(sql_groupes)
connexion.commit()
nb_groupes = curseur.execute("SELECT count(*) FROM Groupes;").fetchone()[0]


# 3. Chargement de la table 'Medicaments'

sql_medics = """
INSERT OR IGNORE INTO Medicaments (idfMedic, denomination, forme, statutAMM, dateAMM, noautorisation, idfGroupe)
SELECT 
    CAST(b.codeCIS AS INTEGER),
    TRIM(b.denomination),
    TRIM(b.forme),
    TRIM(b.statutAMM),
    TRIM(b.dateAMM),
    TRIM(b.numero_autorisation_europeenne),
    CAST(g.idfGroupe AS INTEGER)
FROM brute_CIS_bdpm b
LEFT JOIN brute_CIS_GENER g ON b.codeCIS = g.codeCIS;
"""
curseur.execute(sql_medics)
connexion.commit()
nb_medics = curseur.execute("SELECT count(*) FROM Medicaments;").fetchone()[0]


# 4. Chargement de la table 'Presentations'

sql_presentations = """
INSERT OR IGNORE INTO Presentations (idfPresentation, libelle, statutADM, dateCom, tauxRembt, prixMedic, prixPublic, idfMedic)
SELECT 
    CAST(codeCIP7 AS INTEGER),
    TRIM(libelle),
    TRIM(statutADM),
    TRIM(dateCom),
    CAST(REPLACE(tauxRembt, '%', '') AS REAL),
    CAST(REPLACE(prixMedic, ',', '.') AS REAL),
    CAST(REPLACE(prixPublic, ',', '.') AS REAL),
    CAST(codeCIS AS INTEGER)
FROM brute_CIS_CIP
WHERE codeCIP7 IS NOT NULL AND codeCIP7 != '';
"""
curseur.execute(sql_presentations)
connexion.commit()
nb_pres = curseur.execute("SELECT count(*) FROM Presentations;").fetchone()[0]


# 5. Chargement de 'Substances' et 'Composer'

df_compo = pd.read_sql_query("SELECT * FROM brute_CIS_COMPO", connexion)

# Extraction des substances uniques
df_substances_uniques = df_compo[
    ["denomination", "dosage", "refDosage"]
].drop_duplicates().reset_index(drop=True)

df_substances_uniques["idfSubstance"] = range(1, len(df_substances_uniques) + 1)

# Insertion des substances uniques
df_substances_cible = df_substances_uniques[
    ["idfSubstance", "denomination", "dosage", "refDosage"]
]
df_substances_cible.to_sql("Substances", connexion, if_exists="append", index=False)


# Table de liaison Composer
df_composer = df_compo.merge(
    df_substances_uniques, on=["denomination", "dosage", "refDosage"]
)
df_composer_cible = df_composer[["codeCIS", "idfSubstance"]].drop_duplicates()
df_composer_cible.columns = ["idfMedic", "idfSubstance"]
df_composer_cible["idfMedic"] = df_composer_cible["idfMedic"].astype(int)

df_composer_cible.to_sql("Composer", connexion, if_exists="append", index=False)


# 6. Génération aléatoire de la table 'Prescrire'

patients_ids = [row[0] for row in curseur.execute("SELECT idfPatient FROM Patients;").fetchall()]
medics_ids = [row[0] for row in curseur.execute("SELECT idfMedic FROM Medicaments;").fetchall()]

date_debut = datetime.date(2025, 1, 1)
date_fin = datetime.date.today()
ecart_jours = max(1, (date_fin - date_debut).days)

lignes_prescriptions = []

for id_pat in patients_ids:
    # 1 à 10 médicaments par patient
    nb_medics = random.randint(1, min(10, len(medics_ids)))
    medics_choisis = random.sample(medics_ids, nb_medics)

    for id_m in medics_choisis:
        jours_alea = random.randint(0, ecart_jours)
        date_prise = str(date_debut + datetime.timedelta(days=jours_alea))
        posologie = random.randint(1, 5)
        duree = random.randint(1, 30)

        lignes_prescriptions.append((id_pat, id_m, date_prise, posologie, duree))

curseur.executemany(
    "INSERT OR IGNORE INTO Prescrire (idfPatient, idfMedic, date_prise, posologie, duree) VALUES (?, ?, ?, ?, ?);",
    lignes_prescriptions,
)
connexion.commit()



# 7. Génération de la preuve de chargement

tables_cibles = [
    "Patients",
    "Groupes",
    "Medicaments",
    "Presentations",
    "Substances",
    "Composer",
    "Prescrire",
]

lignes_fichier = []

for table in tables_cibles:
    nb = curseur.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    lignes_fichier.append(f"{table} : {nb} (OK)")

contenu = "\n".join(lignes_fichier) + "\n"

with open("preuve_chargement_cible.txt", "w", encoding="utf-8") as f:
    f.write(contenu)

print("\nRésultat")
print(contenu)
connexion.close()