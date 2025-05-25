import pytest
from datetime import datetime, timedelta
from models.user import User
from models.user import Token

def test_signup_success(client, db):
    """Test successful user registration"""
    response = client.post(
        "/user/",
        json={"email": "test@example.com", "password": "testpass123", "role": "user"}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should match PublicUser model
    assert set(data.keys()) == {"id", "email", "role"}  # Only public fields
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    
    # Verify user was created in database
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.role == "user"

def test_signup_duplicate_email(client, db):
    """Test registration with existing email"""
    # Create initial user
    client.post(
        "/user/",
        json={"email": "duplicate@example.com", "password": "testpass123", "role": "user"}
    )
    
    # Try to create user with same email
    response = client.post(
        "/user/",
        json={"email": "duplicate@example.com", "password": "different123", "role": "user"}
    )
    
    assert response.status_code == 409  
    assert f"A user with email duplicate@example.com already exists" in response.json()["detail"]


def test_login_seeded_users_success(client, db):
    """Test successful login for all seeded users"""
    test_cases = [
        {"email": "super@admin.com", "password": "devpass", "expected_role": "superadmin"},
        {"email": "admin@admin.com", "password": "devpass", "expected_role": "admin"},
        {"email": "customer@customer.com", "password": "devpass", "expected_role": "customer"},
        {"email": "user@user.com", "password": "devpass", "expected_role": "user"},
    ]
    
    for case in test_cases:
        response = client.post(
            "/auth/login",
            json={"email": case["email"], "password": case["password"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"token"}  # Only token field as per AuthToken model
        assert isinstance(data["token"], str)
        
        # Verify token exists and get associated user
        token = db.query(Token).filter(Token.token == data["token"]).first()
        assert token is not None
        assert token.is_active == True
        
        # Verify the user associated with the token has correct role
        user = db.query(User).filter(User.id == token.user_id).first()
        assert user is not None
        assert user.role == case["expected_role"]
        assert user.email == case["email"]



def test_login_invalid_credentials(client, db):
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        json={"email": "super@admin.com", "password": "wrongpass"}
    )
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_login_nonexistent_user(client, db):
    """Test login attempt with email that doesn't exist in the system"""
    response = client.post(
        "/auth/login",
        json={"email": "notauser@fake.com", "password": "anypassword"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_protected_route_with_valid_token(client, db):
    """Test accessing protected route with valid token"""
    # Login and get token
    login_response = client.post(
        "/auth/login",
        json={"email": "super@admin.com", "password": "devpass"}
    )

    token = login_response.json()["token"]

    # Try to access protected route
    response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    # Should match PublicUser model
    assert set(data.keys()) == {"id", "email", "role"}  # Fields from PublicUser model
    assert isinstance(data["id"], int)
    assert isinstance(data["email"], str)
    assert isinstance(data["role"], str)

def test_protected_route_with_expired_token(client, db):
    """Test accessing protected route with expired token"""
    # Login and get token
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@admin.com", "password": "devpass"}
    )
    
    token = login_response.json()["token"]
    
    # Manually expire the token in the database
    db_token = db.query(Token).filter(Token.token == token).first()
    db_token.expires_at = datetime.utcnow() - timedelta(days=1)
    db.commit()
    
    # Try to access protected route
    response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]
    
    # Verify token was marked as inactive
    db_token = db.query(Token).filter(Token.token == token).first()
    assert db_token.is_active == False

def test_protected_route_with_inactive_token(client, db):
    """Test accessing protected route with inactive token"""
    # Login and get token
    login_response = client.post(
        "/auth/login",
        json={"email": "customer@customer.com", "password": "devpass"}
    )
    
    token = login_response.json()["token"]
    
    # Manually deactivate the token
    db_token = db.query(Token).filter(Token.token == token).first()
    db_token.is_active = False
    db.commit()
    
    # Try to access protected route
    response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401
    assert "Token is inactive" in response.json()["detail"] 