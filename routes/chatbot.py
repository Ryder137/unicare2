from flask import Blueprint, request, jsonify, current_app
import google.generativeai as genai
from datetime import datetime
import os

# Initialize Blueprint
chatbot_bp = Blueprint('chatbot', __name__)

# Configure Google AI
def configure_genai():
    """Configure Google's Generative AI with the API key."""
    try:
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            current_app.logger.error("GOOGLE_AI_API_KEY not found in environment variables")
            return False
        
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        current_app.logger.error(f"Error configuring Google AI: {str(e)}")
        return False

# Initialize the model
MODEL_NAME = 'gemini-pro'

# System prompt for the chatbot
SYSTEM_PROMPT = """You are UniCare, a supportive mental health assistant for students. 
Be empathetic, non-judgmental, and encouraging. Keep responses concise and focused on mental well-being.
If someone is in crisis, provide appropriate resources and encourage them to seek professional help.

You can help with:
- General mental health information
- Stress and anxiety management
- Study tips and time management
- Self-care suggestions
- Crisis resources in the Philippines

For serious concerns, always recommend speaking with a mental health professional."""

# Context management
def get_chat_context(session):
    """Get or initialize chat context from session."""
    if 'chat_history' not in session:
        session['chat_history'] = [
            {"role": "user", "parts": [SYSTEM_PROMPT]},
            {"role": "model", "parts": ["Hello! I'm UniCare, your mental health assistant. How can I support you today?"]}
        ]
    return session['chat_history']

# Chat endpoint
@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages using Google's Gemini model."""
    try:
        if not configure_genai():
            return jsonify({"error": "Service configuration error. Please try again later."}), 500
            
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Get chat history from session
        chat_history = get_chat_context(session)
        
        # Add user message to history
        chat_history.append({"role": "user", "parts": [user_message]})
        
        try:
            # Initialize the model
            model = genai.GenerativeModel(MODEL_NAME)
            
            # Generate response
            response = model.generate_content(chat_history)
            
            # Get the response text
            if not response or not response.text:
                raise ValueError("No response from AI model")
                
            bot_response = response.text
            
            # Add bot response to history
            chat_history.append({"role": "model", "parts": [bot_response]})
            
            # Keep chat history manageable
            if len(chat_history) > 10:  # Keep last 5 exchanges (10 messages)
                chat_history = chat_history[-10:]
            
            # Update session
            session['chat_history'] = chat_history
            
            return jsonify({
                "response": bot_response,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            current_app.logger.error(f"Error generating response: {str(e)}")
            return jsonify({
                "error": "I'm having trouble responding right now. Please try again later."
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred. Please try again later."
        }), 500

# Reset chat history
@chatbot_bp.route('/reset', methods=['POST'])
def reset_chat():
    """Reset the chat history."""
    if 'chat_history' in session:
        del session['chat_history']
    return jsonify({"status": "Chat history reset"})
