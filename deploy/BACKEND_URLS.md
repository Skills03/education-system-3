# 🔗 Backend URLs Configuration

## ngrok URLs Template

After starting ngrok tunnels, fill in your URLs here for reference:

### Concept Teacher (Port 5000)
```
Local: http://localhost:5000
ngrok: https://_________________.ngrok.io
```
Update in: `concept.html` line 417

### Project Builder (Port 5001)
```
Local: http://localhost:5001
ngrok: https://_________________.ngrok.io
```
Update in: `project.html` line 345

### Visual Learning (Port 5002)
```
Local: http://localhost:5002
ngrok: https://_________________.ngrok.io
```
Update in: `visual.html` line 357

## How to Get ngrok URLs

1. Start ngrok tunnel:
```bash
ngrok http 5000
```

2. Look for this line in the output:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
            ^^^^^^^^^^^^^^^^^^^^^^
            This is your ngrok URL
```

3. Copy the `https://_____.ngrok.io` URL
4. Paste it in the corresponding HTML file

## Quick Update Script

After getting all three URLs, update all files at once:

```bash
# Replace YOUR_URL_1, YOUR_URL_2, YOUR_URL_3 with actual URLs
sed -i "s|const API_URL = '';|const API_URL = 'https://YOUR_URL_1.ngrok.io';|" concept.html
sed -i "s|const API_URL = '';|const API_URL = 'https://YOUR_URL_2.ngrok.io';|" project.html
sed -i "s|const API_URL = '';|const API_URL = 'https://YOUR_URL_3.ngrok.io';|" visual.html
```

## Important Notes

⚠️ **Free ngrok URLs change every time you restart ngrok**
- Save your URLs after each restart
- Update HTML files before redeploying
- Consider ngrok Pro for static URLs

💡 **Pro Tip**: Use environment variables
- Create `env.js` with all URLs
- Include in each HTML file
- Only update one file when URLs change

## Verification

Test each URL before deployment:

```bash
# Test Concept Teacher
curl https://YOUR_URL_1.ngrok.io/api/session/start -X POST -H "Content-Type: application/json" -d '{}'

# Test Project Builder
curl https://YOUR_URL_2.ngrok.io/api/session/start -X POST -H "Content-Type: application/json" -d '{}'

# Test Visual Learning
curl https://YOUR_URL_3.ngrok.io/api/session/start -X POST -H "Content-Type: application/json" -d '{}'
```

All should return: `{"session_id": "...", "status": "ready"}`
