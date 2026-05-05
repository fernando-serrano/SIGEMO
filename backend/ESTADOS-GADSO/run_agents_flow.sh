#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_CMD="$PWD/.venv/bin/python"
else
  echo "[INFO] No se encontro .venv. Se usara el Python disponible en PATH."
  PYTHON_CMD="${PYTHON:-python3}"
fi

GRUPO="${1:-JV}"
EXTRA_ARG="${2:-}"

case "${GRUPO^^}" in
  --HELP|-H|-\?)
    echo "Uso:"
    echo "  ./run_agents_flow.sh [JV|SELVA|TODOS]"
    echo
    echo "Ejemplos:"
    echo "  ./run_agents_flow.sh"
    echo "  ./run_agents_flow.sh SELVA"
    echo "  ./run_agents_flow.sh TODOS"
    echo "  ./run_agents_flow.sh JV --solo-login"
    exit 0
    ;;
  JV|SELVA|TODOS)
    ;;
  *)
    echo "[ERROR] Grupo invalido: $GRUPO"
    echo "Use: ./run_agents_flow.sh [JV|SELVA|TODOS]"
    exit 2
    ;;
esac

echo "[INFO] Ejecutando flujo SUCAMEC con grupo: ${GRUPO^^}"
"$PYTHON_CMD" -m src.agents_flow.cli --grupo "${GRUPO^^}" ${EXTRA_ARG:+$EXTRA_ARG}

EXIT_CODE=$?
echo "[INFO] Flujo finalizado con codigo: $EXIT_CODE"
exit "$EXIT_CODE"
