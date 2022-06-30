#!/usr/bin/env python3
import argparse
from colorama import Fore, Style
from config import Config
from github import GitHub
from grafana import Grafana
import json

config = Config()
if not config.checkConfig():
    print(Fore.RED + Style.BRIGHT + 'Exiting program' + Fore.RESET + Style.RESET_ALL)

github = GitHub(config=config)
grafana = Grafana(config=config)

### Argument Parser ###
parser = argparse.ArgumentParser()

# Set up subparsers
subparser = parser.add_subparsers(dest='command')
backup = subparser.add_parser('backup')
publish = subparser.add_parser('publish')
help = subparser.add_parser('help')
sync = subparser.add_parser('sync')

# Add arguments to backup subparser
backup.add_argument('--path', type=str)
backup.add_argument('--everything', type=bool)
backup.add_argument('--custom_message', type=str)

# Add arguments to backup subparser
publish.add_argument('--commit_id', type=str)

publish.add_argument('--path', type=str)
publish.add_argument('--everything', type=bool)

publish.add_argument('--overwrite', type=bool)
publish.add_argument('--create_copy', type=bool)

# obvious name -> acronym
# Pretty Intelligent (and) Easy (Grafana Backup) Tool
# Licensing Apache/MIT

# Combinations
backup_parameter_combinations = """
    Backup Options: (e.g. tool backup --path "folder x/prod_dashboard_y")
    --path
    --path --custom_message

    --everything (Disabled by default)
    --everthing --overwrite
    --everthing --create-copy
"""

publish_parameter_combinations = """
    Publishing Options: (e.g. tool publish --commit_id dfbds23r2wfiudsb3022b9fb --path "folder x/prod_dashboard_y.json")
    --commit-id & --path  (works ONLY if there is no dashboard with the same name or uid on the given path!)
    --commit-id & --path & --overwrite 
    --commit-id & --path & --create-copy

    --everything  (ONLY uses latest commits!)
    --everthing & --overwrite
    --everthing & --create-copy
"""

sync_combinations = """
    Syncronising Options: (e.g tool sync)
    No combinations available. Just 'sync' it.
    Sync only allows to backup everything inside of grafana and publish everything inside of GitHub to Grafana.
"""

help_message = """
    This tool provides the following commands:
    'backup', 'publish', 'sync', 'help'
"""

special_chars_msg = Fore.LIGHTBLUE_EX + """
    +--------------------------------------------------------------------+
    |                       - Character Policy -                         |
    | Be aware that the following characters should not be contained     |
    | inside the dashboards name: '/', ':', '&', '?', '.', ',', '%', '"',|
    | '+', '='                                                           |
    +--------------------------------------------------------------------+ 
""" + Fore.RESET

# Parse the arguments
args = parser.parse_args()

def sync_publish():
    continue_prompt = input(Fore.LIGHTWHITE_EX + Style.BRIGHT + 'You are about to overwrite existing dashboards,' +
                            'to continue type Y/y, otherwise N/n: ' + Fore.LIGHTWHITE_EX + Style.RESET_ALL)
    if continue_prompt == 'N' or continue_prompt == 'n':
        print(Fore.YELLOW + 'Operation has been stopped' + Fore.RESET)
    elif continue_prompt == 'Y' or continue_prompt == 'y':
        backup_files = github.downloadRepositoryFileContents()
        # parsing response
        folders = json.loads(backup_files)['data']['repository']['object']['entries']
        for folder in folders:
            root_folder = folder['name']
            # Check if folder is empty or is actually a file
            if 'entries' in folder['object']:
                print(Fore.LIGHTWHITE_EX + Style.BRIGHT + f'Contents of "{root_folder}"' + Fore.RESET + Style.RESET_ALL)
                for dashboard in folder['object']['entries']:
                    dashboard_model = json.loads(dashboard['object']['text'])
                    filename = dashboard['name']
                    path = root_folder + '/' + filename
                    print(f'  |__ {path}')
                    grafana.installDashboard(dashboard_model=dashboard_model, path=path, 
                                                commit_oid='Latest version on GitHub', overwrite=True)
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    else:
        print(Fore.YELLOW + 'Operation has been stopped, please enter valid answers' + Fore.RESET)

def sync_backup():
    print(f'You have chosen to backup everything')
    folderIds = grafana.getAllFoldersIds()
    for folderId in folderIds:
        dashboard_package = grafana.getDashboardUIDs(folderId=folderId)
        #print(dashboard_package)
        dashboard_uids = dashboard_package[0]
        dashboard_root_folder = dashboard_package[1]
        #print(f'FolderId {folderId} contains following dashboards: {dashboard_uids}')
        for i, dashboard_uid in enumerate(dashboard_uids):
            if dashboard_uid is not [] and dashboard_uid != '-1':
                dashboard = grafana.getDashboard(path='-1', dashboard_uid=dashboard_uid)
                filename = dashboard['dashboard']['title']
                root_folder = dashboard_root_folder[i]
                path = root_folder + '/' + filename 
                print(Style.DIM + f'Backing up: "{path}"' + Style.RESET_ALL)
                github.commitDashboard(dashboard=dashboard, path=path, commit_message='-1')
                #print('------------------------------------------------')
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

### Backup Command Section ###
if args.command == 'backup':
    print(special_chars_msg)
    print('## Only folders with actual content will be backed-up ##')
    if args.path and args.everything:
        print(Fore.RED + Style.BRIGHT + 'You are allowed to select either --path OR --everything as an option for backup' + 
            Fore.RESET + Style.RESET_ALL)
    elif args.path:
        #print(f'You have chosen to backup "{args.path}"')
        dashboard = grafana.getDashboard(path=args.path, dashboard_uid='-1')
        if args.custom_message:
            github.commitDashboard(dashboard=dashboard, path=args.path, commit_message=args.custom_message)
        else:
            github.commitDashboard(dashboard=dashboard, path=args.path, commit_message='-1')
    elif args.everything:
        print(f'You have chosen to backup everything')
        folderIds = grafana.getAllFoldersIds()
        #for folderId in tqdm(folderIds, desc='Uploading folders and dashboards'):
        for folderId in folderIds:
            dashboard_package = grafana.getDashboardUIDs(folderId=folderId)
            #print(dashboard_package)
            dashboard_uids = dashboard_package[0]
            dashboard_root_folder = dashboard_package[1]
            #print(f'FolderId {folderId} contains following dashboards: {dashboard_uids}')
            for i, dashboard_uid in enumerate(dashboard_uids):
                if dashboard_uid is not [] and dashboard_uid != '-1':
                    dashboard = grafana.getDashboard(path='-1', dashboard_uid=dashboard_uid)
                    filename = dashboard['dashboard']['title']
                    root_folder = dashboard_root_folder[i]
                    path = root_folder + '/' + filename 
                    print(Style.DIM + f'Backing up: "{path}"' + Style.RESET_ALL)
                    github.commitDashboard(dashboard=dashboard, path=path, commit_message='-1')
                    #print('------------------------------------------------')
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    else:
        print(Fore.RED + Style.BRIGHT + 'You have to select either --path or --everything as an option for backup' + 
            Fore.RESET + Style.RESET_ALL)
        
# create seperate publish and backup functions
### Publish Command Section ###
elif args.command == 'publish':
    if args.commit_id and args.path: 
        if args.overwrite and args.path: 
            continue_prompt = input(Style.BRIGHT + 'You are about to overwrite existing dashboards,' +
                                    'to continue type Y/y, otherwise N/n: ' + Style.RESET_ALL)
            if continue_prompt == 'N' or continue_prompt == 'n':
                print(Fore.YELLOW + 'Operation has been stopped' + Fore.RESET)
            elif continue_prompt == 'Y' or continue_prompt == 'y':
                backup_file = github.downloadFileFromCommit(commit_oid=args.commit_id, path=args.path)
                if backup_file is None:
                    print(Fore.RED + Style.BRIGHT + 
                    f'The file you chose is not on the provided path ({args.path}) on GitHub' +
                    Fore.RESET + Style.RESET_ALL)
                else:
                    grafana.installDashboard(dashboard_model=backup_file, path=args.path, 
                                            commit_oid=args.commit_id, overwrite=True)
            else:
                print(Fore.YELLOW + 'Operation has been stopped, please enter valid answers' + Fore.RESET)
        elif args.create_copy and args.path: 
            backup_file = github.downloadFileFromCommit(commit_oid=args.commit_id, path=args.path)
            if backup_file is None:
                print(Fore.RED + Style.BRIGHT + 
                    f'The file you chose is not on the provided path ({args.path}) on GitHub' +
                    Fore.RESET + Style.RESET_ALL)
            else:
                grafana.installDashboard(dashboard_model=backup_file, path=args.path, 
                                            commit_oid=args.commit_id, create_copy=True)
        else: 
            backup_file = github.downloadFileFromCommit(commit_oid=args.commit_id, path=args.path)
            if backup_file is None:
                print(Fore.RED + Style.BRIGHT + 
                    f'The file you chose is not on the provided path ({args.path}) on GitHub' +
                    Fore.RESET + Style.RESET_ALL)
            else:
                grafana.installDashboard(dashboard_model=backup_file, path=args.path, 
                                        commit_oid=args.commit_id)
    elif args.everything:
        if args.overwrite: 
            continue_prompt = input(Fore.LIGHTWHITE_EX + Style.BRIGHT + 'You are about to overwrite existing dashboards,' +
                                    'to continue type Y/y, otherwise N/n: ' + Fore.LIGHTWHITE_EX + Style.RESET_ALL)
            if continue_prompt == 'N' or continue_prompt == 'n':
                print(Fore.YELLOW + 'Operation has been stopped' + Fore.RESET)
            elif continue_prompt == 'Y' or continue_prompt == 'y':
                backup_files = github.downloadRepositoryFileContents()
                # parsing response
                folders = json.loads(backup_files)['data']['repository']['object']['entries']
                for folder in folders:
                    root_folder = folder['name']
                    # Check if folder is empty or is actually a file
                    if 'entries' in folder['object']:
                        print(Fore.LIGHTWHITE_EX + Style.BRIGHT + f'Contents of "{root_folder}"' + Fore.RESET + Style.RESET_ALL)
                        for dashboard in folder['object']['entries']:
                            dashboard_model = json.loads(dashboard['object']['text'])
                            filename = dashboard['name']
                            path = root_folder + '/' + filename
                            print(f'  |__ {path}')
                            grafana.installDashboard(dashboard_model=dashboard_model, path=path, 
                                                    commit_oid='Latest version on GitHub', overwrite=True)
                            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            else:
                print(Fore.YELLOW + 'Operation has been stopped, please enter valid answers' + Fore.RESET)
        elif args.create_copy: 
            backup_files = github.downloadRepositoryFileContents()
            # parsing response
            folders = json.loads(backup_files)['data']['repository']['object']['entries']
            for folder in folders:
                root_folder = folder['name']
                # Check if folder is empty or is actually a file
                if 'entries' in folder['object']:
                    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + f'Contents of "{root_folder}"' + Fore.RESET + Style.RESET_ALL)
                    for dashboard in folder['object']['entries']:
                        dashboard_model = json.loads(dashboard['object']['text'])
                        filename = dashboard['name']
                        path = root_folder + '/' + filename
                        print(f'\t|__ {path}')
                        grafana.installDashboard(dashboard_model=dashboard_model, path=path, 
                                                commit_oid='Latest version on GitHub', create_copy=True)
                        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        else: 
            backup_files = github.downloadRepositoryFileContents()
            # parsing response
            folders = json.loads(backup_files)['data']['repository']['object']['entries']
            for folder in folders:
                root_folder = folder['name']
                # Check if folder is empty or is actually a file
                if 'entries' in folder['object']:
                    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + f'Contents of "{root_folder}"' + Fore.RESET + Style.RESET_ALL)
                    for dashboard in folder['object']['entries']:
                        dashboard_model = json.loads(dashboard['object']['text'])
                        filename = dashboard['name']
                        path = root_folder + '/' + filename
                        print(f'\t|__ {path}')
                        grafana.installDashboard(dashboard_model=dashboard_model, path=path, commit_oid='Latest version on GitHub')
                        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    else:
        print(Fore.RED + Style.BRIGHT + 
            'The following parameter combinations are allowed:' + 
            Fore.RESET + Style.RESET_ALL + 
            f'\n{publish_parameter_combinations}')
        
elif args.command == 'sync':
    print('Be aware: This command will install all available folders and files on GitHub into Grafana')
    continue_prompt = input(Style.BRIGHT + 'You are about to overwrite existing dashboards,' +
                                    'to continue type Y/y, otherwise N/n: ' + Style.RESET_ALL)
    if continue_prompt == 'N' or continue_prompt == 'n':
        print(Fore.YELLOW + 'Operation has been stopped' + Fore.RESET)
    elif continue_prompt == 'Y' or continue_prompt == 'y':
        sync_backup()
        sync_publish()
        
elif args.command == 'help':
    print(help_message)
    print(backup_parameter_combinations)
    print(publish_parameter_combinations)
    print(sync_combinations)
    
    print('    And for, hopefully none, errors within URLs, tool has a character policy which you should follow')
    print(special_chars_msg)
    
else:
    print(help_message)
    print(backup_parameter_combinations)
    print(publish_parameter_combinations)
    print(sync_combinations)
    
    print('    And for, hopefully none, errors within URLs, tool has a character policy which you should follow')
    print(special_chars_msg)
    
    print('For global access, move (mv) the project into /usr/local/')
    
