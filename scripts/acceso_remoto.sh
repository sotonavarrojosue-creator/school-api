#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Configuración de acceso remoto para school-api
# Opciones: tailscale (recomendado) | ngrok | cloudflared
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

MODO="${1:-tailscale}"
PUERTO="${2:-8000}"

echo "🔧 Configurando acceso remoto para school-api (puerto $PUERTO)"

case "$MODO" in
  tailscale)
    echo "📡 Usando Tailscale (Funnel) — recomiendo esta opción"
    echo ""
    if command -v tailscale &>/dev/null; then
      echo "✅ Tailscale detectado"
      echo "   Para exponer tu API:"
      echo "   sudo tailscale funnel --bg $PUERTO"
      echo ""
      echo "   Para servir solo dentro de tu tailnet:"
      echo "   sudo tailscale serve --bg $PUERTO"
    else
      echo "⚠️  Tailscale no instalado."
      echo "   curl -fsSL https://tailscale.com/install.sh | sh"
    fi
    ;;

  ngrok)
    echo "📡 Usando ngrok"
    echo ""
    if command -v ngrok &>/dev/null; then
      echo "✅ ngrok detectado"
      echo "   ngrok http $PUERTO"
      echo ""
      echo "   📌 Consejo: usa la URL fija con ngrok.yml:"
      echo '   ngrok http --domain=tufijo.ngrok-free.app 8000'
    else
      echo "⚠️  ngrok no instalado."
      echo "   Descarga: https://ngrok.com/download"
    fi
    ;;

  cloudflared)
    echo "📡 Usando Cloudflare Tunnel"
    echo ""
    if command -v cloudflared &>/dev/null; then
      echo "✅ cloudflared detectado"
      echo "   cloudflared tunnel --url http://localhost:$PUERTO"
    else
      echo "⚠️  cloudflared no instalado."
      echo "   Descarga: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
    fi
    ;;

  *)
    echo "Uso: $0 {tailscale|ngrok|cloudflared} [puerto]"
    exit 1
    ;;
esac

echo ""
echo "🚀 Una vez expuesto, actualiza el .env del dashboard:"
echo "   VITE_API_URL=https://tufijo.ngrok.app  (o tu tailscale IP)"
