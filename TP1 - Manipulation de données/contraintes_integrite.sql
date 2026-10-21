DROP TABLE IF EXISTS Composer;
DROP TABLE IF EXISTS Prescrire;
DROP TABLE IF EXISTS Presentations;
DROP TABLE IF EXISTS Medicaments;
DROP TABLE IF EXISTS Groupes;
DROP TABLE IF EXISTS Substances;
DROP TABLE IF EXISTS Patients;

PRAGMA foreign_keys = ON;


CREATE TABLE Patients (
   idfPatient INTEGER PRIMARY KEY,
   prenom VARCHAR(50) NOT NULL,
   nom VARCHAR(50) NOT NULL,
   age INTEGER CHECK (age >= 0 AND age <= 125),
   genre VARCHAR(50) CHECK (genre IN ('Male', 'Female', 'Other')),
   mail VARCHAR(100)
);


CREATE TABLE Substances (
   idfSubstance INTEGER PRIMARY KEY AUTOINCREMENT,
   denomination VARCHAR(255) NOT NULL,
   dosage VARCHAR(50),
   refDosage VARCHAR(100)
);


CREATE TABLE Groupes (
   idfGroupe INTEGER PRIMARY KEY,
   libelle VARCHAR(255) NOT NULL
);


CREATE TABLE Medicaments (
   idfMedic INTEGER PRIMARY KEY,
   denomination VARCHAR(255) NOT NULL,
   forme VARCHAR(150),
   statutAMM VARCHAR(50),
   dateAMM DATE,
   noautorisation VARCHAR(50),
   idfGroupe INTEGER,
   FOREIGN KEY (idfGroupe) REFERENCES Groupes(idfGroupe) ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE Presentations (
   idfPresentation INTEGER PRIMARY KEY,
   libelle VARCHAR(255) NOT NULL,
   statutADM VARCHAR(50),
   dateCom DATE,
   tauxRembt REAL CHECK (tauxRembt >= 0 AND tauxRembt <= 100),
   prixMedic DECIMAL(10,2) CHECK (prixMedic >= 0),
   prixPublic DECIMAL(10,2) CHECK (prixPublic >= 0),
   idfMedic INTEGER NOT NULL,
   FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Prescrire (
   idfPatient INTEGER NOT NULL,
   idfMedic INTEGER NOT NULL,
   date_prise DATE NOT NULL,
   posologie INTEGER NOT NULL CHECK (posologie BETWEEN 1 AND 5),
   duree INTEGER NOT NULL CHECK (duree BETWEEN 1 AND 30),
   PRIMARY KEY (idfPatient, idfMedic, date_prise),
   FOREIGN KEY (idfPatient) REFERENCES Patients(idfPatient) ON DELETE CASCADE ON UPDATE CASCADE,
   FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Composer (
   idfMedic INTEGER NOT NULL,
   idfSubstance INTEGER NOT NULL,
   PRIMARY KEY (idfMedic, idfSubstance),
   FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic) ON DELETE CASCADE ON UPDATE CASCADE,
   FOREIGN KEY (idfSubstance) REFERENCES Substances(idfSubstance) ON DELETE CASCADE ON UPDATE CASCADE
);