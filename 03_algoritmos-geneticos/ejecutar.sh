#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

case "${1:-}" in
  binario)
    shift
    exec python3 proyecto1/proyecto1.py "$@"
    ;;
  real)
    shift
    exec python3 proyecto2/proyecto2.py "$@"
    ;;
  *)
    echo 'Uso: ./ejecutar.sh binario|real [opciones]'
    echo 'Visualización HTML: proyecto1/visualizacion.html'
    exit 2
    ;;
esac
