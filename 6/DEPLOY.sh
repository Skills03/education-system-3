#!/bin/bash
# Quick deployment script

echo "======================================================================="
echo "🚀 Master Teacher - Deployment Helper"
echo "======================================================================="

# Check if ngrok URL is provided
if [ -z "$1" ]; then
    echo ""
    echo "❌ Please provide your ngrok URL"
    echo ""
    echo "Usage: ./DEPLOY.sh YOUR_NGROK_SUBDOMAIN"
    echo "Example: ./DEPLOY.sh abc123"
    echo ""
    echo "Steps:"
    echo "1. Run: python3 server.py"
    echo "2. Run: ngrok http 5000"
    echo "3. Copy subdomain from ngrok URL (e.g., abc123 from https://abc123.ngrok-free.app)"
    echo "4. Run: ./DEPLOY.sh abc123"
    exit 1
fi

NGROK_SUBDOMAIN=$1

echo ""
echo "📝 Updating API_URL in frontend/index.html..."
sed -i "s/YOUR_NGROK_URL/$NGROK_SUBDOMAIN/g" frontend/index.html

echo "✅ Updated API_URL to: https://$NGROK_SUBDOMAIN.ngrok-free.app"

echo ""
echo "🚀 Ready to deploy to Vercel!"
echo ""
echo "Next steps:"
echo "1. cd frontend"
echo "2. vercel --prod"
echo ""
echo "Or run now:"
read -p "Deploy to Vercel now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd frontend
    vercel --prod
fi
