import base64
from datetime import datetime
import hashlib
import json
import requests


### How to backup a dashboard ###
# 1. Find dashboard UID
# 2. 

# Grafana things
GRAFANA_DASHBOARD_UID_POV = '0A0OtHqnk'
GRAFANA_DASHBOARD_UID = 'SlSDRF37k'
GRAFANA_API_TOKEN = 'eyJrIjoiV29ycTJvOG55VUo0V1pDVVhWOGh3UDRnRmI0UHppMjkiLCJuIjoicHJha3Rpa3VtMiIsImlkIjoxfQ=='
GRAFANA_URL = f'http://localhost:3000/api/dashboards/uid/{GRAFANA_DASHBOARD_UID}'

# GitHub things
GITHUB_API_TOKEN = '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'
GITHUB_REPOSITORY_NAME = 'grafana-github-backup'
GITHUB_REPOSITORY_OWNER = 'pietmlr'

# Miscellaneous things
FILENAMING_SCHEME = '.json'

HTTP_CODE_APPROX_MEANING = {
    '1': 'Information',
    '2': 'Success',
    '3': 'Redirection',
    '4': 'Client Error',
    '5': 'Server Error'
}


# select dashboard to backup, alternatively backup up all dashboards

def getGrafanaJSON():
    
    # For the standard (home) dashboard
    grafana_response = requests.get(
        GRAFANA_URL, 
        auth = ('admin', 'admin')
    )
    http_status_code = grafana_response.status_code
    printHTTPStatus(http_status_code, 'Grafana')
    if http_status_code == 200:
        grafana_json = grafana_response.json()
        return json.dumps(grafana_json, indent=4)
    else: 
        error_message = grafana_response.json()['message']
        raise Exception(f'Error downloading Grafana JSON: {error_message}')

# Printing the HTTP status message from a integer HTTP status code
def printHTTPStatus(hsc: int, requestLocation: str):
    if hsc:
        approx_msg = HTTP_CODE_APPROX_MEANING[str(hsc)[0]]
        print(f'HTTP Request Status for {requestLocation}: {approx_msg}/{hsc}')
    else:
        print('Something went wrong during the request, not HTTP status code provided')

def base64encode(string: str):
    string_bytes = string.encode('ascii')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('ascii')
    return base64_string

# A faster way to compare larger string using MD5 hashes
def modified(str1: str, str2: str):
    print(hashlib.md5(str1.encode()).hexdigest())
    print(hashlib.md5(str2.encode()).hexdigest())
    if hashlib.md5(str1.encode()).hexdigest() == hashlib.md5(str2.encode()).hexdigest():
        print('MD5 Hashes are the same')
        return False # Not Modified
    else:
        print('MD5 Hashes are not the same') 
        return True # modified

# cant download recursively --> nested limit of 1 folder, so: folder_xy/file.abc
def downloadRepositoryFileContents():
    
    # GraphQL query
    current_content = """
        query RepoFiles($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                object(expression: "HEAD:") {
                    ... on Tree {
                        entries {
                            name
                            object {
                                ... on Blob {
                                    text
                                }
                                
                                # one level down
                                ... on Tree {
                                    entries {
                                        name
                                        object {
                                            ... on Blob {
                                                text
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """
    
    current_content_variables = {
        'owner': GITHUB_REPOSITORY_OWNER,
        'name': GITHUB_REPOSITORY_NAME
    }
    
    current_content_query = requests.post(
        'https://api.github.com/graphql',
        json = {
            'query': current_content,
            'variables': current_content_variables
        },
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {GITHUB_API_TOKEN}'
        }
    )
    
    printHTTPStatus(current_content_query.status_code, 'GitHub')
    
    return json.dumps(current_content_query.json(), indent=4)
    
def getLatestCommitOiD():
    
    oid_query = """
        query OiDQuery {
            repository(name: "grafana-github-backup", owner: "pietmlr") {
                ref(qualifiedName: "main") {
                    target {
                        oid
                    }
                }
            }
        }
    """
    
    # query last commit OiD (SHA-1) before committing as it is required
    oid_query = requests.post(
       'https://api.github.com/graphql',
        json = {
            'query': oid_query
        },
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {GITHUB_API_TOKEN}'
        }
    )
    
    printHTTPStatus(oid_query.status_code, 'GitHub')
    most_recent_commit_oid = json.dumps(oid_query.json(), indent=4)
    
    return most_recent_commit_oid

# Create GitHub Commit to GitHub GraphQL API
def createGitHubCommit(commit_headline_message: str, fileChanged: str, foldername: str, contentToCommit: str, fileIndex: int = 0):

    # Set dashboard name to filename
    filename = json.loads(contentToCommit)['dashboard']['title'] + fileChanged
    path = foldername + '/' + filename
    print(filename)

    print(downloadRepositoryFileContents())
    # First of all, check if the file needs to be overwritten
    # [:-1] for removing the last character '\n' added by GitHub
    
    current_file_content = json.loads(downloadRepositoryFileContents())['data']['repository']['object']['entries'][fileIndex]['object']['text'][:-1]
    #print(current_file_content)
    
    print(f'Checking "{filename}" for commit')
    
    # Check if a commit is necessary
    if not modified(contentToCommit, current_file_content):
        print('There is no commit necessary (File is not modified)')
        return 
    else:
        print('The dashboard files need to be upgraded (File is modified)')
        
    print(current_file_content)
    print(contentToCommit)
        
    most_recent_commit_oid = getLatestCommitOiD()
    most_recent_commit_oid = json.loads(most_recent_commit_oid)['data']['repository']['ref']['target']['oid']
    # most_recent_commit_oid[:7] GitHub mostly shows the first 7 characters of the sha-1 commit oid hash
    print(f'Last Commit-OiD: {most_recent_commit_oid}, or in short: {most_recent_commit_oid[:7]}')
    
    commit_query = """
        mutation CommitOnBranch($input:CreateCommitOnBranchInput!) {
            createCommitOnBranch(input: $input) {
                commit {
                    url
                    oid
                }
            }
        }
    """ 

    commit_variables = {
        'input': {
            'branch': {
                'repositoryNameWithOwner': (GITHUB_REPOSITORY_OWNER + '/' + GITHUB_REPOSITORY_NAME),
                'branchName': 'main'
            },
            'message': {
                'headline': commit_headline_message
            },
            'fileChanges': {
                'additions': [
                    {
                        'path': path,
                        'contents': base64encode(contentToCommit + '\n')
                    }
                ]
            },
            'expectedHeadOid': most_recent_commit_oid
        }
    }
    
    # The actual commit
    commit_response = requests.post(
        'https://api.github.com/graphql',
        json = {
            'query': commit_query,
            'variables': commit_variables
        },
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {GITHUB_API_TOKEN}'
        }
    )
    
    printHTTPStatus(commit_response.status_code, 'GitHub')
    commit_response = json.dumps(commit_response.json(), indent=4)
    print(commit_response)
    current_commit_url = json.loads(commit_response)['data']['createCommitOnBranch']['commit']['url']
    current_commit_oid = json.loads(commit_response)['data']['createCommitOnBranch']['commit']['oid']
    
    print(f'Commited Grafana Dashboard "{path}" to GitHub [Commit-OiD: (short) {current_commit_oid[:7]}, (long) {current_commit_oid}]\nAccessible through the following URL: {current_commit_url}')
    
createGitHubCommit(commit_headline_message='Folder creation test', fileChanged=FILENAMING_SCHEME, foldername='folder 1', contentToCommit=getGrafanaJSON())

### Download and install Grafana JSON from GitHub into Grafana instance ###
def reinstallGrafanaJSON(overwrite: bool = False, create_copy: bool = False, fileIndex: int = 0, folderId: int = 1):
    
    # Download Grafana JSON from GitHub
    grafana_json = json.loads(json.loads(downloadRepositoryFileContents())['data']['repository']['object']['entries'][fileIndex]['object']['text'][:-1])
    dashboard_name = grafana_json['dashboard']['title']
    print(f'Old dashboard name: "{dashboard_name}"')
    #grafana_json['dashboard'].update(title=f'{dashboard_name}-BackUp-{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}')
    print('Downloaded Backup file')
    #grafana_json = grafana_json['dashboard']
    
    # IMPORTANT: If overwrite is set to True, existing dashboards with the same name in the 
    # same folder get overwritten OR same uid
    # Overwriting works but dashboard content gets deleted
    if overwrite:
        grafana_json['dashboard'].update(overwrite=True)
        dashboard_name = grafana_json['dashboard']['title']
        create_copy = False
    elif create_copy:
        dashboard_name = grafana_json['dashboard']['title'] + '-Copy-' + datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        overwrite = False
        print(f'Creating a copy of old dashboard with selected changes')
        
    # Swap out existing uid to None (NULL) to prevent installation errors due to not 
    # finding the dashboard (uid), uid=NULL will generate a new uid
    grafana_json['dashboard'].update(uid=None)
    grafana_json['dashboard'].update(id=None)
    # Include folderUid?
    # Include/Change this meta data for manipulating the installation path of the dashboard
    # "folderId": 36,
    grafana_json['meta'].update(folderId=folderId)
    # "folderUid": "",
    grafana_json['dashboard'].update(folderUid='Twqp1N3nz')
    # "folderTitle": "General",
    grafana_json['meta'].update(folderTitle='folder 1')
    # "folderUrl": ""
    # grafana_json['meta'].update(folderUrl='f/Twqp1N3nz/folder-2')
        
    example_request = {
        'dashboard': {
            'id': None,
            'uid': None,
            'title': dashboard_name,
            'tags': ['testing'],
            'timezone': 'browser',
            'schemaVersion': 16,
            'version': 0,
            'refresh': '25s'
        },
        'folderId': folderId,
        'message': getLatestCommitOiD(),
        'overwrite': overwrite
    }

    print(f'New dashboard name: "{dashboard_name}"')
    
    dashboard_commit_id = json.loads(getLatestCommitOiD())['data']['repository']['ref']['target']['oid']
    print(f'Install from GitHub commit {dashboard_commit_id[:7]} ({dashboard_commit_id})')
    
    # save it locally for testing purposes
    with open('grafana.json', 'w', encoding='utf-8') as test_file:
        test_file.write(json.dumps(grafana_json, indent=4))
    
    print(json.dumps(grafana_json, indent=4))
    
    reinstall_dashboard_req = requests.post(
        'http://localhost:3000/api/dashboards/db',
        auth=('admin', 'admin'),
        json = grafana_json,
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GRAFANA_API_TOKEN}'
        }
    )
    # get folder name from folderId
    print(f'Grafana response: {json.dumps(reinstall_dashboard_req.json(), indent=4)}')
    if reinstall_dashboard_req.status_code == 200:
        print(f'Installed Grafana Dashboard "{dashboard_name}" in Folder (folderId: {folderId}) from GitHub {dashboard_commit_id[:7]} ({dashboard_commit_id})')
    else:
        print(f'Grafana Dashboard could not be installed')
        printHTTPStatus(reinstall_dashboard_req.status_code ,'Grafana')
        error_message = reinstall_dashboard_req.json()['message']
        print(f'Error message: {error_message}')

#reinstallGrafanaJSON(folderId=0)

# Get all folders, except the "General" folder which apparently is not part of the Grafana HTTP Folder API
# def getAllFolders():
#     response = requests.get(
#         'http://localhost:3000/api/folders',
#         headers = {
#             'Accept': 'application/json',
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {GRAFANA_API_TOKEN}'
#         }
#     )
#     print(f'There are currently {len(response.json())} folders in Grafana')
    
#     if response.status_code == 200:
#         folder_objects = []
#         for folder_json in response.json():
#             folder_obj = Folder(**folder_json)
#             folder_objects.append(folder_obj)
        
#         return folder_objects
#     else: 
#         raise Exception(f'Request failed code {response.status_code}')
    
def getDashboardsInFolder(folderId: int):
    pass

# Enough data to recreate folder structure on github
# print([folder.id for folder in getAllFolders()])
# print([folder.uid for folder in getAllFolders()])
# print([folder.title for folder in getAllFolders()])
# print([folder.toJSON() for folder in getAllFolders()])
#print([folder.id for folder in getAllFolders()]) # add folderId=0 and title="General"

### Create new folders in GitHub repository ###


### CoreCLI class (main) ###
class CoreCLI():
    all_folders = []
    
    def backup(everything: bool = False, path: str = None): pass
    def publish(everything: bool = False, path: str = None, overwrite: bool =  False, create_copy: bool = False): pass