"""
MemoryBox - Unified Single-Port Application Launcher (Port 8080)
Launches FastAPI backend (port 8000), Streamlit frontend (port 8501),
and a high-performance Reverse Proxy on port 8080 with full WebSocket upgrade handling.

Usage:
    python run.py
"""

import sys
import os
import time
import socket
import asyncio
import subprocess
import webbrowser
import httpx
import websockets
import uvicorn
from starlette.applications import Starlette
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

BACKEND_TARGET = "http://127.0.0.1:8000"
FRONTEND_TARGET = "http://127.0.0.1:8501"
FRONTEND_WS_TARGET = "ws://127.0.0.1:8501"
PROXY_PORT = 8080

http_client = httpx.AsyncClient(timeout=60.0)


def wait_for_port_free(port: int, timeout: float = 5.0) -> bool:
    """Waits for any TIME_WAIT socket on the port to release cleanly."""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("127.0.0.1", port))
                return True
            except OSError:
                time.sleep(0.4)
    return False


async def proxy_http_handler(request):
    """
    Reverse proxy HTTP requests:
    - Paths starting with /api, /health, /docs, /openapi.json -> Backend (port 8000)
    - All other paths -> Streamlit Frontend (port 8501)
    """
    path = request.url.path
    query = request.url.query

    if (
        path.startswith("/api")
        or path.startswith("/health")
        or path.startswith("/docs")
        or path.startswith("/openapi.json")
    ):
        target_base = BACKEND_TARGET
    else:
        target_base = FRONTEND_TARGET

    url = f"{target_base}{path}"
    if query:
        url += f"?{query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    body = await request.body()

    try:
        req = http_client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )
        resp = await http_client.send(req, stream=True)

        excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
        response_headers = {
            k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers
        }
        # CORS & Security Headers
        response_headers["access-control-allow-origin"] = "*"
        response_headers["access-control-allow-methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response_headers["access-control-allow-headers"] = "*"

        return StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers=response_headers,
            background=resp.aclose
        )
    except Exception as e:
        return Response(
            content=f"Proxy Gateway Error connecting to {target_base}: {e}",
            status_code=502
        )


async def proxy_websocket_handler(websocket: WebSocket):
    """
    Bidirectional WebSocket proxy with full Upgrade handling for Streamlit live streams (_stcore/stream).
    Handles handshake, negotiates subprotocols ('streamlit'), and proxies binary and text frames.
    """
    client_subprotocols = websocket.headers.get("sec-websocket-protocol", "")
    requested_protocols = [p.strip() for p in client_subprotocols.split(",") if p.strip()]

    selected_subprotocol = requested_protocols[0] if requested_protocols else None
    await websocket.accept(subprotocol=selected_subprotocol)

    path = websocket.url.path
    query = websocket.url.query
    target_ws_url = f"{FRONTEND_WS_TARGET}{path}"
    if query:
        target_ws_url += f"?{query}"

    connect_kwargs = {
        "ping_interval": 20,
        "ping_timeout": 20,
        "max_size": 30 * 1024 * 1024
    }
    if requested_protocols:
        connect_kwargs["subprotocols"] = requested_protocols

    try:
        async with websockets.connect(target_ws_url, **connect_kwargs) as server_ws:
            async def client_to_server():
                try:
                    while True:
                        msg = await websocket.receive()
                        if "text" in msg:
                            await server_ws.send(msg["text"])
                        elif "bytes" in msg:
                            await server_ws.send(msg["bytes"])
                except (WebSocketDisconnect, asyncio.CancelledError):
                    pass

            async def server_to_client():
                try:
                    async for msg in server_ws:
                        if isinstance(msg, str):
                            await websocket.send_text(msg)
                        else:
                            await websocket.send_bytes(msg)
                except (WebSocketDisconnect, asyncio.CancelledError):
                    pass

            done, pending = await asyncio.wait(
                [asyncio.create_task(client_to_server()), asyncio.create_task(server_to_client())],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


proxy_app = Starlette(
    routes=[
        WebSocketRoute("/{path:path}", proxy_websocket_handler),
        Route("/{path:path}", proxy_http_handler, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    ]
)


def run_all():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")

    print("\n" + "="*65)
    print("  [MemoryBox] Single-Port Unified Reverse Proxy Launcher")
    print("  Running Entire Platform on: http://localhost:8080")
    print("="*65 + "\n")

    # Ensure port 8080 is available
    wait_for_port_free(PROXY_PORT, timeout=4.0)

    # 1. Start FastAPI Backend on Port 8000
    print("[1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "127.0.0.1", "--port", "8000"
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir)

    # 2. Start Streamlit Frontend on Port 8501 with Proxy-Friendly Flags
    print("[2/3] Starting Streamlit Frontend on http://127.0.0.1:8501 ...")
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port=8501",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--browser.serverAddress=localhost",
        "--browser.serverPort=8080",
        "--browser.gatherUsageStats=false"
    ]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=root_dir)

    time.sleep(3.0)

    # 3. Start Starlette Reverse Proxy on Port 8080
    print("[3/3] Starting Unified Reverse Proxy on http://localhost:8080 ...")
    print("\n" + "="*65)
    print("  SUCCESS: MemoryBox is LIVE on SINGLE PORT: http://localhost:8080")
    print("  * Streamlit UI & Vault : http://localhost:8080")
    print("  * Backend API Proxy    : http://localhost:8080/api")
    print("  * Swagger API Docs     : http://localhost:8080/docs")
    print("  * System Health        : http://localhost:8080/health")
    print("  (Press Ctrl+C to stop all services)")
    print("="*65 + "\n")

    try:
        webbrowser.open("http://localhost:8080")
    except Exception:
        pass

    try:
        config = uvicorn.Config(proxy_app, host="127.0.0.1", port=PROXY_PORT, log_level="warning")
        server = uvicorn.Server(config)
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down MemoryBox reverse proxy...")
    finally:
        print("Stopping child processes...")
        try:
            backend_proc.terminate()
        except Exception:
            pass
        try:
            frontend_proc.terminate()
        except Exception:
            pass
        print("All processes cleanly stopped. Goodbye!")


if __name__ == "__main__":
    run_all()
