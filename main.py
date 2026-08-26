"""
Main FastAPI REST API Server for BookMyShow Web Scraper.
Run using: python main.py OR uvicorn main.py:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from bms_scraper.routers import router as api_router
from bms_scraper.config import CONFIG

app = FastAPI(
    title="BookMyShow MCP Webscraper RESTful API",
    description=(
        "A high-performance RESTful API for scraping BookMyShow (https://in.bookmyshow.com). "
        "Returns clean, formatted, strictly-typed JSON containing only essential, useful data."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount Static directory for web UI dashboard if present
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
async def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "bookmyshow-mcp-webscraper-api",
        "version": "1.0.0",
        "target": CONFIG.BASE_URL,
    }



if __name__ == "__main__":
    import socket
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))

    def is_port_in_use(h: str, p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((h, p))
                return False
            except OSError:
                return True

    if is_port_in_use(host, port):
        print(f"⚠️ Port {port} is occupied or restricted on {host}.")
        for fallback_port in [8001, 8080, 8081, 8888]:
            if not is_port_in_use(host, fallback_port):
                print(f"🔄 Switching to available port: {fallback_port}")
                port = fallback_port
                break

    print(f"Starting BookMyShow RESTful Scraper API Server on http://{host}:{port} ...")
    uvicorn.run("main:app", host=host, port=port, reload=True)

