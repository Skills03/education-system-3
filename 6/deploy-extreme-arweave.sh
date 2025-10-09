#!/bin/bash
set -e

# ============================================================================
# 🔗 MOST EXTREME DEPLOYMENT - ARWEAVE (PERMANENT FRONTEND)
# Frontend stored FOREVER on blockchain, cannot be deleted or modified
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🔗 ARWEAVE PERMANENT DEPLOYMENT - FRONTEND FOREVER        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  This deploys your frontend to PERMANENT storage (200+ years)"
echo "⚠️  ONE-TIME PAYMENT, CANNOT DELETE, CANNOT MODIFY"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Install Arweave Deploy CLI
echo "📦 Installing Arweave deploy tool..."
npm install -g arweave-deploy arkb

echo "✅ Arweave tools installed"
echo ""

# Check for AR wallet
if [ ! -f "arweave-wallet.json" ]; then
    echo "═══════════════════════════════════════════════════════════════"
    echo "⚠️  NO ARWEAVE WALLET FOUND"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "You need an Arweave wallet with AR tokens to deploy."
    echo ""
    echo "STEP 1: Create wallet at https://arweave.app/"
    echo "STEP 2: Download keyfile as 'arweave-wallet.json'"
    echo "STEP 3: Buy AR tokens (~0.01 AR = $0.50 for small files)"
    echo "        • Exchanges: Binance, Huobi, Gate.io"
    echo "        • Onramps: https://arweave.org/buy"
    echo ""
    echo "STEP 4: Place wallet file here:"
    echo "        /home/mahadev/Desktop/dev/education/6/arweave-wallet.json"
    echo ""
    echo "Then re-run this script."
    echo "═══════════════════════════════════════════════════════════════"
    exit 1
fi

echo "✅ Arweave wallet found"
echo ""

# Get wallet address and balance
WALLET_ADDRESS=$(cat arweave-wallet.json | jq -r '.n' | sha256sum | cut -d' ' -f1)
echo "💰 Wallet: ${WALLET_ADDRESS:0:20}..."

# Check balance
echo "📊 Checking AR balance..."
BALANCE=$(curl -s "https://arweave.net/wallet/$WALLET_ADDRESS/balance" || echo "0")
BALANCE_AR=$(echo "scale=4; $BALANCE / 1000000000000" | bc -l)

echo "   Balance: $BALANCE_AR AR"

if (( $(echo "$BALANCE_AR < 0.001" | bc -l) )); then
    echo ""
    echo "⚠️  WARNING: Low balance. You need ~0.01 AR ($0.50) to deploy."
    echo "   Buy AR at: https://arweave.org/buy"
    echo ""
    read -p "Continue anyway? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        exit 1
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📤 DEPLOYING TO ARWEAVE (PERMANENT)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Create a modified frontend that points to backend
# (or make it standalone if desired)
echo "📝 Preparing frontend files..."

# Option 1: Deploy single HTML file
echo ""
echo "Choose deployment type:"
echo "1) Single file (learn.html only) - Cheapest"
echo "2) Full frontend directory - More expensive"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    # Deploy single file
    echo ""
    echo "🚀 Uploading learn.html to Arweave..."
    echo ""

    TX_ID=$(arkb deploy learn.html \
        --wallet arweave-wallet.json \
        --auto-confirm \
        | grep -oP 'https://arweave.net/\K[A-Za-z0-9_-]+')

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ DEPLOYED TO ARWEAVE - PERMANENT FOREVER!"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "🌐 Permanent URL:"
    echo "   https://arweave.net/$TX_ID"
    echo ""
    echo "🔗 Alternative gateways:"
    echo "   https://arweave.dev/$TX_ID"
    echo "   https://$TX_ID.arweave.net"
    echo ""
    echo "📋 Transaction ID: $TX_ID"
    echo ""
    echo "🔒 IMMUTABILITY GUARANTEES:"
    echo "   ✓ Stored for 200+ years minimum"
    echo "   ✓ Cannot be deleted"
    echo "   ✓ Cannot be modified"
    echo "   ✓ Content-addressed (hash = URL)"
    echo "   ✓ Decentralized storage (miners)"
    echo "   ✓ One-time payment, no recurring fees"
    echo ""
    echo "⚠️  THE FRONTEND IS NOW PERMANENT"
    echo "   To change anything → Must deploy new version with new hash"
    echo "═══════════════════════════════════════════════════════════════"

    # Save deployment info
    echo "$TX_ID" > arweave-deployment.txt
    echo "https://arweave.net/$TX_ID" >> arweave-deployment.txt

    echo ""
    echo "💾 Deployment saved to: arweave-deployment.txt"

else
    # Deploy directory
    echo ""
    echo "🚀 Uploading full frontend to Arweave..."
    echo ""

    # Create manifest and deploy
    arkb deploy-dir . \
        --wallet arweave-wallet.json \
        --index-file learn.html \
        --auto-confirm
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎯 NEXT STEPS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. BACKEND: Deploy backend to Akash (most immutable)"
echo "   → See: deploy-extreme-backend-akash.sh"
echo ""
echo "2. DOMAIN: Map to ENS domain (optional, blockchain DNS)"
echo "   → yourapp.eth → Arweave hash"
echo ""
echo "3. LOCK IT FOREVER:"
echo "   → Delete source code: rm -rf /home/mahadev/Desktop/dev/education/6"
echo "   → Delete wallet: rm arweave-wallet.json"
echo "   → Now NOBODY can upload new version to same hash"
echo ""
echo "═══════════════════════════════════════════════════════════════"
