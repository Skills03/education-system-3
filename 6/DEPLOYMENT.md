# 🚀 Deployment Guide - Vercel + ngrok

## Quick Deploy

### 1. Deploy Backend on ngrok (2 commands)
```bash
# Start Flask server
python3 server.py

# In new terminal - expose with ngrok
ngrok http 5000
```
Copy the ngrok URL (e.g., `https://abc123.ngrok-free.app`)

### 2. Deploy Frontend on Vercel (3 commands)
```bash
# Update API_URL in frontend/index.html with your ngrok URL
sed -i "s|YOUR_NGROK_URL|abc123|g" frontend/index.html

# Deploy to Vercel (install vercel CLI first: npm i -g vercel)
cd frontend
vercel --prod
```

## Detailed Steps

### Backend (ngrok)

**Install ngrok:**
```bash
# Download from https://ngrok.com/download
# Or use snap:
sudo snap install ngrok

# Add auth token (get from ngrok.com):
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

**Run Backend:**
```bash
cd /home/mahadev/Desktop/dev/education/6
python3 server.py
```

**Expose with ngrok:**
```bash
ngrok http 5000
```

**Output:**
```
Forwarding: https://abc123.ngrok-free.app -> http://localhost:5000
```

**Copy the ngrok URL** - you'll need it for frontend.

---

### Frontend (Vercel)

**Install Vercel CLI:**
```bash
npm install -g vercel
```

**Update API URL:**
Edit `frontend/index.html` line 274:
```javascript
const API_URL = 'https://YOUR_NGROK_URL.ngrok-free.app';
```
Replace `YOUR_NGROK_URL` with your actual ngrok subdomain.

**Deploy:**
```bash
cd frontend
vercel --prod
```

**Follow prompts:**
- Set up and deploy? `Y`
- Which scope? (select your account)
- Link to existing project? `N`
- Project name? `master-teacher`
- Directory? `./`
- Override settings? `N`

**Done!** You'll get a URL like `https://master-teacher.vercel.app`

---

## Environment-Specific Config (Advanced)

**frontend/index.html** - Use environment detection:
```javascript
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:5000'
  : 'https://abc123.ngrok-free.app';
```

---

## Free Tier Limitations

**ngrok Free:**
- ❌ URL changes every restart (use paid for static domain)
- ✅ HTTPS included
- ✅ Good for testing

**Vercel Free:**
- ✅ Permanent URL
- ✅ Auto HTTPS
- ✅ Perfect for frontend

---

## Production Alternative

For production, deploy backend to:
- **Render.com** (free tier)
- **Railway.app** (free tier)
- **Fly.io** (free tier)

These give you permanent URLs.

---

## File Structure

```
/6/
├── frontend/                # Deploy this to Vercel
│   ├── index.html          # (renamed from learn.html)
│   └── vercel.json         # Vercel config
├── server.py               # Run this with ngrok
├── agents/
├── tools/
└── ...
```

---

## Quick Reference

**Backend URL:** `https://YOUR_NGROK_URL.ngrok-free.app`
**Frontend URL:** `https://master-teacher.vercel.app` (or your domain)
**Update:** Change `API_URL` in `frontend/index.html` to your ngrok URL
