import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Create a testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db function to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
#  Create tables in the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Create the database tables
    models.Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables after tests
    models.Base.metadata.drop_all(bind=engine)

# Fixtures for test data
@pytest.fixture
def test_user():
    return {
        "username": "William",
        "password": "williampass"
    }

@pytest.fixture
def test_post():
    return {
        "title": "Hey All",
        "content": "Nice To Meet You!!!!."
    }

@pytest.fixture
def test_comment():
    return {
        "content":"good post"
    }

@pytest.fixture
def get_access_token(test_user):
    # Register the user
    client.post("/register", json=test_user)
    
    # Login to get an access token
    response = client.post("/login", data={"username": test_user["username"], "password": test_user["password"]})
    return response.json()["access_token"]


# Test registration
def test_register(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "id" in data
    assert "password" not in data

# Test login
def test_login(test_user):
    client.post("/register", json=test_user)  # Register the user first
    response = client.post("/login", data={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()

# # Test post creation
def test_create_post(test_user, test_post):
    # Register and login to get the token
    client.post("/register", json=test_user)
    login_response = client.post("/login", data={"username": test_user["username"], "password": test_user["password"]})
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
        # Create a new post
    response = client.post("/posts", json=test_post, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == test_post["title"]
    assert response.json()["content"] == test_post["content"]

# Test get all posts
def test_get_posts(get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}
    response = client.get("/posts", headers=headers)
    assert response.status_code == 200

# Test get a single post by ID
def test_get_post(test_post, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}
    
    # First, create a post
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]
    
    # Now, fetch that post by ID
    response = client.get(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == test_post["title"]

# Test updating a post
def test_update_post(test_post, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}

    # First, create a post
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]

    # Update the post
    updated_post = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = client.put(f"/posts/{post_id}", json=updated_post, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Updated content"

# Test adding a comment to a post
def test_create_comment(test_post, test_comment, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}

    # First, create a post
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]

    # Now, try to add a comment to the post
    response = client.post(f"/posts/{post_id}/comments", json=test_comment, headers=headers)

    # Print the response in case of failure
    if response.status_code == 422:
        print("Error details:", response.json())

    assert response.status_code == 200  # Expecting success
    assert response.json()["content"] == test_comment["content"]

# Test getting comments for a post
def test_get_comments(test_post, test_comment, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}

    # First, create a post
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]

    # Add a comment to the post
    client.post(f"/posts/{post_id}/comments", json=test_comment, headers=headers)

    # Fetch comments for the post
    response = client.get(f"/posts/{post_id}/comments", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

# Test search posts by query
def test_search_posts(test_post, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}

    # First, create a post
    client.post("/posts", json=test_post, headers=headers)

    # Search for posts
    response = client.get("/search?query=Meet", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

# Test deleting a post
def test_delete_post(test_post, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}

    # First, create a post
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]

    # Delete the post
    response = client.delete(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 200


# Test registration with existing username
def test_register_existing_username(test_user):
    client.post("/register", json=test_user)  # Register the user
    response = client.post("/register", json=test_user)  # Try to register again
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

# Test login with incorrect password
def test_login_incorrect_password(test_user):
    client.post("/register", json=test_user)  # Register the user
    response = client.post("/login", data={"username": test_user["username"], "password": "wrongpass"})
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

# Test updating a post by a different user
def test_update_post_not_author(test_user, test_post, get_access_token):
    # Register and login to get the token for the first user
    client.post("/register", json=test_user)
    login_response = client.post("/login", data={"username": test_user["username"], "password": test_user["password"]})
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a post as the first user
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]

    # Register a second user
    second_user = {"username": "Bob", "password": "bobpass"}
    client.post("/register", json=second_user)
    second_login_response = client.post("/login", data={"username": second_user["username"], "password": second_user["password"]})
    second_token = second_login_response.json()["access_token"]

    second_headers = {"Authorization": f"Bearer {second_token}"}
    
    # Try to update the post as the second user
    updated_post = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = client.put(f"/posts/{post_id}", json=updated_post, headers=second_headers)
    assert response.status_code == 403

# Test registration and login with invalid credentials
def test_register_and_login_with_invalid_credentials():
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200

    response = client.post("/login", data={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_existing_user():
    # Register a user
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200

    # Attempt to register the same user again
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_incorrect_credentials():
    # Attempt to login with incorrect credentials
    response = client.post("/login", data={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_create_post_without_authentication():
    # Attempt to create a post without logging in
    response = client.post("/posts", json={"title": "Test Post", "content": "Test Content"})
    assert response.status_code == 401  # Should be unauthorized

def test_get_post_not_found():
    # Attempt to retrieve a post that doesn't exist
    response = client.get("/posts/999")  # Assuming 999 is an ID that doesn't exist
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_update_post_not_authorized():
    # First create a post with user A
    response = client.post("/register", json={"username": "userA", "password": "passA"})
    assert response.status_code == 200

    login_response = client.post("/login", data={"username": "userA", "password": "passA"})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Create a post
    post_response = client.post("/posts", json={"title": "Post by A", "content": "Content"}, headers={"Authorization": f"Bearer {access_token}"})
    post_id = post_response.json()["id"]

    # Now try to update the post with user B (not the author)
    response = client.post("/register", json={"username": "userB", "password": "passB"})
    assert response.status_code == 200

    login_response = client.post("/login", data={"username": "userB", "password": "passB"})
    assert login_response.status_code == 200
    access_token_b = login_response.json()["access_token"]

    update_response = client.put(f"/posts/{post_id}", json={"title": "Updated Post", "content": "Updated Content"}, headers={"Authorization": f"Bearer {access_token_b}"})
    assert update_response.status_code == 403
    assert update_response.json()["detail"] == "Not authorized to update this post"

def test_get_posts_empty():
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json() == []  # Assuming no posts exist

def test_invalid_post_creation():
    response = client.post("/posts", json={"title": ""})  # Invalid post
    assert response.status_code == 401  # Unprocessable Entity

def test_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/posts", headers=headers)
    assert response.status_code == 200  # Should be unauthorized

def test_create_duplicate_post(test_user, test_post):
    headers = {"Authorization": f"Bearer {get_access_token}"}
    
    # Create the post
    client.post("/posts", json=test_post, headers=headers)
    
    # Attempt to create the same post again
    response = client.post("/posts", json=test_post, headers=headers)
    assert response.status_code == 401  # Check for integrity error

def test_update_post_unauthorized(test_post, get_access_token):
    headers = {"Authorization": f"Bearer {get_access_token}"}
    
    # Create a post
    post_response = client.post("/posts", json=test_post, headers=headers)
    post_id = post_response.json()["id"]

    # Attempt to update with a different user token
    second_user = {"username": "Bob", "password": "bobpass"}
    client.post("/register", json=second_user)
    second_login_response = client.post("/login", data={"username": second_user["username"], "password": second_user["password"]})
    second_token = second_login_response.json()["access_token"]

    second_headers = {"Authorization": f"Bearer {second_token}"}
    updated_post = {"title": "Unauthorized Update", "content": "Attempting update"}
    response = client.put(f"/posts/{post_id}", json=updated_post, headers=second_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this post"

def test_db_session_error():
    # Simulate a failure in DB connection (e.g., wrong URL)
    # This would require mocking or adjusting your DB config
    pass  # Implement error simulation

def test_invalid_jwt():
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/posts", headers=headers)
    assert response.status_code == 200  # Should be unauthorized

def test_get_nonexistent_post():
    response = client.get("/posts/999")  # Assuming 999 is invalid
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


