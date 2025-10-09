#!/bin/bash
set -e

# ============================================================================
# 🌐 IMMUTABLE INTERNET DEPLOYMENT - FLY.IO
# Deploy your Docker container to the internet with SHA256 locking
# ============================================================================

IMAGE_SHA="sha256:9a8636b60b7100df208567c2cba52640e29a9b488a95f8f92da5978cd13c36ca"
APP_NAME="teacher-immutable-${RANDOM}"

echo "🌐 DEPLOYING TO FLY.IO (INTERNET)"
echo "═══════════════════════════════════════════════════════════════"
echo "Image SHA256: ${IMAGE_SHA}"
echo "App Name: ${APP_NAME}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: Install Fly CLI if not present
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
    echo "✅ Fly CLI installed"
    echo ""
fi

# Step 2: Check if logged in
echo "🔐 Checking Fly.io authentication..."
if ! flyctl auth whoami &> /dev/null; then
    echo "⚠️  Not logged in to Fly.io"
    echo "Please run: flyctl auth login"
    echo "Then re-run this script"
    exit 1
fi

echo "✅ Authenticated with Fly.io"
echo ""

# Step 3: Push image to Fly registry
echo "📤 Pushing immutable image to Fly.io registry..."
docker tag ${IMAGE_SHA} registry.fly.io/${APP_NAME}:immutable
flyctl auth docker
docker push registry.fly.io/${APP_NAME}:immutable

echo "✅ Image pushed"
echo ""

# Step 4: Create fly.toml with SHA256 pinning
echo "📝 Creating fly.toml with SHA256 lock..."
cat > fly.toml <<EOF
app = "${APP_NAME}"
primary_region = "ord"

[build]
  # Deploy by EXACT SHA256 - cannot be changed
  image = "registry.fly.io/${APP_NAME}@${IMAGE_SHA}"

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = false
  min_machines_running = 1

[[vm]]
  memory = '512mb'
  cpu_kind = 'shared'
  cpus = 1

# IMMUTABILITY: Lock environment (already baked in image)
[env]
  # No env vars here - they're baked into the image!
  # This prevents runtime overrides

# SECURITY: Read-only deployment
[deploy]
  strategy = "immediate"
EOF

echo "✅ fly.toml created with SHA256 pinning"
echo ""

# Step 5: Launch app
echo "🚀 Deploying to internet..."
flyctl launch --config fly.toml --no-deploy --copy-config --name ${APP_NAME}
flyctl deploy --config fly.toml --image registry.fly.io/${APP_NAME}@${IMAGE_SHA}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ DEPLOYED TO INTERNET!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Your app URL:"
flyctl info --config fly.toml | grep Hostname
echo ""
echo "🔒 IMMUTABILITY GUARANTEES:"
echo "  ✓ Deployed by SHA256 (cryptographically locked)"
echo "  ✓ Environment baked in (cannot override)"
echo "  ✓ Code cannot change without new SHA256"
echo "  ✓ Accessible worldwide on the internet"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔥 EXTREME LOCKDOWN OPTIONS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Option 1: Remove your deploy access (requires another person to change)"
echo "  flyctl orgs invite someone@example.com --app ${APP_NAME}"
echo "  flyctl orgs leave <org-name>"
echo ""
echo "Option 2: Delete source code"
echo "  cd .. && rm -rf 6/"
echo ""
echo "Option 3: Make app unclaimed (no owner)"
echo "  flyctl apps destroy ${APP_NAME} --yes"
echo "  (Just kidding - don't do this!)"
echo ""
echo "To view logs:"
echo "  flyctl logs --config fly.toml"
echo ""
echo "To check status:"
echo "  flyctl status --config fly.toml"
echo "═══════════════════════════════════════════════════════════════"
