# 🔗 BLOCKCHAIN DEPLOYMENT - AKASH NETWORK

## Most Extreme Immutable Deployment

Akash Network is a **decentralized cloud** built on blockchain. Deployments are:
- Governed by blockchain consensus
- Cannot be changed without cryptographic signature
- Censorship-resistant
- Truly decentralized (no single owner)

---

## Why Akash is MOST Immutable

| Feature | Traditional Cloud | Akash Blockchain |
|---------|------------------|------------------|
| Can admin change? | ✅ Yes (with credentials) | ❌ No (needs private key) |
| Can provider change? | ✅ Yes (AWS/GCP can) | ❌ No (consensus required) |
| Centralized control? | ✅ Yes | ❌ No (decentralized) |
| Can be taken down? | ✅ Yes (by provider) | ❌ Extremely difficult |
| Immutable record? | ❌ Logs can be deleted | ✅ On blockchain forever |

---

## Prerequisites

1. **AKT Tokens** (~5 AKT = $10-20 USD)
   - Buy on crypto exchanges (Kraken, Osmosis)
   - Needed for deployment deposit

2. **Keplr Wallet** (browser extension)
   - https://www.keplr.app/
   - Stores your blockchain private key

3. **Akash CLI**
   ```bash
   # Install Akash CLI
   curl -sSfL https://raw.githubusercontent.com/akash-network/node/master/install.sh | sh
   ```

---

## Step-by-Step Deployment

### 1. Install Akash CLI

```bash
cd /tmp
curl -sSfL https://raw.githubusercontent.com/akash-network/node/master/install.sh | sh
sudo mv ./bin/akash /usr/local/bin/
akash version
```

### 2. Set up Wallet

```bash
# Create new wallet (SAVE THE MNEMONIC SEED!!!)
akash keys add immutable-deployer

# Or import existing wallet
akash keys add immutable-deployer --recover
# (then enter your 24-word seed phrase)

# Get your address
export AKASH_KEY_NAME=immutable-deployer
export AKASH_KEYRING_BACKEND=os
akash keys show $AKASH_KEY_NAME -a
```

### 3. Fund Wallet

```bash
# Get your address
AKASH_ADDRESS=$(akash keys show $AKASH_KEY_NAME -a)
echo "Send AKT tokens to: $AKASH_ADDRESS"

# Check balance
akash query bank balances $AKASH_ADDRESS --node https://rpc.akash.forbole.com:443
```

### 4. Create Deployment Manifest

Create `deploy.yaml`:

```yaml
---
version: "2.0"

services:
  teacher:
    # Deploy by EXACT SHA256 - immutable!
    image: teacher@sha256:9a8636b60b7100df208567c2cba52640e29a9b488a95f8f92da5978cd13c36ca
    expose:
      - port: 5000
        as: 80
        to:
          - global: true
        accept:
          - "teacher-immutable.akash.network"

profiles:
  compute:
    teacher:
      resources:
        cpu:
          units: 0.5
        memory:
          size: 512Mi
        storage:
          size: 1Gi
  placement:
    akash:
      pricing:
        teacher:
          denom: uakt
          amount: 100  # 0.0001 AKT per block

deployment:
  teacher:
    akash:
      profile: teacher
      count: 1
```

### 5. Deploy to Akash (Blockchain)

```bash
# Set environment
export AKASH_NET="https://raw.githubusercontent.com/akash-network/net/main/mainnet"
export AKASH_NODE="https://rpc.akash.forbole.com:443"
export AKASH_CHAIN_ID="akashnet-2"

# Create deployment (writes to blockchain!)
akash tx deployment create deploy.yaml \
  --from $AKASH_KEY_NAME \
  --node $AKASH_NODE \
  --chain-id $AKASH_CHAIN_ID \
  --fees 5000uakt \
  --gas auto

# Get deployment ID
export AKASH_DSEQ=$(akash query deployment list \
  --owner $AKASH_ADDRESS \
  --node $AKASH_NODE \
  --output json | jq -r '.deployments[0].deployment.deployment_id.dseq')

echo "Deployment Sequence: $AKASH_DSEQ"

# Wait for bids from providers
akash query market bid list \
  --owner $AKASH_ADDRESS \
  --node $AKASH_NODE \
  --dseq $AKASH_DSEQ

# Accept a bid (choose provider)
export AKASH_PROVIDER=<provider-address-from-bids>
export AKASH_GSEQ=1
export AKASH_OSEQ=1

akash tx market lease create \
  --dseq $AKASH_DSEQ \
  --gseq $AKASH_GSEQ \
  --oseq $AKASH_OSEQ \
  --provider $AKASH_PROVIDER \
  --from $AKASH_KEY_NAME \
  --node $AKASH_NODE \
  --chain-id $AKASH_CHAIN_ID \
  --fees 5000uakt

# Get your app URL
akash provider lease-status \
  --node $AKASH_NODE \
  --dseq $AKASH_DSEQ \
  --from $AKASH_KEY_NAME \
  --provider $AKASH_PROVIDER
```

### 6. Your App is Now on the Blockchain!

The deployment is recorded on the Akash blockchain. To change it:
- Requires your private key (cryptographic signature)
- Creates new blockchain transaction
- Publicly auditable on blockchain explorer
- Old version stays in blockchain history forever

---

## Extreme Lockdown: Delete Private Key

**ULTIMATE IMMUTABILITY:**

After deploying, if you **delete your private key**, the deployment becomes:
- ❌ Unchangeable by ANYONE (including you)
- ❌ Cannot be stopped
- ❌ Cannot be updated
- ✅ Runs until lease expires

```bash
# Export deployment info first
echo "DSEQ: $AKASH_DSEQ" > deployment-record.txt
echo "Provider: $AKASH_PROVIDER" >> deployment-record.txt

# DELETE YOUR KEY (IRREVERSIBLE!!!)
akash keys delete $AKASH_KEY_NAME

# Now deployment is LOCKED FOREVER
# Can only view, cannot modify
```

⚠️ **WARNING**: This is PERMANENT. You cannot:
- Update the app
- Stop the deployment
- Renew the lease (will expire)
- Get your deposit back

---

## Blockchain Immutability Verification

### View Deployment on Blockchain

```bash
# Your deployment is public on the blockchain
curl "https://api.akash.forbole.com/akash/deployment/v1beta3/deployments/list" \
  | jq ".deployments[] | select(.deployment.deployment_id.owner==\"$AKASH_ADDRESS\")"
```

### View on Block Explorer

https://akash.bigdipper.live/

Search for your address - see all deployments publicly

---

## Comparison: Akash vs Cloud

### Google Cloud Run
- ✅ Easy deployment
- ✅ Reliable
- ❌ Google can shut down
- ❌ Requires continuous payment
- ❌ Centralized

### Akash Network
- ✅ Decentralized (censorship-resistant)
- ✅ Blockchain-verified immutability
- ✅ Public audit trail
- ❌ More complex setup
- ❌ Fewer providers
- ⚠️ Costs AKT tokens

---

## Cost Estimate

**Deployment:**
- Initial fee: ~0.005 AKT ($0.10)
- Monthly lease: ~20-50 AKT ($4-10)
- Deposit: ~5 AKT (refundable)

**Total:** ~$5-15/month

---

## When To Use Akash

✅ **Use Akash When:**
- You need censorship resistance
- You want blockchain-verified deployments
- Maximum decentralization required
- Compliance needs immutable audit trail

❌ **Don't Use Akash When:**
- You need frequent updates
- You want simplest setup
- You need maximum reliability (99.99% SLA)

---

## Recovery

If you lose your private key:
- ✅ App keeps running (until lease expires)
- ❌ Cannot update deployment
- ❌ Cannot close lease
- ❌ Cannot retrieve deposit

**SOLUTION**: Save your 24-word mnemonic seed phrase securely!

---

## Summary

Akash Network provides **blockchain-level immutability**:

1. Deployment manifest on-chain (public)
2. Changes require cryptographic signature
3. History preserved forever on blockchain
4. Decentralized (no single point of control)
5. Can make truly permanent by deleting key

This is the **most extreme** immutable deployment possible.

---

## Quick Start Script

```bash
#!/bin/bash
# Quick Akash deployment

# 1. Install
curl -sSfL https://raw.githubusercontent.com/akash-network/node/master/install.sh | sh

# 2. Create wallet
akash keys add deployer

# 3. Send AKT to wallet address shown

# 4. Create deploy.yaml (see above)

# 5. Deploy
akash tx deployment create deploy.yaml \
  --from deployer \
  --node https://rpc.akash.forbole.com:443 \
  --chain-id akashnet-2 \
  --fees 5000uakt

# 6. Accept bid and create lease
# (follow interactive prompts)

echo "🔗 Deployment on blockchain!"
```

---

**For support:** https://discord.gg/akash
**Docs:** https://docs.akash.network/
