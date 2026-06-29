from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("BELEDIYE_API_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
        self.token: Optional[str] = None
        self.current_user: Optional[Dict[str, Any]] = None
        self._backend_process: Optional[subprocess.Popen] = None
        self._project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self._venv_python = self._resolve_venv_python()
        parsed = urllib.parse.urlparse(self.base_url)
        self._backend_host = parsed.hostname or "127.0.0.1"
        self._backend_port = parsed.port or 8000

    def _resolve_venv_python(self) -> str:
        env_override = os.getenv("BELEDIYE_BACKEND_PYTHON")
        if env_override:
            return env_override

        if os.name == "nt":
            return os.path.join(self._project_root, ".venv", "Scripts", "python.exe")
        return os.path.join(self._project_root, ".venv", "bin", "python")

    def _health_url(self) -> str:
        return f"{self.base_url}/health"

    def _is_backend_reachable(self) -> bool:
        request = urllib.request.Request(self._health_url(), headers={"Accept": "application/json"}, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=2):
                return True
        except Exception:
            return False

    def _start_backend_if_needed(self) -> bool:
        if self._is_backend_reachable():
            return True

        if self._backend_process is not None and self._backend_process.poll() is None:
            return self._wait_for_backend()

        if not os.path.exists(self._venv_python):
            return False

        command = [
            self._venv_python,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            self._backend_host,
            "--port",
            str(self._backend_port),
        ]

        creation_flags = 0
        if os.name == "nt":
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            self._backend_process = subprocess.Popen(
                command,
                cwd=self._project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            )
        except Exception:
            return False

        return self._wait_for_backend()

    def _wait_for_backend(self) -> bool:
        for _ in range(20):
            if self._is_backend_reachable():
                return True
            time.sleep(0.25)
        return False

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        form: bool = False,
        retried: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        data = None
        headers = self._headers()

        if payload is not None:
            if form:
                data = urllib.parse.urlencode(payload).encode("utf-8")
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                data = json.dumps(payload).encode("utf-8")
                headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return None
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            detail = exc.reason
            try:
                body = exc.read().decode("utf-8")
                parsed = json.loads(body)
                detail = parsed.get("detail", detail)
            except Exception:
                pass
            raise ApiError(str(detail)) from exc
        except urllib.error.URLError as exc:
            if not retried and self._start_backend_if_needed():
                return self._request(method, path, payload=payload, form=form, retried=True)
            raise ApiError("Backend servisine baglanilamadi. Sunucunun calistigindan emin olun.") from exc

    def login(self, username: str, password: str) -> Dict[str, Any]:
        data = self._request(
            "POST",
            "/auth/login",
            payload={"username": username, "password": password},
            form=True,
        )
        self.token = data["access_token"]
        self.current_user = self.get("/auth/me")
        return data

    def logout(self) -> None:
        self.token = None
        self.current_user = None

    def get(self, path: str) -> Any:
        return self._request("GET", path)

    def post(self, path: str, payload: Optional[Dict[str, Any]] = None, form: bool = False) -> Any:
        return self._request("POST", path, payload=payload, form=form)

    def put(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("PUT", path, payload=payload)

    def patch(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("PATCH", path, payload=payload)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)


api_client = ApiClient()
