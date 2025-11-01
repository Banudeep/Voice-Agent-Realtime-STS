# 🦜🎤 Voice ReAct Agent - Python Server

A real-time voice-activated ReAct agent powered by OpenAI's Realtime API and LangChain. This Python server enables natural voice conversations with an AI agent that can use tools to perform actions like web search, location lookup, and flight booking.

![Voice ReAct Agent](static/react.png)

## Overview

This is an implementation of a [ReAct](https://arxiv.org/abs/2210.03629)-style agent that uses OpenAI's new [Realtime API](https://platform.openai.com/docs/guides/realtime). The agent can call tools by providing it a list of [LangChain tools](https://python.langchain.com/docs/how_to/custom_tools/#creating-tools-from-functions), making it easy to extend with custom functionality.

## Prerequisites

- **Python 3.10 or later**
- **OpenAI API Key** with Realtime API access
  - Check your access in the [OpenAI Realtime Playground](https://platform.openai.com/playground/realtime)
- **Tavily API Key** (for web search functionality)
  - Get an API key [here](https://app.tavily.com/)
- **FourSquare Service Token** (for location services)
  - Get an API key from [FourSquare Developer Portal](https://developer.foursquare.com/)
- **Amadeus API Key** (for flight booking services)
  - Get an API key from [Amadeus for Developers](https://developers.amadeus.com/)

## Installation

### Method 1: Using `uv` (Recommended)

1. **Install `uv` package manager:**

   ```bash
   pip install uv
   ```

2. **Install dependencies:**
   ```bash
   cd server
   uv sync
   ```

### Method 2: Using Virtual Environment

1. **Create a virtual environment** (from the `server` directory):

   ```bash
   # Windows
   py -3.11 -m venv .venv

   # macOS/Linux
   python3.11 -m venv .venv
   ```

2. **Activate the virtual environment:**

   ```bash
   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # Windows (Command Prompt)
   .venv\Scripts\activate.bat

   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Upgrade pip and wheel:**

   ```bash
   python -m pip install -U pip wheel
   ```

4. **Install dependencies:**

   ```bash
   python -m pip install -r requirements.txt
   ```

   **Alternative:** Since this project uses `pyproject.toml`, you can also install with:

   ```bash
   pip install -e .
   ```

## Environment Variables

Set up your API keys before running the server:

### macOS/Linux (bash/zsh):

```bash
export OPENAI_API_KEY="your-openai-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
export FOURSQUARE_SERVICE_TOKEN="your-foursquare-service-token"
export AMADEUS_API_KEY="your-amadeus-api-key"
```

### Windows PowerShell (session only):

```powershell
$env:OPENAI_API_KEY = "your-openai-api-key"
$env:TAVILY_API_KEY = "your-tavily-api-key"
$env:FOURSQUARE_SERVICE_TOKEN = "your-foursquare-service-token"
$env:AMADEUS_API_KEY = "your-amadeus-api-key"
```

### Windows (permanent for current user):

```powershell
setx OPENAI_API_KEY "your-openai-api-key"
setx TAVILY_API_KEY "your-tavily-api-key"
setx FOURSQUARE_SERVICE_TOKEN "your-foursquare-service-token"
setx AMADEUS_API_KEY "your-amadeus-api-key"
```

**Note:** After using `setx`, restart your terminal for changes to take effect.

### Using `.env` file (Alternative)

You can also create a `.env` file in the `server` directory:

```env
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
FOURSQUARE_SERVICE_TOKEN=your-foursquare-service-token
AMADEUS_API_KEY=your-amadeus-api-key
```

## Running the Server

### Using `uv`:

```bash
cd server
uv run src/server/app.py
```

### Using uvicorn directly:

```bash
cd server
python -m uvicorn src.server.app:app --host 0.0.0.0 --port 3000
```

The server will start on `http://localhost:3000`

## Usage

1. **Start the server** using one of the methods above
2. **Open your browser** and navigate to `http://localhost:3000`
3. **Grant microphone permissions** when prompted by your browser
4. **Start speaking** - the agent will listen and respond in real-time!

**Note:** Chrome is recommended for best compatibility with microphone access.

## Available Tools

The agent comes with the following tools by default:

- **Tavily Search**: Internet search capabilities
- **FourSquare Tools**: Location search, place details, and nearby places
  - `search_near`: Search for places near a location
  - `search_near_point`: Search using coordinates
  - `place_snap`: Quick place lookup
  - `place_details`: Detailed place information
  - `get_location`: Get location coordinates
- **Amadeus Flight Tools**: Flight search and booking
  - `flight_offers_search`: Search for flight offers
  - `flight_offers_price`: Get flight pricing
  - `flight_create_order`: Create flight booking

## Customization

### Adding Your Own Tools

Edit `server/src/server/tools.py` to add custom tools:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Description of what your tool does"""
    # Your tool implementation
    return "result"

# Add to the TOOLS list
TOOLS = [my_custom_tool, ...]
```

### Customizing Agent Instructions

Edit `server/src/server/prompt.py` to change the agent's behavior:

```python
INSTRUCTIONS = "You are a helpful travel assistant. Help in planning trips and finding places. Speak English."
```

## Project Structure

```
server/
├── src/
│   ├── langchain_openai_voice/     # LangChain OpenAI voice integration
│   │   ├── __init__.py
│   │   └── utils.py
│   └── server/
│       ├── app.py                   # Starlette application entry point
│       ├── tools.py                 # Tool definitions
│       ├── prompt.py                # Agent instructions
│       ├── utils.py                 # Utility functions
│       ├── conversation_graph.py    # Conversation flow management
│       ├── fourSquareTool.py       # FourSquare integration
│       ├── amadeusFlightTool.py     # Amadeus flight integration
│       └── static/                  # Frontend files (HTML, JS)
│           ├── index.html
│           ├── audio-processor-worklet.js
│           └── audio-playback-worklet.js
└── pyproject.toml                   # Python dependencies
```

## Troubleshooting

### WebSocket Connection Error (HTTP 403)

This error indicates:

- Your OpenAI account doesn't have Realtime API access
- Insufficient funds in your OpenAI account
- Invalid or expired API key

**Solution:**

- Verify your access at the [OpenAI Realtime Playground](https://platform.openai.com/playground/realtime)
- Check your OpenAI account balance
- Ensure your API key has the correct permissions

### Microphone Not Working

- Ensure your browser has microphone permissions
- Check browser console for errors
- Try using Chrome browser
- Verify your microphone is working in other applications

### Environment Variables Not Loading

- Ensure variables are set in the same terminal session where you run the server
- For permanent setup on Windows, restart your terminal after using `setx`
- If using a virtual environment, activate it before setting environment variables

### Module Import Errors

If you encounter import errors when running with uvicorn:

- Make sure you're running from the `server` directory, or
- Run with the full module path: `python -m uvicorn src.server.app:app --host 0.0.0.0 --port 3000`

## Technology Stack

- **Starlette**: ASGI web framework
- **LangChain**: LLM orchestration and tool integration
- **LangGraph**: Agent state management
- **uvicorn**: ASGI server
- **OpenAI Realtime API**: Real-time voice interaction

## How It Works

1. Browser captures microphone audio and sends it via WebSocket to the server
2. Server forwards audio stream to OpenAI's Realtime API
3. Agent processes audio and can invoke LangChain tools when needed
4. OpenAI generates audio response which is streamed back through server to browser
5. Browser plays the audio response in real-time

## Next Steps

Future enhancements planned:

- [ ] Enable interrupting the AI during responses
- [ ] Enable changing of instructions/tools based on state
- [ ] Add authentication middleware
- [ ] Multi-language support

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- Powered by [LangChain](https://www.langchain.com/)
- Inspired by the [ReAct paper](https://arxiv.org/abs/2210.03629)
