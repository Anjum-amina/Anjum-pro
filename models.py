from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['portfolio_db']

# Collections
profile_collection = db['profile']
chat_messages = db['chat_messages']

class ProfileData:
    @staticmethod
    def get_profile():
        """Fetch profile data from MongoDB"""
        profile = profile_collection.find_one({'_id': 'main_profile'})
        if not profile:
            # Insert default data if not exists
            default_profile = {
                '_id': 'main_profile',
                'name': 'B. Anjum',
                'email': 'beldaranjum623@gmail.com',
                'phone': '+91-9705347623',
                'github': 'https://github.com/anjum',
                'linkedin': 'https://linkedin.com/in/anjum',
                'summary': 'Self-confident individual with a positive mindset. Eager to learn new skills and technologies related to career growth.',
                'education': [
                    {'degree': 'B.Tech (Present)', 'institution': 'GITAMW', 'score': '', 'year': '2023-2027'},
                    {'degree': 'Intermediate', 'institution': 'Vivekananda Junior College', 'score': '82%', 'year': '2021-2023'},
                    {'degree': '10th Standard', 'institution': 'Johns High School', 'score': '86%', 'year': '2021'}
                ],
                'skills': ['C Programming', 'Prompt Engineering', 'Python', 'Flask', 'MongoDB'],
                'soft_skills': ['Communication', 'Leadership', 'Teamwork', 'Problem Solving'],
                'projects': [
                    {
                        'name': 'Portfolio Project',
                        'description': 'A full-stack portfolio website with MongoDB integration and AI chatbot.',
                        'technologies': ['Flask', 'MongoDB', 'HTML/CSS', 'JavaScript'],
                        'link': '#',
                        'github_link': '#'
                    }
                ],
                'certifications': [
                    {'name': 'NSS Certificate', 'organization': 'NSS', 'year': '2024', 'description': 'Participation in Project Expo'}
                ],
                'hobbies': ['Playing Badminton', 'Reading Newspapers', 'Coding', 'Chess'],
                'experience': []
            }
            profile_collection.insert_one(default_profile)
            return default_profile
        return profile
    
    @staticmethod
    def update_profile(data):
        """Update profile data"""
        result = profile_collection.update_one(
            {'_id': 'main_profile'},
            {'$set': data},
            upsert=True
        )
        return result

class ChatHistory:
    @staticmethod
    def save_message(session_id, user_message, bot_response):
        """Save chat conversation to database"""
        message = {
            'session_id': session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.now()
        }
        return chat_messages.insert_one(message)
    
    @staticmethod
    def get_chat_history(session_id, limit=50):
        """Get chat history for a session"""
        messages = chat_messages.find(
            {'session_id': session_id}
        ).sort('timestamp', -1).limit(limit)
        return list(messages)
    
    @staticmethod
    def clear_history(session_id):
        """Clear chat history for a session"""
        result = chat_messages.delete_many({'session_id': session_id})
        return result.deleted_count