import base64
from config import Config
from colorama import Fore, Style
from datetime import datetime
import hashlib
import json
import requests


class GitHub:
    
    FORBIDDEN_CHARS = ['/', '&', '?', '.', ',', '%', '"', '+', '=']
    
    def __init__(self, config: Config):
        self.config = config
        self.API_KEY = self.config.getGitHubKey()
        self.URL = self.config.getGitHubURL()
        self.GITHUB_REPO_OWNER = self.config.getRepositoryOwner()
        self.GITHUB_REPO_NAME = self.config.getRepositoryName()
        self.GITHUB_HEADERS = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {self.API_KEY}'
        }
    
    def commitDashboard(self, dashboard: dict, path: str): 
        """
        commit_headline_message: str, foldername: str
        """
        
        # Seemingly open dashboards (not root folder) got the general folder as root folder
        #upload_new = False
        
        # Set dashboard name to filename
        #filename = dashboard['dashboard']['title']
        path_data = path.split('/')
        root_folder = path_data[0]
        filename = path_data[1]
        
        # Sanity check
        for forbidden_char in self.FORBIDDEN_CHARS:
            if forbidden_char in filename:
                print(Fore.RED + Style.BRIGHT +
                      'The process of commiting was stopped due to invalid characters in the dashboards name\n' +
                      '--> Please change your dashboard name according to the character policy display on start' +
                      Fore.RESET + Style.RESET_ALL)
                return
            
        filename = filename + '.json'
        path = path + '.json'

        #print(self.downloadRepositoryFileContents())
        # First of all, check if the file needs to be overwritten
        # [:-1] for removing the last character '\n' added by GitHub
        # Find the right file to commit to
        repository_files = json.loads(self.downloadRepositoryFileContents())['data']['repository']['object']['entries']
        for file_or_folder in repository_files:
            if file_or_folder['name'] == root_folder:
                for file in file_or_folder['object']['entries']:
                    if file['name'] == filename:
                        print(Style.DIM + f'The file "{path}" does exist in the current repository' + Style.RESET_ALL)
                        current_file_content = json.loads(file['object']['text'][:-1])
                        break
            #             upload_new = False
                    else: 
                        current_file_content = None
            #             #print(f'The file "{path}" does not exist in the current repository')
            #             upload_new = True
            # else: 
            #     upload_new = True
        
        # If the file already exists on GitHub
        #print('this:', json.dumps(current_file_content, indent=4))
        # Check if a commit is necessary
        print(Style.DIM + f'Checking found-dashboard "{filename}" for commit necessity' + Style.RESET_ALL)
        # Convert JSON dictionaries to string for hashing
        if self.modified(json.dumps(dashboard, indent=4), json.dumps(current_file_content, indent=4)) is False:
            print(Fore.GREEN + Style.BRIGHT + 'There is no commit necessary (File is not modified)' + Fore.RESET + Style.RESET_ALL)
            return 
        else:
            print(Style.DIM + 'The dashboard files need to be upgraded (File is modified or does not exist on GitHub yet)' + Style.RESET_ALL)
            
            # print(f'File "{path}" on GitHub:\n {current_file_content}')
            # print(f'File to upload to "{path}": {json.dumps(dashboard, indent=4)}')
                
        print(f'Upload path on GitHub is set to "{path}"')
            
        most_recent_commit_oid = self.getLatestCommitOiD()
        most_recent_commit_oid = json.loads(most_recent_commit_oid)['data']['repository']['ref']['target']['oid']
        # most_recent_commit_oid[:7] GitHub mostly shows the first 7 characters of the sha-1 commit oid hash
        print(Style.DIM + f'Last Commit-OiD: {most_recent_commit_oid}, or in short: {most_recent_commit_oid[:7]}' + Style.RESET_ALL)
        
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
        
        commit_headline = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        commit_variables = {
            'input': {
                'branch': {
                    'repositoryNameWithOwner': (self.GITHUB_REPO_OWNER + '/' + self.GITHUB_REPO_NAME),
                    'branchName': 'main'
                },
                'message': {
                    'headline': f'Backup of "{path}" {commit_headline}'
                },
                'fileChanges': {
                    'additions': [
                        {
                            'path': path,
                            'contents': self.base64encode(json.dumps(dashboard, indent=4) + '\n')
                        }
                    ]
                },
                'expectedHeadOid': most_recent_commit_oid
            }
        }
        
        # The actual commit
        commit_response = requests.post(
            self.URL,
            json = {
                'query': commit_query,
                'variables': commit_variables
            },
            headers = self.GITHUB_HEADERS
        )
        
        #printHTTPStatus(commit_response.status_code, 'GitHub')
        commit_response = json.dumps(commit_response.json(), indent=4)
        current_commit_url = json.loads(commit_response)['data']['createCommitOnBranch']['commit']['url']
        current_commit_oid = json.loads(commit_response)['data']['createCommitOnBranch']['commit']['oid']
        
        print(Fore.MAGENTA + Style.BRIGHT + f'Commited Grafana Dashboard "{path}" to GitHub [Commit-OiD: (short) {current_commit_oid[:7]}, (long) {current_commit_oid}]\n' + 
              Style.DIM + f'Accessible through the following URL: {current_commit_url}' + Fore.RESET, Style.RESET_ALL)

    def commitValidation(): pass
    
    # cant download recursively --> nested limit of 1 folder, so: folder_xy/file.abc
    def downloadRepositoryFileContents(self):
        
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
            'owner': self.GITHUB_REPO_OWNER,
            'name': self.GITHUB_REPO_NAME
        }
        
        current_content_query = requests.post(
            'https://api.github.com/graphql',
            json = {
                'query': current_content,
                'variables': current_content_variables
            },
            headers = self.GITHUB_HEADERS
        )
        
        #printHTTPStatus(current_content_query.status_code, 'GitHub')
        
        return json.dumps(current_content_query.json(), indent=4)
    
    def getLatestCommitOiD(self):
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
            self.URL,
            json = { 'query': oid_query },
            headers = self.GITHUB_HEADERS
        )
        
        #printHTTPStatus(oid_query.status_code, 'GitHub')
        most_recent_commit_oid = json.dumps(oid_query.json(), indent=4)
        
        return most_recent_commit_oid
  
    def downloadFileFromCommit(self, commit_oid: str, path: str):
        
        path = path.replace(' ', '%20')
        query_string = f'https://api.github.com/repos/{self.GITHUB_REPO_OWNER}/{self.GITHUB_REPO_NAME}/contents/{path}?ref={commit_oid}'
        #print(query_string)
        
        commit_files = requests.get(
            query_string,
            headers = self.GITHUB_HEADERS
        )

        if commit_files.status_code == 200:
            return json.loads(self.base64decode(json.dumps(commit_files.json()['content'], indent=4)))
        else:
            print('Couldn\'t download file from GitHub: ' + str(commit_files.status_code) + ' -> ' + commit_files.json()['message'])
  
    def base64encode(self, string: str):
        string_bytes = string.encode('ascii')
        base64_bytes = base64.b64encode(string_bytes)
        base64_string = base64_bytes.decode('ascii')
        return base64_string
    
    def base64decode(self, base64_input: str):
        base64_input = base64_input.replace('\\n', '\n')
        base64_bytes = base64_input.encode('ascii')
        string_bytes = base64.b64decode(base64_bytes)
        decoded_string = string_bytes.decode('ascii')
        return decoded_string
    
    # A faster way to compare larger string using MD5 hashes
    def modified(self, upload_str: str, current_str: str):
        if current_str is not None or current_str != '':
            print(Style.DIM + hashlib.md5(upload_str.encode()).hexdigest() + Style.RESET_ALL)
            print(Style.DIM + hashlib.md5(current_str.encode()).hexdigest() + Style.RESET_ALL)
            if hashlib.md5(upload_str.encode()).hexdigest() == hashlib.md5(current_str.encode()).hexdigest():
                print(Fore.GREEN + Style.BRIGHT + 'MD5 Hashes are the same' + Fore.RESET + Style.RESET_ALL)
                return False # Not Modified
            else:
                print(Fore.YELLOW + Style.BRIGHT + 'MD5 Hashes are not the same' + Fore.RESET + Style.RESET_ALL) 
                return True # modified