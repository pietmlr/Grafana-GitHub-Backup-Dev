from typing import Tuple

class Connector():
    
    def __init__(self, URL: str, headers: dict, auth: Tuple = None):
        self.URL = URL
        self.headers = headers
        self.auth = auth