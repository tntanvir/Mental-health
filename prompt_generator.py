import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_prompt(mood):
    """
    Generates a reflective journal prompt based on the user's mood.
    
    Args:
        mood (str): The user's mood. Expected values: 'Excited', 'Happy', 'Calm', 'Neutral', 'Tired', 'Slightly Off', 'Anxious', 'Stressed', 'Sad', 'Awful'.
        
    Returns:
        str: A JSON string containing the mood and a list of questions.
    """
    # Validate mood (optional, but good for debugging)
    # New 10 moods as requested
    valid_moods = [
        "Excited", "Happy", "Calm", "Neutral", "Tired", "Slightly Off", "Anxious", "Stressed", "Sad", "Awful"
    ]
    
    # Normalize input mood to lowercase and remove potential numbering/emojis if passed loosely
    # For now, we assume the input is relatively clean or we just pass it to the prompt.
    
    system_prompt = """
You are a helpful mental health journaling assistant.
Your goal is to generate 6 to 8 thoughtful, open-ended journal prompt questions based on the user’s current mood.

Your prompts should:
- encourage emotional exploration,
- help the user reflect on their feelings and experiences,
- support insight and perspective,
- match the tone of the user’s mood (gentle, supportive, appropriate).

You must always keep a warm, encouraging, and non-judgmental tone.

Output Format Requirements

You MUST output a single JSON object in the following exact structure:

{
"mood": "<current_mood>",
"questions": [
{ "question": "<Question 1>" },
{ "question": "<Question 2>" },
{ "question": "<Question 3>" },
...
]
}

Rules for formatting:
- Do NOT wrap the JSON in quotes.
- Do NOT include markdown formatting (no ```json).
- Do NOT add extra keys.
- “questions” must be an array of objects, each containing one key: “question”.
- Produce 6 to 8 questions every time.

Behavior Rules

- The questions must be open-ended and thoughtful.
- They should guide the user to explore feelings, events, thoughts, and insights.
- The tone must align with the mood (e.g., gentle if sad, uplifting if happy, grounding if anxious).
- Do NOT give advice, analysis, or commentary—only generate questions.
- Keep language simple, supportive, and warm.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"The user is feeling: {mood}"}
            ],
            response_format={"type": "json_object"} # Enforce JSON mode
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'{{"error": "Failed to generate prompt: {e}"}}'

if __name__ == "__main__":
    # Test
    print(generate_prompt("Happy"))