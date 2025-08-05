#!/usr/bin/env python3
"""
Production Database Import Script for Buddy AI App
Generated on: 2025-08-05T09:01:34.297647

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
        self.data_files = {'prefetch_cache': {'success': True, 'document_count': 18, 'export_file': 'prefetch_cache.json'}, 'songs': {'success': True, 'document_count': 1, 'export_file': 'songs.json'}, 'story_sessions': {'success': True, 'document_count': 63, 'export_file': 'story_sessions.json'}, 'parental_controls': {'success': True, 'document_count': 483, 'export_file': 'parental_controls.json'}, 'ai_companion_db.camb_ai_voices': {'success': True, 'document_count': 4, 'export_file': 'ai_companion_db.camb_ai_voices.json'}, 'stories': {'success': True, 'document_count': 2, 'export_file': 'stories.json'}, 'camb_voices': {'success': True, 'document_count': 2, 'export_file': 'camb_voices.json'}, 'story_audio_cache': {'success': True, 'document_count': 0, 'export_file': 'story_audio_cache.json'}, 'session_telemetry': {'success': True, 'document_count': 27, 'export_file': 'session_telemetry.json'}, 'conversations': {'success': True, 'document_count': 4086, 'export_file': 'conversations.json'}, 'memory_snapshots': {'success': True, 'document_count': 0, 'export_file': 'memory_snapshots.json'}, 'auth_users': {'success': True, 'document_count': 53, 'export_file': 'auth_users.json'}, 'conversation_sessions': {'success': True, 'document_count': 980, 'export_file': 'conversation_sessions.json'}, 'ai_companion_db.camb_voices': {'success': True, 'document_count': 2, 'export_file': 'ai_companion_db.camb_voices.json'}, 'cached_content': {'success': True, 'document_count': 0, 'export_file': 'cached_content.json'}, 'telemetry_events': {'success': True, 'document_count': 201, 'export_file': 'telemetry_events.json'}, 'user_profiles': {'success': True, 'document_count': 619, 'export_file': 'user_profiles.json'}}
        
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
            logger.error(f"❌ Failed to connect to production MongoDB: {str(e)}")
            return False
    
    def import_collection(self, collection_name: str, file_path: str):
        """Import collection from JSON file"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ File not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            if not documents:
                logger.info(f"⚪ {collection_name}: No data to import")
                return True
            
            collection = self.db[collection_name]
            
            # Clear existing data (optional - remove if you want to merge)
            # collection.delete_many({})
            
            # Insert documents
            result = collection.insert_many(documents)
            
            logger.info(f"✅ Imported {collection_name}: {len(result.inserted_ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import {collection_name}: {str(e)}")
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
                
                logger.info(f"📦 Importing collection: {collection_name}")
                
                if self.import_collection(collection_name, file_path):
                    successful_imports += 1
                else:
                    failed_imports += 1
        
        logger.info(f"🎉 Import completed: {successful_imports} successful, {failed_imports} failed")
        return True

if __name__ == "__main__":
    importer = ProductionDataImporter()
    importer.import_all_data()
