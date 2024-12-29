import sqlite3, random
import time
from datetime import datetime

#seed pour la génération aléatoire
random.seed(75005)

# ouverture/initialisation de la base de donnee 
conn = sqlite3.connect('logement.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# ---------------------

### Mesures
# Principe : 
# On fait deux mesures, une de température, une d'humidité.
# On attend ensuite 2s, puis on refait une mesure.
# La différence entre les deux mesures doit être alors limitée d'où l'ajout d'intervalles random dans les deuxièmes mesures.

#température
#random chiffre entre 25 et 45
mesureT1 = random.randrange(25,45)
#ajout dans la DB
c.execute(f'INSERT INTO mesure (FK_capt_act, valeur) SELECT (SELECT id FROM capteur_actionneur WHERE ref = "Allumez le feu") as FK_capt_act, {mesureT1} as valeur;')

#Humidité
#random float * 100 pour qu'on ait la valeur en pourcentage. On se limite à une décimale.
mesureH1 = random.random() * 100
mesureH1 = round(mesureH1, 1) #une décimale
#ajout dans la DB
c.execute(f'INSERT INTO mesure (FK_capt_act, valeur) SELECT (SELECT id FROM capteur_actionneur WHERE ref = "Éteignez le feu") as FK_capt_act, {mesureH1} as valeur;')

time.sleep(2)

#temp2: On va dire qu'un intervalle de +/-2°C dans les mesures est acceptable (même si dans l'absolu c'est déjà beaucoup).
mesureT2 = mesureT1 + random.randrange(-2,2)
#ajout dans la DB
c.execute(f'INSERT INTO mesure (FK_capt_act, valeur) SELECT (SELECT id FROM capteur_actionneur WHERE ref = "Allumez le feu") as FK_capt_act, {mesureT2} as valeur;')

#hum2: intervalle de +/- 1.5 %
mesureH2 = round(mesureH1 + random.randrange(-1,1)*random.random()*1.5, 1)
#ajout db
c.execute(f'INSERT INTO mesure (FK_capt_act, valeur) SELECT (SELECT id FROM capteur_actionneur WHERE ref = "Éteignez le feu") as FK_capt_act, {mesureH2} as valeur;')

# ---------------------


### Factures
# On va dire que les factures arrivent le premier du mois
# Et on va dire qu'elles arrivent le premier du mois actuel (tout du moins, celui de l'ordi sur lequel remplissage.py est executé)

strDate = datetime.today().strftime('%Y-%m-01')
montant1 = round(random.randrange(120,140)+random.random()*random.randint(-1,1),2) # [[120;140]] +/- x ∈ [0;1]
montant2 = round(random.randrange(400,440)+random.random()*random.randint(-1,1),2) # [[400;440]] +/- x ∈ [0;1]
montant3 = round(random.randrange(15,75)+random.random()*random.randint(-1,1),2) # [[15;75]] +/- x ∈ [0;1]
montant4 = round(random.randrange(85,110)+random.random()*random.randint(-1,1),2) # [[85;110]] +/- x ∈ [0;1]

#ajout DB
c.execute(f'INSERT INTO facture (FK_logement, typeFact, dateFact, montant, valeur) SELECT (SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement, "Eau" as typeFact, "{strDate}" as dateFact, {montant1} as montant, "L" as valeur;')
c.execute(f'INSERT INTO facture (FK_logement, typeFact, dateFact, montant, valeur) SELECT (SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement, "Electricite" as typeFact, "{strDate}" as dateFact, {montant2} as montant, "kWh" as valeur;')
c.execute(f'INSERT INTO facture (FK_logement, typeFact, dateFact, montant, valeur) SELECT (SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement, "Gaz" as typeFact, "{strDate}" as dateFact, {montant3} as montant, "m3" as valeur;')
c.execute(f'INSERT INTO facture (FK_logement, typeFact, dateFact, montant, valeur) SELECT (SELECT id FROM logement WHERE adresse = "82 Rue Nationale 37000" AND numero_telephone = 0247613000) as FK_logement, "Déchets" as typeFact, "{strDate}" as dateFact, {montant4} as montant, "m3" as valeur;')

# fermeture
conn.commit()
conn.close()
 