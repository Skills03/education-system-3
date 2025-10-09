#!/bin/bash
set -e

# ============================================================================
# 🌐 IPFS + FLEEK DEPLOYMENT - PERMANENT FRONTEND (Alternative to Arweave)
# Content-addressed, decentralized, permanent via Filecoin
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🌐 IPFS + FLEEK PERMANENT DEPLOYMENT                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Install IPFS
if ! command -v ipfs &> /dev/null; then
    echo "📦 Installing IPFS..."
    wget https://dist.ipfs.tech/kubo/v0.24.0/kubo_v0.24.0_linux-amd64.tar.gz
    tar -xvzf kubo_v0.24.0_linux-amd64.tar.gz
    cd kubo
    sudo bash install.sh
    cd ..
    rm -rf kubo kubo_v0.24.0_linux-amd64.tar.gz
    echo "✅ IPFS installed"
else
    echo "✅ IPFS found: $(ipfs version --number)"
fi

echo ""

# Initialize IPFS
if [ ! -d "$HOME/.ipfs" ]; then
    echo "🔧 Initializing IPFS..."
    ipfs init
fi

# Start IPFS daemon in background
echo "🚀 Starting IPFS daemon..."
ipfs daemon &
IPFS_PID=$!
sleep 3

echo "✅ IPFS daemon running (PID: $IPFS_PID)"
echo ""

# Add files to IPFS
echo "📤 Adding frontend to IPFS..."
echo ""

# Add single file
IPFS_HASH=$(ipfs add -Q learn.html)

echo "✅ Added to IPFS!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 IPFS HASH: $IPFS_HASH"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Access via public gateways:"
echo "   https://ipfs.io/ipfs/$IPFS_HASH"
echo "   https://cloudflare-ipfs.com/ipfs/$IPFS_HASH"
echo "   https://dweb.link/ipfs/$IPFS_HASH"
echo "   https://gateway.pinata.cloud/ipfs/$IPFS_HASH"
echo ""

# Pin to remote services
echo "═══════════════════════════════════════════════════════════════"
echo "📌 PINNING TO PERMANENT STORAGE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "To make permanent, pin to these services:"
echo ""
echo "Option 1: PINATA (Free tier)"
echo "  1. Sign up at https://pinata.cloud"
echo "  2. Get API key"
echo "  3. Pin hash: $IPFS_HASH"
echo ""
echo "Option 2: FLEEK (Automatic IPFS hosting)"
echo "  1. Sign up at https://fleek.co"
echo "  2. Connect GitHub repo"
echo "  3. Auto-deploys to IPFS on push"
echo "  4. Gets ENS domain (yourapp.eth)"
echo ""
echo "Option 3: WEB3.STORAGE (Free 5GB)"
echo "  1. Go to https://web3.storage"
echo "  2. Upload files"
echo "  3. Permanent Filecoin storage"
echo ""

# Save hash
echo "$IPFS_HASH" > ipfs-deployment.txt
echo "https://ipfs.io/ipfs/$IPFS_HASH" >> ipfs-deployment.txt

echo "💾 IPFS hash saved to: ipfs-deployment.txt"
echo ""

# Stop daemon
kill $IPFS_PID

echo "═══════════════════════════════════════════════════════════════"
echo "🔒 IMMUTABILITY:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "✓ Content-addressed (hash = content fingerprint)"
echo "✓ Change 1 byte = completely different hash"
echo "✓ Original hash always serves original content"
echo "✓ Decentralized (no single point of failure)"
echo "✓ Pin to Filecoin = permanent blockchain storage"
echo ""
echo "⚠️  Without pinning service, content may disappear"
echo "   → Pin to Pinata/Fleek/Web3.Storage for permanence"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎯 NEXT: Pin to permanent service above"
echo "═══════════════════════════════════════════════════════════════"
