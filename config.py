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
        if os.path.isfile(self.CONFIG_FILENAME):
            with open(self.CONFIG_FILENAME, 'r') as config_file:
                json.loads(config_file)
        else:
            with open(self.CONFIG_FILENAME, 'w') as config_file:
                config_file.write(self.CONFIG_FILE_SAMPLE)
        
        # Validate the if every key-value -pair is existend

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