# Event Scheduling API
A RESTful API for event scheduling with collaborative features, version history, and role-based permissions.

## Features

1. User Management
   - Registration with username, email, and password
   - JWT token authentication
   - Refresh token support

2. Event Management
   - Create, read, update, and delete events
   - Recurring events with custom patterns
   - Conflict detection for overlapping events
   - Batch event creation

3. Collaboration Features
   - Share events with granular permissions (Owner/Editor/Viewer)
   - Real-time change notifications
   - Complete edit history tracking

4. Version Control
   - View complete changelog for any event
   - Compare differences between versions
   - Rollback to previous versions

## Technologies

- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- SQLite (Development)
- PostgreSQL (Production-ready)
- JWT Authentication
- Redis (Caching & Rate Limiting)

## Setup Instructions

### 1. Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### 2. Clone the repository
git clone https://github.com/krsandeep1808/Event-Management-System.git
cd Event-Scheduler-API


### 3. Set up virtual environment

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate


### 4. Install dependencies
pip install -r requirements.txt


### 5. Configure environment
Create a `.env` file:
DATABASE_URL=sqlite:///./events.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30


### 6. Initialize database
alembic upgrade head

### 7. Run the application
python run.py


**The API will be available at http://127.0.0.1:8000


## API Documentation

Interactive documentation available at:
- Swagger UI: http://127.0.0.1:8000/api/docs
- ReDoc: http://127.0.0.1:8000/api/redoc


## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Invalidate current token

### Event Management
- `POST /api/events` - Create new event
- `GET /api/events` - List all accessible events
- `GET /api/events/{id}` - Get specific event
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event
- `POST /api/events/batch` - Create multiple events

### Collaboration
- `POST /api/events/{id}/share` - Share event with users
- `GET /api/events/{id}/permissions` - List all permissions
- `PUT /api/events/{id}/permissions/{userId}` - Update permissions
- `DELETE /api/events/{id}/permissions/{userId}` - Remove access

### Version History
- `GET /api/events/{id}/history` - Get event changelog
- `GET /api/events/{id}/history/{versionId}` - Get specific version
- `POST /api/events/{id}/rollback/{versionId}` - Rollback to version
- `GET /api/events/{id}/diff/{versionId1}/{versionId2}` - Compare versions


## Example Usage

1. Register a user:
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass"}'

2. Login to get token:
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

3. Create an event:
curl -X POST "http://127.0.0.1:8000/api/events" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Team Meeting","description":"Weekly sync","start_time":"2023-06-01T10:00:00","end_time":"2023-06-01T11:00:00"}'


## Security Features
- JWT token authentication for all endpoints
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Rate limiting on authentication endpoints
- Input validation for all requests

## Deployment

For production deployment:
1. Use PostgreSQL:
   DATABASE_URL=postgresql://user:password@localhost/dbname

2. Set up Redis for caching:
   REDIS_URL=redis://localhost:6379

3. Run with Gunicorn:
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

4. Configure HTTPS and proper CORS settings

## Development

Key components:
- `app/main.py` - FastAPI application setup
- `app/models.py` - Database models
- `app/schemas.py` - Pydantic models
- `app/routers/` - API endpoints
- `app/services/` - Business logic
