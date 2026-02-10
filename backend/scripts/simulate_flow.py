import requests
import json

BASE_URL = 'http://localhost:8000/api'

def run_simulation():
    print(f"--- SIMULATING EMPLOYEE FLOW ---\n")
    
    # 1. LOGIN
    print("[1] Logging in as 'empleado'...")
    try:
        auth_resp = requests.post(f"{BASE_URL}/auth/token/", json={
            'username': 'empleado',
            'password': 'empleado123'
        })
        if auth_resp.status_code != 200:
            print(f"FAILED LOGIN: {auth_resp.text}")
            return
        
        token = auth_resp.json()['access']
        print("LOGIN SUCCESS. Token acquired.\n")
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return

    # 2. CREATE INCIDENT
    print("[2] Submitting Incident ('GENERAR INCIDENTE')...")
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'title': 'Test Automation Incident',
        'description': 'This is a test submission simulating the frontend button click. Check AI response.',
        'url': 'http://malicious-test-example.com',
        'incident_type': 'phishing',
        'threat_type': 'phishing'
    }
    
    try:
        # Note: Frontend sends FormData, but typically JSON works too if view accepts it, 
        # checking views.py it uses parser_classes or standard request.data which handles both.
        # But for file upload support it often expects multipart.
        # Let's try simple data first.
        create_resp = requests.post(f"{BASE_URL}/incidents/create/", data=data, headers=headers)
        
        if create_resp.status_code == 201:
            res_json = create_resp.json()
            # Correct structure: { 'success': True, 'incident': {...}, 'gemini': {...} }
            incident_data = res_json.get('incident', {})
            print(f"ID: {incident_data.get('id')}")
            print(f"Title: {incident_data.get('title')}")
            
            # 3. VERIFY AI ANALYSIS
            gemini = res_json.get('gemini') # Key is 'gemini' not 'gemini_analysis'
            vt = res_json.get('virustotal') # Key is 'virustotal'
            
            print("\n--- AI ANALYSIS RESULT ---")
            if gemini:
                print(f"Risk Level: {gemini.get('risk_level')}")
                print(f"Explanation: {gemini.get('explanation')}")
            else:
                print("NO GEMINI ANALYSIS FOUND")

        else:
            print(f"\n[FAIL] STATUS {create_resp.status_code}")
            print(create_resp.text)
            
    except Exception as e:
        print(f"REQUEST ERROR: {e}")

if __name__ == "__main__":
    run_simulation()
