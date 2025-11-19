#!/bin/bash
# Script de téléchargement et décompression de la base Lichess puzzles

set -e  # Arrête le script en cas d'erreur

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}\n\n=== Initialisation ou mise à jour de la base Lichess Puzzles ===${NC}"

# Vérification des dépendances
echo -e "\n${YELLOW}Vérification des binaires nécessaires ...${NC}"

if ! command -v wget &> /dev/null; then
    echo -e "${RED}Erreur: wget n'est pas installé${NC}"
    echo "Installation: apt install wget"
    exit 1
fi

if ! command -v zstd &> /dev/null; then
    echo -e "${RED}Erreur: zstd n'est pas installé${NC}"
    echo "Installation: apt install zstd"
    exit 1
fi

echo -e "${GREEN}✓ wget et zstd sont disponibles${NC}"

# URL et fichiers
URL="https://database.lichess.org/lichess_db_puzzle.csv.zst"
COMPRESSED="lichess_db_puzzle.csv.zst"
DECOMPRESSED="lichess_db_puzzle.csv"

# Téléchargement
echo -e "\n${YELLOW}Téléchargement de ${COMPRESSED} en cours ...${NC}"
if [ -f "$COMPRESSED" ]; then
    echo -e "${YELLOW}Le fichier existe déjà. Souhaitez vous le remplacer ? (conseillé) (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm "$COMPRESSED"
        wget "$URL"
    else
        echo "Utilisation du fichier existant."
    fi
else
    wget "$URL"
fi

# Décompression
echo -e "\n${YELLOW}Décompression du fichier $COMPRESSED ...${NC}"
if [ -f "$DECOMPRESSED" ]; then
    echo -e "${YELLOW}Le fichier $DECOMPRESSED existe déjà. Souhaitez vous le remplacer ? (conseilllé) (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm "$DECOMPRESSED"
        zstd -d "$COMPRESSED"
    else
        echo "Utilisation du fichier existant."
    fi
else
    zstd -d "$COMPRESSED"
fi

# Statistiques
echo -e "\n${GREEN}=== Terminé ===${NC}"
echo -e "Fichier compressé   : $(ls -lh $COMPRESSED | awk '{print $5}')"
echo -e "Fichier décompressé : $(ls -lh $DECOMPRESSED | awk '{print $5}')"
echo -e "Nombre de lignes    : $(wc -l < $DECOMPRESSED)"

# Suppression de l'archive
echo ""
echo -e "\n${YELLOW}Souhaitez vous effacer le fichier $COMPRESSED ? (conseillé) (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    rm "$COMPRESSED"
    echo -e "\n${GREEN}Le fichier $COMPRESSED à été supprimé${NC}"
else
    echo -e "\n${GREEN}Le fichier $COMPRESSED est conservé${NC}"
fi

# Création des fichiers d'exercice

echo ""
echo -e "\n${YELLOW}Souhaitez vous créer l'ensemble des fichiers d'exercice contenus dans le fichier $DECOMPRESSED (conseillé) ? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    # Vérifier que le venv existe
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Le venv n'existe pas encore !${NC}"
        echo -e "${YELLOW}Créez d'abord l'environnement :${NC}"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install python-chess"
        echo ""
        echo -e "${YELLOW}Puis relancez : ./$0${NC}"
    else
        source venv/bin/activate
        for i in {1..5}; do
		echo -e "\n${YELLOW}Extraction des mats en $i coups ... ${NC}"
                ./extract.py --mat-en $i --verbose $DECOMPRESSED > mat${i}.csv
		echo -e "\n${GREEN}✓ Le ficher mat${i}.csv créé ${NC}"
        done
    fi
else
    echo -e "\n${YELLOW}Le fichier $DECOMPRESSED est prêt à parser avec extract.py !${NC}"
fi

# Suppression du fichier contenant les puzzles
echo ""
echo -e "\n${YELLOW}Souhaitez vous effacer le fichier $DECOMPRESSED ? (conseillé) (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    rm "$DECOMPRESSED"
    echo -e "\n${GREEN}Le fichier $DECOMPRESSED à été supprimé${NC}"
else
    echo -e "\n${GREEN}Le fichier $DECOMPRESSED est conservé${NC}"
fi

# Statistiques
echo -e "\n${GREEN}=== Informations sur les fichiers d'exercices disponibles ===${NC}"
for i in {1..5}; do
    echo -ne "${GREEN}Nombre d'exercice de mats en $i coups : ${NC}"
    wc -l mat${i}.csv
done


echo -e "\n${GREEN}Tout s'est correctement déroulé.\nBon jeu à vous grâce à Lichess ! :)\n\n=> https://lichess.org/ ${NC}"
