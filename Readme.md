# AI Agent with Redis - Docker Setup

## Overview
This repository demonstrates a Dockerized AI agent that uses Redis for communication and LangChain for AI tasks. The AI agent is designed to run as a container and send its results via Redis.

## Prerequisites
- Docker and Docker Compose installed on your system.

## Setup Instructions

### 1. Create the `.env` File
Create a `.env` file in the root directory (same level as `docker-compose.yml`) and add the following variables:

```env
REDIS_HOST=redis
REDIS_PORT=6379
OPENAI_API_KEY=your_openai_api_key
GIT_REPO_ADDRESS=address used for the project you are working on
```
Replace `your_openai_api_key` with your actual OpenAI API key.

### 2. Use an ssh agent to use your host machine ssh key
to avoid too much configureation the container can use the ssh key from your host machine to do things

```bash
# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your SSH key to the agent so it's available in the Docker container
ssh-add ~/.ssh/id_ed25519  # Use this for modern keys (or ~/.ssh/id_rsa if using RSA)

```

### 3. Build and Start the Containers
To build and start the containers, run:

```bash
docker-compose up --build
```
This command will build both the Redis and AI agent containers and start them.

### 4. Running the Agent
The AI agent will run and display its output in the terminal. Any code changes to `main.py` will reflect immediately without needing to rebuild.

### 5. Stopping the Containers
To stop and remove the containers, run:

```bash
docker-compose down
```

### 6. Rebuilding Without Cache
If you need to rebuild without using Docker’s cache, use:

```bash
docker-compose build --no-cache
```

## Environment Variables Reference
- **REDIS_HOST**: The hostname of the Redis server (default: `redis`).
- **REDIS_PORT**: The port of the Redis server (default: `6379`).
- **OPENAI_API_KEY**: Your OpenAI API key.

## Troubleshooting
- Ensure that Docker is running on your system.
- If you encounter permission errors, try using `sudo` before the Docker commands.

Now you're ready to build an AI agent using langchain, pydanticai, Redis, and Docker
