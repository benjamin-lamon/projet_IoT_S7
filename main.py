from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Beaucoup de ce que j'ai utilisé, notamment sur les pages HTML, provient du tutoriel de w3schools sur Bootstrap5.
# https://www.w3schools.com/bootstrap5/index.php

# https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
import urllib.request, json

import sqlite3, random

# Très probablement trouvé ici https://www.programiz.com/python-programming/datetime/current-datetime
import time
from datetime import datetime

#seed pour la génération aléatoire
random.seed(75005)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ouverture/initialisation de la base de donnees
conn = sqlite3.connect('logement.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

#logement
#créer logement
@app.post("/logement")
async def ajouter_logement(adresse:str,numero_telephone:int,ip:str = "-"):
	c.execute(f'INSERT INTO logement (adresse,numero_telephone,ip) VALUES ("{adresse}",{str(numero_telephone)},"{ip}");')
	conn.commit()
	return "Should be good. Check logement.db" #(f'INSERT INTO logement (adresse,numero_telephone,ip) VALUES ("{adresse}",{str(numero_telephone)},"{ip}");')

#piece
#créer piece 
@app.post("/piece")
async def ajouter_piece(adresse:str,x:int,y:int,z:int,nom:str):
	c.execute(f'INSERT INTO piece (x,y,z,nom,FK_logement) SELECT {x} as x, {y} as y, {z} as z, "{nom}" as nom, (SELECT id FROM logement WHERE adresse = "{adresse}") as FK_logement')
	conn.commit()
	return "Si l'adresse est connue, it should be good. Gheck logement.db"

#typemesure
@app.post("/typeMesure")
async def ajouter_type(unite:str,precision:str,autres_infos:str):
	c.execute(f'INSERT INTO typemesure(unite,precis,autres_infos) VALUES ("{unite}","{precision}","{autres_infos}");')
	conn.commit()
	return "Should be good, check db"

#capteur
@app.post("/capteurs_actionneurs")
async def ajouter_capteur_actionneur(adresse:str,piece:str,type_autres_infos:str,ref:str,port:int,actif:bool):
	c.execute(f'INSERT INTO capteur_actionneur (ref,FK_piece,FK_type,port,actif) SELECT "{ref}" as ref, (SELECT id FROM piece WHERE FK_logement = (SELECT id FROM logement WHERE adresse = "{adresse}") AND nom = "{piece}") as FK_piece, (SELECT id FROM typemesure WHERE autres_infos = "{type_autres_infos}") as FK_type, {port} as port, {int(actif)} as actif;')
	conn.commit()
	return "Check db"

#facture
#creer facture
@app.post("/factures")
async def ajout_facture(adresse:str,typefacture:str,montant:float,unit:str):
	# Très probablement trouvé ici https://www.programiz.com/python-programming/datetime/current-datetime
	strDate = datetime.today().strftime('%Y-%m-01')
	c.execute(f'INSERT INTO facture (FK_logement, typeFact, dateFact, montant, unit) SELECT (SELECT id FROM logement WHERE adresse = "{adresse}") as FK_logement,"{typefacture}" as typeFact,"{strDate}" as dateFact,{montant} as montant, "{unit}" as unit;')
	conn.commit()
	return "check db"

# ---------------------

# Exercice 2.2

@app.get("/ChartByTimeStamp/", response_class=HTMLResponse)
async def test(request: Request):
	ListeTest = []
	c.execute(f'SELECT typefact, SUM(montant) AS totalpaid FROM facture GROUP BY typefact')
	dictFact = c.fetchall()
	for x in dictFact:
		ListeTest.append([x['typefact'],x['totalpaid']])

	return templates.TemplateResponse(
		request=request, name="test.html", context={"ListeTest":ListeTest}
	)

@app.get("/ChartByTimeStamp/{month}/{year}")
async def ChartByMonth(request: Request, month:int, year:int):
	liste = []
	c.execute(f'SELECT typefact, SUM(montant) AS totalpaid FROM facture WHERE dateFact = "{year}-{month}-01" GROUP BY typefact')
	dictFact = c.fetchall()
	for x in dictFact:
		liste.append([x['typefact'],x['totalpaid']])
	return templates.TemplateResponse(
		request=request, name="yes.html", context={"ListeTest":liste,"month":month,"year":year}
	)



# ---------------------

#@app.get("/weather")
#à faire quand l'appid marchera...
# Pour l'instant, on va juste afficher la météo actuelle au bâtiment Esclangon (voir latitude et longitude)
# Ensuite, on affichera les prévisions pour les 4 jours suivants, ce qui donne 5j de météo au total.
# https://api.openweathermap.org/data/2.5/weather?lat=48.84504247986033&lon=2.356997339594278&lang=fr&appid=61888b777e3b6101eba085a2ca0c31a3
# https://api.openweathermap.org/data/2.5/forecast?lat=48.84504247986033&lon=2.356997339594278&lang=fr&appid=61888b777e3b6101eba085a2ca0c31a3
# Enfin, on affichera tout ça sur la page d'accueil et pas sur une page annexe /weather
@app.get("/weather",response_class=HTMLResponse)
async def weather(request: Request):
	# Une fois qu'on sera bon, on déplacera tout ça dans la page d'accueil.
	# Fetch la météo actuelle. On met alors le temps et pourquoi pas la température actuelle
	# 273.15K = 0°C

	# #en local pour testzer
	# with open("weatherFR.json", "r") as f:
	# 	data = json.load(f)

	# Source : https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
	with urllib.request.urlopen("https://api.openweathermap.org/data/2.5/weather?lat=48.84504247986033&lon=2.356997339594278&lang=fr&appid=61888b777e3b6101eba085a2ca0c31a3") as url:
		data = json.load(url)
	
	listTemp = list()
	listDesc = list()
	listIcon = list()
	listDate = list()
	listActs = list()


	listTemp.append(round(float(data['main']['temp'])-273.15,1))
	listDesc.append(data['weather'][0]['description'])
	listIcon.append(str(data['weather'][0]['icon']))
	listDate.append(datetime.today().strftime("%Y-%m-%d"))
	# Afficher si le panneau solaire est activé
	# Afficher si l'arrosage est activé
	if ((data['weather'][0]['main'] == "Clear" or data['weather'][0]['main'] == "Clouds") and data['main']['temp']-273.15 > 30):
		# Activation de l'arrosage et/ou du panneau solaire
		if data['weather'][0]['main'] == "Clear":
			listActs.append("Le panneau solaire et l'arrosage seront activés.\n")
		else:
			listActs.append("L'arrosage sera activé.")
	elif data['weather'][0]['main'] == "Clear":
		listActs.append("Le panneau solaire sera activé en journée.")
	else:
		listActs.append(" ")

	with urllib.request.urlopen("https://api.openweathermap.org/data/2.5/forecast?lat=48.84504247986033&lon=2.356997339594278&lang=fr&appid=61888b777e3b6101eba085a2ca0c31a3") as url:
		data = json.load(url)

	
	for i in range(len(data['list'])):

		# On ne prend que la météo à 12h
		if data['list'][i]['dt_txt'][-8:] == "12:00:00":
			# Si le premier élément date d'ajd, on l'ignore et on passe au suivant. Sinon, c'est probablement celui de demain.
			if data['list'][0]['dt_txt'][:10] == datetime.today().strftime("%Y-%m-%d"):
				# demain est placé en [i=1]
				if i>= 1:
					listTemp.append(round(data['list'][i]['main']['temp']-273.15,1))
					listDesc.append(data['list'][i]['weather'][0]['description'])
					listIcon.append(data['list'][i]['weather'][0]['icon'])
					listDate.append(data['list'][i]['dt_txt'][:10])
					if ((data['list'][i]['weather'][0]['main'] == "Clear" or data['list'][i]['weather'][0]['main'] == "Clouds") and data['list'][i]['main']['temp']-273.15 > 30):
						# Activation de l'arrosage et/ou du panneau solaire
						if data['list'][i]['weather'][0]['main'] == "Clear":
							listActs.append("Le panneau solaire et l'arrosage seront activés.\n")
						else:
							listActs.append("L'arrosage sera activé.")
					elif data['list'][i]['weather'][0]['main'] == "Clear":
						listActs.append("Le panneau solaire sera activé.")
					else:
						listActs.append(" ")
			else:
				# demain est placé en [i=0]
				listTemp.append(round(data['list'][i]['main']['temp']-273.15,1))
				listDesc.append(data['list'][i]['weather'][0]['description'])
				listIcon.append(data['list'][i]['weather'][0]['icon'])
				listDate.append(data['list'][i]['dt_txt'][:10])
				if ((data['list'][i]['weather'][0]['main'] == "Clear" or data['list'][i]['weather'][0]['main'] == "Clouds") and data['list'][i]['main']['temp']-273.15 > 30):
					# Activation de l'arrosage et/ou du panneau solaire
					if data['list'][i]['weather'][0]['main'] == "Clear":
						listActs.append("Le panneau solaire et l'arrosage seront activés.\n")
					else:
						listActs.append("L'arrosage sera activé.")
				elif data['list'][i]['weather'][0]['main'] == "Clear":
					listActs.append("Le panneau solaire sera activé.")
				else:
					listActs.append(" ")


	return templates.TemplateResponse(
		# N.B. Y'a probablement un moyen de raccourcir ça. Peut-être que Jinja2 supporte les listes mais eh, c'est fait et ça fonctionne, good enough for me.
		request = request, name="weather.html",context={"iconAct":listIcon[0], "meteoAct":listDesc[0], "tempAct":listTemp[0], "actAct":listActs[0],
														"iconJ1":listIcon[1], "meteoJ1":listDesc[1], "tempJ1":listTemp[1], "dateJ1":listDate[1], "actJ1":listActs[1],
														"iconJ2":listIcon[2], "meteoJ2":listDesc[2], "tempJ2":listTemp[2], "dateJ2":listDate[2], "actJ2":listActs[2],
														"iconJ3":listIcon[3], "meteoJ3":listDesc[3], "tempJ3":listTemp[3], "dateJ3":listDate[3], "actJ3":listActs[3],
														"iconJ4":listIcon[4], "meteoJ4":listDesc[4], "tempJ4":listTemp[4], "dateJ4":listDate[4], "actJ4":listActs[4]
												  		}
	)


@app.get("/accueil",response_class=HTMLResponse)
# Une fois que la page /weather est conforme, on fait un bête copier-coller pour afficher tout ça sur la page d'accueil.
async def accueil(request: Request):
	# Source : https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
	with urllib.request.urlopen("https://api.openweathermap.org/data/2.5/weather?lat=48.84504247986033&lon=2.356997339594278&lang=fr&appid=61888b777e3b6101eba085a2ca0c31a3") as url:
		data = json.load(url)
	
	listTemp = list()
	listDesc = list()
	listIcon = list()
	listDate = list()
	listActs = list()


	listTemp.append(round(float(data['main']['temp'])-273.15,1))
	listDesc.append(data['weather'][0]['description'])
	listIcon.append(str(data['weather'][0]['icon']))
	listDate.append(datetime.today().strftime("%Y-%m-%d"))
	# Afficher si le panneau solaire est activé
	# Afficher si l'arrosage est activé
	if ((data['weather'][0]['main'] == "Clear" or data['weather'][0]['main'] == "Clouds") and data['main']['temp']-273.15 > 30):
		# Activation de l'arrosage et/ou du panneau solaire
		if data['weather'][0]['main'] == "Clear":
			listActs.append("ℹ️ Le panneau solaire et l'arrosage seront activés.\n")
		else:
			listActs.append("L'arrosage sera activé.")
	elif data['weather'][0]['main'] == "Clear":
		listActs.append("ℹ️ Le panneau solaire sera activé en journée.")
	else:
		listActs.append(" ")

	with urllib.request.urlopen("https://api.openweathermap.org/data/2.5/forecast?lat=48.84504247986033&lon=2.356997339594278&lang=fr&appid=61888b777e3b6101eba085a2ca0c31a3") as url:
		data = json.load(url)

	
	for i in range(len(data['list'])):

		# On ne prend que la météo à 12h
		if data['list'][i]['dt_txt'][-8:] == "12:00:00":
			# Si le premier élément date d'ajd, on l'ignore et on passe au suivant. Sinon, c'est probablement celui de demain.
			if data['list'][0]['dt_txt'][:10] == datetime.today().strftime("%Y-%m-%d"):
				# demain est placé en [i=1]
				if i>= 1:
					listTemp.append(round(data['list'][i]['main']['temp']-273.15,1))
					listDesc.append(data['list'][i]['weather'][0]['description'])
					listIcon.append(data['list'][i]['weather'][0]['icon'])
					listDate.append(data['list'][i]['dt_txt'][:10])
					if ((data['list'][i]['weather'][0]['main'] == "Clear" or data['list'][i]['weather'][0]['main'] == "Clouds") and data['list'][i]['main']['temp']-273.15 > 30):
						# Activation de l'arrosage et/ou du panneau solaire
						if data['list'][i]['weather'][0]['main'] == "Clear":
							listActs.append("ℹ️ Le panneau solaire et l'arrosage seront activés.\n")
						else:
							listActs.append("ℹ️ L'arrosage sera activé.")
					elif data['list'][i]['weather'][0]['main'] == "Clear":
						listActs.append("ℹ️ Le panneau solaire sera activé.")
					else:
						listActs.append(" ")
			else:
				# demain est placé en [i=0]
				listTemp.append(round(data['list'][i]['main']['temp']-273.15,1))
				listDesc.append(data['list'][i]['weather'][0]['description'])
				listIcon.append(data['list'][i]['weather'][0]['icon'])
				listDate.append(data['list'][i]['dt_txt'][:10])
				if ((data['list'][i]['weather'][0]['main'] == "Clear" or data['list'][i]['weather'][0]['main'] == "Clouds") and data['list'][i]['main']['temp']-273.15 > 30):
					# Activation de l'arrosage et/ou du panneau solaire
					if data['list'][i]['weather'][0]['main'] == "Clear":
						listActs.append("ℹ️ Le panneau solaire et l'arrosage seront activés.\n")
					else:
						listActs.append("ℹ️ L'arrosage sera activé.")
				elif data['list'][i]['weather'][0]['main'] == "Clear":
					listActs.append("ℹ️ Le panneau solaire sera activé.")
				else:
					listActs.append(" ")


	return templates.TemplateResponse(
		# N.B. Y'a probablement un moyen de raccourcir ça. Peut-être que Jinja2 supporte les listes mais eh, c'est fait et ça fonctionne, good enough for me.
		request = request, name="accueil.html",context={"iconAct":listIcon[0], "meteoAct":listDesc[0], "tempAct":listTemp[0], "actAct":listActs[0],
														"iconJ1":listIcon[1], "meteoJ1":listDesc[1], "tempJ1":listTemp[1], "dateJ1":listDate[1], "actJ1":listActs[1],
														"iconJ2":listIcon[2], "meteoJ2":listDesc[2], "tempJ2":listTemp[2], "dateJ2":listDate[2], "actJ2":listActs[2],
														"iconJ3":listIcon[3], "meteoJ3":listDesc[3], "tempJ3":listTemp[3], "dateJ3":listDate[3], "actJ3":listActs[3],
														"iconJ4":listIcon[4], "meteoJ4":listDesc[4], "tempJ4":listTemp[4], "dateJ4":listDate[4], "actJ4":listActs[4]
												  		}
	)




@app.get("/consommation",response_class=HTMLResponse)
async def consommation(request: Request):
	ListeAnnee = []
	ListeMois = []
	
	#ça va nous être utile pour le titre du graphique
	AnneeActuelle = datetime.today().strftime('%Y')
	MoisActuel = datetime.today().strftime('%m-%Y')
	Entete = ['Type','Consommé']

	#fetch factures de l'année actuelle
	c.execute(f'SELECT typefact, SUM(montant) AS totalcons FROM facture WHERE strftime("%Y", dateFact) = strftime("%Y", DATE("now")) GROUP BY typefact')
	dictFactA = c.fetchall()
	for x in dictFactA:
		ListeAnnee.append([x['typefact'],x['totalcons']])
	if len(ListeAnnee) == 0:
		ListeAnnee.append(['Pas de facture enregistrée cette année',0])

	#fetch factures du mois actuel
	c.execute(f'SELECT typefact, SUM(montant) AS totalcons FROM facture WHERE strftime("%m", dateFact) = strftime("%m", DATE("now")) GROUP BY typefact')
	dictFactM = c.fetchall()
	for x in dictFactM:
		ListeMois.append([x['typefact'],x['totalcons']])
	if len(ListeMois) == 0:
		ListeMois.append(['Pas de facture enregistrée ce mois-ci',0])

	return templates.TemplateResponse(
		request = request, name="consommation.html",context={"AnneeActuelle":AnneeActuelle,"MoisActuel":MoisActuel,"Entete":Entete,"ListeAnnee":ListeAnnee,"ListeMois":ListeMois}
	)

@app.get("/capteurs",response_class=HTMLResponse)
async def capteurs(request: Request, toggleDevice: int | None = None):
	listeData = list()
	# Source de la reqête : https://chatgpt.com/share/676ecc31-0428-8006-8468-ffcd27e0defe
	c.execute('SELECT capteur_actionneur.id, capteur_actionneur.ref, capteur_actionneur.port, capteur_actionneur.date_ajout, piece.nom AS nom_piece, typemesure.autres_infos, capteur_actionneur.actif, logement.adresse AS adresse_logement FROM capteur_actionneur JOIN piece ON capteur_actionneur.FK_piece = piece.id JOIN typemesure ON capteur_actionneur.FK_type = typemesure.id JOIN logement ON piece.FK_logement = logement.id;')
	data = c.fetchall()
	for x in data:
		listeData.append([x['ref'],x['port'],x['date_ajout'],x['nom_piece'],x['autres_infos'],x['actif'],x['id'],x['adresse_logement']])
	if toggleDevice:
		c.execute(f'SELECT actif FROM capteur_actionneur WHERE id = {toggleDevice};')
		# fetch la réponse
		resp = c.fetchone()
		# Si le device est actif, on le désac et vice-versa
		if resp['actif'] == 1:
			c.execute(f'UPDATE capteur_actionneur SET actif = 0 WHERE id = {toggleDevice};')
			conn.commit()
			time.sleep(0.1)
			# Sources :	- https://github.com/encode/starlette/blob/master/docs/responses.md#redirectresponse
			# 			- https://fastapi.tiangolo.com/advanced/custom-response/#redirectresponse
			return RedirectResponse(url="/capteurs")
		else:
			c.execute(f'UPDATE capteur_actionneur SET actif = 1 WHERE id = {toggleDevice};')
			conn.commit()
			time.sleep(0.1)
			return RedirectResponse(url="/capteurs")
	return templates.TemplateResponse(
		request = request, name="capteurs.html",context={"listeData":listeData}
	)


@app.get("/economies",response_class=HTMLResponse)
# Même chose que consommation mais avec un pourcentage en moins comme sur Waze ?
async def economies(request: Request):
	#Copier-coller de "consommation", à un facteur près (voir boucle "for").
	#Pareil pour le HTML, y'a un petit changement mais pas grand chose de plus.
	ListeAnnee = []
	ListeMois = []
	
	AnneeActuelle = datetime.today().strftime('%Y')
	MoisActuel = datetime.today().strftime('%m-%Y')
	Entete = ['Type','Économisé']

	#fetch factures de l'année actuelle
	c.execute(f'SELECT typefact, SUM(montant) AS totalcons FROM facture WHERE strftime("%Y", dateFact) = strftime("%Y", DATE("now")) GROUP BY typefact')
	dictFactA = c.fetchall()
	for x in dictFactA:
		ListeAnnee.append([x['typefact'],0.11*x['totalcons']])
	if len(ListeAnnee) == 0:
		ListeAnnee.append(['Pas de facture enregistrée cette année',0])

	#fetch factures du mois actuel
	c.execute(f'SELECT typefact, SUM(montant) AS totalcons FROM facture WHERE strftime("%m", dateFact) = strftime("%m", DATE("now")) GROUP BY typefact')
	dictFactM = c.fetchall()
	for x in dictFactM:
		ListeMois.append([x['typefact'],0.11*x['totalcons']])
	if len(ListeMois) == 0:
		ListeMois.append(['Pas de facture enregistrée ce mois-ci',0])
	return templates.TemplateResponse(
		request = request, name="economies.html",context={"AnneeActuelle":AnneeActuelle,"MoisActuel":MoisActuel,"Entete":Entete,"ListeAnnee":ListeAnnee,"ListeMois":ListeMois})

@app.get("/configuration",response_class=HTMLResponse)
# Page pour activer ou non l'arrosage, sur quelle énergie on est (typiquement, panneaux solaires ou EDF...)
# Faire une autre table dans la base de données ?
async def configuration(request: Request, toggleFunc: int | None = None):
	data = list()
	c.execute('SELECT fonction.nom, fonction.actif, logement.adresse AS logement, fonction.id FROM fonction JOIN logement ON fonction.FK_logement = logement.id;')
	fetched = c.fetchall()
	for x in fetched:
		data.append([x['nom'],x['actif'],x['logement'],x['id']])
	
	logements = list()
	c.execute('SELECT adresse, numero_telephone, ip, date_insertion FROM logement;')
	fetched = c.fetchall()
	for x in fetched:
		logements.append([x['adresse'],x['numero_telephone'],x['ip'],x['date_insertion']])

	if toggleFunc:
		c.execute(f'SELECT actif FROM fonction WHERE id = {toggleFunc};')
		# fetch la réponse
		resp = c.fetchone()
		if resp['actif'] == 1:
			c.execute(f'UPDATE fonction SET actif = 0 WHERE id = {toggleFunc};')
			conn.commit()
			time.sleep(0.1)
			return RedirectResponse(url="/configuration")

		else:
			c.execute(f'UPDATE fonction SET actif = 1 WHERE id = {toggleFunc};')
			conn.commit()
			time.sleep(0.1)
			return RedirectResponse(url="/configuration")
	return templates.TemplateResponse(
		request = request, name="configuration.html",context={'data':data, 'logements':logements}
	)



@app.get("/testArgsNone")
async def testArgsNone(Mendatory:int, Superficial: int | None = None):
	if Superficial:
		return "defined superficial"
	else:
		return "undefined superficial"


#TODO :	- fix consommation
#		DONE
#		- economies
#		DONE
#		- configuration
#			-> Paramètres utilisateur (Quels sont les logements) (Ajouter un logement ?)
#			-> Ajout de capteurs/actionneurs + METTRE L'ADRESSE SUR L'EMPLACEMENT
#			-> autre ?

# Source : https://eugeneyan.com/writing/how-to-set-up-html-app-with-fastapi-jinja-forms-templates/
# Je n'ai pas réussi à tout faire sur une page, je vais essayer de faire sur plusieurs...

# Référence et adresse
@app.get("/AjoutCapteur1",response_class=HTMLResponse)
async def form_post1(request: Request):
	listeAdresses = []
	c.execute('SELECT adresse FROM logement')
	fetched = c.fetchall()
	for x in fetched:
		listeAdresses.append(x['adresse'])
	result = "Saisissez les informations."
	return templates.TemplateResponse('ajoutCap1.html', context={'request': request, 'result': result, 'listeAdresses':listeAdresses})


@app.post("/AjoutCapteur1",response_class=HTMLResponse)
#Pour une raison que j'ignore, lorsque je change le nom de la variable "num" (en mettant le même dans le champ "name" sur ajoutCap1.html), j'ai une erreur 422...
async def form_post1(request: Request, num: str = Form(...), sellist1: list = Form(...) ):
	result = f'Référence : {num}. Adresse : {sellist1[0]}.'
	return templates.TemplateResponse('ajoutCap1.html', context={'request': request, 'result': result, 'adresse':sellist1[0], 'num':num})


# ---------------------

#piece
@app.get("/AjoutCapteur2",response_class=HTMLResponse)
async def form_post2(request: Request, adresse:str,reference:str):
	listePieces = []	
	#requete pour fetch les pieces
	c.execute(f'SELECT piece.nom FROM piece JOIN logement ON piece.FK_logement = logement.id WHERE logement.adresse = "{adresse}"')	
	fetched = c.fetchall()
	for x in fetched:
		listePieces.append(x['nom'])
	result = f"Saisissez les informations."
	return templates.TemplateResponse('ajoutCap2.html', context={'request': request, 'result': result, 'listePieces':listePieces})



@app.post("/AjoutCapteur2",response_class=HTMLResponse)
async def form_post2(request: Request, adresse:str, reference:str, sellist1: list = Form(...)):
	result = f'Référence : {reference}. Adresse : {adresse}. Piece : {sellist1[0]}.'
	return templates.TemplateResponse('ajoutCap2.html', context={'request': request, 'result': result, 'ref':reference, 'addr':adresse, 'piece':sellist1[0]})

# ---------------------

#type de mesure
@app.get("/AjoutCapteur3",response_class=HTMLResponse)
async def form_post3(request: Request, adresse:str,reference:str,piece:str):
	listeTypes = []	
	#requete pour fetch les types
	c.execute(f'SELECT autres_infos FROM typemesure')

	fetched = c.fetchall()
	for x in fetched:
		listeTypes.append(x['autres_infos'])

	result = f"Saisissez les informations."
	return templates.TemplateResponse('ajoutCap3.html', context={'request': request, 'result': result, 'listeTypes':listeTypes})



@app.post("/AjoutCapteur3",response_class=HTMLResponse)
async def form_post3(request: Request, adresse:str, reference:str,piece:str, sellist1: list = Form(...)):
	port = random.randrange(1025,10000)
	ok = False

	listePorts = list()
	c.execute(f'SELECT port FROM capteur_actionneur')
	fetched = c.fetchall()
	for x in fetched:
		listePorts.append(x['port'])

	while not(ok):
		ok = True				#On sort normalement de la boucle à la prochaine itération
		for x in listePorts:
			if x == port:		#...sauf si le port est déjà utilisé.
				ok = False
				port = random.randrange(1025,10000)

	result = f'Référence : {reference}. Adresse : {adresse}. Piece : {piece}. Type de mesure: {sellist1[0]}. Port : {port}.'
	return templates.TemplateResponse('ajoutCap3.html', context={'request': request, 'result': result, 'ref':reference, 'addr':adresse, 'piece':piece, 'typemesure':sellist1[0], 'port':port})

# ---------------------


@app.get("/AjoutCapteur4",response_class=HTMLResponse)
async def form_post4(request: Request, adresse:str, piece:str, type_autres_infos:str, ref:str, port:int):
	c.execute(f'INSERT INTO capteur_actionneur (ref,FK_piece,FK_type,port,actif) SELECT "{ref}" as ref, (SELECT id FROM piece WHERE FK_logement = (SELECT id FROM logement WHERE adresse = "{adresse}") AND nom = "{piece}") as FK_piece, (SELECT id FROM typemesure WHERE autres_infos = "{type_autres_infos}") as FK_type, {port} as port, 0 as actif;')
	conn.commit()
	result = f'Référence : {ref}. Adresse : {adresse}. Piece : {piece}. Type de mesure: {type_autres_infos}. Port : {port}.'
	msg = f'Le capteur {ref} a été ajouté. Vous pouvez aller sur la page "Capteurs/Actionneurs" pour l\'activer'
	return templates.TemplateResponse('ajoutCap4.html', context={'request': request, 'result': result, 'ref':ref, 'addr':adresse, 'piece':piece, 'typemesure':type_autres_infos, 'port':port, 'msg':msg})

# ---------------------

#Redirection automatique vers la page d'accueil
@app.get("/",response_class=HTMLResponse)
async def redirection(request: Request):
	return RedirectResponse(url="/accueil")
