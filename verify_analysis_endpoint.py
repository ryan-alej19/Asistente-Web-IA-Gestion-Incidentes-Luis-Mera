import requests

def test_analysis_endpoint():
    base_url = 'http://localhost:8000/api'
    
    # 1. Login
    print("Logging in as analyst...")
    try:
        resp = requests.post(f'{base_url}/auth/token/', data={'username': 'analyst', 'password': 'analyst123'})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()['token']
        print("Login successful.")
        
        # 2. Get Incident List to find an ID
        headers = {'Authorization': f'Token {token}'}
        list_resp = requests.get(f'{base_url}/incidents/list/', headers=headers)
        incidents = list_resp.json().get('results', [])
        
        if not incidents:
            print("No incidents found to test.")
            return

        incident_id = incidents[0]['id']
        print(f"Testing incident #{incident_id}...")
        
        # 3. Get Analysis Details
        detail_resp = requests.get(f'{base_url}/incidents/{incident_id}/analysis-details/', headers=headers)
        
        if detail_resp.status_code == 200:
            print("Analysis details fetched successfully:")
            print(detail_resp.json())
        else:
            print(f"Failed to fetch details: {detail_resp.status_code} - {detail_resp.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_analysis_endpoint()
