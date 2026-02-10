import requests

BASE_URL = 'http://localhost:8000/api'

def test_admin_flow():
    # 1. Login as Admin
    print("1. Logging in as admin...")
    resp = requests.post(f'{BASE_URL}/auth/token/', data={'username': 'admin', 'password': 'admin123'})
    if resp.status_code != 200:
        print("Login failed:", resp.text)
        return
    
    token = resp.json()['token']
    headers = {'Authorization': f'Token {token}'}
    print("   Login successful. Token acquired.")

    # 2. List Users
    print("\n2. Listing Users...")
    resp = requests.get(f'{BASE_URL}/users/list/', headers=headers)
    if resp.status_code == 200:
        users = resp.json()
        print(f"   Found {len(users)} users.")
        for u in users:
            print(f"   - {u['username']} ({u['role']}) Active: {u['is_active']}")
    else:
        print("   Failed to list users:", resp.status_code, resp.text)
        return

    # Find 'empleado' user
    empleado = next((u for u in users if u['username'] == 'empleado'), None)
    if not empleado:
        print("   User 'empleado' not found. Cannot test toggle.")
        return

    # 3. Toggle Status (Deactivate)
    print(f"\n3. Toggling status for {empleado['username']}...")
    resp = requests.patch(f'{BASE_URL}/users/{empleado["id"]}/toggle_status/', headers=headers)
    print("   Response:", resp.json())
    
    # 4. Toggle Status (Reactivate)
    print(f"\n4. Re-toggling status for {empleado['username']}...")
    requests.patch(f'{BASE_URL}/users/{empleado["id"]}/toggle_status/', headers=headers)
    print("   Restored status.")

    # 5. Change Role
    print(f"\n5. Changing role of {empleado['username']} to 'analyst'...")
    resp = requests.patch(f'{BASE_URL}/users/{empleado["id"]}/change_role/', json={'role': 'analyst'}, headers=headers)
    print("   Response:", resp.json())

    # 6. Revert Role
    print(f"\n6. Reverting role of {empleado['username']} to 'employee'...")
    requests.patch(f'{BASE_URL}/users/{empleado["id"]}/change_role/', json={'role': 'employee'}, headers=headers)
    print("   Reverted role.")

if __name__ == '__main__':
    try:
        test_admin_flow()
    except Exception as e:
        print("Error:", e)
