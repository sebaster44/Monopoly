"""Start the backend and the frontend dev server together. Ctrl+C stops both.

Usage: python start.py   (set BACKEND_PORT to use another port than 8000)
"""

import os
import shutil
import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
BACKEND_PORT = os.environ.get("BACKEND_PORT", "8000")


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


def start_servers() -> list[subprocess.Popen[bytes]]:
    backend = subprocess.Popen(
        [venv_python(), "-m", "uvicorn", "app.main:app", "--port", BACKEND_PORT], cwd=BACKEND
    )
    # Vite is run through node directly rather than `npm run dev`: on Windows npm adds a cmd.exe
    # wrapper, and terminating the wrapper would leave Vite running.
    frontend = subprocess.Popen(
        ["node", FRONTEND / "node_modules/vite/bin/vite.js"],
        cwd=FRONTEND,
        env={**os.environ, "BACKEND_PORT": BACKEND_PORT},
    )
    return [backend, frontend]


def main() -> None:
    if shutil.which("node") is None:
        sys.exit("Node.js is required: https://nodejs.org")
    install_backend()
    install_frontend()

    servers = start_servers()
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
