"""Application entry point

Local development:
    python run.py

Production (Railway / any server):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT

The Procfile handles production startup automatically.
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,          # reload only in debug/dev mode
        log_level="info",
    )
