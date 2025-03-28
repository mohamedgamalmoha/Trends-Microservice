# Trends-Microservice

## Overview

This is a distributed system built on a microservices architecture pattern, consisting of several specialized services that communicate through event-driven mechanisms. The system appears to be designed for content generation and social media automation, with services handling user management, trend analysis, content thinking/generation, and notifications.

## Core Services

### 1. Users Service
- **Purpose**: Handles user authentication, registration, password management, and authorization
- **Architecture**: Runs as a separate service
- **Data Store**: Dedicated PostgreSQL database (users-db-serv)
- **Network Access**: Exposed to both internal and global networks
- **Dependencies**: Database and RabbitMQ

### 2. Trends Service
- **Purpose**: Searches Google Trends for specified keywords
- **Architecture**: Split into main service and worker components
- **Data Store**: Dedicated PostgreSQL database (trends-db-serv)
- **Background Processing**: Utilizes Celery for asynchronous task execution
- **Network Access**: Exposed to both internal and global networks
- **Dependencies**: Database, RabbitMQ and Redis

### 3. Thinker Service
- **Purpose**: Generates content/posts using LLM technology
- **Architecture**: Split into main service and worker components
- **Data Store**: Dedicated PostgreSQL database (thinker-db-serv)
- **AI Integration**: Relies on Ollama for LLM capabilities
- **Background Processing**: Uses Celery for asynchronous processing
- **Network Access**: Exposed to both internal and global networks
- **Dependencies**: Database, Rabbitmq, Redis, and Ollama

### 4. Tweeter Service (Planned but not implemented)
- **Purpose**: Posts generated content to social media platforms
- **Architecture**: Split into main service and worker components
- **Data Store**: Dedicated PostgreSQL database (tweeter-db-serv)
- **Background Processing**: Utilizes Celery for asynchronous task execution
- **Network Access**: Exposed to both internal and global networks
- **Dependencies**: Database, RabbitMQ and Redis

### 5. Notification Service
- **Purpose**: Sends email notifications based on system events
- **Architecture**: Runs as a separate service
- **Network Access**: Internal network only
- **Dependencies**: RabbitMQ

### 6 Monitoring Service
- **Purpose**: Includes Flower for Celery task monitoring
- **Architecture**: Runs as a separate service
- **Network Access**: Internal network only
- **Dependencies**: Redis

### 7 Nginx Gateway
- **Purpose**: Routes external requests to appropriate microservices, providing a unified API interface
- **Architecture**: Runs as a separate service
- **Network Access**: Exposed to the global network
- **Dependencies**: All services

## Infrastructure Components

### Message Brokers
1. **RabbitMQ**:
   - Used for event-driven communication between services
   - Enables loose coupling between components
   - Central to the event broadcasting system

2. **Redis**:
   - Serves as the broker for Celery task queues
   - Enables asynchronous task processing for Trends and Thinker services

### AI/ML Components
- **Ollama**:
   - Provides LLM capabilities to the Thinker service
   - Runs in its own container with persistent model storage

### Databases
- Three separate PostgreSQL instances:
   - users-db-serv: Stores user data
   - trends-db-serv: Stores trend analysis results
   - thinker-db-serv: Stores content generation data
   - tweeter-db-serv: Stores post data (planned but not implemented)
- Each database is isolated to its respective service

### API Gateway / Load Balancer
- **Nginx**:
   - Acts as the entry point to the system
   - Routes external requests to appropriate microservices
   - Provides a unified API interface to clients

## Networking

The architecture uses two distinct networks:
1. **global-network**: 
   - Accessible by services that need external communication
   - Connected to the Nginx gateway
   
2. **internal-network**:
   - Isolated internal communication layer
   - Used for inter-service communication and database access
   - Improves security by limiting exposure

## Data Flow and Communication Patterns

1. **External Requests**:
   - Enter through Nginx gateway
   - Routed to appropriate service (users, trends, thinker)

2. **Event-Driven Communication**:
   - Services publish events to RabbitMQ
   - Interested services subscribe to relevant events
   - Notification service consumes events that require email notifications

3. **Background Processing**:
   - Long-running tasks delegated to Celery workers
   - Task status tracked through Flower dashboard
   - Results stored in respective databases

## Deployment and Persistence

- Docker containers used for all services
- Volume mounts ensure data persistence:
  - Database data stored in named volumes
  - Application code mounted from host for development
- Container restart policies ensure system resilience
- Shared startup scripts handle initialization tasks

## Monitoring and Management

- Celery Flower provides task monitoring tasks from different workers 
- Accessible through the Nginx proxy

This architecture follows modern microservices best practices with service isolation, event-driven communication, and specialized components for different aspects of the system functionality.