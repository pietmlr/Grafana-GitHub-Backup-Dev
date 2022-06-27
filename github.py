import base64
from datetime import datetime
from config import Config
import hashlib
import json
import requests


class GitHub:
    
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
        commit_headline_message: str, foldername: str, fileIndex: int = 0
        """
        # Set dashboard name to filename
        filename = dashboard['dashboard']['title']
        path = path.split('/')[0] + '/' + filename + '.json'
        print(path)

        print(self.downloadRepositoryFileContents())
        # First of all, check if the file needs to be overwritten
        # [:-1] for removing the last character '\n' added by GitHub
        current_file_content = json.loads(self.downloadRepositoryFileContents())['data']['repository']['object']['entries'][0]['object']['text'][:-1]
        #print(current_file_content)
        
        print(f'Checking "{filename}" for commit')
        
        # Check if a commit is necessary
        if not self.modified(dashboard, current_file_content):
            print('There is no commit necessary (File is not modified)')
            return 
        else:
            print('The dashboard files need to be upgraded (File is modified)')
            
        print(current_file_content)
        print(dashboard)
            
        most_recent_commit_oid = self.getLatestCommitOiD()
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
        
        commit_headline = datetime.now().time().strftime('%Y/%m/%d-%H:%M:%S')

        commit_variables = {
            'input': {
                'branch': {
                    'repositoryNameWithOwner': (self.GITHUB_REPO_OWNER + '/' + self.GITHUB_REPO_NAME),
                    'branchName': 'main'
                },
                'message': {
                    'headline': f'Backup of "{filename}" {commit_headline}'
                },
                'fileChanges': {
                    'additions': [
                        {
                            'path': path,
                            'contents': self.base64encode(dashboard + '\n')
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
            headers = self.GITHUB_HEADERS
        )
        
        #printHTTPStatus(commit_response.status_code, 'GitHub')
        commit_response = json.dumps(commit_response.json(), indent=4)
        print(commit_response)
        current_commit_url = json.loads(commit_response)['data']['createCommitOnBranch']['commit']['url']
        current_commit_oid = json.loads(commit_response)['data']['createCommitOnBranch']['commit']['oid']
        
        print(f'Commited Grafana Dashboard "{path}" to GitHub [Commit-OiD: (short) {current_commit_oid[:7]}, (long) {current_commit_oid}]\nAccessible through the following URL: {current_commit_url}')

    def commitValidation(): pass
    
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