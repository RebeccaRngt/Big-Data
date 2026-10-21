CREATE TABLE Patients(
   idfPatient INT,
   prenom VARCHAR(50),
   nom VARCHAR(50),
   age INT,
   genre VARCHAR(50),
   mail VARCHAR(50),
   PRIMARY KEY(idfPatient)
);

CREATE TABLE Substances(
   idfSubstance INT,
   denomination VARCHAR(255),
   dosage VARCHAR(50),
   refDosage VARCHAR(100),
   PRIMARY KEY(idfSubstance)
);

CREATE TABLE Groupes(
   idfGroupe INT,
   libelle VARCHAR(255),
   PRIMARY KEY(idfGroupe)
);

CREATE TABLE Medicaments(
   idfMedic INT,
   denomination VARCHAR(255),
   forme VARCHAR(150),
   statutAMM VARCHAR(50),
   dateAMM DATE,
   noautorisation VARCHAR(50),
   idfGroupe INT,
   PRIMARY KEY(idfMedic),
   FOREIGN KEY(idfGroupe) REFERENCES Groupes(idfGroupe)
);

CREATE TABLE Presentations(
   idfPresentation VARCHAR(50),
   libelle VARCHAR(255),
   statutADM VARCHAR(50),
   dateCom DATE,
   tauxRembt REAL,
   prixMedic DECIMAL(10,2),
   prixPublic DECIMAL(10,2),
   idfMedic INT NOT NULL,
   PRIMARY KEY(idfPresentation),
   FOREIGN KEY(idfMedic) REFERENCES Medicaments(idfMedic)
);

CREATE TABLE Prescrire(
   idfPatient INT,
   idfMedic INT,
   date_prise DATE,
   posologie INT,
   duree INT,
   PRIMARY KEY(idfPatient, idfMedic),
   FOREIGN KEY(idfPatient) REFERENCES Patients(idfPatient),
   FOREIGN KEY(idfMedic) REFERENCES Medicaments(idfMedic)
);

CREATE TABLE Composer(
   idfMedic INT,
   idfSubstance INT,
   PRIMARY KEY(idfMedic, idfSubstance),
   FOREIGN KEY(idfMedic) REFERENCES Medicaments(idfMedic),
   FOREIGN KEY(idfSubstance) REFERENCES Substances(idfSubstance)
);