import json
import sqlite3

DATABASE_FILE = "base_tp.sqlite"
LIMIT_RECORDS = 5000


def exporter_medicaments(cur):

    # 1. Récupération des médicaments et de leur groupe
    cur.execute(f"""
        SELECT 
            m.idfMedic, 
            m.denomination, 
            m.forme, 
            m.statutAMM, 
            m.dateAMM,
            g.idfGroupe, 
            g.libelle AS libelleGroupe
        FROM Medicaments m
        LEFT JOIN Groupes g ON m.idfGroupe = g.idfGroupe
        LIMIT {LIMIT_RECORDS};
    """)
    medicaments_rows = cur.fetchall()

    medicaments_dict = {}
    for row in medicaments_rows:
        idf_medic, denom, forme, statut, date_amm, idf_grp, lib_grp = row
        medicaments_dict[idf_medic] = {
            "_id": idf_medic,
            "denomination": denom,
            "forme": forme,
            "statutAMM": statut,
            "dateAMM": date_amm,
            "groupe": (
                {"idfGroupe": idf_grp, "libelle": lib_grp}
                if idf_grp is not None
                else None
            ),
            "substances": [],
            "presentations": [],
        }

    liste_idf = list(medicaments_dict.keys())
    if not liste_idf:
        print("Aucun médicament trouvé.")
        return

    placeholders = ",".join("?" for _ in liste_idf)

    # 2. Récupération et imbrication des substances (via idfSubstance)
    cur.execute(
        f"""
        SELECT 
            c.idfMedic, 
            s.denomination, 
            s.dosage
        FROM Composer c
        JOIN Substances s ON c.idfSubstance = s.idfSubstance
        WHERE c.idfMedic IN ({placeholders});
    """,
        liste_idf,
    )
    for row in cur.fetchall():
        idf_medic, denom_sub, dosage = row
        if idf_medic in medicaments_dict:
            medicaments_dict[idf_medic]["substances"].append(
                {"denomination": denom_sub, "dosage": dosage}
            )

    # 3. Récupération et imbrication des présentations
    cur.execute(
        f"""
        SELECT 
            idfMedic, 
            idfPresentation, 
            libelle, 
            statutADM, 
            tauxRembt, 
            prixPublic
        FROM Presentations
        WHERE idfMedic IN ({placeholders});
    """,
        liste_idf,
    )
    for row in cur.fetchall():
        idf_medic, idf_pres, libelle, statut, taux, prix = row
        if idf_medic in medicaments_dict:
            medicaments_dict[idf_medic]["presentations"].append(
                {
                    "idfPresentation": idf_pres,
                    "libelle": libelle,
                    "statutADM": statut,
                    "tauxRembt": taux,
                    "prixPublic": prix,
                }
            )

    with open("medicaments.json", "w", encoding="utf-8") as f:
        json.dump(
            list(medicaments_dict.values()), f, ensure_ascii=False, indent=2
        )
    print(
        f"{len(medicaments_dict)} médicaments exportés dans"
        " 'medicaments.json'"
    )


def exporter_patients(cur):

    # 1. Récupération des patients
    cur.execute(f"""
        SELECT idfPatient, nom, prenom, age, genre, mail
        FROM Patients
        LIMIT {LIMIT_RECORDS};
    """)
    patients_rows = cur.fetchall()

    patients_dict = {}
    for row in patients_rows:
        idf_pat, nom, prenom, age, genre, mail = row
        patients_dict[idf_pat] = {
            "_id": idf_pat,
            "nom": nom,
            "prenom": prenom,
            "age": age,
            "genre": genre,
            "mail": mail,
            "prescriptions": [],
        }

    liste_idf = list(patients_dict.keys())
    if not liste_idf:
        print("Aucun patient trouvé.")
        return

    placeholders = ",".join("?" for _ in liste_idf)

    # 2. Récupération et imbrication des prescriptions
    cur.execute(
        f"""
        SELECT idfPatient, idfMedic, date_prise, posologie, duree
        FROM Prescrire
        WHERE idfPatient IN ({placeholders});
    """,
        liste_idf,
    )
    for row in cur.fetchall():
        idf_pat, idf_medic, date_prise, posologie, duree = row
        if idf_pat in patients_dict:
            patients_dict[idf_pat]["prescriptions"].append(
                {
                    "idfMedic": idf_medic,
                    "date_prise": date_prise,
                    "posologie": posologie,
                    "duree": duree,
                }
            )

    with open("patients.json", "w", encoding="utf-8") as f:
        json.dump(list(patients_dict.values()), f, ensure_ascii=False, indent=2)
    print(f"{len(patients_dict)} patients exportés dans 'patients.json'")


def main():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        exporter_medicaments(cur)
        exporter_patients(cur)
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Erreur SQLite : {e}")


if __name__ == "__main__":
    main()