from models.user import User  # Ensure this path is correct
from dependencies.dependencies import get_db

# test that a user is successfully created given all the perfect conditions. 
def test_create_user(client, db):
    """Test user registration and verify in the database"""
    user = db.query(User).filter(User.email == "testing11@users.com").first()
    # Step 1: Send API request to create a user
    response = client.post("/user/", json={"email": "testing11@users.com", "password": "devpass", "role":"admin"})
    
    user_check = db.query(User).filter(User.email == "testing11@users.com").first()

    assert user_check.email == "testing11@users.com"
    assert response.status_code == 200  # Ensure the request was successful
    data = response.json()
    # Check response structure
    # assert "id" in data
    assert "id" in data
    assert "email" in data
    assert "role" in data
    assert data["email"] == "testing11@users.com"
    assert data["role"] == "admin"

    # Step 2: Verify that the user was actually added to the test database
    user = db.query(User).filter(User.email == "testing11@users.com").first()
    
    assert user is not None  # Ensure user exists
    assert user.email == "testing11@users.com"
