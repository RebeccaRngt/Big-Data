import sqlite3
import pandas as pd
from ydata_profiling import ProfileReport

print("Connexion à la base de données...")
connexion = sqlite3.connect("base_tp.sqlite")

requete = """
SELECT 
    p.age,
    p.genre,
    pr.date_prise,
    pr.posologie,
    pr.duree,
    m.forme,
    pres.tauxRembt,
    pres.prixPublic
FROM Prescrire pr
JOIN Patients p ON pr.idfPatient = p.idfPatient
JOIN Medicaments m ON pr.idfMedic = m.idfMedic
LEFT JOIN Presentations pres ON m.idfMedic = pres.idfMedic;
"""

print("Extraction des données...")
df = pd.read_sql_query(requete, connexion)
connexion.close()

print(f"-> {len(df)} lignes extraites.")
print("Génération du rapport avec ydata-profiling en cours...")

# minimal=True est indispensable pour éviter que le calcul ne freeze sur 90 000 lignes
profile = ProfileReport(df, title="Rapport de Profilage - Données Cibles", minimal=True)
profile.to_file("profiling_report.html")

print("Fichier 'profiling_report.html' généré avec succès.")