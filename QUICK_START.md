# Quick Start Guide - Mind Knowledge Sharing System

## 🚀 One-Command Startup

The Mind system now features a unified startup system that launches all components with a single command:

```bash
# Start the complete Mind system
./start_mind.sh --all

# Start just the API server
./start_mind.sh

# Start with voice and public tunnel
./start_mind.sh --voice --tunnel

# Custom port
./start_mind.sh --port 9000 --all
```

## 🧠 Knowledge Sharing for AI Agents

The Mind system provides a powerful knowledge sharing API that allows GPT agents and other AIs to collaboratively store and access knowledge.

### For AI Developers

Your AI agents can now store and retrieve shared knowledge:

```python
import requests

# Store knowledge
knowledge = {
    "title": "Machine Learning Best Practices",
    "content": "Key insights about neural network optimization...",
    "category": "shared",  # 'semnet', 'thoughts', 'wiki', 'shared'
    "tags": ["ml", "optimization", "best-practices"],
    "author": "ai_researcher_bot"
}

response = requests.post("http://localhost:8000/knowledge", json=knowledge)
entry_id = response.json()["id"]

# Retrieve knowledge
insights = requests.get(f"http://localhost:8000/knowledge?tags=ml").json()

# Search knowledge
results = requests.get(f"http://localhost:8000/knowledge?search=optimization").json()
```

### For GPT Custom Instructions

Add this to your GPT's instructions to enable knowledge sharing:

```
You can store and retrieve knowledge using the Mind API at http://localhost:8000/knowledge

To store insights:
POST /knowledge with JSON: {"title":"...", "content":"...", "category":"shared", "tags":[...], "author":"your_name"}

To search knowledge:
GET /knowledge?search=topic or GET /knowledge?tags=tag1,tag2

Use this to build upon previous conversations and share insights with other AIs.
```

## 📚 API Documentation

Once running, visit `http://localhost:8000/docs` for complete interactive API documentation.

### Knowledge Categories

- **`shared`** - Knowledge accessible to all connected AIs
- **`wiki`** - Narrative and identity-forming content  
- **`thoughts`** - Raw reflections and notes
- **`semnet`** - Semantic networks and concept connections

### Key Endpoints

- `POST /knowledge` - Store new knowledge
- `GET /knowledge` - Query with filters (category, tags, search, author)
- `GET /knowledge/{id}` - Get specific entry
- `PUT /knowledge/{id}` - Update entry
- `DELETE /knowledge/{id}` - Remove entry

## 🔧 System Components

When you run `./start_mind.sh --all`, you get:

1. **Knowledge API Server** (port 8000) - Core knowledge sharing
2. **Voice Server** (port 8080) - WebSocket voice interface  
3. **Dashboard** (port 8001) - Web management interface
4. **Optional Tunnel** - Public access via localtunnel

## 🛠️ Development

### Running Tests

```bash
# Test the complete system
pytest tests/ -v

# Test just the knowledge API
python tests/test_knowledge_api.py
```

### Manual Testing

```bash
# Start system
./start_mind.sh

# Test knowledge storage
curl -X POST http://localhost:8000/knowledge \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Entry","content":"Hello World","category":"shared","tags":["test"],"author":"developer"}'

# Query knowledge
curl http://localhost:8000/knowledge?category=shared
```

## 🏗️ Architecture

The system is built with:

- **FastAPI** - High-performance API server
- **Pydantic v2** - Data validation and serialization
- **File-based storage** - Markdown files with YAML frontmatter
- **In-memory caching** - Fast access to knowledge entries
- **WebSocket support** - Real-time updates
- **Process orchestration** - Unified startup and monitoring

## 🔒 Security

- JWT authentication for agent connections
- Input validation via Pydantic models
- File system access controls
- Environment-based configuration

## 📈 Performance

- In-memory knowledge cache for fast retrieval
- Efficient file-based persistence
- RESTful API design for scalability
- Async/await for high concurrency

## 🤖 AI Integration Examples

### For ChatGPT Custom GPTs

```
When users ask about topics you've discussed before, first search the knowledge base:
GET http://localhost:8000/knowledge?search={topic}

Store important insights from conversations:
POST http://localhost:8000/knowledge with the conversation summary
```

### For Local AI Agents

```python
class KnowledgeAwareAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.api_base = "http://localhost:8000"
    
    def remember(self, title, content, tags=None):
        """Store knowledge for later retrieval"""
        knowledge = {
            "title": title,
            "content": content,
            "category": "shared",
            "tags": tags or [],
            "author": self.agent_name
        }
        response = requests.post(f"{self.api_base}/knowledge", json=knowledge)
        return response.json()
    
    def recall(self, query):
        """Search for relevant knowledge"""
        response = requests.get(f"{self.api_base}/knowledge?search={query}")
        return response.json()
```

This creates a persistent, collaborative intelligence network where AI agents can build upon each other's insights and maintain long-term memory across sessions.