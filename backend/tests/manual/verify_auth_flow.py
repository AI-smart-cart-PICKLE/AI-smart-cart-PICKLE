import requests

def test_signup_and_login():
    base_url = "http://localhost:8000"
    
    # 1. Signup
    signup_data = {
        "email": "test_user_unique@test.com",
        "password": "Password123!",
        "nickname": "Tester"
    }
    
    print(f"Trying to signup with {signup_data['email']}...")
    try:
        signup_res = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        if signup_res.status_code == 200:
            print("✅ Signup success!")
        elif signup_res.status_code == 400:
            print(f"ℹ️ User might already exist: {signup_res.json()}")
        else:
            print(f"❌ Signup failed: {signup_res.status_code}, {signup_res.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Login
    login_data = {
        "email": "test_user_unique@test.com",
        "password": "Password123!"
    }
    
    print(f"Trying to login with {login_data['email']}...")
    login_res = requests.post(f"{base_url}/api/auth/login", json=login_data)
    
    if login_res.status_code == 200:
        data = login_res.json()
        token = data.get("access_token")
        print(f"✅ Login success! Token: {token[:10]}...")
        
        # 3. Get Me
        print("Trying to fetch user info with token...")
        me_res = requests.get(
            f"{base_url}/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if me_res.status_code == 200:
            print(f"✅ GetMe success! User: {me_res.json()}")
            return True
        else:
            print(f"❌ GetMe failed: {me_res.status_code}, {me_res.text}")
    else:
        print(f"❌ Login failed: {login_res.status_code}, {login_res.text}")
    
    return False

if __name__ == "__main__":
    test_signup_and_login()
