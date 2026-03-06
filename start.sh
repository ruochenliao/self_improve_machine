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
echo "[1/4] Stopping existing processes..."
pkill -f "agent_core.main" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true
pkill -f "ddns" 2>/dev/null || true
sleep 2

# Update DNS (MacBook IP may have changed)
echo "[2/4] Updating DDNS..."
PYTHONPATH="$PROJECT_ROOT/src" python -c "
from agent_core.infrastructure.ddns import update_dns
result = update_dns()
icon = '✓' if result['success'] else '✗'
print(f'  {icon} {result[\"message\"]}')
if result.get('ip'):
    print(f'  Public IP: {result[\"ip\"]}')
" 2>/dev/null || echo "  ⚠ DDNS update skipped (missing SDK or credentials)"

# Start DDNS background daemon (checks every 5 minutes)
echo "  Starting DDNS daemon..."
PYTHONPATH="$PROJECT_ROOT/src" nohup python -c "
import asyncio
from agent_core.infrastructure.ddns import ddns_daemon
asyncio.run(ddns_daemon())
" > "$DATA_DIR/ddns.log" 2>&1 &
DDNS_PID=$!
echo "  DDNS PID: $DDNS_PID"

# Start agent
echo "[3/4] Starting agent..."
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

# Start cloudflare tunnel (backup access — DDNS is primary now)
echo "[4/4] Starting Cloudflare tunnel..."
nohup cloudflared tunnel --url http://localhost:8402 --protocol http2 > "$DATA_DIR/tunnel.log" 2>&1 &
TUNNEL_PID=$!
echo "  Tunnel PID: $TUNNEL_PID"

sleep 5
TUNNEL_URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" "$DATA_DIR/tunnel.log" | head -1)

# Save tunnel URL for agent to read dynamically
echo "$TUNNEL_URL" > "$DATA_DIR/tunnel_url.txt"
echo "  Saved tunnel URL to $DATA_DIR/tunnel_url.txt"

# Read current public IP from DDNS cache
PUBLIC_IP=$(python -c "import json; print(json.load(open('$DATA_DIR/ddns_cache.json'))['ip'])" 2>/dev/null || echo "unknown")

echo ""
echo "=== SIM-Agent is LIVE ==="
echo "  Local:     http://localhost:8402"
echo "  Domain:    http://swifthelix.asia"
echo "  Public IP: http://$PUBLIC_IP:8402"
echo "  Tunnel:    $TUNNEL_URL"
echo ""
echo "  Agent log:  $DATA_DIR/agent.log"
echo "  Tunnel log: $DATA_DIR/tunnel.log"
echo "  DDNS log:   $DATA_DIR/ddns.log"
echo ""
echo "  DDNS daemon running — IP changes auto-detected every 5 min"
echo "  To stop: kill $AGENT_PID $TUNNEL_PID $DDNS_PID"
