# FastShip Backend System Diagrams

This document contains comprehensive system diagrams for the FastShip delivery management backend.

## Database Schema

```mermaid
erDiagram
    User {
        string name
        string email
        boolean email_verified
        string password_hash
    }
    
    Seller {
        uuid id PK
        datetime created_at
        string address
        int zip_code
    }
    
    DeliveryPartner {
        uuid id PK
        datetime created_at
        int max_handling_capacity
    }
    
    Location {
        int zip_code PK
    }
    
    ServiceableLocation {
        uuid partner_id PK,FK
        int location_id PK,FK
    }
    
    Shipment {
        uuid id PK
        datetime created_at
        string client_contact_email
        int client_contact_phone
        string content
        float weight
        int destination
        datetime estimated_delivery
        uuid seller_id FK
        uuid delivery_partner_id FK
    }
    
    ShipmentEvent {
        uuid id PK
        datetime created_at
        int location
        string status
        string description
        uuid shipment_id FK
    }
    
    Tag {
        uuid id PK
        string name
        string instruction
    }
    
    ShipmentTag {
        uuid shipment_id PK,FK
        uuid tag_id PK,FK
    }
    
    Review {
        uuid id PK
        datetime created_at
        int rating
        string comment
        uuid shipment_id FK
    }

    %% Inheritance relationships
    Seller ||--|| User : inherits
    DeliveryPartner ||--|| User : inherits
    
    %% One-to-many relationships
    Seller ||--o{ Shipment : creates
    DeliveryPartner ||--o{ Shipment : handles
    Shipment ||--o{ ShipmentEvent : has_timeline
    Shipment ||--|| Review : has_review
    
    %% Many-to-many relationships
    DeliveryPartner }o--o{ Location : services
    Shipment }o--o{ Tag : categorized_by
    
    %% Junction tables
    DeliveryPartner ||--o{ ServiceableLocation : ""
    ServiceableLocation }o--|| Location : ""
    Shipment ||--o{ ShipmentTag : ""
    ShipmentTag }o--|| Tag : ""
```

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebClient[Web Client]
        MobileApp[Mobile App]
        API_Docs[Scalar API Docs]
    end
    
    subgraph "API Gateway"
        FastAPI[FastAPI Application]
        CORS[CORS Middleware]
        Auth[JWT Authentication]
    end
    
    subgraph "API Layer"
        SellerAPI[Seller Router]
        PartnerAPI[Partner Router]
        ShipmentAPI[Shipment Router]
        Dependencies[Dependencies & Schemas]
    end
    
    subgraph "Business Logic"
        SellerService[Seller Service]
        PartnerService[Partner Service]
        ShipmentService[Shipment Service]
        NotificationService[Notification Service]
        UserService[User Service]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        Redis[(Redis Cache)]
        Models[SQLModel Models]
        Session[Async Sessions]
    end
    
    subgraph "Background Processing"
        Celery[Celery Workers]
        EmailQueue[Email Queue]
        Tasks[Background Tasks]
    end
    
    subgraph "External Services"
        SMTP[SMTP Server]
        EmailTemplates[Jinja2 Templates]
    end
    
    %% Client connections
    WebClient --> FastAPI
    MobileApp --> FastAPI
    API_Docs --> FastAPI
    
    %% Middleware flow
    FastAPI --> CORS
    CORS --> Auth
    Auth --> SellerAPI
    Auth --> PartnerAPI
    Auth --> ShipmentAPI
    
    %% API to Services
    SellerAPI --> SellerService
    PartnerAPI --> PartnerService
    ShipmentAPI --> ShipmentService
    Dependencies --> UserService
    
    %% Service dependencies
    SellerService --> NotificationService
    PartnerService --> NotificationService
    ShipmentService --> NotificationService
    
    %% Data access
    SellerService --> Models
    PartnerService --> Models
    ShipmentService --> Models
    UserService --> Models
    Models --> Session
    Session --> PostgreSQL
    
    %% Cache access
    Auth --> Redis
    SellerService --> Redis
    PartnerService --> Redis
    
    %% Background processing
    NotificationService --> Celery
    Celery --> EmailQueue
    EmailQueue --> Tasks
    Tasks --> SMTP
    Tasks --> EmailTemplates
    
    style FastAPI fill:#e1f5fe
    style PostgreSQL fill:#f3e5f5
    style Redis fill:#fff3e0
    style Celery fill:#e8f5e8
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant AuthService
    participant Redis
    participant Database
    participant EmailService
    
    Note over Client,EmailService: User Registration Flow
    
    Client->>FastAPI: POST /seller/signup
    FastAPI->>AuthService: Create user account
    AuthService->>Database: Save user (email_verified=false)
    AuthService->>EmailService: Send verification email
    EmailService-->>Client: Verification email sent
    
    Note over Client,EmailService: Email Verification
    
    Client->>FastAPI: GET /seller/verify?token=xyz
    FastAPI->>AuthService: Verify token
    AuthService->>Database: Update email_verified=true
    AuthService-->>Client: Account verified
    
    Note over Client,EmailService: Login Flow
    
    Client->>FastAPI: POST /seller/token
    FastAPI->>AuthService: Validate credentials
    AuthService->>Database: Check user credentials
    Database-->>AuthService: User data
    AuthService-->>FastAPI: JWT token
    FastAPI-->>Client: Access token
    
    Note over Client,EmailService: Protected Request
    
    Client->>FastAPI: GET /shipment/ (with Bearer token)
    FastAPI->>AuthService: Validate JWT
    AuthService->>Redis: Check blacklist
    Redis-->>AuthService: Token valid
    AuthService-->>FastAPI: User authenticated
    FastAPI-->>Client: Protected resource
    
    Note over Client,EmailService: Logout Flow
    
    Client->>FastAPI: GET /seller/logout
    FastAPI->>AuthService: Extract token JTI
    AuthService->>Redis: Add JTI to blacklist
    Redis-->>AuthService: Token blacklisted
    AuthService-->>Client: Logged out successfully
```

## Shipment Lifecycle

```mermaid
stateDiagram-v2
    [*] --> placed: Seller creates shipment
    
    placed --> processing: System assigns delivery partner
    processing --> in_transit: Partner picks up shipment
    in_transit --> out_for_delivery: Shipment reaches destination area
    out_for_delivery --> delivered: Customer receives shipment
    
    placed --> cancelled: Seller cancels
    processing --> cancelled: System/Partner cancels
    in_transit --> returned: Delivery failed
    out_for_delivery --> returned: Customer unavailable
    
    delivered --> [*]: Review submitted (optional)
    cancelled --> [*]
    returned --> [*]
    
    note right of delivered
        Email notification sent
        Review link provided
    end note
    
    note right of cancelled
        Cancellation email sent
        Partner capacity freed
    end note
    
    note right of returned
        Return notification sent
        Partner capacity freed
    end note
```

## API Request Flow

```mermaid
flowchart TD
    Start([API Request]) --> Auth{Requires Auth?}
    
    Auth -->|No| PublicEndpoint[Public Endpoint]
    Auth -->|Yes| ValidateJWT[Validate JWT Token]
    
    ValidateJWT --> CheckBlacklist[Check Redis Blacklist]
    CheckBlacklist --> TokenValid{Token Valid?}
    
    TokenValid -->|No| Unauthorized[401 Unauthorized]
    TokenValid -->|Yes| ExtractUser[Extract User from Token]
    
    ExtractUser --> RouteRequest[Route to Controller]
    PublicEndpoint --> RouteRequest
    
    RouteRequest --> ValidateInput[Validate Request Schema]
    ValidateInput --> CallService[Call Business Service]
    
    CallService --> DatabaseOp[Database Operation]
    DatabaseOp --> BusinessLogic[Apply Business Logic]
    
    BusinessLogic --> SideEffects{Side Effects?}
    SideEffects -->|Yes| BackgroundTask[Queue Background Task]
    SideEffects -->|No| FormatResponse[Format Response]
    
    BackgroundTask --> EmailNotification[Send Email Notification]
    EmailNotification --> FormatResponse
    
    FormatResponse --> CacheUpdate[Update Cache if Needed]
    CacheUpdate --> Response([Return Response])
    
    Unauthorized --> Response
    
    style Start fill:#e1f5fe
    style Response fill:#e8f5e8
    style Unauthorized fill:#ffebee
    style BackgroundTask fill:#fff3e0
```

## Background Task Processing

```mermaid
graph LR
    subgraph "FastAPI Application"
        Service[Notification Service]
        Queue[Task Queue]
    end
    
    subgraph "Celery Worker"
        Worker[Celery Worker Process]
        EmailTask[Email Task Handler]
    end
    
    subgraph "External Services"
        SMTP[SMTP Server]
        Templates[Email Templates]
    end
    
    subgraph "Email Types"
        PlacedEmail[Shipment Placed]
        DeliveryEmail[Out for Delivery]
        DeliveredEmail[Delivered]
        CancelledEmail[Cancelled]
        VerifyEmail[Email Verification]
        ResetEmail[Password Reset]
    end
    
    Service --> Queue
    Queue --> Worker
    Worker --> EmailTask
    EmailTask --> Templates
    EmailTask --> SMTP
    
    EmailTask --> PlacedEmail
    EmailTask --> DeliveryEmail
    EmailTask --> DeliveredEmail
    EmailTask --> CancelledEmail
    EmailTask --> VerifyEmail
    EmailTask --> ResetEmail
    
    style Service fill:#e1f5fe
    style Worker fill:#e8f5e8
    style SMTP fill:#fff3e0
```

## Data Flow Architecture

```mermaid
flowchart TB
    subgraph "Presentation Layer"
        API[REST API Endpoints]
        Docs[API Documentation]
        Forms[HTML Forms]
    end
    
    subgraph "Application Layer"
        Controllers[FastAPI Routers]
        Auth[Authentication Middleware]
        Validation[Request Validation]
    end
    
    subgraph "Business Layer"
        Services[Business Services]
        Rules[Business Rules]
        Events[Domain Events]
    end
    
    subgraph "Data Access Layer"
        ORM[SQLModel ORM]
        Repositories[Data Repositories]
        Migrations[Alembic Migrations]
    end
    
    subgraph "Infrastructure Layer"
        Database[(PostgreSQL)]
        Cache[(Redis)]
        Queue[Message Queue]
        Email[Email Service]
    end
    
    API --> Controllers
    Docs --> Controllers
    Forms --> Controllers
    
    Controllers --> Auth
    Auth --> Validation
    Validation --> Services
    
    Services --> Rules
    Rules --> Events
    Events --> Services
    
    Services --> ORM
    ORM --> Repositories
    Repositories --> Database
    
    Services --> Cache
    Events --> Queue
    Queue --> Email
    
    Migrations --> Database
    
    style API fill:#e1f5fe
    style Services fill:#e8f5e8
    style Database fill:#f3e5f5
    style Cache fill:#fff3e0
```