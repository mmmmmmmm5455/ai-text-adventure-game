# AI Text Adventure Engine

A local-first text adventure powered by **Ollama**, **Streamlit**, **LangChain/LangGraph**, and **ChromaDB** for long-term memory.

## Quick start

1. Install [Ollama](https://ollama.com/) and pull `llama3` (and `nomic-embed-text` for embeddings).  
2. `pip install -r requirements.txt`  
3. Copy `.env.example` to `.env`  
4. From the project root, set `PYTHONPATH` to the repo root, set `PYTHONIOENCODING=UTF-8` (recommended on Windows), then run:  
   `python -m streamlit run frontend/app.py`  
   Or use `start.bat` / `start.sh`.

See `README.md` (Chinese) for full details.
