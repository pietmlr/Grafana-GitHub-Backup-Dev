from config import Config
import requests
import json

class Grafana:
    def __init__(self, config: Config):
        self.config = config
        self.API_KEY = self.config.getGrafanaKey()
        self.URL = self.config.getGrafanaURL()
        self.GRAFANA_USER = self.config.getGrafanaUser()
        self.GRAFANA_PASSWORD = self.config.getGrafanaPassword()
        
    def getDashboard(self, path: str): 
        """ Gets a single dashboard JSON model

        Args:
            path (str): path (e.g.: grafana_folder/dashboard)

        Raises:
            Exception: If the download failed, displaying error message

        Returns:
            dashboard (dict): dashboard
        """
        
        # For the standard (home) dashboard
        grafana_response = requests.get(
            self.URL, 
            auth = (self.GRAFANA_USER, self.GRAFANA_PASSWORD)
        )
        http_status_code = grafana_response.status_code
        #printHTTPStatus(http_status_code, 'Grafana')
        if http_status_code == 200:
            grafana_json = grafana_response.json()
            return json.dumps(grafana_json, indent=4)
        else: 
            error_message = grafana_response.json()['message']
            raise Exception(f'Error downloading Grafana JSON: {error_message}')
        

    def getDashboards(self): pass