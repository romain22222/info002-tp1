# TP1

## Utilisation

`python3 main.py <CMD> [ARGS] [OPTIONS]`

Exemples :
- `python3 main.py test config -A36 -s=8`
- `python3 main.py test hash un_mot_de_passe`
- `python3 main.py bruteforce 16de25af888480da1af57a71855f3e8c515dcb61 -A26A -s=4`
- `python3 main.py create 1000 1000 26As4.txt y --size=4 -A26A`

Pour plus d'informations, voir `python3 main.py help`

---
## Questions

### 5
1. La complexité serait de O(log(hauteur) * largeur) (log(hauteur) car recherche dichotomique et largeur/2 car on va trouver le hash en moyenne à la moitié du tableau) et une complexité spaciale de O(hauteur)
2. Concernant la complexité du bruteforce, elle serait de O(taille_alphabet ^ taille_mot_de_passe) >> complexité de la méthode intermédiaire mais spaciale de O(1) (aucun stockage),
Pour la complexité de la méthode "rapide",  elle serait de O(log(hauteur)) (une seule recherche dichotomique) et une complexité spaciale de O(taille_alphabet ^ taille_mot_de_passe) >> complexité spaciale de la méthode intermédiaire

---
### 8
L'ajout de t dans h2i permet d'éviter les cycles de calcul. En effet, si on a un cycle de calcul, alors au bout d'un moment, on va retomber sur un hash déjà calculé et donc on va boucler sur ce cycle. En ajoutant t dans h2i, on évite ce problème car on ne cycle pas.

De plus, si par chance on retombe sur un indice déjà calculé dans une autre colonne, alors le hash suivant sera différent et on augmentera la diversité de la table.

---
### 12
Dans une table arc en ciel, la complexité serait de O(log(hauteur) * largeur * largeur)

log(hauteur) car recherche dichotomique,

largeur car on va trouver le hash en moyenne à la moitié du tableau, s'il est valide et correspond à un mot de passe trouvable par la table

largeur(2) car à chaque boucle, on doit recalculer le nouveau candidat à chercher, qui prend (largeur - t) itérations soit en moyenne largeur/2 itérations

Cette recherche aura une complexité spaciale de O(hauteur) car il faut charger la table en mémoire.

Les autres calculs sont considérés comme négligeables. (la vérification des candidats est tout le temps constant sauf cas exceptionnel) 

---
### 14

- 16de25af888480da1af57a71855f3e8c515dcb61 / alphabet = ABCDEFGHIJKLMNOPQRSTUVWXYZ / size = 4

j'ai choisi une table de taille 1000 * 1000 car le coverage est suffisant (~78%) pour trouver le mot de passe en 540ms tout en étant assez rapide à générer (~710ms) et pas trop lourde à stocker (~4ko) (mdp = "CODE")
- dafaa5e15a30ecd52c2d1dc6d1a3d8a0633e67e2 / alphabet = abcdefghijklmnopqrstuvwxyz0123456789,;:$. / size = 5

j'ai choisi une table de taille 20000 * 10000 car le coverage est suffisant (~71%) pour trouver le mot de passe en 1160ms tout en étant assez rapide à générer (~2m) et pas trop lourde à stocker (~100ko) (mdp = "n00b.")

---
### 15
Alphabet = abcdefghijklmnopqrstuvwxyz0123456789 / size = 8

Compte tenu de la taille du mot de passe ainsi de l'alphabet, il faudrait une table si possible qui ait un coverage de +99%.
D'après la fonction stats, il faudrait une table de taille 1000000000 80000 pour avoir un coverage de 99.57%.
Elle prendrait 8000000000o de mémoire, soit 8 Go.

Si on part du principe que doubler le nombre de lignes ou doubler le nombre de colonnes double le temps de calcul,
il faudrait environ 0.7 * 1000000000/1000 * 80000/1000 = 56000000 secondes, soit 648 jours pour générer la table.

---
### 16
- 16de25af888480da1af57a71855f3e8c515dcb61 / alphabet = ABCDEFGHIJKLMNOPQRSTUVWXYZ / size = 4 / N = 456976

En bruteforce, il faut 60ms pour trouver le mot de passe.
- (hash de ZZZZ)

En bruteforce, il faut 740ms pour trouver le mot de passe.

---
- dafaa5e15a30ecd52c2d1dc6d1a3d8a0633e67e2 / alphabet = abcdefghijklmnopqrstuvwxyz0123456789,;:$. / size = 5 / N = 115856201

En bruteforce, il faut 72s pour trouver le mot de passe.
- (hash de .....)

En bruteforce, il faut 255s pour trouver le mot de passe.

---
Si on suppose que le temps de calcul est proportionnel à N, alors sur la config 

alphabet = abcdefghijklmnopqrstuvwxyz0123456789 / size = 8 / N = 2821109907456

il faudrait en moyenne 255 / 115856201 * 2821109907456 / 2 = 3104638s, soit 36 jours pour trouver le mot de passe.

On peut voir qu'en python avec un mot de passe de taille 8, il est préférable de faire une table arc-en-ciel uniquement si on veut trouver +18 mots de passe, sinon il est "préférable" de faire du bruteforce.

---
### 17

Le sel permet d'éviter que deux mots de passe identiques aient le même hash. Il est donc impossible de faire une table arc-en-ciel car on ne peut pas prédire le sel.