# app.py
from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime
import uuid
import re
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# MongoDB Localhost Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['portfolio_db']

# Collections
profile_collection = db['profile']
chat_messages = db['chat_messages']
visitors_collection = db['visitors']

# Initialize default profile data if not exists
def init_profile_data():
    if profile_collection.count_documents({}) == 0:
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
        print("✅ Default profile data inserted into MongoDB")
    else:
        print("✅ Profile data already exists in MongoDB")

# Call initialization
init_profile_data()

# Chatbot Class
class PortfolioChatbot:
    def __init__(self):
        self.profile = profile_collection.find_one({'_id': 'main_profile'})
        self.context = {}
        
        # Define intent patterns
        self.intents = {
            'greeting': {
                'patterns': [r'hello|hi|hey|greetings|good morning|good evening|namaste'],
                'responses': [
                    "Hello! I'm Anjum's portfolio assistant. How can I help you today?",
                    "Hi there! Feel free to ask me about Anjum's skills, education, projects, or contact information.",
                    "Hey! What would you like to know about Anjum?"
                ]
            },
            'name': {
                'patterns': [r'your name|who are you|what is your name'],
                'responses': [
                    "I'm Anjum's virtual assistant! Anjum is a B.Tech student passionate about technology.",
                    "This is Anjum's portfolio assistant. Anjum is a self-motivated individual and tech enthusiast."
                ]
            },
            'skills': {
                'patterns': [r'skills|technologies|tech stack|what can.*do|programming languages|technical skills'],
                'responses': []
            },
            'education': {
                'patterns': [r'education|study|degree|college|school|qualification|academic'],
                'responses': []
            },
            'projects': {
                'patterns': [r'projects|work|built|created|portfolio|made|developed'],
                'responses': []
            },
            'experience': {
                'patterns': [r'experience|work experience|job|internship|professional'],
                'responses': [
                    "Anjum is currently a student focusing on building technical skills. While there's no professional experience yet, Anjum has completed several projects and is actively learning and growing."
                ]
            },
            'contact': {
                'patterns': [r'contact|email|phone|reach|get in touch|connect|call|mail'],
                'responses': []
            },
            'hobbies': {
                'patterns': [r'hobbies|interests|free time|like to do|passion'],
                'responses': []
            },
            'certifications': {
                'patterns': [r'certification|certificate|achievement|award|nss'],
                'responses': []
            },
            'help': {
                'patterns': [r'help|what can you do|features|commands|how to use'],
                'responses': [
                    "I can tell you about:\n• Skills & Technologies\n• Education Background\n• Projects\n• Contact Information\n• Hobbies & Interests\n• Certifications\n\nJust ask me anything about Anjum!"
                ]
            },
            'bye': {
                'patterns': [r'bye|goodbye|see you|exit|quit|thanks|thank you'],
                'responses': [
                    "Thanks for visiting Anjum's portfolio! Have a great day! 👋",
                    "Goodbye! Feel free to come back anytime.",
                    "Take care! Would you like to leave a message?"
                ]
            }
        }
        
        # Generate dynamic responses
        self._generate_dynamic_responses()
    
    def _generate_dynamic_responses(self):
        # Skills response
        skills_list = ', '.join(self.profile.get('skills', []))
        soft_skills_list = ', '.join(self.profile.get('soft_skills', []))
        self.intents['skills']['responses'] = [
            f"Anjum has expertise in: {skills_list}. Soft skills include: {soft_skills_list}.",
            f"Technical Skills: {skills_list}. Soft Skills: {soft_skills_list}."
        ]
        
        # Education response
        edu_text = []
        for edu in self.profile.get('education', []):
            edu_text.append(f"• {edu['degree']} from {edu['institution']}" + (f" with {edu['score']}" if edu['score'] else ""))
        self.intents['education']['responses'] = [
            "Anjum's educational background:\n" + "\n".join(edu_text)
        ]
        
        # Projects response
        proj_text = []
        for proj in self.profile.get('projects', []):
            proj_text.append(f"• {proj['name']}: {proj['description']}")
        self.intents['projects']['responses'] = [
            "Here are Anjum's projects:\n" + "\n".join(proj_text)
        ] if proj_text else ["No projects added yet. Check back soon!"]
        
        # Contact response
        self.intents['contact']['responses'] = [
            f"You can reach Anjum at:\n📧 Email: {self.profile.get('email')}\n📞 Phone: {self.profile.get('phone')}\n🔗 GitHub: {self.profile.get('github')}\n🔗 LinkedIn: {self.profile.get('linkedin')}"
        ]
        
        # Hobbies response
        hobbies_list = ', '.join(self.profile.get('hobbies', []))
        self.intents['hobbies']['responses'] = [
            f"Anjum enjoys: {hobbies_list}"
        ]
        
        # Certifications response
        cert_text = []
        for cert in self.profile.get('certifications', []):
            cert_text.append(f"• {cert['name']} - {cert.get('description', '')}")
        self.intents['certifications']['responses'] = [
            "Certifications & Achievements:\n" + "\n".join(cert_text)
        ] if cert_text else ["No certifications yet."]
    
    def get_response(self, message):
        """Generate response based on user message"""
        message = message.lower().strip()
        
        # Check for specific intents
        for intent, data in self.intents.items():
            for pattern in data['patterns']:
                if re.search(pattern, message):
                    return random.choice(data['responses'])
        
        # Default response for unrecognized queries
        default_responses = [
            "I'm not sure about that. Would you like to know about Anjum's skills, education, projects, or contact info?",
            "That's an interesting question! I specialize in answering questions about Anjum's portfolio. Try asking about skills, projects, or education.",
            "I don't have information about that. Feel free to ask me anything about Anjum's background, skills, or contact details!"
        ]
        return random.choice(default_responses)

# Initialize chatbot
chatbot = PortfolioChatbot()

# Routes
@app.route('/')
def home():
    """Render the main portfolio page"""
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    # Track visitor
    visitor_data = {
        'session_id': session.get('chat_session_id'),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'timestamp': datetime.now()
    }
    visitors_collection.insert_one(visitor_data)
    
    return render_template('index.html')

@app.route('/api/profile')
def get_profile():
    """API endpoint to get profile data"""
    profile = profile_collection.find_one({'_id': 'main_profile'})
    if profile and '_id' in profile:
        profile['_id'] = str(profile['_id'])
    return jsonify(profile)

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    """Admin endpoint to update profile"""
    try:
        data = request.json
        result = profile_collection.update_one(
            {'_id': 'main_profile'},
            {'$set': data},
            upsert=True
        )
        # Reinitialize chatbot with new data
        global chatbot
        chatbot = PortfolioChatbot()
        return jsonify({'success': True, 'modified': result.modified_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot API endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = session.get('chat_session_id', str(uuid.uuid4()))
        
        # Get chatbot response
        bot_response = chatbot.get_response(user_message)
        
        # Save to database
        message_data = {
            'session_id': session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.now()
        }
        chat_messages.insert_one(message_data)
        
        return jsonify({
            'response': bot_response,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.', 'error': str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for current session"""
    session_id = session.get('chat_session_id')
    if session_id:
        history = list(chat_messages.find({'session_id': session_id}).sort('timestamp', -1).limit(50))
        # Convert ObjectId and datetime for JSON
        for msg in history:
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat()
        return jsonify(history)
    return jsonify([])

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for current session"""
    session_id = session.get('chat_session_id')
    if session_id:
        deleted = chat_messages.delete_many({'session_id': session_id})
        return jsonify({'success': True, 'deleted': deleted.deleted_count})
    return jsonify({'success': False})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get portfolio statistics"""
    total_chats = chat_messages.count_documents({})
    unique_sessions = len(chat_messages.distinct('session_id'))
    total_visitors = visitors_collection.count_documents({})
    return jsonify({
        'total_messages': total_chats,
        'unique_visitors': unique_sessions,
        'total_visits': total_visitors
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask Application...")
    print(f"📊 MongoDB connected to: {MONGO_URI}")
    print(f"🎯 Portfolio available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
