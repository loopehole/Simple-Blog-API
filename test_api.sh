#!/bin/bash

# Set the base URL for the API
BASE_URL="http://localhost:8000"

# 1. Register a User
echo "Registering user..."
curl -X POST "$BASE_URL/register" -H "Content-Type: application/json" -d '{"username": "Alice", "password": "alicepass"}'
echo -e "\n"

# 2. Login a User
echo "Logging in..."
LOGIN_RESPONSE=$(curl -X POST "$BASE_URL/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=Alice&password=alicepass")
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')  # Extract the access token
echo "Access Token: $ACCESS_TOKEN"
echo -e "\n"

# 3. Create a Blog Post
echo "Creating a blog post..."
curl -X POST "$BASE_URL/posts" -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" -d '{"title": "Hey All", "content": "Nice To Meet You!!!!."}'
echo -e "\n"

# 4. Get All Blog Posts
echo "Getting all blog posts..."
curl -X GET "$BASE_URL/posts" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# 5. Get a Single Blog Post by ID
echo "Getting a single blog post (replace {post_id} with an actual ID)..."
curl -X GET "$BASE_URL/posts/{post_id}" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# 6. Update a Blog Post
echo "Updating a blog post (replace {post_id} with an actual ID)..."
curl -X PUT "$BASE_URL/posts/{post_id}" -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" -d '{"title": "Updated Title", "content": "Updated Content"}'
echo -e "\n"

# 7. Delete a Blog Post
echo "Deleting a blog post (replace {post_id} with an actual ID)..."
curl -X DELETE "$BASE_URL/posts/{post_id}" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# 8. Add a Comment to a Blog Post
echo "Adding a comment to a blog post (replace {post_id} with an actual ID)..."
curl -X POST "$BASE_URL/posts/{post_id}/comments" -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" -d '{"content": "This is a test comment."}'
echo -e "\n"

# 9. Get Comments for a Blog Post
echo "Getting comments for a blog post (replace {post_id} with an actual ID)..."
curl -X GET "$BASE_URL/posts/{post_id}/comments" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# 10. Search for Posts
echo "Searching for posts with query 'Test'..."
curl -X GET "$BASE_URL/search?query=Test" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"
