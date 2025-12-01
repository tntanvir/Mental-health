import os
from chatbot_agent import MentalHealthChatbot
from prompt_generator import generate_prompt

# Initialize chatbot instance once to reuse connection if possible, 
# though MentalHealthChatbot re-inits client on each call or init.
# For stateless serverless functions, this might be re-initialized per request.
_chatbot_instance = None

def get_chatbot_instance():
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = MentalHealthChatbot()
    return _chatbot_instance

def process_chat_message(user_input, history=None, location=None):
    """
    Process a user's chat message and return the bot's response.

    Args:
        user_input (str): The message text from the user.
        history (list, optional): List of previous message dictionaries 
                                  [{'role': 'user'|'assistant', 'content': '...'}].
                                  Defaults to empty list.
        location (str, optional): User's current location (e.g. "New York, USA") 
                                  for crisis resource localization.

    Returns:
        str: The text response from the chatbot.
    """
    bot = get_chatbot_instance()
    return bot.get_response(user_input, conversation_history=history, user_location=location)

def generate_journal_prompts(mood):
    """
    Generate a list of journal prompts based on the user's mood.

    Args:
        mood (str): The user's current mood. 
                    Valid values: "excellent", "very good", "good", "okay", "neutral", 
                                  "slightly off", "low", "stressed", "sad", "awful".

    Returns:
        str: A JSON string containing the mood and a list of questions.
             Example: '{"mood": "happy", "questions": ["Q1", "Q2"]}'
    """
    return generate_prompt(mood)