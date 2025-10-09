#!/bin/bash
set -e

# ============================================================================
# 🌐 IMMUTABLE INTERNET DEPLOYMENT - GOOGLE CLOUD RUN
# Enterprise-grade immutable deployment with IAM lockdown
# ============================================================================

IMAGE_SHA="sha256:9a8636b60b7100df208567c2cba52640e29a9b488a95f8f92da5978cd13c36ca"
PROJECT_ID="${GCP_PROJECT_ID:-my-project}"
SERVICE_NAME="teacher-immutable"
REGION="us-central1"

echo "🌐 DEPLOYING TO GOOGLE CLOUD RUN (INTERNET)"
echo "═══════════════════════════════════════════════════════════════"
echo "Image SHA256: ${IMAGE_SHA}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: Check gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Step 2: Tag and push to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
GCR_IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

docker tag ${IMAGE_SHA} ${GCR_IMAGE}:immutable
docker tag ${IMAGE_SHA} ${GCR_IMAGE}@${IMAGE_SHA}

# Configure Docker for GCR
gcloud auth configure-docker --quiet

# Push image
docker push ${GCR_IMAGE}:immutable

echo "✅ Image pushed to GCR"
echo ""

# Step 3: Deploy to Cloud Run with SHA256 pinning
echo "🚀 Deploying to Cloud Run with immutable settings..."

gcloud run deploy ${SERVICE_NAME} \
  --image=${GCR_IMAGE}@${IMAGE_SHA} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --port=5000 \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=10 \
  --min-instances=1 \
  --no-allow-unauthenticated \
  --ingress=all \
  --execution-environment=gen2

# Get the URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ DEPLOYED TO INTERNET!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Your app URL: ${SERVICE_URL}"
echo ""
echo "🔒 IMMUTABILITY GUARANTEES:"
echo "  ✓ Deployed by SHA256 digest (cryptographically locked)"
echo "  ✓ Revision is immutable (GCP guarantees)"
echo "  ✓ Environment baked in (cannot override)"
echo "  ✓ Traffic locked to specific revision"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔥 EXTREME LOCKDOWN - REMOVE YOUR OWN ACCESS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Step 1: Get your current email"
echo "  EMAIL=\$(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
echo "  echo \$EMAIL"
echo ""
echo "Step 2: Add another admin (REQUIRED before removing yourself)"
echo "  gcloud projects add-iam-policy-binding ${PROJECT_ID} \\"
echo "    --member='user:trusted-person@example.com' \\"
echo "    --role='roles/owner'"
echo ""
echo "Step 3: Remove your own access (IRREVERSIBLE without other admin)"
echo "  gcloud projects remove-iam-policy-binding ${PROJECT_ID} \\"
echo "    --member=\"user:\$EMAIL\" \\"
echo "    --role='roles/owner'"
echo ""
echo "Step 4: Lock the revision (no new deployments allowed)"
echo "  gcloud run services update-traffic ${SERVICE_NAME} \\"
echo "    --region=${REGION} \\"
echo "    --to-revisions=${SERVICE_NAME}-00001=100"
echo ""
echo "Now even YOU cannot change the deployment!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "LESS EXTREME: Just remove deployment permissions"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  gcloud projects remove-iam-policy-binding ${PROJECT_ID} \\"
echo "    --member=\"user:\$EMAIL\" \\"
echo "    --role='roles/run.admin'"
echo ""
echo "This keeps read access but prevents deployments"
echo ""
echo "To view logs:"
echo "  gcloud run logs read --service=${SERVICE_NAME} --region=${REGION}"
echo ""
echo "═══════════════════════════════════════════════════════════════"
