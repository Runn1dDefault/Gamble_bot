import json
from datetime import datetime
from typing import Dict, Any, List
from urllib.parse import urljoin
from logging import getLogger

from requests import Request, post

from config import API_URL, API_LOG_INCLUDE
from service.utils import configure_logger
from api.request_handler import RequestHandler


class APIClient(RequestHandler):
    def __init__(self, token: str = None, username: str = None, password: str = None):
        if username is None and password is None:
            assert token is not None
        super().__init__()
        self.username = username
        self._password = password
        self._token = token
        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)

    @property
    def token(self):
        return self._token

    def auth(self) -> Dict[str, Any]:
        self.logger.info('Trying login on server...')
        return self.process_response(post(urljoin(API_URL, 'api/auth/'),
                                          data=json.dumps({'username': self.username,
                                                           'password': self._password}),
                                          headers={'Content-Type': 'application/json'}))

    def _sign_request(self, request: Request):
        if self._token is None:
            self._token = self.auth().get('token', None)
        request.headers['Content-Type'] = 'application/json'
        if self._token is not None:
            request.headers['Authorization'] = 'Token ' + self._token

    def user_profile_info(self) -> Dict[str, Any]:
        self.logger.info('Getting profile info...')
        result = self.get('api/profile/')
        if isinstance(result, list):
            return result[0]
        return result

    def get_registrations(self, pk: str = None):
        self.logger.info('Getting registrations details...')
        path = f'api/registration/{pk}' if pk is not None else 'api/registration/'
        return self.get(path)

    def get_sites_list(self) -> List[Dict[str, Any]]:
        self.logger.info('Getting sites...')
        return self.get('api/betsites', params={'is_game': '1'})

    def get_betsites(self):
        return self.get_sites_list()[0].get('betsites', [])

    def save_logs(self,  site_name: str, message: str):
        if not API_LOG_INCLUDE:
            return

        payload = {
            'logs_output': f'{datetime.now()}, INFO: {message}',
            'betsites': site_name,
            'time': str(datetime.now())
        }
        return self.post('/api/logs/', params=payload)
