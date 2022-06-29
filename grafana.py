from colorama import Fore, Style
from config import Config
from dashboard import Dashboard
from datetime import datetime
import requests
import json

class Grafana:
    GRAFANA_API_ENDPOINTS = {
        'SEARCH': '/api/search?',
        'DASHBOARD_UID': '/api/dashboards/uid/',
        'FOLDERS': '/api/folders',
        'CREATE_DASHBOARD': '/api/dashboards/db'
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

    def installDashboard(self, dashboard_model: dict, path: str, commit_oid: str, overwrite: bool = False, create_copy: bool = False, everything: bool = False):
    
        # Get title and meta data for installation
        dashboard_name = dashboard_model['dashboard']['title']
        #print(json.dumps(dashboard_model, indent=4))
        path_split = path.split('/')
        root_folder = path_split[0]
        filename = path_split[1]
        
        root_folder_url = root_folder.replace(' ', '%20')
        #print(root_folder)
        # Get folderId and folderUid from folderTitle from Grafana Dashbord/Folder Search API
        if root_folder != 'General':
            query_string = self.URL + \
                           self.GRAFANA_API_ENDPOINTS['SEARCH'] + \
                           f'?query=' + root_folder_url + \
                           '&type=dash-folder'
                           
            folder_meta_data = requests.get(
                query_string,
                headers=self.GRAFANA_HEADERS,
                auth=self.GRAFANA_AUTH
            )
            
            #print(json.dumps(folder_meta_data.json(), indent=4))
            
            for folder in folder_meta_data.json():
                if folder['title'] == root_folder:
                    folderId = folder['id']
                    folderUid = folder['uid']
                    # Meta data changes for installing the dashboard into the desired location
                    # TODO: Which of these is really necessary??
                    dashboard_model.update(folderId=folderId)
                    dashboard_model.update(folderUid=folderUid)
        else:
            folderId = 0

        dashboard_model['meta'].update(folderTitle=root_folder)
        dashboard_model['dashboard'].update(message=commit_oid)
        
        ## IF dashboard deleted OR shall be overwritten
        # Swap out existing uid to None (NULL) to prevent installation error due to not 
        # finding the dashboard (uid) by Grafana API, uid=NULL will generated a new uid
        dashboard_model['dashboard'].update(uid=None)
        dashboard_model['dashboard'].update(id=None)
        
        # Check parameters and act accordingly
        if overwrite:
            dashboard_model['dashboard'].update(overwrite=True)
            create_copy = False
            print('Overwriting selected dashboards in Grafana')
        elif create_copy:
            # Update dashboard name
            dashboard_name_suffix = '-Copy-' + datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            new_dashboard_name = dashboard_name + dashboard_name_suffix
            dashboard_model['dashboard'].update(title=new_dashboard_name)
            overwrite = False
            
            # Swap out existing uid to None (NULL) to prevent installation error due to not 
            # finding the dashboard (uid) by Grafana API, uid=NULL will generated a new uid
            dashboard_model['dashboard'].update(uid=None)
            dashboard_model['dashboard'].update(id=None)
            
            print('Creating a copy of the old dashboard with selected commit changes')
        
        # Update version in meta data to prevent version mismatch errors
        # Increment version by 0.1 at every installation
        new_version = dashboard_model['dashboard']['version'] + 1
        dashboard_model['meta'].update(version=new_version)
        dashboard_model['dashboard'].update(version=new_version)

        # example_request = {
        #     'dashboard': {
        #         'id': None,
        #         'uid': None,
        #         'title': dashboard_name,
        #         'tags': ['testing'],
        #         'timezone': 'browser',
        #         'schemaVersion': 16,
        #         'version': 0,
        #         'refresh': '25s'
        #     },
        #     'folderId': folderId,
        #     'message': commit_oid,
        #     'overwrite': overwrite
        # }
        
        print(Style.DIM + f'Dashboard name: "{dashboard_name}"' + Style.RESET_ALL)
        
        print(f'Model to upload: {json.dumps(dashboard_model, indent=4)}')
        
        query_string = self.URL + self.GRAFANA_API_ENDPOINTS['CREATE_DASHBOARD']
        
        reinstall_dashboard_response = requests.post(
            query_string,
            json=dashboard_model,
            headers=self.GRAFANA_HEADERS,
            auth=self.GRAFANA_AUTH
        )
        
        # Get folder name from folderIds
        if reinstall_dashboard_response.status_code == 200:
            print(json.dumps(reinstall_dashboard_response.json(), indent=4))
            print(Fore.GREEN + Style.BRIGHT + 
                  f'The installation of "{dashboard_name}" at "{root_folder}" was successfull' +
                  Fore.RESET + Style.RESET_ALL)
        else:
            print(Fore.RED + Style.BRIGHT + 
                  json.dumps(reinstall_dashboard_response.json()['message'], indent=4) + 
                  f'\nHTTP status code: {str(reinstall_dashboard_response.status_code)}' +
                  Fore.RESET + Style.RESET_ALL)