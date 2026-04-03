#!/bin/bash

# Hook automatique pour réanalyser GitNexus après chaque modification de fichier
# Se déclenche après les outils: Edit, Write, git commit, git merge

# Récupérer le nom de l'outil utilisé
TOOL_NAME="$1"

# Vérifier si c'est un outil qui modifie des fichiers
case "$TOOL_NAME" in
    "Edit"|"Write"|"NotebookEdit")
        echo "🔄 Fichier modifié détecté avec $TOOL_NAME - Lancement de l'analyse GitNexus..."

        # Utiliser l'image Docker personnalisée pour l'analyse
        docker run --rm \
            -v "/Users/bilalmeziane/Desktop/Meziane_Monitoring:/workspace" \
            -w /workspace \
            gitnexus:latest 2>&1 | head -n 20

        if [ $? -eq 0 ]; then
            echo "✅ Analyse GitNexus terminée avec succès"
        else
            echo "⚠️  Erreur lors de l'analyse GitNexus"
        fi
        ;;

    "Bash")
        # Vérifier si c'est un commit ou merge git
        BASH_COMMAND="$2"
        if echo "$BASH_COMMAND" | grep -qE "git (commit|merge)"; then
            echo "🔄 Opération Git détectée - Lancement de l'analyse GitNexus..."

            docker run --rm \
                -v "/Users/bilalmeziane/Desktop/Meziane_Monitoring:/workspace" \
                -w /workspace \
                gitnexus:latest 2>&1 | head -n 20

            if [ $? -eq 0 ]; then
                echo "✅ Analyse GitNexus post-commit terminée"
            else
                echo "⚠️  Erreur lors de l'analyse GitNexus post-commit"
            fi
        fi
        ;;
esac

exit 0
