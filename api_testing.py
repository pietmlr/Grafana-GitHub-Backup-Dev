import requests
import json


GRAFANA_DASHBOARD_UID = 'SlSDRF37k'
GRAFANA_API_TOKEN = 'eyJrIjoiV29ycTJvOG55VUo0V1pDVVhWOGh3UDRnRmI0UHppMjkiLCJuIjoicHJha3Rpa3VtMiIsImlkIjoxfQ=='
GRAFANA_URL = f'http://localhost:3000/'
GRAFANA_API_SEARCH_ENDPOINT = '/api/search?'


def getDashboardUIDs(folderId: int):
    
    GRAFANA_API_TOKEN = 'eyJrIjoiV29ycTJvOG55VUo0V1pDVVhWOGh3UDRnRmI0UHppMjkiLCJuIjoicHJha3Rpa3VtMiIsImlkIjoxfQ=='
    GRAFANA_URL = f'http://localhost:3000/'
    GRAFANA_API_SEARCH_ENDPOINT = '/api/search?'
    
    if GRAFANA_URL[-1] == '/':
        GRAFANA_URL = GRAFANA_URL[:-1]
    
    print(f'API call to: {GRAFANA_URL + GRAFANA_API_SEARCH_ENDPOINT}')
    
    # For the standard (home) dashboard
    grafana_response = requests.get(
        GRAFANA_URL + GRAFANA_API_SEARCH_ENDPOINT + f'folderIds={folderId}', 
        auth = ('admin', 'admin'),
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GRAFANA_API_TOKEN}'
        }
    )
    
    # folderUrl example: 
    # --> ("folderUrl": "/dashboards/f/TaAt1N37k/folder-1") 
    # --> ("folderUrl": "/dashboards/f/:dashboard-uid/:folder-name")
    folder_urls = []
    for dashboard in grafana_response.json():
        folder_url = dashboard['folderUrl']
        folder_urls.append(folder_url)

    return folder_urls
    
for folder_url in getDashboardUIDs(35):
    parsed_folder_url = str(folder_url).split('/')
    dashboard_uid = parsed_folder_url['3']
    root_folder = parsed_folder_url['4']

    # http_status_code = grafana_response.status_code
    # printHTTPStatus(http_status_code, 'Grafana')
    # if http_status_code == 200:
    #     grafana_json = grafana_response.json()
    #     return json.dumps(grafana_json, indent=4)
    # else: 
    #     error_message = grafana_response.json()['message']
    #     raise Exception(f'Error downloading Grafana JSON: {error_message}')