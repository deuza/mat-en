# ♟️ Lichess Puzzle Suite ♟️

Suite complète d'outils CLI pour télécharger, transformer et s'entraîner sur les puzzles d'échecs de la base Lichess. 🎯

**Composants :**
- 🌐 `download_puzzles.sh` : Téléchargement et décompression automatique
- 🔧 `extract.py` : Transformation des puzzles (calcul du FEN après premier coup)
- 🎮 `puzzle_trainer.py` : Entraînement interactif avec vérification des coups

---

## Table des matières

1. [Prérequis système](#1-prérequis-système)
2. [Installation de l'environnement Python](#2-installation-de-lenvironnement-python)
3. [Téléchargement de la base Lichess](#3-téléchargement-de-la-base-lichess)
4. [Extraction et transformation des puzzles](#4-extraction-et-transformation-des-puzzles)
5. [Entraînement interactif](#5-entraînement-interactif)
6. [Workflow complet](#6-workflow-complet)
7. [Configuration avancée](#7-configuration-avancée)
8. [Informations techniques](#8-informations-techniques)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prérequis système

Avant de commencer, vous devez installer les binaires nécessaires sur votre système.

### Sur Debian/Ubuntu/Raspbian
```bash
# Mise à jour des dépôts
sudo apt update

# Installation des outils nécessaires
sudo apt install -y python3 python3-venv wget zstd

# Vérification des versions installées
python3 --version    # Python 3.7+ requis
wget --version
zstd --version
```

### Explication des binaires

- **python3** : Interpréteur Python pour exécuter les scripts
- **python3-venv** : Module pour créer des environnements virtuels isolés
- **wget** : Télécharge la base de données Lichess
- **zstd** : Décompresse le fichier `.zst` (Zstandard compression)

---

## 2. Installation de l'environnement Python

### Étape 1 : Créer le répertoire de travail
```bash
# Créer le répertoire (si nécessaire)
mkdir -p ~/mat-en

# Se placer dedans
cd ~/mat-en
```

### Étape 2 : Créer l'environnement virtuel
```bash
# Création du venv (environnement Python isolé)
python3 -m venv venv

# Activation du venv
# IMPORTANT : à faire à chaque nouvelle session terminal
source venv/bin/activate

# Votre prompt devrait maintenant afficher (venv) au début
```

**Explication** : Le venv isole les bibliothèques Python pour ne pas polluer le système. Tout ce qui est installé via `pip` reste dans `~/mat-en/venv/`.

### Étape 3 : Installer python-chess
```bash
# S'assurer que le venv est activé (vous devez voir (venv) dans le prompt)
pip install python-chess

# Vérification de l'installation
python3 -c "import chess; print(chess.__version__)"
```

### Étape 4 : Rendre les scripts exécutables
```bash
# Télécharger ou créer les scripts, puis les rendre exécutables
chmod +x download_puzzles.sh
chmod +x extract.py
chmod +x puzzle_trainer.py
```

### À ce stade, vous devriez avoir :
```
~/mat-en/
├── venv/                    # Environnement virtuel Python
├── download_puzzles.sh      # Script de téléchargement
├── extract.py               # Script de parsing Python
└── puzzle_trainer.py        # Trainer interactif
```

---

## 3. Téléchargement de la base Lichess

Le script `download_puzzles.sh` automatise le téléchargement et la décompression.

### Utilisation du script
```bash
# Se placer dans le répertoire
cd ~/mat-en

# Lancer le script
./download_puzzles.sh
```

### Ce que fait le script

1. **Vérifie** que `wget` et `zstd` sont installés
2. **Télécharge** `lichess_db_puzzle.csv.zst` (~263 Mo)
3. **Décompresse** le fichier en `lichess_db_puzzle.csv` (~1.5 Go)
4. **Affiche** des statistiques sur le fichier

### Sortie attendue
```
=== Téléchargement de la base Lichess Puzzles ===

Vérification des binaires...
✓ wget et zstd sont disponibles

Téléchargement de lichess_db_puzzle.csv.zst (~263 Mo)...
--2025-11-11 10:30:00--  https://database.lichess.org/lichess_db_puzzle.csv.zst
[...]
Saving to: 'lichess_db_puzzle.csv.zst'
100%[================================>] 263.00M  5.20MB/s    in 51s

Décompression...
lichess_db_puzzle.csv.zst: 1560823808 bytes

=== Terminé ===
Fichier compressé   : 263M
Fichier décompressé : 1.5G
Nombre de lignes    : 5524872

Prêt à parser avec extract.py !
```

### Gestion des fichiers existants

Si vous relancez le script alors que les fichiers existent déjà, il vous demandera si vous voulez les remplacer :
```bash
Le fichier existe déjà. Remplacement ? (y/N)
```

- Répondez `y` pour télécharger/décompresser à nouveau
- Répondez `N` ou `Entrée` pour garder le fichier existant

---

## 4. Extraction et transformation des puzzles

Le script `extract.py` transforme les puzzles Lichess en positions FEN exploitables.

### ⚠️ Activer le venv à chaque session modifiant les fichiers d'entrainement

**IMPORTANT** : À chaque fois que vous ouvrez un nouveau terminal, vous devez activer le venv :
```bash
cd ~/mat-en
source venv/bin/activate
```

Vous devriez voir `(venv)` apparaître dans votre prompt.

### Syntaxe de base
```bash
./extract.py [OPTIONS] fichier.csv > sortie.csv
```

### Options disponibles

| Option | Description | Exemple |
|--------|-------------|---------|
| `--help` | Affiche l'aide | `./extract.py --help` |
| `--mat-en N` | Filtre les mats en N coups (1-5) | `--mat-en 1` |
| `--no_id` | Exclut le PuzzleId de la sortie | `--no_id` |
| `--verbose` ou `-v` | Affiche la progression | `--verbose` |

### Format de sortie

#### Avec ID (par défaut)
```csv
PuzzleId,FEN_après_coup_adversaire,Solution,URL,OpeningTags
```

#### Sans ID (--no_id) - Recommandé pour le trainer
```csv
FEN_après_coup_adversaire,Solution,URL,OpeningTags
```

### Exemples d'extraction

#### Exemple 1 : Extraire tous les mats en 1
```bash
# Avec IDs (pour sauvegarde)
./extract.py --mat-en 1 --verbose lichess_db_puzzle.csv > mat1_avec_id.csv

# Sans IDs (pour le trainer)
./extract.py --mat-en 1 --no_id --verbose lichess_db_puzzle.csv > mat1.csv
```

**Sortie console** :
```
# Démarrage du traitement...
# 10000 puzzles traités | dernier coup: b4b7 | ligne 21834
# 20000 puzzles traités | dernier coup: d7f8 | ligne 43878
[...]
# Terminé: 767302 puzzles traités sur 5524872 lignes
```

**Temps d'exécution** : ~5-6 minutes sur Raspberry Pi 4

#### Exemple 2 : Générer tous les niveaux d'un coup
```bash
# Boucle pour générer mat1.csv à mat5.csv (sans IDs)
for i in {1..5}; do
    echo "Extraction des mats en $i..."
    ./extract.py --mat-en $i --no_id --verbose lichess_db_puzzle.csv > mat${i}.csv
    echo "✓ mat${i}.csv créé"
done

# Vérifier les tailles
wc -l mat*.csv
```

**Temps total** : ~20-25 minutes sur Raspberry Pi 4 pour les 5 niveaux

---

## 5. Entraînement interactif

Le script `puzzle_trainer.py` est un trainer interactif en mode CLI pour s'entraîner sur les puzzles.

### ⚠️ Prérequis

- Au moins un fichier `mat*.csv` doit exister dans le répertoire

### Lancement du trainer
```bash
cd ~/mat-en
./puzzle_trainer.py
```

### Interface du trainer

#### Menu principal (exemple)
```
============================================================
            🏆 LICHESS PUZZLE TRAINER 🏆
============================================================

Fichiers de puzzles disponibles :

  [1] Mat en 1 coup(s) - 767,302 puzzles
  [3] Mat en 3 coup(s) - 523,441 puzzles
  [4] Mat en 4 coup(s) - 156,782 puzzles

  [Q] Quitter

Choisissez votre niveau : 
```

#### Affichage d'un puzzle
```
🎯 PUZZLE - Mat en 1 coup(s)
Ouverture: Sicilian_Defense Sicilian_Defense_McDonnell_Attack

Position FEN :
r4rk1/pp3ppp/3b4/2p1pPB1/7N/2PP3n/PP4PP/R2Q2RK b - - 0 18

URL Lichess: https://lichess.org/d04UP3XD#35

Prêt à valider votre génie tactique ? 🧠
Entrez votre coup en notation UCI (ex: d6h2) ou 's' pour la solution:
> 
```

### Fonctionnalités du trainer

✅ **Détection automatique** des fichiers mat*.csv disponibles  
✅ **Mats en plusieurs coups** pris en charge  
✅ **Vérification des coups** - valide si votre coup est correct  
✅ **Phrases amusantes** variées  
✅ **Statistiques de session** - taux de réussite en temps réel  
✅ **Interface colorée** avec émojis  
✅ **Historique des puzzles** (si fichier avec IDs) - ne retombe jamais sur le même puzzle  
✅ **Gestion des formats** : avec ou sans IDs  
✅ **Commandes** :
  - Taper votre coup (ex: `h3f2`)
  - `s` pour voir la solution sans tenter
  - `q` pour quitter à tout moment
  - `c` pour continuer après un puzzle

### Exemple de session
```bash
$ ./puzzle_trainer.py

============================================================
            🏆 LICHESS PUZZLE TRAINER 🏆
============================================================

Fichiers de puzzles disponibles :

  [1] Mat en 1 coup(s) - 767,302 puzzles
  [3] Mat en 3 coup(s) - 523,441 puzzles

  [Q] Quitter

Choisissez votre niveau : 1

ℹ Format détecté: Sans IDs (fichier généré avec --no_id)
⚠ L'historique des puzzles vus ne sera pas sauvegardé

============================================================
              🎮 SESSION - Mat en 1 coup(s)
============================================================


🎯 PUZZLE - Mat en 1 coup(s)

Position FEN :
2kr1b1r/p1p2pp1/2pqN3/7p/6n1/2NPB3/PPP2PPP/R2Q1RK1 b - - 0 13

URL Lichess: https://lichess.org/seIMDWkD#25

Vous donnez votre langue au chat ? 😺
Entrez votre coup en notation UCI (ex: d6h2) ou 's' pour la solution:
> d6h2

✓ Bravo ! 🎉 Le coup d6h2 est correct !

────────────────────────────────────────────────────────────

[C]ontinuer ou [Q]uitter ? c

[... autre puzzle ...]

============================================================
                📊 STATISTIQUES DE LA SESSION
============================================================

Puzzles tentés: 15
Puzzles réussis: 12
Taux de réussite: 80.0%

Merci d'avoir joué ! À bientôt camarade 🤘
```

### Commandes avancées
```bash
# Lancer le trainer et rediriger les erreurs dans un fichier
./puzzle_trainer.py 2> errors.log

# Utiliser screen pour une session détachable
screen -S chess
./puzzle_trainer.py
# Ctrl+A puis D pour détacher
# screen -r chess pour rattacher
```

---

## 6. Workflow complet

Voici le workflow recommandé du téléchargement à l'entraînement.

### Première installation (une seule fois)
```bash
# 1. Installer les dépendances système
sudo apt update
sudo apt install -y python3 python3-venv wget zstd

# 2. Créer l'environnement
mkdir -p ~/mat-en
cd ~/mat-en

# 3. Setup Python
python3 -m venv venv
source venv/bin/activate
pip install python-chess

# 4. Rendre les scripts exécutables
chmod +x *.sh *.py
```

### Téléchargement et préparation des puzzles
```bash
# 1. Activer le venv
cd ~/mat-en
source venv/bin/activate

# 2. Télécharger la base Lichess
./download_puzzles.sh

# 3. Extraire tous les niveaux (mat1 à mat5)
for i in {1..5}; do
    echo "Extraction niveau $i..."
    ./extract.py --mat-en $i --no_id --verbose lichess_db_puzzle.csv > mat${i}.csv
done

# Vérification
ls -lh mat*.csv
```

**Temps total** : ~20 minutes sur Raspberry Pi 4 (téléchargement + extraction)

---

## 7. Configuration avancée

### Modifier la fréquence d'affichage en mode verbose (extract.py)

Éditez `extract.py`, ligne ~15 :
```python
# Affiche un message tous les X puzzles traités
VERBOSE_INTERVAL = 10000
```

**Valeurs recommandées** :
- `5000` : affichage toutes les ~1-2 secondes (très verbeux)
- `10000` : affichage toutes les ~3-5 secondes (recommandé)
- `50000` : affichage toutes les ~15-20 secondes (peu de spam)

### Personnaliser les phrases fun (puzzle_trainer.py)

Éditez `puzzle_trainer.py`, ligne ~20 :
```python
PHRASES_FUN = [
    "Vous donnez votre langue au chat ? 😺",
    "Alors, trouvé le coup gagnant ? 🤔",
    # Ajoutez vos propres phrases ici !
    "Échec et mat ou échec tout court ? 🤨",
]
```

### Réinitialiser l'historique des puzzles

Si vous voulez recommencer à zéro :
```bash
# Supprimer l'historique d'un niveau spécifique
rm .puzzles_history_mat1

# Supprimer tout l'historique
rm .puzzles_history_*
```

### Générer uniquement certains niveaux
```bash
# Seulement mat1 et mat3
./extract.py --mat-en 1 --no_id --verbose lichess_db_puzzle.csv > mat1.csv
./extract.py --mat-en 3 --no_id --verbose lichess_db_puzzle.csv > mat3.csv
```

---

## 8. Informations techniques

### Performance

Tests sur **Raspberry Pi 4** (4 Go RAM) :

| Opération | Temps | Détails |
|-----------|-------|---------|
| Téléchargement | ~51 secondes | 263 Mo @ 5 Mo/s |
| Décompression | ~15 secondes | zstd → 1.5 Go |
| Extraction Python (par niveau) | ~5-6 minutes | Calcul FEN avec python-chess |
| Extraction Perl (filtrage simple) | ~56 secondes | Sans transformation FEN |
| Trainer (chargement puzzle) | <1 seconde | Instantané |

### Structure du fichier Lichess original
```csv
PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags
```

**Exemple de ligne** :
```csv
000rZ,2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13,d4e6 d6h2,755,80,100,339,kingsideAttack mate mateIn1 oneMove opening,https://lichess.org/seIMDWkD#25,Scandinavian_Defense
```

### Transformation effectuée par extract.py

**Entrée** (ligne CSV Lichess) :
```
000rZ,2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13,d4e6 d6h2,[...]
```

Le soucis est que le FEN n'est pas jouable immédiatement, puisqu'un coup doit être joué avant de résoudre le puzzle.
Plutôt que de tout parser rapidement tel quel en Perl, j'ai préféré passer par Python Chess et faire jouer chacun des coups avant d'enregistrer le FEN "prêt à résoudre"

**Traitement** :
1. Parse le FEN : `2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13`
2. Joue le premier coup `d4e6` avec `python-chess`
3. Calcule le nouveau FEN
4. Extrait la solution : `d6h2`

**Sortie** (CSV transformé) :
```
000rZ,2kr1b1r/p1p2pp1/2pqN3/7p/6n1/2NPB3/PPP2PPP/R2Q1RK1 b - - 0 13,d6h2,https://lichess.org/seIMDWkD#25,Scandinavian_Defense
```

Le nouveau FEN représente **la position exacte à résoudre**.

### Tailles des fichiers
```
lichess_db_puzzle.csv.zst  : 263 Mo (compressé)
lichess_db_puzzle.csv      : 1.5 Go (5 524 872 lignes)
mat1.csv                   : ~90 Mo (767 302 lignes)
mat2.csv                   : ~110 Mo (916 465 lignes)
mat3.csv                   : ~75 Mo (523 441 lignes)
mat4.csv                   : ~23 Mo (156 782 lignes)
mat5.csv                   : ~8 Mo (51 329 lignes)
.puzzles_history_mat*      : <1 Ko (IDs des puzzles vus)
```

### Notation UCI utilisée

**Exemples de coups UCI** :
- `e2e4` : pion de e2 vers e4
- `g1f3` : cavalier de g1 vers f3
- `e7e8q` : promotion en dame (pion e7 → e8)
- `e1g1` : petit roque (roi e1 → g1)

Le trainer accepte les coups en minuscules sans distinction.

---

## 9. Troubleshooting

### Problème : Le trainer ne trouve pas les fichiers mat*.csv

**Erreur** :
```
✗ Aucun fichier mat*.csv valide trouvé dans le répertoire actuel !
```

**Solution** :
```bash
# Vérifier votre répertoire actuel
pwd  # Doit être ~/mat-en

# Lister les fichiers
ls -la mat*.csv

# Si pas de fichiers, générer avec extract.py
source venv/bin/activate
./extract.py --mat-en 1 --no_id lichess_db_puzzle.csv > mat1.csv
```

---

### Problème : Le venv n'est pas activé

**Symptôme** : Pas de `(venv)` dans le prompt

**Erreur possible** :
```
ModuleNotFoundError: No module named 'chess'
```

**Solution** :
```bash
cd ~/mat-en
source venv/bin/activate

# Vérifier
which python3  # Doit pointer vers ~/mat-en/venv/bin/python3
```

**Astuce** : Créer un alias dans `~/.bashrc` :
```bash
alias activ='cd ~/mat-en && source venv/bin/activate'
```

---

### Problème : Permission denied sur les scripts

**Erreur** :
```
bash: ./extract.py: Permission denied
```

**Solution** :
```bash
chmod +x download_puzzles.sh extract.py puzzle_trainer.py
```

---

### Problème : wget ou zstd introuvable

**Erreur** :
```
Erreur: wget n'est pas installé
```

**Solution** :
```bash
# Debian/Ubuntu
sudo apt install wget zstd

# FreeBSD
pkg install wget zstd
```

---

### Problème : Le trainer affiche "Format CSV invalide"

**Erreur** :
```
✗ Format CSV invalide dans mat1.csv (moins de 3 colonnes)
```

**Causes possibles** :
1. Fichier corrompu lors de la génération
2. Redirection mal faite (écrasement partiel)
3. Fichier vide

**Solution** :
```bash
# Vérifier le fichier
head -3 mat1.csv
wc -l mat1.csv

# Si problème, régénérer
source venv/bin/activate
./extract.py --mat-en 1 --no_id --verbose lichess_db_puzzle.csv > mat1.csv
```

---

### Problème : Le script extract.py est très lent

**C'est normal** : Le calcul du nouveau FEN avec `python-chess` prend du temps.

**Solutions** :
- Laissez tourner en arrière-plan : `nohup ./extract.py ... > output.csv &`
- Utilisez `screen` ou `tmux` pour détacher la session
- Exécutez la nuit sur un Raspberry Pi
- Pour filtrage rapide sans FEN : utilisez le script Perl (si disponible)

---

### Problème : Historique des puzzles ne se sauvegarde pas

**Symptôme** : Le trainer redemande les mêmes puzzles

**Cause** : Fichier CSV généré avec `--no_id`

**Explication** : Sans IDs uniques, impossible de tracker les puzzles vus.

**Solutions** :
1. **Régénérer avec IDs** (recommandé pour tracking) :
```bash
   ./extract.py --mat-en 1 --verbose lichess_db_puzzle.csv > mat1_avec_id.csv
```
2. **Accepter** que les puzzles se répètent (mode aléatoire pur)

---

### Problème : Couleurs ANSI ne s'affichent pas

**Symptôme** : Le trainer affiche des codes comme `\033[92m`

**Cause** : Terminal ne supporte pas les codes ANSI

**Solution** :
- Utilisez un terminal moderne (bash, zsh)
- Sur Windows : utilisez WSL ou Windows Terminal

---

### Problème : Le trainer plante avec "Impossible de trouver un puzzle valide"

**Erreur** :
```
✗ Impossible de trouver un puzzle valide après 10 tentatives
```

**Causes** :
- Fichier CSV très corrompu
- Format complètement invalide

**Solution** :
```bash
# Vérifier l'intégrité du fichier
head -20 mat1.csv | cat -A  # Affiche les caractères cachés

# Régénérer le fichier
rm mat1.csv
./extract.py --mat-en 1 --no_id --verbose lichess_db_puzzle.csv > mat1.csv
```

---

## Structure finale du répertoire
```
~/mat-en/
├── venv/                          # Environnement virtuel Python
│   ├── bin/
│   │   ├── python3
│   │   ├── pip
│   │   └── activate
│   ├── lib/
│   └── ...
├── download_puzzles.sh            # Script de téléchargement
├── extract.py                     # Parser Python (transformation FEN)
├── puzzle_trainer.py              # Trainer interactif
├── lichess_db_puzzle.csv.zst      # Base compressée (263 Mo)
├── lichess_db_puzzle.csv          # Base décompressée (1.5 Go)
├── mat1.csv                       # Mats en 1 (767k lignes)
├── mat2.csv                       # Mats en 2 (916k lignes)
├── mat3.csv                       # Mats en 3 (523k lignes)
├── mat4.csv                       # Mats en 4 (156k lignes)
├── mat5.csv                       # Mats en 5 (51k lignes)
├── .puzzles_history_mat1          # Historique des puzzles vus (niveau 1)
├── .puzzles_history_mat2          # Historique niveau 2
└── ...                            # Autres historiques
```

---

## Commandes rapides (mémo)
```bash
# Installation initiale (une seule fois)
cd ~/mat-en
python3 -m venv venv
source venv/bin/activate
pip install python-chess
chmod +x *.sh *.py

# Télécharger la base
./download_puzzles.sh

# Extraire tous les niveaux
for i in {1..5}; do
    ./extract.py --mat-en $i --no_id --verbose lichess_db_puzzle.csv > mat${i}.csv
done

# Désactiver le venv
deactivate

# Utilisation quotidienne
cd ~/mat-en
./puzzle_trainer.py

```

---

## Exemples d'utilisation avancée

### Générer des puzzles pour un usage spécifique
```bash
# Seulement les mats en 1 avec ouvertures siciliennes
grep "Sicilian" lichess_db_puzzle.csv | ./extract.py --mat-en 1 --no_id > mat1_sicilian.csv

# Les 100 premiers mats en 2
./extract.py --mat-en 2 --no_id lichess_db_puzzle.csv | head -100 > mat2_sample.csv
```

### Statistiques sur vos sessions
```bash
# Combien de puzzles de niveau 1 avez-vous vus ?
wc -l .puzzles_history_mat1

# Pourcentage de progression
TOTAL=$(wc -l < mat1.csv)
SEEN=$(wc -l < .puzzles_history_mat1)
echo "scale=2; $SEEN * 100 / $TOTAL" | bc
```

### Backup et synchronisation
```bash
# Sauvegarder vos progressions
tar -czf chess_backup_$(date +%Y%m%d).tar.gz .puzzles_history_*

# Restaurer sur une autre machine
tar -xzf chess_backup_20251111.tar.gz
```

---

## Ressources externes

- **Base Lichess** : https://database.lichess.org/
- **Documentation python-chess** : https://python-chess.readthedocs.io/
- **Notation UCI** : https://www.chessprogramming.org/UCI
- **Lichess Analysis** : https://lichess.org/analysis (pour tester les FEN, mais désactiver l'analyse pour ne pas avoir la solution immédiatememennt !)

---

## Contributeurs et remerciements

**Développement** : DeuZa - Novembre 2025

Ancien DBA Oracle Senior @ Club-Internet  
Hacker, activiste digital, passionné d'échecs

**Remerciements** :
- Lichess.org pour la base de données publique <3
- Lichess.org pour proposer l'équivalent de ce qui est payant ailleurs entiérement gratuit et open-source <3
- La communauté python-chess
- Tous les contributeurs open source et fournisseurs de data love

---

## Licence

Les données Lichess sont sous licence Creative Commons CC0 (domaine public).
Les scripts de ce projet également sous licence CC0 (domaine public), faites en ce que vous voulez.
---

## Améliorations futures possibles

- 🎨 Interface TUI (Text User Interface) avec `rich` ou `textual`
- 📊 Graphiques de progression avec `matplotlib`
- 🌐 Mode multi-joueurs en réseau
- 🤖 Intégration avec Stockfish pour analyses
- 📱 Export vers Anki pour révisions espacées
- 🏆 Système de badges et achievements
- ⏱️ Mode chronomètre pour puzzles rapides
- 💾 Export des statistiques en JSON/CSV

Si vous avez des idées ou contributions, n'hésitez pas ! 🚀

---

**Bon entraînement aux échecs ! **
