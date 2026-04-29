# app.py
from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient, errors
from datetime import datetime
import uuid
import re
import random
import os
import sys

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Try to connect to local MongoDB, but don't fail if not available
mongodb_available = False
db = None
profile_collection = None
chat_messages = None
visitors_collection = None

try:
    # Try to connect to local MongoDB
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    # Check if connection is successful
    client.admin.command('ping')
    db = client['portfolio_db']
    profile_collection = db['profile']
    chat_messages = db['chat_messages']
    visitors_collection = db['visitors']
    mongodb_available = True
    print("✅ Connected to MongoDB on localhost:27017", file=sys.stderr)
except errors.ServerSelectionTimeoutError:
    print("⚠️ MongoDB not available on localhost:27017 - running without database", file=sys.stderr)
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e} - running without database", file=sys.stderr)

# In-memory storage fallback (used when MongoDB is not available)
in_memory_profile = None
in_memory_chats = {}
in_memory_visitors = []

# Initialize default profile data
def init_profile_data():
    global in_memory_profile
    
    default_profile = {
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
        'skills': ['C Programming', 'Prompt Engineering', 'Python', 'Flask'],
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
    
    if mongodb_available:
        if profile_collection.count_documents({}) == 0:
            profile_collection.insert_one(default_profile)
            print("✅ Default profile inserted into local MongoDB", file=sys.stderr)
    else:
        in_memory_profile = default_profile
        print("✅ Using in-memory storage", file=sys.stderr)

init_profile_data()

def get_profile():
    if mongodb_available:
        profile = profile_collection.find_one({})
        if profile and '_id' in profile:
            profile['_id'] = str(profile['_id'])
        return profile
    else:
        return in_memory_profile

def save_chat(session_id, user_msg, bot_msg):
    if mongodb_available:
        chat_messages.insert_one({
            'session_id': session_id,
            'user_message': user_msg,
            'bot_response': bot_msg,
            'timestamp': datetime.now()
        })
    else:
        if session_id not in in_memory_chats:
            in_memory_chats[session_id] = []
        in_memory_chats[session_id].append({
            'user_message': user_msg,
            'bot_response': bot_msg,
            'timestamp': datetime.now().isoformat()
        })

def get_chat_history(session_id):
    if mongodb_available:
        history = list(chat_messages.find({'session_id': session_id}).sort('timestamp', -1).limit(50))
        for msg in history:
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat()
        return history
    else:
        return in_memory_chats.get(session_id, [])[::-1]

# Chatbot Class
class PortfolioChatbot:
    def __init__(self):
        self.profile = get_profile()
        
        self.intents = {
            'greeting': {
                'patterns': [r'hello|hi|hey|greetings|good morning|good evening'],
                'responses': [
                    "Hello! I'm Anjum's portfolio assistant. How can I help you?",
                    "Hi there! Ask me about Anjum's skills, education, or projects."
                ]
            },
            'skills': {
                'patterns': [r'skills|technologies|tech stack|programming'],
                'responses': [f"Anjum knows: {', '.join(self.profile.get('skills', []))}"]
            },
            'education': {
                'patterns': [r'education|study|degree|college|school'],
                'responses': []
            },
            'projects': {
                'patterns': [r'projects|work|built|created'],
                'responses': []
            },
            'contact': {
                'patterns': [r'contact|email|phone|reach'],
                'responses': [f"Email: {self.profile.get('email')} | Phone: {self.profile.get('phone')}"]
            },
            'help': {
                'patterns': [r'help|what can you do'],
                'responses': ["Ask me about skills, education, projects, or contact info!"]
            }
        }
        
        # Generate education response
        edu_text = []
        for edu in self.profile.get('education', []):
            edu_text.append(f"• {edu['degree']} from {edu['institution']}")
        self.intents['education']['responses'] = ["Education:\n" + "\n".join(edu_text)]
        
        # Generate projects response
        proj_text = []
        for proj in self.profile.get('projects', []):
            proj_text.append(f"• {proj['name']}: {proj['description']}")
        self.intents['projects']['responses'] = ["Projects:\n" + "\n".join(proj_text)]
    
    def get_response(self, message):
        message = message.lower().strip()
        for intent, data in self.intents.items():
            for pattern in data['patterns']:
                if re.search(pattern, message):
                    return random.choice(data['responses'])
        return "I can help with skills, education, projects, or contact info. What would you like to know?"

chatbot = PortfolioChatbot()

@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/profile')
def api_profile():
    return jsonify(get_profile())

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_msg = data.get('message', '')
    session_id = session.get('session_id')
    
    bot_response = chatbot.get_response(user_msg)
    save_chat(session_id, user_msg, bot_response)
    
    return jsonify({'response': bot_response})

@app.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    session_id = session.get('session_id')
    history = get_chat_history(session_id)
    return jsonify(history)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
