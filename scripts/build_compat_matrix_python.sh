#!/bin/bash
# scripts/test_matrix_final.sh
# Teste toutes les versions de Python de 3.9 à 3.20
# Continue malgré les échecs — s'arrête seulement si aucune nouvelle version n'est trouvée

# Désactivation de -e pour gérer les erreurs manuellement
set -u
set -o pipefail

# Chemins absolus
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.test_matrix_venv"
RESULTS_FILE="$REPO_ROOT/docs/compatibility_table.md"
LOG_DIR="$REPO_ROOT/logs"
LOG="$LOG_DIR/execution.log"

# On se place à la racine pour que toutes les commandes relatives fonctionnent
cd "$REPO_ROOT" || exit 1

mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$RESULTS_FILE")"
rm -f "$LOG"
touch "$LOG"

echo "🔧 Démarrage du script de test de compatibilité Python" | tee -a "$LOG"
echo "📂 Racine du projet : $REPO_ROOT" | tee -a "$LOG"

# 1. Créer un environnement pour le script lui-même
echo "📊 Préparation de l'environnement de contrôle..." | tee -a "$LOG"
if [ ! -d "$VENV_DIR" ]; then
    uv venv "$VENV_DIR" &>> "$LOG"
fi

# Fonction pour activer le venv
activate_venv() {
    local path="$1"
    if [ -f "$path/bin/activate" ]; then
        # shellcheck disable=SC1091
        source "$path/bin/activate"
    elif [ -f "$path/Scripts/activate" ]; then
        # shellcheck disable=SC1091
        source "$path/Scripts/activate"
    else
        return 1
    fi
}

activate_venv "$VENV_DIR" || { echo "❌ Impossible d'activer le venv de contrôle"; exit 1; }
echo "✅ Environnement de contrôle prêt : $(python --version)" | tee -a "$LOG"

# 2. Vérifier uv
if ! uv python --help &>/dev/null; then
    echo "❌ Votre version de uv ne supporte pas 'uv python'." | tee -a "$LOG"
    exit 1
fi

# 3. Configuration
PYTHON_VERSIONS=("3.9" "3.10" "3.11" "3.12" "3.13" "3.14" "3.15" "3.16" "3.17" "3.18" "3.19" "3.20")
echo "| Version Python | Résultat | Notes |" > "$RESULTS_FILE"
echo "|----------------|----------|-------|" >> "$RESULTS_FILE"

SUCCESS_COUNT=0
TOTAL_COUNT=0
CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE=2 

# 4. Boucle de test
for PY_VER in "${PYTHON_VERSIONS[@]}"; do
    echo "---" | tee -a "$LOG"
    echo "🔍 Analyse de Python $PY_VER..." | tee -a "$LOG"

    # Tentative d'installation
    if ! uv python install "$PY_VER" &>> "$LOG"; then
        echo "⏭️  $PY_VER non disponible ou erreur d'installation." | tee -a "$LOG"
        ((CONSECUTIVE_FAILURES++))
        if [ $CONSECUTIVE_FAILURES -ge $MAX_CONSECUTIVE ]; then
            echo "🔚 Fin de liste (plusieurs versions absentes de suite)." | tee -a "$LOG"
            break
        fi
        continue
    fi

    CONSECUTIVE_FAILURES=0
    ((TOTAL_COUNT++))
    
    TEST_LOG="$LOG_DIR/test_$PY_VER.log"
    echo "🧪 Test pour Python $PY_VER (Logs: $TEST_LOG)" | tee -a "$LOG"

    # Nettoyage
    rm -rf ".venv_test_$PY_VER"

    # Exécution isolée
    # On utilise un fichier de statut car les variables dans ( ) ne remontent pas
    STATUS_FILE=".status_$PY_VER"
    echo "INIT" > "$STATUS_FILE"

    (
        # On essaie de créer le venv
        if ! uv venv ".venv_test_$PY_VER" --python "$PY_VER" &> "$TEST_LOG"; then
            echo "VENV_FAIL" > "$STATUS_FILE"
            exit 0
        fi

        # On active
        if ! activate_venv ".venv_test_$PY_VER" &>> "$TEST_LOG"; then
            echo "ACT_FAIL" > "$STATUS_FILE"
            exit 0
        fi
        
        # Installation du projet (en mode éditable)
        if ! uv pip install -e . &>> "$TEST_LOG"; then
            echo "INST_FAIL" > "$STATUS_FILE"
            exit 0
        fi

        # Installation de pytest
        uv pip install pytest &>> "$TEST_LOG"

        # Lancement des tests
        if pytest tests/smoke/ -v --tb=short &>> "$TEST_LOG"; then
            echo "SUCCESS" > "$STATUS_FILE"
        else
            echo "TEST_FAIL" > "$STATUS_FILE"
        fi
    )

    RESULT=$(cat "$STATUS_FILE")
    rm -f "$STATUS_FILE"

    case "$RESULT" in
        "SUCCESS")
            echo "| $PY_VER | ✅ Succès | Tests passés |" >> "$RESULTS_FILE"
            echo "✅ Succès pour $PY_VER" | tee -a "$LOG"
            ((SUCCESS_COUNT++))
            ;;
        "VENV_FAIL")
            echo "| $PY_VER | ❌ Échec | Erreur création venv |" >> "$RESULTS_FILE"
            echo "❌ Échec venv pour $PY_VER" | tee -a "$LOG"
            ;;
        "INST_FAIL")
            echo "| $PY_VER | ❌ Échec | Installation échouée |" >> "$RESULTS_FILE"
            echo "❌ Échec installation pour $PY_VER" | tee -a "$LOG"
            ;;
        *)
            echo "| $PY_VER | ❌ Échec | Tests en erreur |" >> "$RESULTS_FILE"
            echo "❌ Échec tests pour $PY_VER" | tee -a "$LOG"
            ;;
    esac

    # Nettoyage final de l'environnement de test
    rm -rf ".venv_test_$PY_VER"
done

# Résumé final
echo "" >> "$RESULTS_FILE"
echo "### Résumé" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "✅ $SUCCESS_COUNT / $TOTAL_COUNT versions testées avec succès." >> "$RESULTS_FILE"
echo "📅 Mis à jour le : $(date)" >> "$RESULTS_FILE"

echo "✨ Terminé ! Rapport : $RESULTS_FILE" | tee -a "$LOG"