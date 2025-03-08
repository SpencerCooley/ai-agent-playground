# AI Agent with Redis - Docker Setup

## Overview
This repository contains a backend for creating an AI agent. It is built with FastAPI, Celery, and Redis. Everything is containerized and can be run locally.

## System Design
The application follows a distributed architecture pattern with the following key components:

![System Architecture Diagram](docs/system-architecture.png)

### Components
- **FastAPI Backend**: Handles HTTP requests and serves as the main API gateway
- **Celery Workers**: Process asynchronous tasks and long-running operations
- **Redis**: Serves dual purposes:
  - Message broker for Celery task queue
  - Caching layer for temporary data storage
- **PostgreSQL**: Persistent storage for application data

### Data Flow
1. Clients send requests to the FastAPI backend
2. For long-running operations, the backend dispatches tasks to Celery workers via Redis
3. Celery workers process tasks asynchronously and publish results to Redis
4. Websocket endpoints are used to stream results to the client by subscribing to Redis channels.
5. Permanent data is stored in PostgreSQL.

## Prerequisites
- Docker and Docker Compose installed on your system.

## Setup Instructions

### 1. Create the `.env` File
Create a `.env` file in the root directory (same level as `docker-compose.yml`) and add the following variables:

```env
REDIS_HOST=redis
REDIS_PORT=6379
OPENAI_API_KEY=your_openai_api_key
POSTGRES_USER=development
POSTGRES_PASSWORD=devpass
POSTGRES_DB=dev_db
POSTGRES_PORT=5432
```
Replace `your_openai_api_key` with your actual OpenAI API key.


### 2. Build and Start the Containers
To build and start the containers, run:

```bash
docker-compose up --build
```
This command will build all the containers and start them. This icludes containers for fastapi, celery workers, redis, and postgres. view the docker-compose.yml file to see the services and their configurations.

### 3. Stopping the Containers
To stop and remove the containers, run:

```bash
docker-compose down --remove-orphans
```

This is a good starting point for developing LLM driven applications.
