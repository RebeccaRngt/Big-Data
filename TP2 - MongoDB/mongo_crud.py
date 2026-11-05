from pymongo import MongoClient


def get_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["TPMongo"]
    return db["medicaments"]


def demonstration_crud():
    medicaments = get_collection()

    # 1. CREATE : Ajouter un nouveau médicament de test
    
    test_id = 99999999
    medicaments.delete_one({"_id": test_id})

    nouveau_medicament = {
        "_id": test_id,
        "denomination": "IBUPROFENE TEST TP 400 mg, comprimé",
        "forme": "comprimé pelliculé",
        "statutAMM": "Autorisation active",
        "dateAMM": "2026-01-15",
        "groupe": {
            "idfGroupe": 999,
            "libelle": "IBUPROFENE 400 mg - COMPRIME PELLICULE",
        },
        "substances": [{"denomination": "IBUPROFENE", "dosage": "400 mg"}],
        "presentations": [
            {
                "idfPresentation": 9999991,
                "libelle": "plaquette thermoformée de 10 comprimés",
                "statutADM": "Présentation active",
                "tauxRembt": 65.0,
                "prixPublic": 2.45,
            }
        ],
    }

    result_insert = medicaments.insert_one(nouveau_medicament)
    print(f"Médicament inséré avec l'ID : {result_insert.inserted_id}")


    # 2. READ : Requête de recherche simple (Recherche des médicaments de forme comprimé)

    print("\n Médicaments de forme comprimé (limité à 3) :")
    filtre_simple = {"forme": {"$regex": "comprimé", "$options": "i"}}
    resultats = medicaments.find(filtre_simple).limit(3)

    for doc in resultats:
        print(f" - ID: {doc['_id']} | Dénomination: {doc.get('denomination')}")

    
    # 3. UPDATE : Mettre à jour le document de test créé
    # Modification du statut AMM et ajout d'un champ 'modifie_le'
    
    filtre_update = {"_id": test_id}
    mise_a_jour = {
        "$set": {
            "statutAMM": "Autorisation modifiée",
            "statut_tp": "Valide et vérifié",
        }
    }

    result_update = medicaments.update_one(filtre_update, mise_a_jour)
    print(
        f"\nDocuments modifiés : {result_update.modified_count} "
        f"pour le médicament ID {test_id}"
    )

    doc_verif = medicaments.find_one({"_id": test_id})
    print(f"Nouveau statut AMM en base : {doc_verif.get('statutAMM')}")

    # 4. DELETE : Supprimer le médicament de test
    result_delete = medicaments.delete_one({"_id": test_id})
    print(
        f"Documents supprimés : {result_delete.deleted_count} "
        f"pour le médicament ID {test_id}"
    )

    doc_supprime = medicaments.find_one({"_id": test_id})
    if doc_supprime is None:
        print("Le document n'existe plus dans la base")



if __name__ == "__main__":
    demonstration_crud()