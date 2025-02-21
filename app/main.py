import redis
from langchain_openai import ChatOpenAI

# Redis connection
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
redis_client.set('greeting', 'Hello, AI Agent!')
print(redis_client.get('greeting').decode())

# OpenAI integration
chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
response = chat.invoke("What is an AI agent?")
print(response.content)  # Use `.content` to print the response text
