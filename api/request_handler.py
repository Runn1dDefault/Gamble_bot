from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests

from config import API_URL, API_ERROR_STATUSES
from exceptions import APIError


class RequestHandler:
    def __init__(self):
        self.session = requests.Session()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request('GET', path=path, params=params)

    def post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request('POST', path=path, json=params)

    def request(self, method: str, path: str = None, **kwargs) -> Any:
        if path.startswith('/'):
            path = path[1:]
        request = requests.Request(method, urljoin(API_URL, path), **kwargs)
        self._sign_request(request)
        response = self.session.send(request.prepare())
        return self.process_response(response)

    def put(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request('PUT', path=path, json=params)

    def patch(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request('PATCH', path=path, json=params)

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request('DELETE', path=path, json=params)

    def _sign_request(self, request: requests.Request):
        pass

    @staticmethod
    def process_response(response: requests.Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if isinstance(data, dict) and data.get("detail") and response.status_code in API_ERROR_STATUSES:
                raise APIError(data['detail'])
            return data
