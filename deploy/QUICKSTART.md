# ⚡ Quick Start Deployment Guide

## 5-Minute Deployment

### 1. Start Backend Servers (3 terminals)

```bash
# Terminal 1
python3 /home/mahadev/Desktop/dev/education/teacher_server.py

# Terminal 2
python3 /home/mahadev/Desktop/dev/education/4/project_server.py

# Terminal 3
python3 /home/mahadev/Desktop/dev/education/5/visual_server.py
```

### 2. Start ngrok Tunnels (3 more terminals)

```bash
# Terminal 4
ngrok http 5000
# Copy the URL: https://______.ngrok.io

# Terminal 5
ngrok http 5001
# Copy the URL: https://______.ngrok.io

# Terminal 6
ngrok http 5002
# Copy the URL: https://______.ngrok.io
```

### 3. Update Frontend Files

Edit these lines with your ngrok URLs:

**concept.html** line 417:
```javascript
const API_URL = 'https://YOUR-URL-1.ngrok.io';
```

**project.html** line 345:
```javascript
const API_URL = 'https://YOUR-URL-2.ngrok.io';
```

**visual.html** line 357:
```javascript
const API_URL = 'https://YOUR-URL-3.ngrok.io';
```

### 4. Deploy to Vercel

```bash
cd /home/mahadev/Desktop/dev/education/deploy
vercel --prod
```

### 5. Done! 🎉

Visit your Vercel URL and test all three systems.

## Common Commands

```bash
# Redeploy after changes
vercel --prod

# View deployment logs
vercel logs

# Open deployed site
vercel open
```

## Troubleshooting

**CORS Error?**
```python
# Add to each server:
CORS(app, origins=['https://your-site.vercel.app'])
```

**ngrok URL changed?**
- Update API_URL in HTML files
- Redeploy: `vercel --prod`

**Need help?**
- See full README.md
- Check backend logs: `tail -f /tmp/*_server.log`
- Visit ngrok dashboard: http://localhost:4040
