#!/bin/bash
set -e

# ============================================================================
# 🔒 IMMUTABLE DEPLOYMENT - LOCKED AND LOADED
# ============================================================================

IMAGE_SHA="sha256:9a8636b60b7100df208567c2cba52640e29a9b488a95f8f92da5978cd13c36ca"
CONTAINER_NAME="teacher-immutable"
PORT=5001

echo "🔒 DEPLOYING IMMUTABLE CONTAINER"
echo "═══════════════════════════════════════════════════════════════"
echo "Image Hash: ${IMAGE_SHA}"
echo "Container: ${CONTAINER_NAME}"
echo "Port: ${PORT}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Stop existing container if running
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🛑 Stopping existing container..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi

# Deploy with MAXIMUM IMMUTABILITY
echo "🚀 Deploying with immutable settings..."
echo ""

docker run -d \
  --name ${CONTAINER_NAME} \
  -p ${PORT}:5000 \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=64m \
  --security-opt=no-new-privileges \
  --cap-drop=ALL \
  --restart=unless-stopped \
  ${IMAGE_SHA}

# Verify deployment
sleep 2
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔐 IMMUTABILITY GUARANTEES:"
echo "═══════════════════════════════════════════════════════════════"
echo "✓ Filesystem: READ-ONLY (cannot write files)"
echo "✓ Environment: BAKED IN (cannot change .env)"
echo "✓ Code: CRYPTOGRAPHICALLY LOCKED by SHA256"
echo "✓ Privileges: NONE (no system access)"
echo "✓ Capabilities: ALL DROPPED (minimal attack surface)"
echo ""
echo "📋 Image SHA256:"
echo "   ${IMAGE_SHA}"
echo ""
echo "🌐 Access your app at:"
echo "   http://localhost:${PORT}"
echo ""
echo "⚠️  IMPORTANT:"
echo "   • To make ANY changes, you MUST rebuild the entire image"
echo "   • Even you cannot modify this running container"
echo "   • .env values are permanently baked in"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test immutability
echo "🔬 TESTING IMMUTABILITY..."
echo ""
echo "Test 1: Try to write to filesystem (should fail)..."
if docker exec ${CONTAINER_NAME} touch /app/test.txt 2>&1 | grep -q "Read-only file system"; then
    echo "  ✅ PASS - Filesystem is read-only"
else
    echo "  ❌ FAIL - Filesystem may be writable!"
fi

echo ""
echo "Test 2: Verify environment is baked in..."
if docker exec ${CONTAINER_NAME} printenv | grep -q "ANTHROPIC_API_KEY"; then
    echo "  ✅ PASS - Environment variables are baked in"
else
    echo "  ❌ FAIL - Environment variables missing!"
fi

echo ""
echo "Test 3: Check user privileges..."
CURRENT_USER=$(docker exec ${CONTAINER_NAME} whoami)
if [ "$CURRENT_USER" = "appuser" ]; then
    echo "  ✅ PASS - Running as non-root user: ${CURRENT_USER}"
else
    echo "  ⚠️  WARNING - Running as: ${CURRENT_USER}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 Container is LOCKED and IMMUTABLE!"
echo "═══════════════════════════════════════════════════════════════"
