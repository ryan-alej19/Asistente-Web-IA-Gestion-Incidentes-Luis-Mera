import requests

def test_stats():
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
        
        # 2. Get Stats
        print("Fetching stats...")
        headers = {'Authorization': f'Token {token}'}
        resp = requests.get(f'{base_url}/incidents/stats/', headers=headers)
        
        if resp.status_code == 200:
            print("Stats fetched successfully:")
            print(resp.json())
        else:
            print(f"Failed to fetch stats: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_stats()
