# AutoCode

An agentic LLM system that lets users generate and execute Python code through natural language. Describe what you need — the agent writes Python, executes it, and interprets the results.

**Built with:** FastAPI + Ollama + TinyLlama (1.1B parameters)

---

## 🏗 Architecture

```
User Interface (HTML/JS)
           ↓  HTTP POST /chat
     FastAPI Backend (localhost:8000)
           ↓
     Ollama API (localhost:11434)
           ↓  TinyLlama Model
     Code Generation & Extraction
           ↓
     Code Executor (subprocess + 60s timeout)
           ↓
     Output Capture
           ↓
     Result Interpretation
           ↓
     JSON response → Frontend displays code, output, interpretation
```

---

## 📁 Project Structure

```
autocode/
├── backend/
│   ├── main.py              # FastAPI app, routes, CORS, input validation
│   ├── agent.py             # LLM orchestration & code execution pipeline
│   ├── executor.py          # Subprocess code runner with timeout
│   ├── prompts.py           # System prompt for TinyLlama
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (not tracked)
├── frontend/
│   └── index.html           # Web UI for chat interface
├── .gitignore
└── README.md
```

---

## ✅ Prerequisites

- **Ollama** installed locally: [ollama.ai](https://ollama.ai)
- **Python 3.11+**
- **TinyLlama model** (pulled via Ollama)

---

## 🚀 Setup & Run

### 1. Download and Start Ollama

**Windows/Mac/Linux:**
```bash
# Download from https://ollama.ai
# Run Ollama (it starts on port 11434)
ollama serve
```

In a **new terminal**, pull the TinyLlama model:
```bash
ollama pull tinyllama
```

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Dependencies:
- fastapi==0.115.0
- uvicorn==0.30.6
- requests (Ollama API calls)
- pandas, numpy, matplotlib, scipy, yfinance, plotly, seaborn
- python-dotenv

### 3. Start the FastAPI Backend

```bash
cd backend
python main.py
```

You should see:
```
Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
```

Verify: `curl http://localhost:8000/health`

### 4. Open the Frontend

**Option A: Direct file access**
```bash
# Just open in your browser
file:///path/to/frontend/index.html
```

**Option B: Serve with Python**
```bash
cd frontend
python -m http.server 8001
# Open http://localhost:8001/index.html
```

---

## 📡 API Endpoints

### POST /chat
Generates Python code and executes it.

**Request:**
```json
{
  "message": "print sum of [1,2,3,4,5]",
  "history": []
}
```

**Response:**
```json
{
  "llm_response": "I'll write code to calculate the sum...",
  "code": "print(sum([1,2,3,4,5]))",
  "execution": {
    "success": true,
    "stdout": "15\n",
    "stderr": "",
    "plot_path": null
  },
  "interpretation": "The sum equals 15."
}
```

### GET /health
Health check.

**Response:**
```json
{
  "status": "ok"
}
```

---

## 📝 Example Prompts

- `"print 'hello world'"`
- `"calculate 2 + 2"`
- `"print sum of [1,2,3,4,5]"`
- `"create a list of numbers 1 to 10 and print them"`
- `"write a loop to print 1 to 5"`

---

## 🔄 How It Works

1. **User enters prompt** in frontend UI
2. **Backend calls Ollama API** with TinyLlama model
3. **TinyLlama generates Python code** in markdown format
4. **Code is extracted** using regex from response
5. **Code executes** in subprocess (60-second timeout)
6. **Output is captured** (stdout/stderr)
7. **Result sent back** to frontend
8. **Frontend displays** code, output, and interpretation

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| "Connection refused on localhost:11434" | Ensure Ollama is running: `ollama serve` |
| "Model not found" | Pull model: `ollama pull tinyllama` |
| "Port 8000 in use" | Change port in `main.py` or kill process |
| "Code execution timeout" | Adjust timeout in `executor.py` (default 60s) |
| "Frontend won't connect" | Check CORS is enabled in `main.py` |

---

## ⚡ Performance

- **Response time:** 15-30 seconds per request (CPU inference)
- **Model size:** TinyLlama ~640MB
- **API timeout:** 300 seconds
- **Execution timeout:** 60 seconds
- **Best for:** Code generation, simple data tasks, calculations

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message, get back code + output + interpretation |
| GET | `/health` | Health check |

### POST `/chat` Request Body

```json
{
  "message": "Plot AAPL stock for the last 100 days",
  "history": []
}
```

### Response

```json
{
  "llm_response": "...",
  "code": "import yfinance as yf\n...",
  "execution": {
    "stdout": "Mean: 182.4 ...",
    "stderr": "",
    "plot": "<base64 encoded PNG>",
    "success": true
  },
  "interpretation": "Apple's stock has trended upward...",
  "retry_attempted": false
}
```

---

## Known Limitations

- Code runs in a subprocess (not a full Docker sandbox). Production deployment should use E2B or Docker for stronger isolation.
- No file upload support yet (planned for Week 2).
- Session history resets on page reload (no persistence).
- Rate limited by Anthropic API — heavy parallel use may hit limits.

---

## Future Work (Week 2 & 3)

- CSV file upload and analysis (Scenario B)
- Docker/E2B sandboxed execution
- Streaming responses for real-time output
- More robust error recovery with multiple retries
- Unit tests for the execution pipeline

---

## AI Tool Usage Acknowledgment

Claude (Anthropic) was used to assist with boilerplate code generation and debugging during development. All architecture decisions, system prompt design, and overall design are original work by the team.
