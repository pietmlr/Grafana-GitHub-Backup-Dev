# Release Notes
## 20.06.2022 - 23.06.2022
1. Downloading Grafana Dashboard from Grafana
2. Commiting Grafana Dashboard to GitHub
3. Downloading Grafana Dashboard from GitHub
4. Installing Grafana Dashboard into Grafana
    1. If the dashboard really got deleted,then step 4 will restore it
    1. If the dashboard is still existing (given still the same name, folder, uid and id, Grafana will refuse to create a new dashboard with the following error 
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

## 24.06.2022
1. The main code (scraper.py) has been broken into modules and classes according to the
    project graph.
    * Following modules and classes have been created: 
        * Grafana
        * GitHub
        * Core
        * CLI
2. The "sync" command has been brought to the creators attention combining fundamental
    command "backup" and "publish". It can only be used to synchronise everything, not single files or directories.

## 27.06.2022
1. Transition to a fully modular approach is done
2. Everything is working, controlled by the core module
3. Added ArgumentParser for the "backup" command
    1. "python3 core.py backup --everything True" works totally fine
    2. "python3 core.py backup --path 'folder/dashboard'" works totally fine

# ToDo
- [x] Check if downloadRepositoryFileContents() return nested file structure and parse JSON accordingly
    * Resolved: Grafana structure only allows 1 nested folder
    * Addtionally: GitHub GraphQL API does not support recursive output of repository 
        structure
- [x] Test upload of a whole folder
- [] Finish the publish command
    - [] Testing publishing options: everything, path, overwrite, copy
    - [] Expand ArgumentParser to include publishing options

# Upcoming Features
- [x] Downloading Grafana dashboard JSON models
- [x] Commiting Grafana dashboard JSON models to GitHub
- [x] Downloading Grafana dashboard JSON models from GitHub
- [x] Installing Grafana dashboards into Grafana with the following options:
    * overwrite
    * create_copy
- [x] Break code into modules
- [x] Mirror folder structure of Grafana on GitHub (ACTIVE)
    - [ ] Remirror folder structure on backup from GitHub to Grafana
        - [ ] Using update in dashboard meta data 
- [ ] Using Grafana version history comments as github commit headlines 
- [ ] Commmand Line Interface using Shell
- [ ] Dokumentation (Daily release notes in Markdown) (ACTIVE)

# Modulstruktur
- [x] Core (CLI)(main)
    - Interfacing of all system components
    - Passing input data from shell into certain components
    - Passing output data back to shell
    - Parsing and validating input data
- [x] GitHub
    - For handling everything that concerns the GitHub REST- and GraphQL API
- [x] Grafana
    - For handling everything that concers the Grafana API
- [x] Config 
    - [x] config.json (into .gitignore for security purposes)
        -  For saving: 
            * API_KEYS
            * Grafana Login Data
            * GitHub Repository Owner and Name

