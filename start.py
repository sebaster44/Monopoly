"""Start the backend and the frontend dev server together. Ctrl+C stops both.

Usage: python start.py
The backend takes port 8000, or the next free port if 8000 is busy. The frontend is always
served at http://localhost:5173.
"""

import os
import shutil
import socket
import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
FRONTEND_PORT = 5173


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def install_backend() -> None:
    if venv_python().exists():
        return
    print("Setting up the backend (first run only)...")
    venv.create(VENV, with_pip=True)
    subprocess.run([venv_python(), "-m", "pip", "install", "-e", ".[dev]"], cwd=BACKEND, check=True)


def install_frontend() -> None:
    if (FRONTEND / "node_modules").exists():
        return
    print("Setting up the frontend (first run only)...")
    subprocess.run([shutil.which("npm") or "npm", "install"], cwd=FRONTEND, check=True)


def is_free(port: int) -> bool:
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


def free_backend_port() -> int:
    if not is_free(FRONTEND_PORT):
        sys.exit(f"The frontend needs port {FRONTEND_PORT}, but something else is using it.")
    return next(port for port in range(8000, 8100) if is_free(port))


def start_servers(backend_port: int) -> list[subprocess.Popen[bytes]]:
    backend = subprocess.Popen(
        [venv_python(), "-m", "uvicorn", "app.main:app", "--port", str(backend_port)], cwd=BACKEND
    )
    # Vite is run through node directly rather than `npm run dev`: on Windows npm adds a cmd.exe
    # wrapper, and terminating the wrapper would leave Vite running.
    frontend = subprocess.Popen(
        ["node", FRONTEND / "node_modules/vite/bin/vite.js", "--strictPort"],
        cwd=FRONTEND,
        env={**os.environ, "BACKEND_PORT": str(backend_port)},
    )
    return [backend, frontend]


def main() -> None:
    if shutil.which("node") is None:
        sys.exit("Node.js is required: https://nodejs.org")
    install_backend()
    install_frontend()

    backend_port = free_backend_port()
    print(f"\nBackend on port {backend_port}. Open http://localhost:{FRONTEND_PORT} to play.\n")
    servers = start_servers(backend_port)
    try:
        while all(server.poll() is None for server in servers):
            time.sleep(0.5)
        print("A server stopped; shutting down the other one.")
    except KeyboardInterrupt:
        pass
    finally:
        for server in servers:
            server.terminate()
        for server in servers:
            server.wait()


if __name__ == "__main__":
    main()
