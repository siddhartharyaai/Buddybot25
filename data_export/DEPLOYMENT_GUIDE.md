# Buddy AI App - Production Deployment Guide
Generated on: 2025-08-05T09:01:34.297810

## Overview
This guide will help you deploy the Buddy AI app to production using:
- **Frontend**: Netlify (React app)
- **Backend**: Railway/Render/DigitalOcean (FastAPI)
- **Database**: MongoDB Atlas (or other cloud MongoDB)

## Step 1: Set Up Production Database

### Option A: MongoDB Atlas (Recommended)
1. Go to https://www.mongodb.com/atlas
2. Create free account and cluster
3. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/buddy_ai_production`
4. Whitelist your IP addresses (0.0.0.0/0 for development)

### Option B: Railway MongoDB
1. Go to https://railway.app
2. Create new project → Add MongoDB
3. Get connection string from environment variables

### Option C: DigitalOcean Managed MongoDB
1. Go to https://www.digitalocean.com
2. Create → Databases → MongoDB
3. Get connection string from database overview

## Step 2: Import Your Data

1. **Set environment variables:**
   ```bash
   export PRODUCTION_MONGO_URL="your_production_mongodb_connection_string"
   export PRODUCTION_DB_NAME="buddy_ai_production"
   ```

2. **Run the import script:**
   ```bash
   cd /app/data_export
   pip install pymongo
   python production_import.py
   ```

## Step 3: Deploy Backend

### Option A: Railway (Recommended)
1. Go to https://railway.app
2. Connect GitHub repository
3. Deploy from `/app/backend` directory
4. Set environment variables:
   ```
   MONGO_URL=your_production_mongodb_connection_string
   DB_NAME=buddy_ai_production
   GEMINI_API_KEY=your_gemini_api_key
   DEEPGRAM_API_KEY=your_deepgram_api_key
   ```

### Option B: Render
1. Go to https://render.com
2. Create new Web Service
3. Connect repository, set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### Option C: DigitalOcean App Platform
1. Go to https://www.digitalocean.com/products/app-platform
2. Create app from GitHub repository
3. Configure build and run commands

## Step 4: Update Frontend for Production

1. **Update environment variables in frontend/.env:**
   ```
   REACT_APP_BACKEND_URL=https://your-backend-production-url.com
   ```

2. **Build frontend:**
   ```bash
   cd /app/frontend
   npm run build
   ```

## Step 5: Deploy Frontend to Netlify

1. Go to https://netlify.com
2. Connect GitHub repository
3. Set build settings:
   - Build command: `npm run build`
   - Publish directory: `build`
   - Base directory: `frontend`

4. **Set environment variables in Netlify:**
   - Go to Site settings → Environment variables
   - Add: `REACT_APP_BACKEND_URL=https://your-backend-production-url.com`

## Step 6: Configure CORS (Important!)

Update your backend CORS settings to allow your Netlify domain:

```python
# In backend/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-netlify-app.netlify.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Data Export Summary
- **Total Collections Exported**: 17
- **Successful Exports**: 17
- **Failed Exports**: 0

### Exported Collections:
- prefetch_cache: 18 documents
- songs: 1 documents
- story_sessions: 63 documents
- parental_controls: 483 documents
- ai_companion_db.camb_ai_voices: 4 documents
- stories: 2 documents
- camb_voices: 2 documents
- story_audio_cache: 0 documents
- session_telemetry: 27 documents
- conversations: 4086 documents
- memory_snapshots: 0 documents
- auth_users: 53 documents
- conversation_sessions: 980 documents
- ai_companion_db.camb_voices: 2 documents
- cached_content: 0 documents
- telemetry_events: 201 documents
- user_profiles: 619 documents

## Estimated Costs
- **MongoDB Atlas**: Free tier (512MB)
- **Railway**: $5/month for backend
- **Netlify**: Free tier for frontend
- **Total**: ~$5/month

## Environment Variables Checklist

### Backend (.env):
```
MONGO_URL=your_production_mongodb_connection_string
DB_NAME=buddy_ai_production
GEMINI_API_KEY=your_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### Frontend (.env):
```
REACT_APP_BACKEND_URL=https://your-backend-production-url.com
```

## Testing Your Deployment
1. Visit your Netlify frontend URL
2. Test user signup/signin
3. Test story generation and audio
4. Check browser console for errors
5. Monitor backend logs

## Troubleshooting
- **CORS errors**: Update CORS settings in backend
- **Database connection issues**: Check MongoDB connection string and IP whitelist
- **API key errors**: Verify all environment variables are set correctly
- **Build failures**: Check Node.js version compatibility

Need help? Check the logs in your deployment platform or contact support.
