<<<<<<< HEAD
# Simple-Blog-API

## Overview
This is a simple blog API built with FastAPI that supports user registration, authentication, and CRUD operations for blog posts and comments. It utilizes JWT for secure user authentication and provides endpoints for listing and searching posts.

## Features
- User registration and authentication with JWT.
- CRUD operations for blog posts.
- List and search blog posts by title or content.
- Commenting on blog posts, tied to both users and posts.
- Unit tests covering major functionalities.

## Endpoints

### Authentication
- **POST** `/register`: Register a new user.
- **POST** `/login`: Login and obtain a JWT token.

### Blog Posts
- **POST** `/posts`: Create a new blog post (authentication required).
- **GET** `/posts`: List all blog posts.
- **GET** `/posts/{post_id}`: Get a single blog post by ID.
- **PUT** `/posts/{post_id}`: Update a blog post (authentication required; only the author can update).
- **DELETE** `/posts/{post_id}`: Delete a blog post (authentication required; only the author can delete).

### Comments
- **POST** `/posts/{post_id}/comments`: Add a comment to a blog post (authentication required).
- **GET** `/posts/{post_id}/comments`: List comments for a blog post.

### Search
- **GET** `/search?query={search_term}`: Search for a post by title or content.

### Home
- **GET** `/`: Home page endpoint.

## Database
- Uses SQLite for simplicity, but can be configured for other databases (e.g., PostgreSQL).

## Models
- **User**: Represents users in the system.
- **Post**: Represents blog posts with title, content, and timestamp.
- **Comment**: Represents comments tied to both users and posts.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd simple_blog_API
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Before running the application, ensure that you set your secret key:
```bash
export SECRET_KEY="your_secret_key_here"
```

## Running the API
To run the FastAPI application, use the following command:
```bash
uvicorn main:app --reload
```
The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Instructions to Test Endpoints
1. Make it executable: Run the following command in your terminal:
   ```bash
   chmod +x test_api.sh
   ```
3. Run the script: Execute the script:
   ```bash
   ./test_api.sh
   ```

## Testing
To run tests, use:
```bash
pytest tests/test_main.py
```
Achieved 93% code coverage for the entire codebase.

## Documentation
The API is self-documented using FastAPI's automatic documentation feature. Access it at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Error Handling
Custom exception handlers are implemented for consistent error responses throughout the API.

## License
This project is licensed under the MIT License.
>>>>>>> commit_hash
