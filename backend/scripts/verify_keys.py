import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load keys
load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
VT_KEY = os.getenv('VIRUSTOTAL_API_KEY')

print(f"Loaded Keys:\nGemini: {'*' * 10}{GEMINI_KEY[-4:] if GEMINI_KEY else 'NONE'}\nVT: {'*' * 10}{VT_KEY[-4:] if VT_KEY else 'NONE'}")

# --- TEST GEMINI ---
print("\n[1/2] Testing Gemini API...")
try:
    if not GEMINI_KEY:
        raise ValueError("No Gemini Key found")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Gemini OK'")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAIL: {str(e)}")

# --- TEST VIRUSTOTAL ---
print("\n[2/2] Testing VirusTotal API...")
try:
    if not VT_KEY:
        raise ValueError("No VirusTotal Key found")
    headers = {"x-apikey": VT_KEY}
    # Test with a known safe IP (8.8.8.8)
    url = "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("SUCCESS: Connection established.")
        print(f"Attributes: {response.json()['data']['id']}")
    elif response.status_code == 403:
        print("FAIL: 403 Forbidden (Invalid Key)")
    else:
        print(f"FAIL: HTTP {response.status_code} - {response.text}")

except Exception as e:
    print(f"FAIL: {str(e)}")
