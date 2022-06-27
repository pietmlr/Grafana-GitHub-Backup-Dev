import requests
import json
from dashboard import Dashboard


GRAFANA_API_TOKEN = 'eyJrIjoiV29ycTJvOG55VUo0V1pDVVhWOGh3UDRnRmI0UHppMjkiLCJuIjoicHJha3Rpa3VtMiIsImlkIjoxfQ=='
GRAFANA_URL = f'http://localhost:3000'
GRAFANA_API_SEARCH_ENDPOINT = '/api/search?'
GRAFANA_API_DASHBOARD_UID_ENDPOINT = '/api/dashboards/uid/'
GRAFANA_API_FOLDER_ENDPOINT = '/api/folders'


def getAllFolders() -> list:
    query_string = GRAFANA_URL + GRAFANA_API_FOLDER_ENDPOINT
    
    response = requests.get(
        query_string,
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GRAFANA_API_TOKEN}'
        },
        auth = ('admin', 'admin')
    )
    print(query_string)
    #print(f'There are currently {len(response.json())} folders in Grafana')
    
    if response.status_code == 200:
        # Only returning the folder ids, appending 0 to the list to include the general folder HAS TO BE DONE
        return [folder_json['id'] for folder_json in response.json()]
    else: 
        raise Exception(f'Request to Grafana failed, code {response.status_code}')

def getDashboardUIDs(folderId: int):
    query_string = GRAFANA_URL + GRAFANA_API_SEARCH_ENDPOINT + f'folderIds={folderId}'
    print(f'API call to: {query_string}')
    
    # Get dashboards inside a certain folder using folderId
    grafana_response = requests.get(
        query_string, 
        auth = ('admin', 'admin'),
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GRAFANA_API_TOKEN}'
        }
    )
    
    #print(json.dumps(grafana_response.json(), indent=4))
    
    # folderUrl example: 
    # --> ("folderUrl": "/dashboards/f/TaAt1N37k/folder-1") 
    # --> ("folderUrl": "/dashboards/f/:dashboard-uid/:folder-name")
    dashboard = Dashboard(grafana_response.json())
    return dashboard.getDashboardUid()

def getDashboard(dashboardUid: str):
    query_string = GRAFANA_URL +  GRAFANA_API_DASHBOARD_UID_ENDPOINT + dashboardUid
    
    grafana_response = requests.get(
        query_string, 
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GRAFANA_API_TOKEN}'
        },
        auth = ('admin', 'admin')
    )
    http_status_code = grafana_response.status_code
    # printHTTPStatus(http_status_code, 'Grafana')
    if http_status_code == 200:
        grafana_json = grafana_response.json()
        return json.dumps(grafana_json, indent=4)
    else: 
        error_message = grafana_response.json()['message']
        raise Exception(f'Error downloading Grafana JSON: {error_message}')


folder_ids = getAllFolders()
for folder_id in folder_ids:
    # Get the dashboard uids from dashboards in the folder with the assigned folder_id
    dashboard_uids = getDashboardUIDs(folder_id)
    for dashboard_uid in dashboard_uids:
        dashboard = getDashboard(dashboardUid=dashboard_uid)
        print(dashboard)