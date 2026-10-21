import sqlite3
import pandas as pd

# 1. Définition des colonnes officielles pour chaque fichier sans en-tête

cols_bdpm = [
    "codeCIS",
    "denomination",
    "forme",
    "voies_admin",
    "statutAMM",
    "type_procedure",
    "etat_commercialisation",
    "dateAMM",
    "statutBdm",
    "numero_autorisation_europeenne",
    "titulaires",
    "surveillance_renforcee",
]

cols_cip = [
    "codeCIS",
    "codeCIP7",
    "libelle",
    "statutADM",
    "etat_commercialisation",
    "dateCom",
    "codeCIP13",
    "agrement_collectivites",
    "tauxRembt",
    "prixMedic",
    "prixPublic",
    "indications_remboursement",
]

cols_compo = [
    "codeCIS",
    "designation_element",
    "code_substance",
    "denomination",
    "dosage",
    "refDosage",
    "nature_composant",
    "numero_liaison",
]

cols_gener = [
    "idfGroupe",
    "libelle",
    "codeCIS",
    "type_generique",
    "numero_tri",
]

# 2. Configuration des fichiers

fichiers = {
    "brute_CIS_bdpm": {
        "chemin": "CIS_bdpm.txt",
        "sep": "\t",
        "encoding": "iso-8859-1",
        "header": None,
        "names": cols_bdpm,
    },
    "brute_CIS_CIP": {
        "chemin": "CIS_CIP_bdpm.txt",
        "sep": "\t",
        "encoding": "iso-8859-1",
        "header": None,
        "names": cols_cip,
    },
    "brute_CIS_COMPO": {
        "chemin": "CIS_COMPO_bdpm.txt",
        "sep": "\t",
        "encoding": "iso-8859-1",
        "header": None,
        "names": cols_compo,
    },
    "brute_CIS_GENER": {
        "chemin": "CIS_GENER_bdpm.txt",
        "sep": "\t",
        "encoding": "iso-8859-1",
        "header": None,
        "names": cols_gener,
    },
    "brute_Healthcare_data": {
        "chemin": "Healthcare_data.csv",
        "sep": ",",
        "encoding": "utf-8",
        "header": 0,
        "names": None,
    },
}


# 3. Connexion SQLite

connexion = sqlite3.connect("base_tp.sqlite")


# 4. Lecture et injection dans SQLite

for nom_table, params in fichiers.items():
    print("=" * 60)
    print(f"Chargement de : {params['chemin']}")

    try:
        df = pd.read_csv(
            params["chemin"],
            sep=params["sep"],
            encoding=params["encoding"],
            header=params["header"],
            names=params["names"],
            low_memory=False,
        )
        
        if "codeCIS" in df.columns:
            df["codeCIS"] = df["codeCIS"].astype(str).str.strip()

        print(f"-> {df.shape[0]} lignes insérées.")
        print(f"-> Colonnes : {list(df.columns[:4])}...")

        # Envoi dans SQLite
        df.to_sql(nom_table, connexion, if_exists="replace", index=False)

    except FileNotFoundError:
        print(f"ERREUR : Fichier '{params['chemin']}' introuvable.")
    except Exception as e:
        print(f"ERREUR sur '{params['chemin']}' : {e}")

print("=" * 60)
print("Importation terminée avec succès dans base_tp.sqlite.")


# 5. Vérifications SQL de la cohérence des données

print("\n--- Tests de cohérence en SQL ---")

# Test 1 : Médicaments sans aucune composition répertoriée
req_compo = """
SELECT count(*) AS nb_sans_composition
FROM brute_CIS_bdpm m
LEFT JOIN brute_CIS_COMPO c ON m.codeCIS = c.codeCIS
WHERE c.codeCIS IS NULL;
"""
res_compo = pd.read_sql_query(req_compo, connexion)
print("1. Médicaments orphelins de substance active :")
print(res_compo)

# Test 2 : Présentations orphelines (qui ne figurent pas dans la liste des médicaments)
req_cip = """
SELECT count(*) AS nb_presentations_orphelines
FROM brute_CIS_CIP p
LEFT JOIN brute_CIS_bdpm m ON p.codeCIS = m.codeCIS
WHERE m.codeCIS IS NULL;
"""
res_cip = pd.read_sql_query(req_cip, connexion)
print("\n2. Présentations sans médicament correspondant :")
print(res_cip)

# Test 3 : Médicaments sans aucune boîte / présentation enregistrée
req_medic_sans_cip = """
SELECT count(*) AS nb_medics_sans_presentation
FROM brute_CIS_bdpm m
LEFT JOIN brute_CIS_CIP p ON m.codeCIS = p.codeCIS
WHERE p.codeCIS IS NULL;
"""
res_medic_sans_cip = pd.read_sql_query(req_medic_sans_cip, connexion)
print("\n3. Médicaments sans aucune boîte (CIP) associée :")
print(res_medic_sans_cip)

# Test 4 : Génériques rattachés à un médicament inexistant
req_gener_orphelins = """
SELECT count(*) AS nb_generiques_sans_medicament
FROM brute_CIS_GENER g
LEFT JOIN brute_CIS_bdpm m ON g.codeCIS = m.codeCIS
WHERE m.codeCIS IS NULL;
"""
res_gener_orphelins = pd.read_sql_query(req_gener_orphelins, connexion)
print("\n4. Groupes génériques pointant vers un code CIS introuvable :")
print(res_gener_orphelins)

# Test 5 : Doublons sur le code CIP7 (clé primaire de Présentations)
req_doublons_cip = """
SELECT count(*) AS nb_doublons_codeCIP7
FROM (
    SELECT codeCIP7
    FROM brute_CIS_CIP
    GROUP BY codeCIP7
    HAVING count(*) > 1
);
"""
res_doublons_cip = pd.read_sql_query(req_doublons_cip, connexion)
print("\n5. Doublons détectés sur le code CIP7 :")
print(res_doublons_cip)

# Test 6 : Présentations sans prix ou avec un prix nul / négatif
req_prix_anormaux = """
SELECT count(*) AS nb_prix_manquants_ou_nuls
FROM brute_CIS_CIP
WHERE prixMedic IS NULL 
   OR CAST(REPLACE(prixMedic, ',', '.') AS REAL) <= 0;
"""
res_prix_anormaux = pd.read_sql_query(req_prix_anormaux, connexion)
print("\n6. Présentations sans prix ou avec prix nul / négatif :")
print(res_prix_anormaux)

# Test 7 : Patients avec des âges suspects (< 0 ou > 120 ans)
req_age_suspect = """
SELECT count(*) AS nb_ages_aberrants
FROM brute_Healthcare_data
WHERE age < 0 OR age > 120;
"""
res_age_suspect = pd.read_sql_query(req_age_suspect, connexion)
print("\n7. Patients avec un âge anormal (< 0 ou > 120 ans) :")
print(res_age_suspect)

# Fermeture propre de la base
connexion.close()