import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


class APIError(Exception):
    """Raised when the DormMon API returns an error response."""


class DormmonAPI:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url or os.environ.get(
            "DORMMON_API_BASE_URL", "http://localhost:5000"
        )
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "application/json")
        try:
            response = requests.request(
                method, url, timeout=self.timeout, headers=headers, **kwargs
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            message = self._extract_error_message(exc.response)
            raise APIError(message) from exc
        except requests.RequestException as exc:
            raise APIError(str(exc)) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("Invalid JSON payload returned by server") from exc

    @staticmethod
    def _extract_error_message(response: Optional[requests.Response]) -> str:
        if response is None:
            return "Unknown server error"
        try:
            payload = response.json()
            return (
                payload.get("error")
                or payload.get("message")
                or response.text
                or "Unknown server error"
            )
        except ValueError:
            return response.text or "Unknown server error"

    def get_users(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/users").get("users", [])

    def get_categories(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/categories").get("categories", [])

    def get_events(self, **params) -> List[Dict[str, Any]]:
        return self._request("GET", "/events", params=params).get("events", [])

    def create_event(
        self,
        payload: Dict[str, Any],
        photo_bytes: bytes,
        filename: str = "event.jpg",
    ) -> Dict[str, Any]:

        form_data: List[Tuple[str, Any]] = []
        for key, value in payload.items():
            if value is None:
                continue
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                for entry in value:
                    form_data.append((key, entry))
            else:
                form_data.append((key, value))

        files = {"photo": (filename, photo_bytes, "image/jpeg")}
        return self._request("POST", "/events", data=form_data, files=files)

    def perform_face_recognition(self, photo_bytes: bytes) -> Dict[str, Any]:
        files = {"photo": ("snapshot.jpg", photo_bytes, "image/jpeg")}
        return self._request("POST", "/face/recognize", files=files)

    def get_schedule(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/schedule").get("schedule", [])

    def get_task_status(self) -> Dict[str, Any]:
        return self._request("GET", "/status_view")

