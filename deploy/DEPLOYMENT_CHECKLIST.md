# ✅ Deployment Checklist

Complete this checklist before and after deployment to ensure everything works.

## Pre-Deployment

### Backend Setup
- [ ] All Python dependencies installed
  ```bash
  pip3 list | grep -E "claude-agent-sdk|flask|fal-client"
  ```

- [ ] FAL_KEY environment variable set
  ```bash
  echo $FAL_KEY  # Should show your key
  ```

- [ ] All backend servers start without errors
  - [ ] teacher_server.py (port 5000)
  - [ ] project_server.py (port 5001)
  - [ ] visual_server.py (port 5002)

### ngrok Setup
- [ ] ngrok installed
  ```bash
  ngrok version
  ```

- [ ] ngrok authenticated
  ```bash
  ngrok config check
  ```

- [ ] All three ngrok tunnels started
  - [ ] ngrok http 5000
  - [ ] ngrok http 5001
  - [ ] ngrok http 5002

- [ ] All ngrok URLs saved in BACKEND_URLS.md

### Frontend Configuration
- [ ] concept.html: API_URL updated with ngrok URL
- [ ] project.html: API_URL updated with ngrok URL
- [ ] visual.html: API_URL updated with ngrok URL

### Vercel Setup
- [ ] Vercel CLI installed
  ```bash
  vercel --version
  ```

- [ ] Logged into Vercel
  ```bash
  vercel whoami
  ```

## Deployment

- [ ] Navigate to deploy folder
  ```bash
  cd /home/mahadev/Desktop/dev/education/deploy
  ```

- [ ] Deploy to Vercel
  ```bash
  vercel --prod
  ```

- [ ] Deployment successful (got URL)
- [ ] Deployment URL saved: ___________________________

## Post-Deployment Testing

### Landing Page
- [ ] Visit: https://your-site.vercel.app
- [ ] All three cards displayed
- [ ] Links work correctly

### Concept Teacher
- [ ] Click "Launch Concept Teacher"
- [ ] "Start Session" button works
- [ ] Send message: "Explain Python list comprehensions"
- [ ] Response received with:
  - [ ] Code examples shown
  - [ ] Tools called (show_code_example, etc.)
  - [ ] Markdown rendered correctly
  - [ ] Cost displayed

### Project Builder
- [ ] Click "Launch Project Builder"
- [ ] "Start Session" button works
- [ ] Send message: "Let's build a simple calculator"
- [ ] Response received with:
  - [ ] Project kickoff shown
  - [ ] Incremental code additions
  - [ ] Tools called (code_live_increment, etc.)
  - [ ] Markdown rendered correctly
  - [ ] Cost displayed

### Visual Learning
- [ ] Click "Launch Visual Learning"
- [ ] "Start Session" button works
- [ ] Send message: "Explain linked lists with a diagram"
- [ ] Response received with:
  - [ ] Image generated and displayed
  - [ ] Tools called (generate_data_structure_viz)
  - [ ] Explanation with visual reference
  - [ ] Cost displayed

## Browser Testing

Test on multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Edge

## Mobile Testing

- [ ] Test on mobile device
- [ ] Responsive layout works
- [ ] Sessions work on mobile
- [ ] Images load on mobile

## Performance

- [ ] Page loads in < 3 seconds
- [ ] Images load properly
- [ ] No console errors
- [ ] SSE streaming works smoothly

## Security

- [ ] CORS configured correctly
- [ ] No API keys exposed in frontend
- [ ] HTTPS used for all connections
- [ ] Security headers present

## Monitoring

- [ ] Vercel analytics enabled
- [ ] Backend logs accessible
- [ ] ngrok dashboard accessible (http://localhost:4040)

## Documentation

- [ ] README.md reviewed
- [ ] QUICKSTART.md available
- [ ] BACKEND_URLS.md filled out
- [ ] Team members can access deployment

## Backup

- [ ] ngrok URLs backed up
- [ ] Backend server IPs/ports documented
- [ ] Deployment URL saved
- [ ] Configuration screenshots taken

## Troubleshooting Checklist

If issues occur:

1. **Check Backend Servers**
   ```bash
   curl http://localhost:5000/api/session/start -X POST -d '{}'
   curl http://localhost:5001/api/session/start -X POST -d '{}'
   curl http://localhost:5002/api/session/start -X POST -d '{}'
   ```

2. **Check ngrok Tunnels**
   - Visit http://localhost:4040 for each tunnel
   - Verify requests going through
   - Check for errors

3. **Check Frontend Configuration**
   - View page source
   - Find `API_URL` constant
   - Verify it matches ngrok URL

4. **Check Browser Console**
   - F12 → Console tab
   - Look for errors
   - Check Network tab for failed requests

5. **Check CORS**
   - Look for CORS errors in console
   - Verify backend CORS configuration
   - Test with curl:
     ```bash
     curl -H "Origin: https://your-site.vercel.app" \
          -H "Access-Control-Request-Method: POST" \
          -X OPTIONS \
          https://your-ngrok-url.ngrok.io/api/session/start -v
     ```

## Success Criteria

Deployment is successful when:

- ✅ All three systems accessible via Vercel URL
- ✅ All backend services responding
- ✅ Images generating correctly (Visual Learning)
- ✅ Sessions persisting in localStorage
- ✅ No console errors
- ✅ Mobile responsive
- ✅ Performance acceptable

## Sign-Off

Deployment completed by: _________________

Date: _________________

Vercel URL: _________________

All tests passed: ☐ Yes ☐ No

Notes:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
