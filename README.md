# Projet d'IoT - Logement éco-responsable

## Avant-propos
On utilise ici SQLite3 sur Python. En principe, SQLite3 est déjà inclus dans Python. Si ce n'est pas le cas, je vous laisse l'installer, probablement avec ```pip install db-sqlite3```. De même, j'utilise ```datetime```, ```random```, ```time```, ```json```, ```urllib.request```, tous en principe déjà inclus dans Python.

De même, il faut installer la librairie FastAPI :``` pip install "fastapi[standard]"```
Ensuite, pour lancer le serveur web, entrez dans le terminal ```fastapi dev main.py```;
Vous trouverez l'ensemble des commandes sur 
```localhost:[port]/docs ```
**N.B.** le port est à vérifier dans le terminal

Vous pouvez alors accéder aussi à l'interface web sur ```localhost:[port]```. Vous serez automatiquement redirigé vers la page d'accueil.

### Protocole à suivre pour le bon fonctionnement du serveur

1 - Créez la base de données. Exécutez ```sqlite3 logement.db<logement.sql```

2 - Lancez le serveur avec la commande ```fastapi dev main.py```

3 - Une fois le serveur lancé, assurez-vous d'exécuter les commandes bash dans curlCommands.txt (vous pouvez utiliser ```bash curlCommands.txt```)

4 - Go to ```http://localhost:[port]```

5 - You're done, enjoy.



## 1 - Base de données
### 1.1 - Spécifications de la base de données
#### Question 1 
Vous trouvrez le modèle relationnel de la base de données dans le fichier .png associé. Il y aura cependant quelques différences étant donné que celui-ci a été fait lors du premier TP. J'ai probablement rajouté quelques champs en plus par-ci par-là.

#### Questions 2 et 3
Dans le fichier logement.sql, vous trouverez les ordres correspondants entre les lignes 1 et 82.

#### Questions 4 à 8
Toujours dans le même fichier, des lignes 110 à 240.

On peut alors créer le fichier de la base de données en utilisant la commande : 
```sqlite3 logement.db<logement.sql```

### 1.2 Remplissage de la base de données
Vous pouvez éxecuter le fichier ```remplissage2.py```. Toutes les explications relatives à la cohérence des données sont en commentaire, à l'exception du champ timestamp pour les mesures car celui-ci est rempli automatiquement.

## 2 - Serveur RESTful
### 2.1 - Exercice 1 : remplissage de la base de données
En ce qui concerne le remplissage de la base de données, les lignes 30 à 70 de ```main.py ``` nous donnent les fonctions qui nous donneront les requêtes pour remplir la base de données en consultant ```localhost:[port]/docs ```. En ce qui concerne la consultation des données, on peut utiliser https://sqliteviewer.app/ pour consulter si ce qu'on a ajouté a bien été pris en compte (en plus d'avoir une présentation plus claire et lisible).

e.g.
```bash
curl -X 'POST' \
  'http://localhost:8000/logement?adresse=8%20Rue%20Cuvier%2075005&numero_telephone=0143254665&ip=-' \
  -H 'accept: application/json' \
  -d ''
```
```bash
curl -X 'POST' \
  'http://localhost:8000/piece?adresse=8%20Rue%20Cuvier%2075005&x=1&y=2&z=3&nom=Salle1' \
  -H 'accept: application/json' \
  -d ''
```
```bash
curl -X 'POST' \
  'http://localhost:8000/typeMesure?unite=Pascal&precision=oui&autres_infos=Pression' \
  -H 'accept: application/json' \
  -d ''
```
```bash
 curl -X 'POST'  \
  'http://localhost:8000/capteurs_actionneurs?adresse=8%20Rue%20Cuvier%2075005&piece=nom&type_autres_infos=Pression&ref=007&port=12&actif=false' \
   -H 'accept: application/json' \
   -d ''
```
```bash
curl -X 'POST' \
  'http://localhost:8000/factures?adresse=8%20Rue%20Cuvier%2075005&typefacture=Gaz&montant=19.43&unit=m3' \
  -H 'accept: application/json' \
  -d ''
```
### 2.1 - Exercice 2 : Serveur Web
Comme dit précédemment, il faut lancer le serveur web ```main.py``` avec FastAPI.

Pour la partie serveur, vous trouverez le code Python à la ligne 70. Pour la partie HTML, il faut se référer aux fichiers ```item.html``` et ```test.html```

Le résultat de cet exercice se trouve sur ```localhost:[port]/ChartByTimeStamp ```. 
De plus, on peut consulter les factures d'un mois précis en se connectant sur ```localhost:[port]/ChartByTimeStamp/[mois]/[année] ```

### 2.3 - Exercice 3 : météo
Partie serveur : trouvable à la ligne 100 + ```localhost:[port]/weather``` (Les prévisions météos sont aussi sur la page d'accueil)
Partie HTML : fichier ```weather.html```

## 3 - HTML/CSS/Javascript
### 1 - Consommation
Ligne 290 dans le code source du serveur. Pour y accéder : ```localhost:[port]/consommation```
Fichier HTML : ```consommation.html```

### 2 - État des capteurs/actionneurs
Ligne 320 dans le code source du serveur. Pour y accéder : ```localhost:[port]/capteurs```
Fichier HTML : ```capteurs.html```

### 3 - Économies réalisées
Ligne 350 dans le code source du serveur. Pour y accéder : ```localhost:[port]/economies```
Fichier HTML : ```economies.html```

### 4 - Configuration
Ligne 380 dans le code source du serveur. Pour y accéder : ```localhost:[port]/configuration```
Fichier HTML : ```configuration.html```
