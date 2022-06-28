from config import Config
from dashboard import Dashboard
import requests
import json

class Grafana:
    GRAFANA_API_ENDPOINTS = {
        'SEARCH': '/api/search?',
        'DASHBOARD_UID': '/api/dashboards/uid/',
        'FOLDERS': '/api/folders'
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.API_KEY = self.config.getGrafanaKey()
        self.URL = self.config.getGrafanaURL()
        self.GRAFANA_USER = self.config.getGrafanaUser()
        self.GRAFANA_PASSWORD = self.config.getGrafanaPassword()
        self.GRAFANA_AUTH = (self.GRAFANA_USER, self.GRAFANA_PASSWORD)
        self.GRAFANA_HEADERS = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.API_KEY}'
        }
     
    def getDashboardUidFromPath(self, path: str) -> str: 
        """ Gets a single dashboard JSON model from Grafana. Requests the Grafana API in the following steps:
            - Get all folders and match the folder names against given root folder name for the dashboard

        Args:
            path (str): path (e.g.: grafana_folder/dashboard; folder 23/dashboard 53)

        Raises:
            Exception: If the download failed, displaying error message

        Returns:
            dashboard (dict): dashboard
        """
        
        root_folder = path.split('/')[0]
        dashboard_title = path.split('/')[1]
        
        print(f'Searching for "{dashboard_title}" in "{root_folder}" on Grafana')
        
        query_string = self.URL + \
                       self.GRAFANA_API_ENDPOINTS['SEARCH'] + \
                       f'query={dashboard_title}'
        
        grafana_response = requests.get(
            query_string, 
            headers = self.GRAFANA_HEADERS,
            auth = self.GRAFANA_AUTH
        )
        
        # After retrieval of the response, it has to be validated that the response
        # really covers a dashboard object, not a folder with the same name
        http_status_code = grafana_response.status_code
        if http_status_code == 200:
            grafana_json = grafana_response.json()
            # If the request did not find any matches, Grafana API returns an empty lists
            if grafana_json is not []:
                # Check for the right dashboard by comparing the root folder name (the same 
                # name for a dashboard in a folder is not allowed)
                for found_dashboard in grafana_json:
                    if 'folderTitle' in found_dashboard:
                        if found_dashboard['folderTitle'] == root_folder:
                            return found_dashboard['uid']
                        else: print(f'Could not find "{dashboard_title}" in "{root_folder}"')
                    else:
                        # Case: Dashboard is in the General folder
                        return found_dashboard['uid']
            else: print(f'Could not find "{dashboard_title}" in "{root_folder}"')
        else: 
            error_message = grafana_response.json()['message']
            raise Exception(f'Error Searching Grafana API for {dashboard_title}: {error_message}; Query String: {query_string}')

    def getDashboard(self, path: str, dashboard_uid: str) -> dict:
        """Downloads the Dashboard JSON model from Grafana given the path to it

        Args:
            path (str): path to dashboard in Grafana (e.g.: "folder 1/Dashboard 1")
                        Insert '-1' to use option --everything and use dashboard_uid function
                        argument to directly pass a dashboard_uid
            dashboard_uid (str): dashboard_uid from a Grafana dashboard
                        Insert '-1' to use option --path and use the path function argument
            
        Raises:
            Exception: _description_

        Returns:
            dict: Grafana dashboard JSON model
        """
        if path != '-1' and dashboard_uid == '-1':
            dashboard_uid = self.getDashboardUidFromPath(path)
        elif path == '-1' and dashboard_uid != '-1':
            pass
        
        query_string = self.URL +  self.GRAFANA_API_ENDPOINTS['DASHBOARD_UID'] + dashboard_uid
        
        grafana_response = requests.get(
            query_string, 
            headers = self.GRAFANA_HEADERS,
            auth = self.GRAFANA_AUTH
        )
        
        http_status_code = grafana_response.status_code
        if http_status_code == 200:
            grafana_json = grafana_response.json()
            return grafana_json
        else: 
            error_message = grafana_response.json()['message']
            raise Exception(f'Error downloading Grafana JSON Model for "{path}": {error_message}; Query String: {query_string}')

    def getAllFoldersIds(self) -> list:
        query_string = self.URL + self.GRAFANA_API_ENDPOINTS['FOLDERS']
        
        response = requests.get(
            query_string,
            headers = self.GRAFANA_HEADERS,
            auth = self.GRAFANA_AUTH
        )
        
        if response.status_code == 200:
            # Only returning the folder ids, appending 0 to the list to include the general folder
            folder_ids = [folder_json['id'] for folder_json in response.json()]
            folder_ids.append(0)
            return folder_ids
        else: 
            raise Exception(f'Request to Grafana failed, code {response.status_code}')

    def getDashboardUIDs(self, folderId: int) -> list:
        query_string = self.URL + self.GRAFANA_API_ENDPOINTS['SEARCH'] + f'folderIds={folderId}'
        
        # Get dashboards inside a certain folder using folderId
        grafana_response = requests.get(
            query_string, 
            headers = self.GRAFANA_HEADERS,
            auth = self.GRAFANA_AUTH
        )
        
        #print(json.dumps(grafana_response.json(), indent=4))
        dashboard = Dashboard(grafana_response.json())
        return [dashboard.getDashboardUid(), dashboard.getRootFolder()]

# from path/to/dashboard to dashboard uid
# possibilites:
# - 1 (for backuping everything)
#   - get all folder ids
#   - get every dashboard uid in every folder id
#   - get every dashboard by dashboard uid
# - 2 (back up a single dashboard by path)
#   - get path e.g.: folder 5/dashboard 3
#   - use grafana dashboard/folder search api
#   - get back the dashboard uid
#   - use dashboard uid to get a whole dashboard JSON model