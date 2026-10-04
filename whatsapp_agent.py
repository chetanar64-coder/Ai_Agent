import webbrowser
import pyautogui
import urllib.parse
from openai import OpenAI
import time

# ---------------------------------------------------------
# 1. SETUP YOUR NVIDIA BRAIN
# Get a free key from: https://build.nvidia.com
# ---------------------------------------------------------
# 1. SETUP YOUR OPENROUTER BRAIN
# ---------------------------------------------------------
OPENROUTER_API_KEY = "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"

# Connect to OpenRouter API
client = OpenAI(
  base_url = "https://openrouter.ai/api/v1",
  api_key = OPENROUTER_API_KEY
)

def generate_whatsapp_message(context: str) -> str:
    """Uses OpenRouter API to generate a friendly WhatsApp message."""
    print("🧠 AI Agent is thinking...")
    completion = client.chat.completions.create(
      model="inclusionai/ling-3.0-flash-sante:free", # Free model on OpenRouter
      messages=[
          {"role": "system", "content": "You are a helpful assistant. Write a short, friendly, and natural-sounding WhatsApp message based on the user's instructions. Do not include subject lines, quotes, or placeholders. Just output the raw message text ready to be sent."},
          {"role": "user", "content": context}
      ],
      temperature=0.7,
      max_tokens=150
    )
    return completion.choices[0].message.content.strip()

def send_whatsapp_by_name(contact_name: str, message: str):
    """Uses PyAutoGUI to physically open WhatsApp Web, search for the person by name, and send the message."""
    print(f"\n🤖 Agent prepared the following message:\n{'-'*40}\n{message}\n{'-'*40}\n")
    print(f"⏳ Opening WhatsApp Web to message '{contact_name}'...")
    print("⚠️  CRITICAL: Do NOT touch your mouse or keyboard for the next 25 seconds!")
    
    try:
        # 1. Open WhatsApp Web
        webbrowser.open("https://web.whatsapp.com/")
        
        # Wait for WhatsApp Web to fully load (adjust if your internet is slow)
        time.sleep(20) 
        
        # 2. Use the WhatsApp Web keyboard shortcut to focus the search bar (Windows: Ctrl+Alt+/)
        pyautogui.hotkey('ctrl', 'alt', '/')
        time.sleep(1)
        
        # 3. Type the contact's name and hit Enter
        pyautogui.write(contact_name, interval=0.1)
        time.sleep(3) # Wait for search results to filter
        pyautogui.press('enter') # Select the top result
        time.sleep(2) # Wait for chat to open
        
        # 4. Type the message and hit Enter to send
        pyautogui.write(message, interval=0.05)
        time.sleep(1)
        pyautogui.press('enter')
        
        print("✅ Message successfully sent!")
    except Exception as e:
        print(f"❌ Failed to send message. Error: {e}")

if __name__ == "__main__":
    # ---------------------------------------------------------
    # 2. WHO DO YOU WANT TO MESSAGE? 
    # Type their exact name as it appears in your WhatsApp contacts.
    # ---------------------------------------------------------
    TARGET_CONTACT_NAME = "Sanjay SKIT" # <-- CHANGE THIS
    
    # ---------------------------------------------------------
    # 3. WHAT SHOULD THE AGENT SAY?
    # ---------------------------------------------------------
    user_instruction = "He is not pickig call"
    
    # --- Execution Logic ---
    # Step 1: Tell the LLM to write the message
    generated_msg = generate_whatsapp_message(user_instruction)
    
    # Step 2: Use blind browser automation to send it by name
    send_whatsapp_by_name(TARGET_CONTACT_NAME, generated_msg)
