import requests
import os

def debug_api():
    # Login as admin to get token (assuming admin exists)
    try:
        auth_resp = requests.post('http://localhost:8000/api/auth/token/', json={
            'username': 'admin', 
            'password': 'admin123' 
        })
        if auth_resp.status_code != 200:
            print(f"Auth failed: {auth_resp.text}")
            return

        token = auth_resp.json()['token']
        headers = {'Authorization': f'Token {token}'}

        # Get Incidents
        resp = requests.get('http://localhost:8000/api/incidents/list/', headers=headers)
        if resp.status_code != 200:
            print(f"List failed: {resp.text}")
            return
            
        data = resp.json()
        results = data.get('results', [])
        
        print(f"Total incidents: {len(results)}")
        for inc in results:
            print(f"ID: {inc['id']}, Type: '{inc['incident_type']}', Risk: '{inc['risk_level']}'")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_api()
