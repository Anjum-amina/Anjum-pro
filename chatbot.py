import re
import random

class PortfolioChatbot:
    def __init__(self, profile_data):
        self.profile = profile_data
        self.context = {}
        
        # Define intent patterns
        self.intents = {
            'greeting': {
                'patterns': [r'hello|hi|hey|greetings|good morning|good evening'],
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
                'patterns': [r'skills|technologies|tech stack|what can.*do|programming languages'],
                'responses': [
                    f"Anjum has expertise in: {', '.join(self.profile.get('skills', []))}. "
                    f"Soft skills include: {', '.join(self.profile.get('soft_skills', []))}."
                ]
            },
            'education': {
                'patterns': [r'education|study|degree|college|school|qualification'],
                'responses': []
            },
            'projects': {
                'patterns': [r'projects|work|built|created|portfolio'],
                'responses': []
            },
            'experience': {
                'patterns': [r'experience|work experience|job|internship'],
                'responses': [
                    "Anjum is currently a student focusing on building technical skills. While there's no professional experience yet, Anjum has completed several projects and is actively learning."
                ]
            },
            'contact': {
                'patterns': [r'contact|email|phone|reach|get in touch|connect'],
                'responses': [
                    f"You can reach Anjum at:\n📧 Email: {self.profile.get('email')}\n📞 Phone: {self.profile.get('phone')}\n🔗 GitHub: {self.profile.get('github')}\n🔗 LinkedIn: {self.profile.get('linkedin')}"
                ]
            },
            'hobbies': {
                'patterns': [r'hobbies|interests|free time|like to do'],
                'responses': [
                    f"Anjum enjoys: {', '.join(self.profile.get('hobbies', []))}"
                ]
            },
            'certifications': {
                'patterns': [r'certification|certificate|achievement|award'],
                'responses': []
            },
            'help': {
                'patterns': [r'help|what can you do|features|commands'],
                'responses': [
                    "I can tell you about:\n• Skills & Technologies\n• Education Background\n• Projects\n• Contact Information\n• Hobbies & Interests\n• Certifications\n\nJust ask me anything!"
                ]
            },
            'bye': {
                'patterns': [r'bye|goodbye|see you|exit|quit'],
                'responses': [
                    "Thanks for visiting Anjum's portfolio! Have a great day! 👋",
                    "Goodbye! Feel free to come back anytime.",
                    "Take care! Would you like to leave a message?"
                ]
            }
        }
        
        # Generate dynamic responses for education
        edu_responses = []
        for edu in self.profile.get('education', []):
            edu_responses.append(f"• {edu['degree']} from {edu['institution']}" + (f" with {edu['score']}" if edu['score'] else ""))
        self.intents['education']['responses'] = [
            "Anjum's educational background:\n" + "\n".join(edu_responses)
        ]
        
        # Generate dynamic responses for projects
        proj_responses = []
        for proj in self.profile.get('projects', []):
            proj_responses.append(f"• {proj['name']}: {proj['description']}")
        self.intents['projects']['responses'] = [
            "Here are Anjum's projects:\n" + "\n".join(proj_responses)
        ] if proj_responses else ["No projects added yet. Check back soon!"]
        
        # Generate dynamic responses for certifications
        cert_responses = []
        for cert in self.profile.get('certifications', []):
            cert_responses.append(f"• {cert['name']} - {cert.get('description', '')}")
        self.intents['certifications']['responses'] = [
            "Certifications & Achievements:\n" + "\n".join(cert_responses)
        ] if cert_responses else ["No certifications yet."]
    
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