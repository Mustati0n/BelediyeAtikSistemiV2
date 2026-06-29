from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "BELEDIYE_API_URL",
            "http://77.83.37.48:8000/api/v1",
        ).rstrip("/")
        self.token: Optional[str] = None
        self.current_user: Optional[Dict[str, Any]] = None

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
            raise ApiError(
                f"Backend servisine baglanilamadi: {self.base_url}. "
                "Sunucunun calistigindan ve 8000 portunun acik oldugundan emin olun."
            ) from exc

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
