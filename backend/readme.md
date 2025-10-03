# FastShip Backend

A comprehensive FastAPI backend application for delivery management demonstrating modern Python web development practices with authentication, database management, and real-world API design patterns.

## 🚀 Features

- **RESTful API**: Complete CRUD operations for shipment, seller, and delivery partner management
- **JWT Authentication**: Secure user authentication with token-based sessions for sellers and delivery partners
- **Database Integration**: PostgreSQL with async SQLAlchemy and Alembic migrations
- **Redis Caching**: Session management and token blacklisting
- **Email Notifications**: Automated email notifications for shipment status changes using Celery
- **Background Processing**: Celery integration for asynchronous task processing
- **Shipment Tracking**: Real-time shipment status tracking with timeline events
- **Tag System**: Shipment categorization (express, fragile, heavy, etc.)
- **Review System**: Customer feedback and rating system for shipments
- **Modern Architecture**: Clean separation of concerns with services, dependencies, and routers
- **API Documentation**: Interactive documentation with Scalar UI
- **Type Safety**: Full type hints with Pydantic models and SQLModel
- **Environment Configuration**: Secure configuration management with environment variables

## 🛠 Tech Stack

### Core Framework

- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: Latest Python features and performance improvements
- **Uvicorn**: Lightning-fast ASGI server

### Database & ORM

- **PostgreSQL**: Robust relational database with async support
- **SQLModel**: Modern ORM combining SQLAlchemy and Pydantic
- **Alembic**: Database migration management
- **asyncpg**: High-performance PostgreSQL adapter

### Authentication & Security

- **JWT (JSON Web Tokens)**: Stateless authentication
- **bcrypt**: Secure password hashing
- **OAuth2**: Industry-standard authorization framework

### Caching & Session Management

- **Redis**: In-memory data store for caching and session management
- **Token Blacklisting**: Secure logout functionality

### Development Tools

- **Pydantic**: Data validation and serialization
- **email-validator**: Email format validation
- **python-dotenv**: Environment variable management
- **Celery**: Distributed task queue for background processing
- **FastAPI-Mail**: Email sending capabilities
- **Pytest**: Testing framework

## 📋 API Endpoints

### Seller Authentication

- `POST /seller/signup` - Register new seller account
- `POST /seller/token` - Login and receive JWT token
- `GET /seller/logout` - Logout and blacklist token
- `GET /seller/verify` - Verify seller email
- `GET /seller/forgot_password` - Send password reset link
- `POST /seller/reset_password` - Reset seller password
- `GET /seller/reset_password_form` - Password reset form

### Delivery Partner Authentication

- `POST /partner/signup` - Register new delivery partner account
- `POST /partner/token` - Login and receive JWT token
- `POST /partner/` - Update delivery partner information
- `GET /partner/logout` - Logout and blacklist token
- `GET /partner/verify` - Verify delivery partner email

### Shipment Management

- `GET /shipment?id={id}` - Retrieve shipment details (requires authentication)
- `GET /shipment/track?id={id}` - Get shipment tracking page
- `POST /shipment` - Create new shipment (requires authentication)
- `PATCH /shipment?id={id}` - Update shipment information
- `GET /shipment/cancel?id={id}` - Cancel shipment
- `GET /shipment/review` - Submit review page
- `POST /shipment/review` - Submit shipment review
- `GET /shipment/tag?id={id}&tag_name={tag}` - Add tag to shipment
- `DELETE /shipment/tag?id={id}&tag_name={tag}` - Remove tag from shipment
- `GET /shipment/tagged?tag_name={tag}` - Get shipments with specific tag

### Documentation

- `GET /scalar` - Interactive API documentation

## 🏗 Project Structure

```
app/
├── api/                    # API layer
│   ├── dependencies.py     # Dependency injection
│   ├── router.py          # Main router aggregation
│   ├── tag.py             # API tags definition
│   ├── routers/           # Individual route modules
│   │   ├── seller.py      # Seller endpoints
│   │   ├── delivery_partner.py # Delivery partner endpoints
│   │   └── shipment.py    # Shipment endpoints
│   └── schemas/           # Pydantic schemas
│       ├── seller.py      # Seller request/response models
│       ├── delivery_partner.py # Delivery partner request/response models
│       └── shipment.py    # Shipment request/response models
├── core/                  # Core functionality
│   ├── security.py        # Security utilities
│   └── exceptions.py      # Custom exception handlers
├── database/              # Database layer
│   ├── models.py          # SQLModel database models
│   ├── session.py         # Database session management
│   └── redis.py           # Redis connection and utilities
├── services/              # Business logic layer
│   ├── base.py            # Base service class
│   ├── seller.py          # Seller business logic
│   ├── deliver_partner.py # Delivery partner business logic
│   ├── shipment.py        # Shipment business logic
│   ├── shipment_event.py  # Shipment event tracking
│   ├── notification.py    # Email notification service
│   └── user.py            # Base user business logic
├── templates/             # Email and HTML templates
│   ├── mail_*.html        # Email templates for notifications
│   └── password/          # Password reset templates
├── tests/                 # Test suite
│   ├── conftest.py        # Test configuration
│   └── test_main.py       # Main test file
├── worker/                # Background task processing
│   └── tasks.py           # Celery task definitions
├── config.py              # Configuration settings
├── main.py                # FastAPI application entry point
└── utils.py               # Utility functions
migrations/                # Alembic database migrations
├── env.py                 # Migration environment configuration
└── versions/              # Migration version files
```

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+

### 1. Clone Repository

```bash
git clone <repository-url>
cd fastship/backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Security Configuration
JWT_SECRET=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
```

### 4. Database Setup

#### PostgreSQL

Start your PostgreSQL service and create the database:

```bash
createdb your_database
```

#### Redis with Docker

```bash
docker run -d --name redis-server \
  -v redis-data:/data \
  -p 6379:6379 \
  redis/redis-stack-server:latest
```

Or use a different port to avoid conflicts:

```bash
docker run -d --name redis-server \
  -v redis-data:/data \
  -p 6679:6379 \
  redis/redis-stack-server:latest
```

If using port 6679, update your `.env`:

```env
REDIS_PORT=6679
```

### 5. Database Migrations

```bash
# Initialize migration environment (if not done)
alembic init migrations

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Run the Application

```bash
# Development server with auto-reload
fastapi dev app/main.py

# Or using uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at:

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/scalar

## 🔧 Development Workflow

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Testing Authentication

1. Register a new seller via `POST /seller/signup` or delivery partner via `POST /partner/signup`
2. Login via `POST /seller/token` or `POST /partner/token` to receive JWT token
3. Use the token in the `Authorization: Bearer <token>` header for protected endpoints

## 📊 Data Models

### User (Base Model)

- **Name**: User's display name
- **Email**: Unique email address (validated)
- **Password Hash**: Securely hashed password (excluded from serialization)

### Seller (inherits from User)

- **ID**: UUID primary key
- **Created At**: Account creation timestamp
- **Shipments**: One-to-many relationship with shipments

### Delivery Partner (inherits from User)

- **ID**: UUID primary key
- **Created At**: Account creation timestamp
- **Serviceable Zip Codes**: Array of serviceable zip codes
- **Max Handling Capacity**: Maximum shipment handling capacity
- **Shipments**: One-to-many relationship with assigned shipments
- **Properties**: Active shipments count, current handling capacity

### Shipment

- **ID**: UUID primary key
- **Created At**: Shipment creation timestamp
- **Content**: Description of shipment contents
- **Weight**: Package weight (max 25kg)
- **Destination**: Destination zip code
- **Status**: ShipmentStatus enum (placed, processing, in_transit, out_for_delivery, delivered, returned, cancelled)
- **Estimated Delivery**: Expected delivery datetime
- **Seller**: Many-to-one relationship with seller
- **Delivery Partner**: Many-to-one relationship with delivery partner
- **Timeline**: Relationship with shipment events for tracking
- **Tags**: Many-to-many relationship with tags for categorization
- **Review**: One-to-one relationship with shipment review

### ShipmentEvent

- **ID**: UUID primary key
- **Created At**: Event timestamp
- **Status**: Event status
- **Message**: Event description
- **Shipment**: Many-to-one relationship with shipment

### Tag

- **ID**: UUID primary key
- **Name**: TagName enum (express, standard, fragile, heavy, international, domestic, temperature_controlled, gift, return, documents)
- **Instruction**: Special handling instructions
- **Shipments**: Many-to-many relationship with shipments

### Review

- **ID**: UUID primary key
- **Created At**: Review timestamp
- **Rating**: Rating (1-5 stars)
- **Comment**: Optional review comment
- **Shipment**: One-to-one relationship with shipment

## 🔒 Security Features

- **Password Hashing**: Industry-standard bcrypt hashing
- **JWT Tokens**: Stateless authentication with configurable algorithms
- **Token Blacklisting**: Secure logout via Redis-based token invalidation
- **Input Validation**: Comprehensive request validation with Pydantic
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM

## 📚 Learning Objectives

This project demonstrates:

- Modern FastAPI application architecture with delivery management domain
- Async database operations with PostgreSQL
- JWT authentication implementation with dual user roles
- Database migration management with Alembic
- Redis integration for caching and session management
- Background task processing with Celery
- Email notification system with FastAPI-Mail
- Shipment tracking and timeline management
- Tag-based categorization system
- Review and rating system
- Clean code organization and separation of concerns
- Type-safe Python development with comprehensive models
- RESTful API design principles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
