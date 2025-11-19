#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lichess Puzzle Trainer - Entraînement interactif aux mats en X coups
"""

import sys
import os
import random

# ============================================================================
# CONFIGURATION
# ============================================================================

# Fichier temporaire pour l'historique des puzzles vus
HISTORY_FILE = ".puzzles_history"

# Phrases pour demander la solution
PHRASES_FUN = [
    "Vous donnez votre langue au chat ? 😺",
    "Alors, trouvé le coup gagnant ? 🤔",
    "Prêt à valider votre génie tactique ? 🧠",
    "C'est mat ou échec et mat ? ♟️",
    "Euréka ou abandon ? 💡",
    "Le coup de maître, c'est quoi ? 🎯",
    "Stockfish vous susurre la réponse ? 🤖",
    "Allez, balance ton coup ! 🚀",
    "T'as trouvé ou tu bluffes ? 😏",
    "La solution est au bout de vos doigts... ⌨️"
]

# Couleurs ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def print_header(text):
    """Affiche le header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Affiche une info"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text):
    """Affiche un warning"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

# ============================================================================
# GESTION DES FICHIERS
# ============================================================================

def detect_puzzle_files():
    """Détecte les fichiers mat*.csv disponibles"""
    files = {}
    for i in range(1, 6):
        filename = f"mat{i}.csv"
        if os.path.exists(filename):
            try:
                # Compter le nombre de lignes
                with open(filename, 'r') as f:
                    count = sum(1 for _ in f)

                if count == 0:
                    print_warning(f"Le fichier {filename} est vide, ignoré")
                    continue

                files[i] = {'filename': filename, 'count': count}
            except Exception as e:
                print_warning(f"Erreur lors de la lecture de {filename}: {e}")
                continue
    return files

def detect_csv_format(filename):
    """Détecte si le CSV a des IDs (première colonne) ou pas (--no_id)"""
    try:
        with open(filename, 'r') as f:
            first_line = f.readline().strip()

            if not first_line:
                print_error(f"Le fichier {filename} est vide !")
                return None

            fields = first_line.split(',')

            if len(fields) < 3:
                print_error(f"Format CSV invalide dans {filename} (moins de 3 colonnes)")
                print_info(f"Ligne trouvée: {first_line[:50]}...")
                return None

            # Si la première colonne ressemble à un FEN (contient des espaces et '/'), pas d'ID
            if ' ' in fields[0] and '/' in fields[0]:
                return False  # Pas d'ID
            else:
                return True   # Avec ID

    except FileNotFoundError:
        print_error(f"Fichier {filename} introuvable !")
        return None
    except Exception as e:
        print_error(f"Erreur lors de la lecture de {filename}: {e}")
        return None

def load_puzzle(filename, has_id, seen_puzzles, max_retries=10):
    """Charge un puzzle aléatoire depuis le fichier CSV"""
    retries = 0

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        if not lines:
            print_error(f"Le fichier {filename} est vide !")
            return None

        # Filtrer les puzzles déjà vus si on a des IDs
        if has_id:
            available = [l for l in lines if l.split(',')[0] not in seen_puzzles]
            if not available:
                return None  # Tous les puzzles ont été vus
            pool = available
        else:
            pool = lines

        # Essayer de charger un puzzle valide
        while retries < max_retries:
            line = random.choice(pool)
            fields = line.strip().split(',')

            # Validation du nombre de champs
            min_fields = 4 if has_id else 3
            if len(fields) < min_fields:
                retries += 1
                continue

            if has_id:
                puzzle_id = fields[0]
                fen = fields[1]
                solution = fields[2]
                url = fields[3]
                opening = fields[4] if len(fields) > 4 else ""
            else:
                puzzle_id = None
                fen = fields[0]
                solution = fields[1]
                url = fields[2]
                opening = fields[3] if len(fields) > 3 else ""

            # Validation basique du FEN
            if '/' not in fen or ' ' not in fen:
                retries += 1
                continue

            # Validation de la solution (au moins un coup)
            if not solution.strip():
                retries += 1
                continue

            # Puzzle valide trouvé
            return {
                'id': puzzle_id,
                'fen': fen,
                'solution': solution,
                'url': url,
                'opening': opening
            }

        # Si on arrive ici, impossible de trouver un puzzle valide
        print_error(f"Impossible de trouver un puzzle valide après {max_retries} tentatives")
        return None

    except Exception as e:
        print_error(f"Erreur lors du chargement du puzzle: {e}")
        return None

def load_history(filename):
    """Charge l'historique des puzzles vus"""
    if not os.path.exists(filename):
        return set()
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print_warning(f"Erreur lors du chargement de l'historique: {e}")
        return set()

def save_to_history(filename, puzzle_id):
    """Sauvegarde un puzzle ID dans l'historique"""
    try:
        with open(filename, 'a') as f:
            f.write(f"{puzzle_id}\n")
    except Exception as e:
        print_warning(f"Impossible de sauvegarder l'historique: {e}")

# ============================================================================
# LOGIQUE DU JEU
# ============================================================================

def normalize_move(move):
    """Normalise un coup UCI (minuscules, sans espaces)"""
    return move.lower().strip()

def display_puzzle(puzzle, level):
    """Affiche le puzzle"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}🎯 PUZZLE - Mat en {level} coup(s){Colors.RESET}")

    if puzzle['opening']:
        print(f"{Colors.CYAN}Ouverture: {puzzle['opening']}{Colors.RESET}")

    print(f"\n{Colors.BOLD}Position FEN :{Colors.RESET}")
    print(f"{Colors.GREEN}{puzzle['fen']}{Colors.RESET}")

    print(f"\n{Colors.BLUE}URL Lichess: {puzzle['url']}{Colors.RESET}")

    if puzzle['id']:
        print(f"{Colors.YELLOW}Puzzle ID: {puzzle['id']}{Colors.RESET}")

def play_puzzle_sequence(puzzle, level):
    """
    Joue la séquence complète d'un puzzle avec alternance joueur/adversaire.
    
    Retourne:
    - 'success' : Tous les coups corrects
    - 'failed' : Au moins un coup incorrect
    - 'solution' : L'utilisateur a demandé la solution
    - 'quit' : L'utilisateur veut quitter
    """
    solution_moves = puzzle['solution'].split()
    
    if not solution_moves:
        print_error("Solution vide dans le puzzle !")
        return 'failed'
    
    print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
    phrase = random.choice(PHRASES_FUN)
    print(f"{Colors.BOLD}{phrase}{Colors.RESET}")
    print(f"{Colors.CYAN}Commandes: [votre coup UCI] / [S]olution / [Q]uitter{Colors.RESET}\n")
    
    move_number = 1
    
    for index, expected_move in enumerate(solution_moves):
        # Les coups pairs (index 0, 2, 4...) sont pour le joueur
        # Les coups impairs (index 1, 3, 5...) sont pour l'adversaire
        
        if index % 2 == 0:
            # Tour du joueur
            prompt = f"{Colors.BOLD}💭 Votre coup #{move_number}: {Colors.RESET}"
            user_input = input(prompt).strip()
            
            # Gérer les commandes spéciales
            if user_input.lower() == 'q':
                return 'quit'
            elif user_input.lower() == 's':
                return 'solution'
            
            # Vérifier le coup
            if normalize_move(user_input) != normalize_move(expected_move):
                print_error(f"Incorrect ! ❌ Le bon coup était : {Colors.BOLD}{expected_move}{Colors.RESET}")
                return 'failed'
            else:
                print_success(f"Excellent ! ✓ {user_input}")
                move_number += 1
        else:
            # Tour de l'adversaire (afficher seulement)
            print(f"{Colors.YELLOW}👤 L'adversaire joue : {Colors.BOLD}{expected_move}{Colors.RESET}")
    
    # Si on arrive ici, tous les coups étaient corrects !
    return 'success'

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def display_menu(available_files):
    """Affiche le menu de sélection du niveau"""
    print_header("🏆 LICHESS PUZZLE TRAINER 🏆")

    print(f"{Colors.BOLD}Fichiers de puzzles disponibles :{Colors.RESET}\n")

    for level, info in sorted(available_files.items()):
        print(f"  {Colors.GREEN}[{level}]{Colors.RESET} Mat en {level} coup(s) - {Colors.CYAN}{info['count']:,}{Colors.RESET} puzzles")

    print(f"\n  {Colors.RED}[Q]{Colors.RESET} Quitter\n")

    choice = input(f"{Colors.BOLD}Choisissez votre niveau : {Colors.RESET}").strip().lower()

    if choice == 'q':
        return None

    try:
        level = int(choice)
        if level in available_files:
            return level
        else:
            print_error("Niveau invalide !")
            return None
    except ValueError:
        print_error("Entrée invalide !")
        return None

# ============================================================================
# BOUCLE PRINCIPALE
# ============================================================================

def main():
    """Fonction principale du trainer"""

    # Détection des fichiers disponibles
    available_files = detect_puzzle_files()

    if not available_files:
        print_error("Aucun fichier mat*.csv valide trouvé dans le répertoire actuel !")
        print_info("Générez d'abord vos fichiers avec extract.py")
        print_info("Exemple: ./extract.py --mat-en 1 --no_id lichess_db_puzzle.csv > mat1.csv")
        sys.exit(1)

    # Menu de sélection
    level = display_menu(available_files)

    if level is None:
        print_info("À bientôt ! 👋")
        sys.exit(0)

    # Infos sur le fichier sélectionné
    filename = available_files[level]['filename']
    has_id = detect_csv_format(filename)

    # Vérification du format
    if has_id is None:
        print_error("Impossible de détecter le format du fichier CSV !")
        print_info("Vérifiez que le fichier est bien formaté")
        print_info("Format attendu: PuzzleId,FEN,Solution,URL,OpeningTags")
        print_info("            ou: FEN,Solution,URL,OpeningTags (avec --no_id)")
        sys.exit(1)

    # Charger l'historique si le fichier a des IDs
    seen_puzzles = set()
    history_file = f"{HISTORY_FILE}_mat{level}"

    if has_id:
        seen_puzzles = load_history(history_file)
        remaining = available_files[level]['count'] - len(seen_puzzles)
        print_info(f"Format détecté: Avec IDs (historique activé)")
        print_info(f"Puzzles déjà vus: {len(seen_puzzles)} / Restants: {remaining}")
    else:
        print_warning(f"Format détecté: Sans IDs (fichier généré avec --no_id)")
        print_warning(f"L'historique des puzzles vus ne sera pas sauvegardé")

    # Stats de session
    total_attempts = 0
    total_success = 0

    # Boucle de jeu
    print_header(f"🎮 SESSION - Mat en {level} coup(s)")

    while True:
        # Charger un puzzle
        puzzle = load_puzzle(filename, has_id, seen_puzzles)

        if puzzle is None:
            if has_id and seen_puzzles and len(seen_puzzles) >= available_files[level]['count']:
                print_success("🎉 Félicitations ! Vous avez résolu TOUS les puzzles de ce niveau !")
            else:
                print_error("Impossible de charger un puzzle. Fin de la session.")
            break

        # Afficher le puzzle
        display_puzzle(puzzle, level)

        # Jouer la séquence complète du puzzle
        result = play_puzzle_sequence(puzzle, level)
        
        # Gérer le résultat
        if result == 'quit':
            print_info("Abandon de la session...")
            break
        elif result == 'solution':
            print(f"\n{Colors.YELLOW}💡 Solution complète: {Colors.BOLD}{puzzle['solution']}{Colors.RESET}")
            total_attempts += 1
        elif result == 'success':
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 BRAVO ! Échec et mat ! 🎉{Colors.RESET}")
            total_attempts += 1
            total_success += 1
        elif result == 'failed':
            print(f"\n{Colors.RED}Solution complète: {Colors.BOLD}{puzzle['solution']}{Colors.RESET}")
            total_attempts += 1

        # Sauvegarder dans l'historique si ID présent
        if has_id and puzzle['id']:
            seen_puzzles.add(puzzle['id'])
            save_to_history(history_file, puzzle['id'])

        # Demander si on continue
        print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
        continue_choice = input(f"\n{Colors.BOLD}[C]ontinuer ou [Q]uitter ? {Colors.RESET}").strip().lower()

        if continue_choice == 'q':
            break

    # Stats finales
    print_header("📊 STATISTIQUES DE LA SESSION")

    print(f"{Colors.BOLD}Puzzles tentés:{Colors.RESET} {total_attempts}")
    print(f"{Colors.BOLD}Puzzles réussis:{Colors.RESET} {total_success}")

    if total_attempts > 0:
        success_rate = (total_success / total_attempts) * 100
        print(f"{Colors.BOLD}Taux de réussite:{Colors.RESET} {Colors.GREEN}{success_rate:.1f}%{Colors.RESET}")

    if has_id:
        remaining = available_files[level]['count'] - len(seen_puzzles)
        print(f"{Colors.BOLD}Puzzles restants:{Colors.RESET} {remaining}")

    print(f"\n{Colors.YELLOW}Merci d'avoir joué ! À bientôt 🤘{Colors.RESET}\n")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interruption détectée. À plus tard ! 👋{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
