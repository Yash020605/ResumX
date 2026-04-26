# AI Resume Analyzer - Quick Reference Guide

## 🚀 30-Second Setup

```bash
# Set API key
$env:ANTHROPIC_API_KEY = "your_key_here"  # Windows PowerShell
# or
export ANTHROPIC_API_KEY="your_key_here"  # Mac/Linux

# Run app
.\start.bat  # Windows
./start.sh   # Mac/Linux

# Open browser
http://localhost:3000
```

## 📋 Common Tasks

### Task: Analyze a Resume
1. Paste resume or upload PDF
2. Paste job description
3. Click "📊 Analyze Resume"
4. Wait 10-30 seconds
5. View results in "📊 Analysis" tab

### Task: Improve Your Resume
1. Complete analysis first
2. Click "✨ Improve Resume"
3. Wait 10-20 seconds
4. View in "✨ Improved Resume" tab
5. Click Copy or Download

### Task: Explore Career Paths
1. Paste your resume
2. Click "💼 Career Fields"
3. Wait 10-20 seconds
4. See 5-7 career suggestions
5. View job titles and industries

### Task: Prepare for Interview
1. Paste resume and job description
2. Click "🎤 Interview Prep"
3. Wait 10-20 seconds
4. View probable questions
5. See sample answers

### Task: Upload PDF Resume
1. Click file upload area
2. Select PDF file
3. System extracts text
4. Text appears in resume field
5. Ready to analyze

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| API key error | Set ANTHROPIC_API_KEY environment variable |
| Port 5000 in use | Change port in `backend/wsgi.py` |
| Port 3000 in use | Change port in `frontend/vite.config.js` |
| CORS error | Ensure backend running on port 5000 |
| Slow response | Normal (10-30s); check internet connection |
| Analysis fails | Check API key and internet connection |
| PDF won't upload | Ensure file is valid PDF < 16MB |

## 📂 File Locations

| File | Purpose |
|------|---------|
| `backend/wsgi.py` | Backend entry point |
| `frontend/src/App.jsx` | Frontend entry point |
| `backend/app/routes/analysis.py` | API endpoints |
| `backend/app/services/resume_analyzer.py` | AI logic |
| `frontend/src/pages/HomePage.jsx` | Main UI |

## 🔑 Important URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:5000 |
| API Base | http://localhost:5000/api |
| Health Check | http://localhost:5000/api/health |

## 📊 API Endpoints Quick Reference

```
GET  /api/health
     Check backend status

POST /api/analyze
     Body: {resume, job_description}
     Returns: Analysis with match score

POST /api/improve-resume
     Body: {resume, job_description, improvements}
     Returns: Improved resume text

POST /api/career-fields
     Body: {resume}
     Returns: Career suggestions

POST /api/interview-prep
     Body: {resume, job_description}
     Returns: Interview questions & answers

POST /api/upload-pdf
     Body: FormData with 'file' field
     Returns: Extracted text
```

## 🎯 Performance Tips

| Tip | Effect |
|-----|--------|
| Use complete job descriptions | Better analysis accuracy |
| Include all experience details | Improves skill matching |
| First request is slower | Caches connection |
| Reduce resume length | Faster processing |
| Clear cache between runs | Fresh analysis |

## 🛠️ Development Tips

### Add New Feature
1. Create component in `frontend/src/components/`
2. Add endpoint in `backend/app/routes/`
3. Implement service in `backend/app/services/`
4. Update API client in `frontend/src/services/api.js`
5. Wire in `HomePage.jsx`

### Debug Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pdb wsgi.py
```

### Debug Frontend
```bash
cd frontend
npm run dev
# Open DevTools (F12)
# Check Console tab for errors
```

## 📚 Documentation Quick Links

| Document | Contains |
|----------|----------|
| README.md | Overview & features |
| SETUP_GUIDE.md | Detailed setup & usage |
| ARCHITECTURE.md | Technical details |
| COMPLETION_SUMMARY.md | Project stats & status |
| ENV_SETUP.md | Environment configuration |
| VISUAL_GUIDE.md | Flowcharts & diagrams |
| This file | Quick reference |

## 🚀 Deployment Checklist

### Before Production
- [ ] Set strong API key
- [ ] Use production Claude model
- [ ] Set FLASK_ENV=production
- [ ] Configure CORS for specific domains
- [ ] Setup SSL/HTTPS
- [ ] Configure database backups
- [ ] Setup error logging
- [ ] Test all endpoints
- [ ] Performance test with load
- [ ] Security audit

### Docker Deployment
```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 💡 Pro Tips

1. **Better Resume Matching**: Include metrics and achievements
2. **Faster Analysis**: Keep job descriptions under 1000 words
3. **Accurate Improvements**: Review suggestions before using
4. **Interview Prep**: Practice answers before using in real interview
5. **Career Exploration**: Try multiple resumes for different goals

## 🔒 Security Checklist

- [ ] API key not in code
- [ ] Environment variables configured
- [ ] CORS properly configured
- [ ] Input validation enabled
- [ ] HTTPS in production
- [ ] Rate limiting enabled
- [ ] Regular security updates
- [ ] Backup strategy in place

## 📞 Getting Help

1. **Setup Issues**: See SETUP_GUIDE.md → Troubleshooting
2. **Feature Questions**: See README.md → Features
3. **Technical Details**: See ARCHITECTURE.md
4. **How to Deploy**: See SETUP_GUIDE.md → Deployment
5. **Code Examples**: Check component files with comments

## 🎓 Learning Resources

- **React Docs**: https://react.dev
- **Flask Docs**: https://flask.palletsprojects.com
- **Anthropic Docs**: https://docs.anthropic.com
- **Tailwind CSS**: https://tailwindcss.com
- **Vite**: https://vitejs.dev

## ⚡ Quick Command Reference

```bash
# Backend
cd backend
python -m venv venv              # Create env
source venv/bin/activate         # Activate
pip install -r requirements.txt  # Install deps
python wsgi.py                   # Run server

# Frontend
cd frontend
npm install                      # Install deps
npm run dev                      # Dev server
npm run build                    # Build prod

# Docker
docker-compose up --build        # Build & run
docker-compose down              # Stop & remove
docker-compose logs -f           # View logs

# Testing APIs
curl http://localhost:5000/api/health
```

## 📈 Expected Response Times

| Operation | Time |
|-----------|------|
| Health check | < 1s |
| PDF upload | 1-3s |
| Analysis | 10-30s |
| Resume improve | 10-20s |
| Career fields | 10-20s |
| Interview prep | 10-30s |

First request slower due to API connection warmup.

## 🎯 Next Steps

1. **Just Starting?** → Read README.md
2. **Ready to Install?** → Follow SETUP_GUIDE.md
3. **Understanding Architecture?** → See ARCHITECTURE.md
4. **Want Visual Overview?** → Check VISUAL_GUIDE.md
5. **Deploying Production?** → Use docker-compose.yml

---

**Version**: 1.0.0  
**Last Updated**: January 2025

For more details, see the comprehensive documentation files! 📚
