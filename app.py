from flask import Flask, render_template, request, jsonify, session
from models import ProfileData, ChatHistory
from chatbot import PortfolioChatbot
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Initialize chatbot
profile_data = ProfileData.get_profile()
chatbot = PortfolioChatbot(profile_data)

@app.route('/')
def home():
    """Render the main portfolio page"""
    # Create or get session ID for chat
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/profile')
def get_profile():
    """API endpoint to get profile data"""
    profile = ProfileData.get_profile()
    # Remove MongoDB _id for JSON response
    if '_id' in profile:
        profile['_id'] = str(profile['_id'])
    return jsonify(profile)

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    """Admin endpoint to update profile (protected in production)"""
    data = request.json
    result = ProfileData.update_profile(data)
    return jsonify({'success': True, 'modified': result.modified_count})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot API endpoint"""
    data = request.json
    user_message = data.get('message', '')
    session_id = session.get('chat_session_id', str(uuid.uuid4()))
    
    # Get chatbot response
    bot_response = chatbot.get_response(user_message)
    
    # Save to database
    ChatHistory.save_message(session_id, user_message, bot_response)
    
    return jsonify({
        'response': bot_response,
        'session_id': session_id
    })

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for current session"""
    session_id = session.get('chat_session_id')
    if session_id:
        history = ChatHistory.get_chat_history(session_id)
        # Convert ObjectId to string for JSON
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
        deleted = ChatHistory.clear_history(session_id)
        return jsonify({'success': True, 'deleted': deleted})
    return jsonify({'success': False})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get portfolio statistics"""
    total_chats = ChatHistory.chat_messages.count_documents({})
    unique_sessions = len(ChatHistory.chat_messages.distinct('session_id'))
    return jsonify({
        'total_messages': total_chats,
        'unique_visitors': unique_sessions
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)