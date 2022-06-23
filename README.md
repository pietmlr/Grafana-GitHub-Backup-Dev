# Release Notes
## 20.06.2022 - 23.06.2022
1. Downloading Grafana Dashboard from Grafana
2. Commiting Grafana Dashboard to GitHub
3. Downloading Grafana Dashboard from GitHub
4. Installing Grafana Dashboard into Grafana
    1. If the dashboard really got deleted,then step 4 will restore it
    1. If the dashboard is still existing (given still the same name, folder, uid and id), 
    Grafana will refuse to create a new dashboard with the following error 
    message: "A dashboard with the same name in the folder already exists" OR
    "A dashboard with the same uid already exists"
    1. If the user wants to replace the existing dashboard with some version from GitHub,
    he can enable the overwrite=True option, overwriting the existing dashboard with 
    the new data (TEST NECESSARY)!! (INSTALLATION INTO ANYTHING OTHER THAN THEN GENERAL 
                                    FOLDER IS CURRENTLY NOT POSSIBLE)
    1. If the user wants the version from GitHub but also does not want to loose the 
    existing version of the dashboard, he can enable the create_copy=True option, 
    which will not delete the existing dashboard but rather uploads the GitHub 
    dashboard seperately with a name similar to "NAME-Copy-Y/m/d-H:M:S"

# Upcoming Features
- Break code into modules
- Mirror folder structure of Grafana on GitHub
    - Remirror folder structure on backup from GitHub to Grafana
        - Using update in dashboard meta data 
- Using Grafana version history comments as github commit headlines 
- Commmand Line Interface using Shell
- Dokumentation

# Modulstruktur
- Folder
- Dashboard
- Core (CLI)(main)
    - Calls further methods
- Connector
    - GrafanaConnector
    - GitHubConnector
- Config 
    - Scraper-Config.config (into .gitignore)
        -  For saving API_KEYS
