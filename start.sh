#!/bin/bash
# Start the SIM-Agent and Cloudflare tunnel
# Usage: ./start.sh

set -e
cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"
DATA_DIR="$PROJECT_ROOT/data"
mkdir -p "$DATA_DIR"

echo "=== SIM-Agent Launcher ==="

# Kill existing processes
echo "[1/3] Stopping existing processes..."
pkill -f "agent_core.main" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 2

# Start agent
echo "[2/3] Starting agent..."
TOKENIZERS_PARALLELISM=false nohup python -c "
import sys; sys.path.insert(0, 'src')
from agent_core.main import boot
import asyncio
asyncio.run(boot())
" > "$DATA_DIR/agent.log" 2>&1 &
AGENT_PID=$!
echo "  Agent PID: $AGENT_PID"

# Wait for API server to come up
echo "  Waiting for API server..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8402/health > /dev/null 2>&1; then
        echo "  API server is up!"
        break
    fi
    sleep 1
done

# Start cloudflare tunnel
echo "[3/3] Starting Cloudflare tunnel..."
nohup cloudflared tunnel --url http://localhost:8402 --protocol http2 > "$DATA_DIR/tunnel.log" 2>&1 &
TUNNEL_PID=$!
echo "  Tunnel PID: $TUNNEL_PID"

sleep 5
TUNNEL_URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" "$DATA_DIR/tunnel.log" | head -1)

echo ""
echo "=== SIM-Agent is LIVE ==="
echo "  Local:  http://localhost:8402"
echo "  Public: $TUNNEL_URL"
echo "  Agent log: $DATA_DIR/agent.log"
echo "  Tunnel log: $DATA_DIR/tunnel.log"
echo ""
echo "  To stop: kill $AGENT_PID $TUNNEL_PID"
