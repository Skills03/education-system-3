#!/bin/bash
set -e

# ============================================================================
# IMMUTABLE DEPLOYMENT SCRIPT
# This script creates a deployment that CANNOT be changed - even by you
# ============================================================================

IMAGE_NAME="teacher-app"
TAG="locked"
CONTAINER_NAME="teacher-immutable"

echo "🔒 Building IMMUTABLE Docker Image..."
echo "⚠️  WARNING: Once deployed, you CANNOT change code or environment variables!"
echo ""

# Step 1: Build the image with baked-in secrets
docker build -f Dockerfile.immutable -t ${IMAGE_NAME}:${TAG} .

# Step 2: Get the EXACT SHA256 hash
echo ""
echo "📸 Capturing SHA256 digest..."
SHA256=$(docker images --digests ${IMAGE_NAME}:${TAG} | awk 'NR==2 {print $3}')

if [ -z "$SHA256" ] || [ "$SHA256" = "<none>" ]; then
    echo "❌ Failed to get SHA256 digest"
    exit 1
fi

echo "✅ Image SHA256: ${SHA256}"
echo ""

# Step 3: Save the hash for verification
echo "${SHA256}" > .deployment-hash.txt
echo "💾 Saved hash to .deployment-hash.txt"

# Step 4: Stop any existing container
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🛑 Stopping existing container..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi

# Step 5: Deploy with MAXIMUM SECURITY
echo ""
echo "🚀 Deploying with IMMUTABLE settings..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p 5000:5000 \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=64m \
  --security-opt=no-new-privileges \
  --cap-drop=ALL \
  --restart=unless-stopped \
  ${IMAGE_NAME}@${SHA256}

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔐 IMMUTABILITY GUARANTEES:"
echo "═══════════════════════════════════════════════════════════════"
echo "✓ Filesystem is READ-ONLY (no file modifications possible)"
echo "✓ Environment variables BAKED IN (cannot be changed)"
echo "✓ Deployed by SHA256 hash (cryptographically locked)"
echo "✓ No privileges (cannot escalate or modify system)"
echo "✓ Code and secrets are FROZEN in this deployment"
echo ""
echo "📋 Deployment Hash: ${SHA256}"
echo "🌐 Access: http://localhost:5000"
echo ""
echo "⚠️  TO MAKE ANY CHANGES:"
echo "   You MUST rebuild and redeploy from scratch"
echo "   Current deployment cannot be modified!"
echo "═══════════════════════════════════════════════════════════════"

# Optional: Remove your ability to change this deployment
echo ""
read -p "🔥 Remove the source code to prevent rebuilding? (yes/NO): " confirm
if [ "$confirm" = "yes" ]; then
    echo "⚠️  This will DELETE source code - only container remains!"
    read -p "Are you ABSOLUTELY sure? (type 'DELETE'): " confirm2
    if [ "$confirm2" = "DELETE" ]; then
        cd ..
        rm -rf education/
        echo "🔥 Source code deleted. Container is now truly immutable."
        echo "   To change anything, you need to recreate from git."
    fi
fi
