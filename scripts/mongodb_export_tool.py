#!/usr/bin/env python3
"""
MongoDB Data Export Tool for Buddy AI App
Exports all data from localhost MongoDB for production deployment
"""

import pymongo
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BuddyDataExporter:
    def __init__(self):
        # MongoDB connection settings from your current setup
        self.mongo_url = "mongodb://localhost:27017"
        self.db_name = "ai_companion_db"
        self.client = None
        self.db = None
        
        # Export directory
        self.export_dir = "/app/data_export"
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Collections to export (based on your app structure)
        self.collections_to_export = [
            "user_profiles",
            "auth_users", 
            "conversation_sessions",
            "story_sessions",
            "conversation_history",
            "memory_snapshots",
            "parental_controls",
            "telemetry_events",
            "content_library",
            "user_preferences",
            "safety_logs"
        ]
    
    def connect_to_mongodb(self):
        """Connect to localhost MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB: {self.mongo_url}")
            self.client = pymongo.MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections"""
        stats = {}
        
        try:
            # Get all collection names in the database
            collection_names = self.db.list_collection_names()
            logger.info(f"📊 Found {len(collection_names)} collections in database")
            
            for collection_name in collection_names:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                
                # Get sample document to understand structure
                sample_doc = collection.find_one()
                
                stats[collection_name] = {
                    "document_count": count,
                    "has_data": count > 0,
                    "sample_fields": list(sample_doc.keys()) if sample_doc else []
                }
                
                logger.info(f"📋 {collection_name}: {count} documents")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {str(e)}")
            return {}
    
    def export_collection(self, collection_name: str) -> bool:
        """Export a single collection to JSON file"""
        try:
            collection = self.db[collection_name]
            documents = list(collection.find({}))
            
            if not documents:
                logger.info(f"⚪ {collection_name}: No data to export")
                return True
            
            # Convert ObjectIds to strings for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                
                # Convert any other ObjectId fields
                for key, value in doc.items():
                    if hasattr(value, 'binary'):  # ObjectId check
                        doc[key] = str(value)
            
            # Export to JSON file
            export_file = os.path.join(self.export_dir, f"{collection_name}.json")
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"✅ Exported {collection_name}: {len(documents)} documents → {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export {collection_name}: {str(e)}")
            return False
    
    def export_all_data(self):
        """Export all collections and create migration metadata"""
        logger.info("🚀 Starting complete data export...")
        
        # Get collection statistics
        stats = self.get_collection_stats()
        
        # Track export results
        export_results = {
            "export_timestamp": datetime.now().isoformat(),
            "source_database": {
                "mongo_url": self.mongo_url,
                "database_name": self.db_name
            },
            "collections": {},
            "successful_exports": 0,
            "failed_exports": 0
        }
        
        # Export each collection
        for collection_name in stats.keys():
            logger.info(f"📦 Exporting collection: {collection_name}")
            
            success = self.export_collection(collection_name)
            
            export_results["collections"][collection_name] = {
                "success": success,
                "document_count": stats[collection_name]["document_count"],
                "export_file": f"{collection_name}.json" if success else None
            }
            
            if success:
                export_results["successful_exports"] += 1
            else:
                export_results["failed_exports"] += 1
        
        # Save export metadata
        metadata_file = os.path.join(self.export_dir, "export_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(export_results, f, indent=2, default=str)
        
        # Create import script for production
        self.create_import_script(export_results)
        
        # Create deployment guide
        self.create_deployment_guide(export_results)
        
        logger.info(f"🎉 Export completed: {export_results['successful_exports']} successful, {export_results['failed_exports']} failed")
        logger.info(f"📁 All exported data saved to: {self.export_dir}")
        
        return export_results
    
    def create_import_script(self, export_results: Dict[str, Any]):
        """Create Python script for importing data to production database"""
        
        import_script = f'''#!/usr/bin/env python3
"""
Production Database Import Script for Buddy AI App
Generated on: {datetime.now().isoformat()}

Instructions:
1. Set your production MongoDB connection string in PRODUCTION_MONGO_URL
2. Install pymongo: pip install pymongo
3. Run this script: python production_import.py
"""

import pymongo
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDataImporter:
    def __init__(self):
        # REPLACE WITH YOUR PRODUCTION MONGODB CONNECTION STRING
        # Examples:
        # MongoDB Atlas: "mongodb+srv://username:password@cluster.mongodb.net/database_name"
        # Railway: "mongodb://username:password@hostname:port/database_name"
        # DigitalOcean: "mongodb://username:password@hostname:port/database_name"
        
        self.production_mongo_url = os.environ.get('PRODUCTION_MONGO_URL', 'REPLACE_WITH_YOUR_PRODUCTION_MONGO_URL')
        self.production_db_name = os.environ.get('PRODUCTION_DB_NAME', 'buddy_ai_production')
        
        # Data files to import
        self.data_files = {export_results['collections']}
        
        self.client = None
        self.db = None
    
    def connect_to_production_db(self):
        """Connect to production MongoDB"""
        try:
            logger.info(f"Connecting to production MongoDB...")
            self.client = pymongo.MongoClient(self.production_mongo_url)
            self.db = self.client[self.production_db_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to production MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to production MongoDB: {{str(e)}}")
            return False
    
    def import_collection(self, collection_name: str, file_path: str):
        """Import collection from JSON file"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ File not found: {{file_path}}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            if not documents:
                logger.info(f"⚪ {{collection_name}}: No data to import")
                return True
            
            collection = self.db[collection_name]
            
            # Clear existing data (optional - remove if you want to merge)
            # collection.delete_many({{}})
            
            # Insert documents
            result = collection.insert_many(documents)
            
            logger.info(f"✅ Imported {{collection_name}}: {{len(result.inserted_ids)}} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import {{collection_name}}: {{str(e)}}")
            return False
    
    def import_all_data(self):
        """Import all exported data to production database"""
        logger.info("🚀 Starting production data import...")
        
        if not self.connect_to_production_db():
            return False
        
        successful_imports = 0
        failed_imports = 0
        
        for collection_name, info in self.data_files.items():
            if info.get('success') and info.get('export_file'):
                file_path = info['export_file']
                
                logger.info(f"📦 Importing collection: {{collection_name}}")
                
                if self.import_collection(collection_name, file_path):
                    successful_imports += 1
                else:
                    failed_imports += 1
        
        logger.info(f"🎉 Import completed: {{successful_imports}} successful, {{failed_imports}} failed")
        return True

if __name__ == "__main__":
    importer = ProductionDataImporter()
    importer.import_all_data()
'''
        
        script_file = os.path.join(self.export_dir, "production_import.py")
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(import_script)
        
        logger.info(f"📝 Created import script: {script_file}")
    
    def create_deployment_guide(self, export_results: Dict[str, Any]):
        """Create comprehensive deployment guide"""
        
        guide_content = f'''# Buddy AI App - Production Deployment Guide
Generated on: {datetime.now().isoformat()}

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
   cd {self.export_dir}
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
- **Total Collections Exported**: {len(export_results['collections'])}
- **Successful Exports**: {export_results['successful_exports']}
- **Failed Exports**: {export_results['failed_exports']}

### Exported Collections:
{chr(10).join([f"- {name}: {info['document_count']} documents" for name, info in export_results['collections'].items() if info['success']])}

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
'''
        
        guide_file = os.path.join(self.export_dir, "DEPLOYMENT_GUIDE.md")
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        logger.info(f"📚 Created deployment guide: {guide_file}")
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Closed MongoDB connection")

def main():
    """Main export function"""
    exporter = BuddyDataExporter()
    
    try:
        # Connect to MongoDB
        if not exporter.connect_to_mongodb():
            logger.error("❌ Cannot proceed without database connection")
            return False
        
        # Export all data
        results = exporter.export_all_data()
        
        logger.info("🎉 DATA EXPORT COMPLETED SUCCESSFULLY!")
        logger.info(f"📁 Find your exported data in: {exporter.export_dir}")
        logger.info("📚 Read DEPLOYMENT_GUIDE.md for next steps")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Export failed: {str(e)}")
        return False
        
    finally:
        exporter.close_connection()

if __name__ == "__main__":
    main()