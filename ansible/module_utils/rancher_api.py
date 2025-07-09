from urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests


API_ARG_SPEC = {
    "endpoint": {"type": "str", "required": "true"},
    "tls_verify": {"type": "bool", "default": "True"},
    "username": {"type": "str", "required": "true"},
    "password": {"type": "str", "required": "true", "no_log": "True"},
}


class RancherAPI:
    def __init__(self, endpoint, ssl_verify=True, token=None, session=None):
        self.session = session or requests.Session()
        self.session.headers.update(Authorization=token or "")
        if session is None:
            self.__set_retries()

        self._version = None
        self.endpoint = endpoint
        self.ssl_verify = ssl_verify

    @classmethod
    def login(cls, endpoint, username, password, session=None, ssl_verify=True):
        api = cls(endpoint, ssl_verify, session=session)
        api.__authenticate(username, password, verify=ssl_verify)
        return api

    def __set_retries(self, status_forcelist=(500, 502, 504), **kwargs):
        kwargs.update(
            backoff_factor=kwargs.get('backoff_factor', 10.0),
            total=kwargs.get('total', 1),
            status_forcelist=status_forcelist,
        )
        retry_strategy = Retry(**kwargs)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def __authenticate(self, username, password, **kwargs):
        path = "v3-public/localProviders/local"

        params = dict(
            action="login",
        )

        body = dict(
            description="Ansible Rancher",
            responseType="token",
            username=username,
            password=password,
        )

        result = self.__post(path, params=params, json=body, **kwargs)
        try:
            assert result.status_code == 201, "Failed to authenticate"
        except AssertionError:
            pass
        else:
            token = f"Bearer {result.json()['token']}"
            self.session.headers.update(Authorization=token)
            self._version = None
        return result.json

    def __get(self, path, **kwargs):
        url = self.__get_url(path)
        return self.session.get(url, **kwargs)

    def __post(self, path, **kwargs):
        url = self.__get_url(path)
        return self.session.post(url, **kwargs)

    def __get_url(self, path):
        return urljoin(self.endpoint, path)

    def get(self, path):
        return self.__get(path, verify=self.ssl_verify)

    def post(self, path, params=dict(), json=dict()):
        return self.__post(path, params=params, json=json, verify=self.ssl_verify)
