# ProjetInfoPI2C
Projet d'informatique ayant pour but de créer une IA pour le jeu abalone.

Le but principal de cet IA est de déterminer le coup le plus intéréssant à jour dans le but de gagner la partie.

## Bibliothèques utilisées : 

Voici une liste des bibliothèques utiliseés dans le cadre du projet et une brève déscription de celle-ci : 
1) 'socket' : Socket est utilisé pour communiquer un message à travers le réseaux. Ce message transite entre réseaux local ou connecté à distance et l'ordinateur avec sa propre connection à celui-ci.
2) 'threading' : Treading permet au programme de lancer de multiples processus en même temps.
3) 'sys' : Sys permet à l'interpréteur d'utiliser certaines variables du programme.
4) 'copy' : Permet d'effectuer une copie de variables.
5) 'time' : Time fournit une multitude de fonctions manipulant le temps.
6) 'sqrt' de 'math' : Permet d'utiliser une fonction réalisant la racine carrée d'un nombre ou d'un chiffre.
7) 'defaultdict' de 'collections' : Est un dictionnaire qui, lorsque la cléf demandée est inexistante, renvoie une valeur par défaut définit à l'avance.
8) 'json' : Elle permet d'utiliser et de communiquer avec des fichiers json.
9) 'random' : Permet d'utiliser des fonctions génératrices de nombre pseudo-aléatoires.

## Subdivision du code : 

1) Game.py : Series d'exceptions nécessaire à la détérmination des coups possibles ainsi qu'au bon déroulement du jeu. 
2) JsonNetwork : Permet la communication réseaux sous format json.
3) IA : Permet de déterminer les meilleurs coups possibles en fonction de l'état du jeu.
4) Client : Permet de s'inscrire et de communiquer au serveur gérant les parties.


## Démarrage de l'IA : 
Tapez la ligne de commande dans un terminal : 

python .\clientfinal.py port -name=nom_désiré

Le port par défaut est le 3100 et le nom par défaut est "195048,195178"

## Listes des requêtes / réponse : 

### Inscription : 

Afin de pouvoir jouer, le client doit s'inscrire sur celui-ci. Pour cela, il doit envoyer un message sous format Json au serveur contenant ses données, en communiquant au serveur qui se trouve sur le port 3000.

Contenu du message : 

```json
{
"request": "subscribe",
"port": port,
"name": name,
"matricules": ["195048", "195178"]
}
```

Par défaut, les variables port et name sont réspectivement : 3100 et "195048,195178".

Si tout se passe correctement, le serveur répond : 

```json
{
   "response": "ok"
}
```


### Vérification de la présence : 


 Afin de vérifier si le client est toujours connecté, le serveur envoit régulièrement des requète "ping" sur le port mentionné lors de l'inscription, auquelle nous devons répondre "pong"

Requète ping : 

```json
{
   "request": "ping"
}
```
Réponse : 

```json
{
   "response": "pong"
}
```

### Requête de coup : 



Lorsque c'est au tour du joueur de donner son coup, le serveur envoit une requête play au client qu idevra renvoyer son coup dans les 3 secondes suivantes.


Requête play du serveur : 

```json
{
   "request": "play",
   "lives": 3,
   "errors": list_of_errors,
   "state": state_of_the_game
}
```

La variable lives donne le nombre de vies restantes du joueur, chaque joueur a 3 vies par match et en perd une à chaque mauvais mouvement effectué. Si le nombre de vies tombe à 0, le joueur perd.

La variable errors liste les raisons pour lesquelles les coups joués étaient mauvais.

La variable state donne l'état du jeu, elle contient différentes infos nécéssaire au client afin qu'il puisse décider comment jouer. 

Contenu de state : 

```json
{
   "players": ["LUR", "LRG"],
   "current": 0,
   "board": [
      ["W", "W", "W", "W", "W", "X", "X", "X", "X"],
      ["W", "W", "W", "W", "W", "W", "X", "X", "X"],
      ["E", "E", "W", "W", "W", "E", "E", "X", "X"],
      ["E", "E", "E", "E", "E", "E", "E", "E", "X"],
      ["E", "E", "E", "E", "E", "E", "E", "E", "E"],
      ["X", "E", "E", "E", "E", "E", "E", "E", "E"],
      ["X", "X", "E", "E", "B", "B", "B", "E", "E"],
      ["X", "X", "X", "B", "B", "B", "B", "B", "B"],
      ["X", "X", "X", "X", "B", "B", "B", "B", "B"]
   ]
}
```

La variable Players donne les noms des joueurs inscris au match, le premier joueur représente celui qui joueura en premier avec les pions noirs. 

La variable current donne l'indice dans la liste Players du joueur devant donner son coup.

La variable board donne le plateau de jeu. 


## Stratégie utilisée pour la génération des coups :

Premièrement afin de pouvoir déterminer le meilleur coup jouable, nous devons lister tout les coups jouables par tout les mabres/trains de marbres. 

La première étape dans cet détermination de tout les coups est la détermination de la position de tout les marbres et de tout les trains de marbres. Pour cela nous avons écrit 2 fonctions, une pour déterminer la position des marbres et l'autre servant à déterminer tout les trains de marbres présent sur le tableau. 

Par après, nous déterminons tout les coups possibles en excluant tout les mauvais.

Pour finir, afin de génerer le meilleur coup, l'IA parcoure tout les états possibles liés à l'état donné et évaluer ceux-ci (les états liés sont donnés par un coup, l'état initial avec le coup joué = état lié), le tout sur plusieurs profondeurs. Par la suite, elle évalue ces états avec une heuristique. 

Elle détermine le meilleur coup possible comme étant le coup la menant à l'état avec la meilleur heuristique. 

L'heuristique que nous avons mis en place prend 2 paramètres en compte : 

1. La position des pions par rapport au centre : plus les pions sont au centres, plus l'heuristique remet une valeur haute. En effet dans abalone, plus les pions sont au centre, plus cela est avantageux pour le joueur car l'autre joueur aura plus de mal à pousser vers l'extérieur nos pions .
2. La différence de pions entre les 2 joueurs. Avec cette variable, nous souhaitons maximiser le nombre de pions adverses que nous poussons tout en gardant un maximum des notres. 

Pour relier les 2, nous avons utiliser un facteur 50, déterminé comme optimal à travers des test. En effet si nous ne metton pas de facteur entre les 2, la différence de pions est trop faible pour impacter la décision de l'IA et si le facteur est trop elevé, l'IA joue "trop agressivement" et a tendance à trop s'éloigner du centre et perd donc l'avantage du centre.
En outre, lorsque le client voit une victoire potentielle, l'heuristique de cet état sera démesurément grande afin que il sâche que cet état est de loin le meilleur atteignable.

Pour finir, la fonction negamaxfinal parcours tout les états liés aux principal, et ce de manière réccursive, tout en évaluant ceux-ci grâce à l'heuristique. Pour finir, il renvoie le meilleur move (lié à l'état ayant la meilleure heurisitque donc) qu'il aura trouver dans le temps imparti (ici fixé à 2.8sec, car le client doit répondre en 3sec. Les 0.2sec sont la comme sécurité au cas ou la communication réseaux prednrait trop de temps).
