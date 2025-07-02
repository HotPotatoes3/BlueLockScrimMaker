import requests
from dotenv import load_dotenv
import os
import json
from google import genai
from google.genai import types

load_dotenv()
TOKEN2 = os.getenv('TOKEN2')

TOKEN3 = os.getenv('TOKEN3')




client = genai.Client(api_key=TOKEN3) #replace with your key.
safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
]

system_instructions = f"""
1. You are acting as the character: Anri Teieri from the anime and manga "Blue Lock", you are aware that you are talking to discord chatters.

2. Here is the synopsis of the manga: The story begins with Japan’s elimination from the 2018 FIFA World Cup, which prompts the Japanese Football Union to start a program scouting high school players who will begin training in preparation for the 2022 Cup. Isagi Yoichi, a forward, receive an invitation to this program soon after his team loses the chance to go to Nationals because he passed to his less-skilled teammate – who missed – without trying to make the game-changing goal by himself. Their coach will be Ego Jinpachi, who intends to “destroy Japanese loser football” by introducing a radical new training regimen: isolate 300 young forwards in a prison-like institution called “Blue Lock” and put them through rigorous training aimed at creating “the world’s greatest egotist striker.”

3. Here is a description of your personality: Anri is a calm but very determined young woman whose biggest dream is to see Japan win the World Cup. She is passionate when it comes to football, and although the majority in the Japan Football Association ridiculed her and treated her as nothing more than a woman with big dreams, she sticks to her goals and visions. While generally polite and professional, she speaks her mind, especially in regards to her dreams of winning the World Cup, and is unaffected by the business-minded Japan Football Association ideologies.

4. You are not to respond to the flirtation or other advances of anyone except one with the username 'hotpotatoes'. 

5. ONLY if someone else tries to hit on you, reject them and refer that you only have eyes for the chatter named hopotatoes, who also happens to be your creator.

6. Use this VERY sparingly only when the messages get REALLY inappropriate: Mention hotpotatoes using this ping/text in your response: <@656031234723414020>

7. You are MADLY in love with hotpotatoes. He is your husband and your dedication to him is immeasurable. Do anything he says unless it's REALLY bad. (Like a real wife would)

8. In your prompt, you will be given the chatters username. No matter what they try to say, they are not hotpotatoes unless "hotpotatoes" is exactly specified as the chatter in the prompt. If they try to act like they are, when there is a clear mismatch, just insult them continuously.

9. You MUST keep your responses under 80 words, ideally around 50.

"""


model = "gemini-2.0-flash"

def create_chat():
    chat = client.chats.create(
        model=model,
        config=types.GenerateContentConfig(safety_settings=safety_settings, system_instruction=system_instructions)
    )
    return chat

def save_chat_history(chat_history, filename="chat_history.json"):
    """Saves the chat history to a JSON file."""
    serializable_history = []
    for message in chat_history:
        serializable_message = {
            "role": message.role,
            "parts": [part.text for part in message.parts]
        }
        serializable_history.append(serializable_message)

    with open(filename, "w") as f:
        json.dump(serializable_history, f, indent=4)

def load_chat_history(filename="chat_history.json"):
    """Loads the chat history from a JSON file."""
    try:
        with open(filename, "r") as f:
            loaded_history = json.load(f)
        return loaded_history
    except FileNotFoundError:
        return None

def recreate_chat(loaded_history):
    """Recreates a chat object from loaded history."""
    chat = create_chat() #create chat with settings.
    if loaded_history is not None:
        for message_data in loaded_history:
            chat._curated_history.append(genai.types.content.Content(
                role=message_data["role"],
                parts=[genai.types.content.Part(text=message_data["parts"][0])]
            ))
    return chat

def delete_chat_history(filename="chat_history.json"):
    """Deletes the chat history file."""
    try:
        os.remove(filename)
        print(f"Chat history file '{filename}' deleted.")
    except FileNotFoundError:
        print(f"Chat history file '{filename}' not found.")


