import os
import json

class Config:
    
    CONFIG_FILENAME = 'config.json'
    CONFIG_FILE_SAMPLE = {
        'GITHUB_API_KEY': 'YOUR_GITHUB_API_KEY',
        'GRAFANA_API_KEY': 'YOUR_GRAFANA_API_KEY',
        'GITHUB_REPOSITORY_OWNER': 'YOUR_REPOSITORY_OWNER',
        'GITHUB_REPOSITORY_NAME': 'YOUR_REPOSITORY_NAME',
        'GITHUB_URL': 'YOUR_GITHUB_URL',
        'GRAFANA_URL': 'YOUR_GRAFANA_URL',
        'GRAFANA_USER': 'YOUR_GRAFANA_USER',
        'GRAFANA_PASSWORD': 'YOUR_GRAFANA_PASSWORD'
    }
    
    def __init__(self):
        # Create it if it does not exist, otherwise load it
        if not os.path.isfile(self.CONFIG_FILENAME):
            with open(self.CONFIG_FILENAME, 'w') as config_file:
                #print(type(self.CONFIG_FILE_SAMPLE), type(json.dumps(self.CONFIG_FILE_SAMPLE)))
                config_file.write(json.dumps(self.CONFIG_FILE_SAMPLE, indent=4))
        
        # Load the config file
        self.config_file = json.loads(open(self.CONFIG_FILENAME, 'r').read())
        
    def checkConfig(self):
        user_keys = self.config_file.keys()
        for user_key in user_keys:
            for system_key in self.CONFIG_FILE_SAMPLE:
                if user_key != system_key:
                    print(f'Your configuration file is invalid, take a look at {user_key}')
                    return False
                else: return True

    def getGitHubKey(self): 
        return self.config_file['GITHUB_API_KEY'] 
    
    def getGrafanaKey(self): 
        return self.config_file['GRAFANA_API_KEY']  

    def getRepositoryOwner(self): 
        return self.config_file['GITHUB_REPOSITORY_OWNER']  
    
    def getRepositoryName(self): 
        return self.config_file['GITHUB_REPOSITORY_NAME']  
    
    def getGitHubURL(self): 
        return self.config_file['GITHUB_URL']  
    
    def getGrafanaURL(self): 
        return self.config_file['GRAFANA_URL']  

    def getGrafanaUser(self): 
        return self.config_file['GRAFANA_USER']
    
    def getGrafanaPassword(self): 
        return self.config_file['GRAFANA_PASSWORD']