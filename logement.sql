-- commandes de destruction des tables
DROP TABLE IF EXISTS typemesure;
DROP TABLE IF EXISTS facture;
DROP TABLE IF EXISTS mesure;
DROP TABLE IF EXISTS capteur_actionneur;
DROP TABLE IF EXISTS piece;
DROP TABLE IF EXISTS logement;
DROP TABLE IF EXISTS fonction;

--Tableaux
-- On va créer des pk à chaque fois. 
-- Techniquement on n'en a pas besoin, peut-être que ça compliquera les choses plus tard, j'espère que non.
CREATE TABLE logement(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	adresse TEXT NOT NULL,
	numero_telephone INTEGER,
	ip TEXT,
	date_insertion DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE piece(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	x INTEGER, --coordonnées (nord-sud)
	y INTEGER, --coordonnées (hauteur)
	z INTEGER, --coordonnées (est-ouest)
	nom TEXT NOT NULL,
	FK_logement INTEGER,
	FOREIGN KEY (FK_logement) REFERENCES logement(id)
	-- nb. les commandes de FK doivent être ajoutées à la fin de CREATE TABLE
	-- CONSTRAINT PK_piece (nom,coords)
);

--plusieurs capts dans une piece. Un capt est dans une piece
--un capteur a un seul type de mesure
--un capteur fait plusieurs mesures
CREATE TABLE capteur_actionneur(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ref TEXT NOT NULL,
	FK_piece INTEGER,
	FK_type INTEGER,
	port INTEGER NOT NULL,
	date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
	--https://stackoverflow.com/questions/843780/store-boolean-value-in-sqlite
	actif BOOLEAN NOT NULL CHECK (actif IN (0, 1)),
	FOREIGN KEY (FK_piece) REFERENCES piece(id),
	FOREIGN KEY (FK_type) REFERENCES typemesure(id)
	-- sinon ça ne marche pas
);

--Un type de mesure peut être associé à plusieurs capteurs. Un capteur mesure avec un seul type.
CREATE TABLE typemesure(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	unite TEXT NOT NULL,
	precis TEXT NOT NULL,
	autres_infos TEXT
);

--Une mesure est faite par un capteur. Un capteur a plusieurs mesures
CREATE TABLE mesure(
	FK_capt_act INTEGER,
	valeur FLOAT NOT NULL,
	date_mesure DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (FK_capt_act) REFERENCES capteur_actionneur(id)
);

--Une facture est associée à un logement. Un logement a plusieurs factures.
CREATE TABLE facture(
	FK_logement INTEGER,
	typeFact TEXT NOT NULL, --eau/gaz/elec...
	dateFact DATE NOT NULL,
	montant FLOAT NOT NULL, --€
	unit TEXT NOT NULL, --volume d'eau, kWh d'élec... p-ê renommer "unité" ?
	FOREIGN KEY (FK_logement) REFERENCES logement(id)
);

CREATE TABLE fonction(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nom TEXT NOT NULL,
	actif BOOLEAN NOT NULL CHECK (actif IN (0, 1)),
	FK_logement INTEGER,
	FOREIGN KEY (FK_logement) REFERENCES logement(id)
);

-- --Relations
-- --À créer si on a des relations N..N. Ici on n'en a pas, donc on ne les crée pas.

-- CREATE TABLE divPiece(

-- );

-- CREATE TABLE estFacture(

-- );

-- CREATE TABLE estAssocieA(

-- );

-- CREATE TABLE mesure(

-- );

-- CREATE TABLE quantifie(

-- );





-- Création d'un logement de 4 pièces
INSERT INTO logement (adresse,numero_telephone,ip) VALUES 
	("82 Rue Nationale 37000",0247613000,"-");

	-- (0,0,1,"salle 1"),
	-- (0,0,0,"comptoir"),
	-- (0,0,2,"salle 2"),
	-- (0,1,0,"salle 3");

INSERT INTO piece (x,y,z,nom,FK_logement) 
	SELECT
		0 as x,
		0 as y,
		1 as z,
		"salle 1" as nom,
    	(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO piece (x,y,z,nom,FK_logement) 
	SELECT
		0 as x,
		0 as y,
		0 as z,
		"comptoir" as nom,
    	(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO piece (x,y,z,nom,FK_logement) 
	SELECT
		0 as x,
		0 as y,
		2 as z,
		"salle 2" as nom,
    	(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO piece (x,y,z,nom,FK_logement) 
	SELECT
		0 as x,
		1 as y,
		0 as z,
		"salle 3" as nom,
    	(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

--Création de 4 types de mesures
INSERT INTO typemesure(unite,precis,autres_infos) VALUES
	("°C", "+/- 1°C", "température"),
	("%", "+/- 5%", "taux d'humidité"),
	("m/s^2", "+/- 1", "accélération"),
	("°", "+/- 5", "gyroscope");




--Création de 2 capteurs
INSERT INTO capteur_actionneur (ref,FK_piece,FK_type,port,actif)
	SELECT
		"Allumez le feu" as ref,
		(SELECT id FROM piece WHERE FK_logement = (SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) AND nom = "salle 3") as FK_piece,
		(SELECT id FROM typemesure WHERE autres_infos = "température") as FK_type,
		69 as port,
		1 as actif;

INSERT INTO capteur_actionneur (ref,FK_piece,FK_type,port,actif)
	SELECT
		"Éteignez le feu" as ref,
		(SELECT id FROM piece WHERE FK_logement = (SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) AND nom = "salle 3") as FK_piece,
		(SELECT id FROM typemesure WHERE autres_infos = "taux d'humidité") as FK_type,
		42 as port,
		1 as actif;


-- 2 mesures par capteur

--Allumez le feu
INSERT INTO mesure (FK_capt_act, valeur)
	SELECT
		(SELECT id FROM capteur_actionneur WHERE ref = "Allumez le feu") as FK_capt_act,
		232.8 as valeur;

INSERT INTO mesure (FK_capt_act, valeur)
	SELECT
		(SELECT id FROM capteur_actionneur WHERE ref = "Allumez le feu") as FK_capt_act,
		1000.0 as valeur;

--Eteignez le feu
INSERT INTO mesure (FK_capt_act, valeur)
	SELECT
		(SELECT id FROM capteur_actionneur WHERE ref = "Éteignez le feu") as FK_capt_act,
		10.0 as valeur;

INSERT INTO mesure (FK_capt_act, valeur)
	SELECT
		(SELECT id FROM capteur_actionneur WHERE ref = "Éteignez le feu") as FK_capt_act,
		20.0 as valeur;


--4 factures

INSERT INTO facture (FK_logement, typeFact, dateFact, montant, unit)
	SELECT
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement,
		"Eau" as typeFact,
		"2024-11-01" as dateFact,
		133.70 as montant,
		"L" as unit;

INSERT INTO facture (FK_logement, typeFact, dateFact, montant, unit)
	SELECT
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement,
		"Electricite" as typeFact,
		"2024-11-01" as dateFact,
		420.0 as montant,
		"kWh" as unit;

INSERT INTO facture (FK_logement, typeFact, dateFact, montant, unit)
	SELECT
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement,
		"Gaz" as typeFact,
		"2024-11-01" as dateFact,
		194.3 as montant,
		"m3" as unit;

INSERT INTO facture (FK_logement, typeFact, dateFact, montant, unit)
	SELECT
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement,
		"Déchets" as typeFact,
		"2024-11-02" as dateFact,
		100.0 as montant,
		"m3" as unit;



INSERT INTO fonction(nom,actif,FK_logement)
	SELECT	
		'Arrosage' as nom,
		0 as actif,
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO fonction(nom,actif,FK_logement)
	SELECT	
		'Panneau solaire' as nom,
		0 as actif,
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO fonction(nom,actif,FK_logement)
	SELECT	
		'Éclairage' as nom,
		1 as actif,
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO fonction(nom,actif,FK_logement)
	SELECT	
		'Humidificateur' as nom,
		1 as actif,
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;

INSERT INTO fonction(nom,actif,FK_logement)
	SELECT	
		'Chauffage' as nom,
		1 as actif,
		(SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement;