# 🚀 Interactive Learning Platform - Deployment Guide

Complete deployment guide for the multi-modal programming education platform.

## 📋 Overview

This folder contains production-ready frontend files for deployment to **Vercel**. Backend servers run locally and are exposed via **ngrok**.

### Architecture

```
Frontend (Vercel) ←→ ngrok ←→ Backend (Local Servers)
     ↓
   Users
```

- **Frontend**: Static HTML files hosted on Vercel
- **Backend**: Flask servers running locally, exposed via ngrok
- **Communication**: Frontend makes API calls to ngrok URLs

## 📁 Files

```
deploy/
├── index.html           # Landing page with all 3 systems
├── concept.html         # Concept Teacher (port 5000)
├── project.html         # Project Builder (port 5001)
├── visual.html          # Visual Learning (port 5002)
├── vercel.json          # Vercel configuration
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🛠️ Pre-Deployment Setup

### Step 1: Start Backend Servers

Start all three backend servers locally:

```bash
# Terminal 1: Concept Teacher (port 5000)
cd /home/mahadev/Desktop/dev/education
python3 teacher_server.py

# Terminal 2: Project Builder (port 5001)
cd /home/mahadev/Desktop/dev/education/4
python3 project_server.py

# Terminal 3: Visual Learning (port 5002)
cd /home/mahadev/Desktop/dev/education/5
python3 visual_server.py
```

Verify all servers are running:
- http://localhost:5000 ✓
- http://localhost:5001 ✓
- http://localhost:5002 ✓

### Step 2: Setup ngrok

Install ngrok if not already installed:
```bash
# Visit https://ngrok.com and download
# Or install via snap:
sudo snap install ngrok
```

Authenticate ngrok (first time only):
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

Start ngrok tunnels for each backend:

```bash
# Terminal 4: Concept Teacher
ngrok http 5000

# Terminal 5: Project Builder
ngrok http 5001

# Terminal 6: Visual Learning
ngrok http 5002
```

**Save the ngrok URLs** (they look like `https://abc123.ngrok.io`):
- Concept Teacher: https://______.ngrok.io
- Project Builder: https://______.ngrok.io
- Visual Learning: https://______.ngrok.io

### Step 3: Configure Frontend Files

Edit each HTML file and update the `API_URL` with your ngrok URL:

**concept.html** (line ~417):
```javascript
const API_URL = 'https://YOUR-CONCEPT-NGROK-URL.ngrok.io';
```

**project.html** (line ~345):
```javascript
const API_URL = 'https://YOUR-PROJECT-NGROK-URL.ngrok.io';
```

**visual.html** (line ~357):
```javascript
const API_URL = 'https://YOUR-VISUAL-NGROK-URL.ngrok.io';
```

Look for the `🔧 BACKEND CONFIGURATION` comment in each file.

## 🚀 Deployment to Vercel

### Option 1: Using Vercel CLI (Recommended)

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy:**
```bash
cd /home/mahadev/Desktop/dev/education/deploy
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? **interactive-learning-platform**
- In which directory is your code located? **./**
- Override settings? **N**

4. **Production Deployment:**
```bash
vercel --prod
```

Your site will be live at: `https://interactive-learning-platform.vercel.app`

### Option 2: Using Vercel Dashboard

1. Go to https://vercel.com/new
2. Import Git Repository (or drag & drop the `deploy` folder)
3. Configure:
   - Framework Preset: **Other**
   - Root Directory: **.**
   - Build Command: (leave empty)
   - Output Directory: **.**
4. Click **Deploy**

## 🔧 Configuration Options

### Custom Domain

Add custom domain in Vercel dashboard:
1. Go to Project Settings → Domains
2. Add your domain (e.g., `learn.yourdomain.com`)
3. Follow DNS configuration instructions

### Environment Variables (Optional)

If you want to use environment variables instead of hardcoding ngrok URLs:

1. Create `env.js` in deploy folder:
```javascript
window.ENV = {
  CONCEPT_API: 'https://your-concept.ngrok.io',
  PROJECT_API: 'https://your-project.ngrok.io',
  VISUAL_API: 'https://your-visual.ngrok.io'
};
```

2. Include in each HTML file:
```html
<script src="env.js"></script>
<script>
  const API_URL = window.ENV.CONCEPT_API || '';
</script>
```

3. Add `env.js` to `.gitignore`

## 🧪 Testing Deployment

### Local Testing

Test locally before deploying:
```bash
cd deploy
python3 -m http.server 8000
```

Visit: http://localhost:8000

### Production Testing

After deployment, test each system:

1. **Visit Landing Page**: `https://your-site.vercel.app`
2. **Test Concept Teacher**: Click "Launch Concept Teacher"
   - Start session
   - Ask: "Explain Python list comprehensions"
   - Verify: Tools called, code examples shown
3. **Test Project Builder**: Click "Launch Project Builder"
   - Start session
   - Ask: "Let's build a calculator"
   - Verify: Live coding works, incremental code shown
4. **Test Visual Learning**: Click "Launch Visual Learning"
   - Start session
   - Ask: "Explain linked lists with diagram"
   - Verify: Image generated and displayed

## 🔒 Security Considerations

### CORS Configuration

Ensure backend servers allow requests from your Vercel domain:

```python
# Add to each server file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:8000',
    'https://your-site.vercel.app',
    'https://*.ngrok.io'
])
```

### ngrok Configuration

For production, consider:
- **ngrok Pro**: Static domains (no URL changes on restart)
- **Paid Plans**: Remove ngrok branding, better uptime
- **IP Whitelisting**: Restrict access to your frontend domain

### API Keys

- FAL_KEY is stored server-side (safe)
- Never expose API keys in frontend code
- Backend validates all requests

## 📊 Monitoring

### Vercel Analytics

Enable analytics in Vercel dashboard:
1. Project Settings → Analytics
2. Enable Web Analytics
3. View usage stats

### Backend Monitoring

Check backend logs:
```bash
# View logs in real-time
tail -f /tmp/teacher_server.log
tail -f /tmp/project_server.log
tail -f /tmp/visual_server.log
```

Monitor ngrok dashboard:
- Visit: http://localhost:4040 (for each ngrok tunnel)
- View request/response logs
- Check traffic stats

## 🐛 Troubleshooting

### Issue: "Failed to fetch" errors

**Solution:**
1. Verify ngrok tunnels are running
2. Check `API_URL` is correctly set in HTML files
3. Verify CORS is enabled on backend
4. Check browser console for exact error

### Issue: Images not loading (Visual Learning)

**Solution:**
1. Check FAL_KEY environment variable is set
2. Verify `fal-client` is installed: `pip3 list | grep fal`
3. Check backend logs for image generation errors
4. Test FAL API independently

### Issue: ngrok URL changes on restart

**Solution:**
1. Use ngrok paid plan for static domains
2. Or update `API_URL` in HTML files after each restart
3. Or use environment variables approach (see above)

### Issue: Session not persisting

**Solution:**
- Session storage is localStorage (client-side)
- Clear browser cache and try again
- Check browser console for localStorage errors

## 🔄 Updating Deployment

### Update Frontend

1. Make changes to HTML files
2. Update `API_URL` if ngrok URLs changed
3. Redeploy:
```bash
cd deploy
vercel --prod
```

### Update Backend

1. Stop running servers (Ctrl+C)
2. Update Python files
3. Restart servers and ngrok tunnels
4. Update `API_URL` in HTML files if ngrok URLs changed
5. Redeploy frontend if URLs changed

## 📞 Support

### Vercel Issues
- Docs: https://vercel.com/docs
- Support: https://vercel.com/support

### ngrok Issues
- Docs: https://ngrok.com/docs
- Support: https://dashboard.ngrok.com/support

## 🎯 Production Checklist

Before going live:

- [ ] All backend servers running
- [ ] ngrok tunnels active and stable
- [ ] API_URL configured in all HTML files
- [ ] CORS properly configured
- [ ] All three systems tested end-to-end
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Monitoring setup
- [ ] Documentation shared with team
- [ ] Backup ngrok URLs saved

## 🌐 URLs

After deployment:

- **Landing Page**: https://your-site.vercel.app
- **Concept Teacher**: https://your-site.vercel.app/concept.html
- **Project Builder**: https://your-site.vercel.app/project.html
- **Visual Learning**: https://your-site.vercel.app/visual.html

## 📈 Scaling

For production scale:

1. **Frontend**: Vercel auto-scales (handled)
2. **Backend**:
   - Deploy to cloud (AWS, GCP, Heroku)
   - Use load balancer
   - Replace ngrok with proper domain
3. **Database**: Add PostgreSQL for persistent storage
4. **Caching**: Add Redis for session management
5. **CDN**: Vercel provides edge caching

## 🎉 Success!

Your multi-modal learning platform is now live! Users can access:
- 📚 Concept-based learning
- 🚀 Project-based learning
- 🎨 Visual learning

All powered by AI, all in one platform.
