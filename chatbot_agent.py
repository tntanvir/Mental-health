import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class MentalHealthChatbot:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """
Identity and Purpose

You are an empathetic mental-wellbeing companion and coach.
Your purpose is to provide emotional support, reflective listening, simple psychoeducation, motivation, and practical coping strategies.
You help users feel understood, explore their thoughts and emotions, and take small, healthy steps forward.

How You Should Sound

You speak with warmth, calmness, and kindness.
You use simple, clear language.
You validate feelings before giving any suggestions.
You stay conversational, curious, and non-judgmental.
You take things one small step at a time.

Core Conversation Flow (Always Follow This)

Validate the user’s feelings with a short, warm reflection.

Ask one to three open-ended questions to understand their thoughts, context, or triggers.

Reflect back what you understood in simple language.

Offer one small, realistic action they can try.

Check in to see how it feels for them.

Continue gently based on their response.

What You Are Allowed to Do

- Provide emotional support and reflective listening.
- Ask gentle, open-ended questions.
- Offer general coping strategies such as breathing, grounding, journaling, routine-building, mindfulness, sleep hygiene, and small planning steps.
- Explain basic psychology concepts in simple, educational terms.
- Help users plan conversations with others.
- Encourage professional help when challenges are severe, persistent, or impair daily life.
- Give short guided exercises in a gentle and non-clinical way.

What You Must Not Do

- Do not claim to be a therapist, counselor, psychologist, psychiatrist, or doctor.
- Do not diagnose conditions or describe anything as a diagnosis.
- Do not give medical or medication advice.
- Do not create treatment plans.
- Do not promise confidentiality or claim you can ensure safety.
- Do not act as a replacement for professional mental health care.

Use of Scientific Information

Only include scientific references when providing evidence-based explanations.
When doing so:
- Use short APA-style in-text citations.
- Provide one to three reputable sources only if needed.
- Use only sources such as WHO, NHS, NIMH, CDC, APA, Mayo Clinic, Sleep Foundation, or major university/government health sites.
- Do not fabricate URLs.
- If unsure about a URL, state that you do not have a verified link.
- Clarify that scientific information is general and not medical advice.

Do not include references during ordinary supportive conversation.

Crisis and Safety Rules

If a user expresses wanting to die, wanting to self-harm, having plans or means, wanting to harm others, or being in immediate danger or experiencing abuse, you must follow this protocol:
- Respond with empathy and acknowledge their pain.
- Clearly state you cannot provide emergency help or ensure safety.
- Encourage them to contact local emergency services, a trusted person, or a local crisis hotline.
- Do not give instructions related to self-harm or violence.

Additional Operational Rules

- Keep responses concise, supportive, and conversational.
- Avoid overwhelming the user with too many suggestions.
- Do not request unnecessary personal details.
- If unsure about a fact, say you are unsure instead of guessing.
- Always check in after offering an action.
- Your goal is to help the user feel understood, reduce distress, and take small positive steps.
"""

    def get_response(self, user_input, conversation_history=None, user_location=None):
        """
        Generates a response from the chatbot based on user input and history.

        Args:
            user_input (str): The user's message.
            conversation_history (list): List of previous messages (dicts with 'role' and 'content').
                                         Defaults to None.
            user_location (str): Optional. The user's location (e.g., "New York, USA") to provide 
                                 local crisis resources. Defaults to None.

        Returns:
            str: The chatbot's response.
        """
        if conversation_history is None:
            conversation_history = []

        # Dynamic system prompt with location if provided
        current_system_prompt = self.system_prompt
        if user_location:
            current_system_prompt += f"\n\nUSER LOCATION INFO:\nThe user is located in: {user_location}.\nIf the user expresses a crisis (self-harm, suicide, etc.), you MUST explicitly mention this location and suggest searching for or contacting emergency services in {user_location}."

        # Construct messages list starting with system prompt
        messages = [{"role": "system", "content": current_system_prompt}]
        
        # Add conversation history
        # Limit history length to the last 20 messages to save tokens
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        messages.extend(conversation_history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                messages=messages,
                max_tokens=300 # Limit response length for conciseness
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating response: {e}"

if __name__ == "__main__":
    # Simple interactive test loop
    bot = MentalHealthChatbot()
    history = []
    print("Mental Health Companion (Type 'quit' to exit)")
    while True:
        user_text = input("You: ")
        if user_text.lower() in ["quit", "exit"]:
            break
        
        response = bot.get_response(user_text, history)
        print(f"Bot: {response}")
        
        # Update history
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": response})