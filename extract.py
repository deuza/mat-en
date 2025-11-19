#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour parser les puzzles Lichess et calculer le FEN après le premier coup
"""

import sys

# ============================================================================
# VÉRIFICATION DU VENV - DOIT ÊTRE AVANT L'IMPORT DE CHESS
# ============================================================================

def check_virtual_env():
    """Vérifie que le script est dans le venv"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        # TOUS les print() doivent avoir file=sys.stderr
        print("\n" + "="*60, file=sys.stderr)
        print("❌ ERREUR : Environnement virtuel non activé", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print("\nCe script nécessite l'activation de l'environnement virtuel.", file=sys.stderr)
        print("\n📋 Marche à suivre :", file=sys.stderr)
        print("   1. Se placer dans le répertoire : cd ~/mat-en", file=sys.stderr)
        print("   2. Activer le venv : source venv/bin/activate", file=sys.stderr)
        print("   3. Relancer le script\n", file=sys.stderr)
        print("💡 Votre prompt devrait afficher (venv) une fois activé.\n", file=sys.stderr)
        sys.exit(1)

# Appeler la vérification au démarrage
check_virtual_env()

# Maintenant on peut importer chess en toute sécurité
import argparse
import chess

# ============================================================================
# CONFIGURATION DU MODE VERBOSE
# ============================================================================
VERBOSE_INTERVAL = 10000

# ============================================================================
# CONFIGURATION DES ARGUMENTS
# ============================================================================

parser = argparse.ArgumentParser(
    description='Parse les puzzles Lichess et calcule le FEN après le premier coup',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Exemples:
  ./extract.py mat_en.csv > output.csv
  ./extract.py --mat-en=1 lichess_db_puzzle.csv > mat1.csv
  ./extract.py --no_id --mat-en=2 mat_en.csv > mat2.csv
  ./extract.py --verbose --mat-en=1 mat_en.csv > mat1.csv
"""
)

parser.add_argument(
    '--mat-en',
    type=int,
    choices=[1, 2, 3, 4, 5],
    help='Filtre sur les mats en X coups (1 à 5)'
)

parser.add_argument(
    '--no_id',
    action='store_true',
    help='Exclut le PuzzleId de la sortie'
)

parser.add_argument(
    '--verbose', '-v',
    action='store_true',
    help='Affiche la progression sur STDERR'
)

parser.add_argument(
    'input_file',
    nargs='?',
    type=argparse.FileType('r'),
    default=sys.stdin,
    help='Fichier CSV à parser (ou STDIN si non spécifié)'
)

# Parse les arguments
args = parser.parse_args()

# ============================================================================
# VÉRIFICATION : Afficher --help si pas d'arguments ET pas de pipe
# ============================================================================

# Si aucun fichier fourni ET stdin est un terminal (pas de pipe)
# alors afficher l'aide
import os
if args.input_file == sys.stdin and os.isatty(sys.stdin.fileno()):
    parser.print_help()
    sys.exit(0)

# ============================================================================
# TRAITEMENT
# ============================================================================

line_count = 0
processed = 0

if args.verbose:
    print(f"# Démarrage du traitement...", file=sys.stderr)

for line in args.input_file:
    line_count += 1
    line = line.strip()
    fields = line.split(',', 9)

    if args.mat_en:
        themes = fields[7]
        if f"mateIn{args.mat_en}" not in themes:
            continue

    puzzle_id = fields[0]
    fen_original = fields[1]
    moves = fields[2]
    game_url = fields[8]
    opening_tags = fields[9]

    moves_list = moves.split()
    premier_coup = moves_list[0]
    solution = ' '.join(moves_list[1:])

    try:
        board = chess.Board(fen_original)
        board.push_uci(premier_coup)
        nouveau_fen = board.fen()

        output_fields = []
        if not args.no_id:
            output_fields.append(puzzle_id)

        output_fields.extend([
            nouveau_fen,
            solution,
            game_url,
            opening_tags
        ])

        print(','.join(output_fields))

        processed += 1

        if args.verbose and processed % VERBOSE_INTERVAL == 0:
            print(f"# {processed} puzzles traités | dernier coup: {premier_coup} | ligne {line_count}", file=sys.stderr)

    except Exception as e:
        if args.verbose:
            print(f"# ERREUR ligne {line_count}: {e}", file=sys.stderr)
        continue

if args.verbose:
    print(f"# Terminé: {processed} puzzles traités sur {line_count} lignes", file=sys.stderr)
