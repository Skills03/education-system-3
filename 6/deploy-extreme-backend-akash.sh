#!/bin/bash
set -e

# ============================================================================
# ⛓️  MOST EXTREME BACKEND DEPLOYMENT - AKASH + DELETE KEY
# Backend on blockchain, then DELETE private key = PERMANENT LOCK
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   ⛓️  AKASH BLOCKCHAIN BACKEND - PERMANENT LOCK             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

IMAGE_SHA="skills003/teacher-app@sha256:43b75bb596c36e54194899f6c0f2b190732e58cffeff497703f532faccbf4a65"

echo "📦 Docker Image: ${IMAGE_SHA:0:30}..."
echo ""

# Install Akash CLI
if ! command -v akash &> /dev/null; then
    echo "📦 Installing Akash CLI..."
    curl -sSfL https://raw.githubusercontent.com/akash-network/node/master/install.sh | sh
    export PATH="$PATH:./bin"
    sudo mv ./bin/akash /usr/local/bin/ 2>/dev/null || true
    echo "✅ Akash CLI installed"
else
    echo "✅ Akash CLI found: $(akash version | head -1)"
fi

echo ""

# Environment setup
export AKASH_NET="https://raw.githubusercontent.com/akash-network/net/main/mainnet"
export AKASH_NODE="https://rpc.akash.forbole.com:443"
export AKASH_CHAIN_ID="akashnet-2"

echo "═══════════════════════════════════════════════════════════════"
echo "STEP 1: CREATE WALLET"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ ! -f "$HOME/.akash-key-backup.txt" ]; then
    echo "Creating new Akash wallet..."
    echo ""
    echo "⚠️  SAVE THE 24-WORD SEED PHRASE - THIS IS YOUR ONLY BACKUP!"
    echo ""

    akash keys add deployer --keyring-backend os > $HOME/.akash-key-backup.txt 2>&1

    echo ""
    echo "✅ Wallet created and saved to: $HOME/.akash-key-backup.txt"
    echo ""
    echo "⚠️  IMPORTANT: Backup this file securely!"
    echo "   cat $HOME/.akash-key-backup.txt"
    echo ""
else
    echo "✅ Wallet already exists"
fi

# Get address
export AKASH_KEY_NAME=deployer
AKASH_ADDRESS=$(akash keys show $AKASH_KEY_NAME -a --keyring-backend os)

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 2: FUND WALLET"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "💰 Your Akash address:"
echo "   $AKASH_ADDRESS"
echo ""
echo "You need ~5 AKT (~$10-20 USD) to deploy"
echo ""
echo "Buy AKT from:"
echo "  • Osmosis: https://app.osmosis.zone"
echo "  • Kraken"
echo "  • Gate.io"
echo ""
echo "Checking balance..."

BALANCE=$(akash query bank balances $AKASH_ADDRESS --node $AKASH_NODE -o json 2>/dev/null | jq -r '.balances[0].amount' || echo "0")
BALANCE_AKT=$(echo "scale=2; $BALANCE / 1000000" | bc -l)

echo "   Balance: $BALANCE_AKT AKT"
echo ""

if (( $(echo "$BALANCE_AKT < 0.5" | bc -l) )); then
    echo "⚠️  Insufficient balance. Need ~5 AKT to deploy."
    echo ""
    read -p "Press ENTER when wallet is funded, or Ctrl+C to exit..."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 3: CREATE DEPLOYMENT MANIFEST"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Create SDL (Stack Definition Language) file
cat > akash-deploy.yaml <<EOF
---
version: "2.0"

services:
  teacher:
    # Deploy by EXACT SHA256 - immutable!
    image: ${IMAGE_SHA}
    expose:
      - port: 5000
        as: 80
        to:
          - global: true

profiles:
  compute:
    teacher:
      resources:
        cpu:
          units: 1
        memory:
          size: 1Gi
        storage:
          size: 1Gi

  placement:
    akash:
      pricing:
        teacher:
          denom: uakt
          amount: 1000

deployment:
  teacher:
    akash:
      profile: teacher
      count: 1
EOF

echo "✅ Deployment manifest created: akash-deploy.yaml"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "STEP 4: DEPLOY TO BLOCKCHAIN"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  This creates a BLOCKCHAIN TRANSACTION"
echo "   • Deployment recorded on Akash blockchain"
echo "   • Visible at: https://stats.akash.network"
echo "   • Cannot be hidden or deleted"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "🚀 Creating deployment on blockchain..."

# Create deployment
akash tx deployment create akash-deploy.yaml \
  --from $AKASH_KEY_NAME \
  --node $AKASH_NODE \
  --chain-id $AKASH_CHAIN_ID \
  --keyring-backend os \
  --fees 25000uakt \
  --gas auto \
  --gas-adjustment 1.5 \
  -y

echo ""
echo "⏳ Waiting for transaction confirmation..."
sleep 10

# Get deployment sequence
DSEQ=$(akash query deployment list \
  --owner $AKASH_ADDRESS \
  --node $AKASH_NODE \
  -o json | jq -r '.deployments[0].deployment.deployment_id.dseq')

echo ""
echo "✅ Deployment created on blockchain!"
echo "   Sequence: $DSEQ"
echo ""

# Save deployment info
cat > akash-deployment-info.txt <<EOF
Deployment Sequence: $DSEQ
Owner Address: $AKASH_ADDRESS
Blockchain: Akash mainnet
Transaction visible at: https://stats.akash.network/deployments/$DSEQ
EOF

echo "💾 Deployment info saved to: akash-deployment-info.txt"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "STEP 5: WAIT FOR BIDS & CREATE LEASE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "⏳ Waiting for provider bids (30 seconds)..."
sleep 30

# List bids
echo ""
echo "Available providers:"
akash query market bid list \
  --owner $AKASH_ADDRESS \
  --node $AKASH_NODE \
  --dseq $DSEQ

echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo ""
echo "1. Choose a provider from the list above"
echo "2. Create lease with:"
echo ""
echo "   export AKASH_PROVIDER=<provider-address>"
echo "   akash tx market lease create \\"
echo "     --dseq $DSEQ \\"
echo "     --gseq 1 \\"
echo "     --oseq 1 \\"
echo "     --provider \$AKASH_PROVIDER \\"
echo "     --from $AKASH_KEY_NAME \\"
echo "     --node $AKASH_NODE \\"
echo "     --chain-id $AKASH_CHAIN_ID \\"
echo "     --keyring-backend os \\"
echo "     --fees 25000uakt -y"
echo ""
echo "3. Check status:"
echo "   akash provider lease-status \\"
echo "     --node $AKASH_NODE \\"
echo "     --dseq $DSEQ \\"
echo "     --from $AKASH_KEY_NAME \\"
echo "     --provider \$AKASH_PROVIDER"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "🔥 STEP 6: DELETE PRIVATE KEY (PERMANENT LOCK)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "⚠️⚠️⚠️  EXTREME WARNING  ⚠️⚠️⚠️"
echo ""
echo "After lease is active, you can DELETE YOUR PRIVATE KEY"
echo "This makes the deployment PERMANENTLY LOCKED:"
echo ""
echo "✓ Cannot update deployment"
echo "✓ Cannot stop deployment"
echo "✓ Cannot retrieve deposit"
echo "✓ Runs until lease expires"
echo "✓ NOBODY can change it (not even you)"
echo ""
echo "Command to delete key (DO NOT RUN YET):"
echo "   akash keys delete $AKASH_KEY_NAME --keyring-backend os"
echo ""
echo "⚠️  ONLY do this AFTER:"
echo "   • Lease is active and working"
echo "   • You've tested the deployment"
echo "   • You're 100% sure you want it permanent"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT ON BLOCKCHAIN COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
