import requests

# 1. Get Token (Admin or Employee)
login_url = 'http://localhost:8000/api/auth/token/'
analyze_url = 'http://localhost:8000/api/incidents/analyze/'

try:
    # Login
    resp = requests.post(login_url, json={'username': 'empleado', 'password': 'empleado123'})
    if resp.status_code != 200:
        print("Login Failed:", resp.text)
        exit()
    
    token = resp.json()['access']
    print("Login Successful. Token obtained.")

    # Test Analyze
    payload = {
        'description': 'URGENTE: Acceda a este link para evitar el bloqueo de su cuenta bancaria. Es muy importante.',
        'url': 'http://banco-falso-login.com'
    }
    
    print("\nSending Analysis Request...")
    analyze_resp = requests.post(analyze_url, json=payload, headers={'Authorization': f'Bearer {token}'})
    
    if analyze_resp.status_code == 200:
        data = analyze_resp.json()
        print("\n--- ANALYSIS RESULT ---")
        print(f"Success: {data['success']}")
        if data.get('analysis'):
            print(f"Risk Level: {data['analysis'].get('risk_level')}")
            print(f"Confidence: {data['analysis'].get('confidence')}")
            print(f"Explanation: {data['analysis'].get('explanation')}")
    else:
        print("Analysis Failed:", analyze_resp.text)

except Exception as e:
    print("Error:", e)
