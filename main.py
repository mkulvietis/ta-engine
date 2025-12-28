import logging
import uvicorn
import argparse
from fastapi import FastAPI
from server.server import router as api_router
from server.server import mcp

app = FastAPI(title="Technical Analysis Engine")

# Include the unified router (REST endpoints)
app.include_router(api_router)

# Mount MCP Server (SSE)
app.mount("/mcp", mcp.sse_app())

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ta-engine"}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description="Technical Analysis Engine")
    subparsers = parser.add_subparsers(dest="command")
    
    # Server command (REST + SSE)
    server_parser = subparsers.add_parser("server", help="Run the unified REST/MCP server")
    server_parser.add_argument("--port", type=int, default=8001, help="Port to run on")
    server_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run on")
    
    # MCP Stdio command
    subparsers.add_parser("mcp-server", help="Run the MCP server in stdio mode")
    
    args = parser.parse_args()
    
    if args.command == "server":
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.command == "mcp-server":
        mcp.run()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
