import argparse
from colorama import Fore, Style
from config import Config
from github import GitHub
from grafana import Grafana
import json
from tqdm import tqdm


config = Config()
github = GitHub(config=config)
grafana = Grafana(config=config)

### Argument Parser ###
parser = argparse.ArgumentParser()

# Set up subparsers
subparser = parser.add_subparsers(dest='command')
backup = subparser.add_parser('backup')
publish = subparser.add_parser('publish')
sync = subparser.add_parser('sync')

# Add arguments to backup subparser
backup.add_argument('--path', type=str)
backup.add_argument('--everything', type=bool)

# Add arguments to backup subparser
publish.add_argument('--commit_id', type=str)

publish.add_argument('--path', type=str)
publish.add_argument('--everything', type=bool)

publish.add_argument('--overwrite', type=bool)
publish.add_argument('--create_copy', type=bool)

publish.add_argument('--test', type=bool)

# Combinations
publish_parameter_combinations = """
    # --commit-id & --path  (works only if there is no dashboard with the same name or uid on this path!)
    # --commit-id & --path & --overwrite
    # --commit-id & --path & --create-copy

    # --everything  # uses latest commits
    # --everthing & --overwrite
    # --everthing & --create-copy
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

### Backup Command Section ###
if args.command == 'backup':
    print(special_chars_msg)
    print('## Only folders with actual content will be backed-up ##')
    if args.path and args.everything:
        print(Fore.RED + Style.BRIGHT + 'You are allowed to select either --path OR --everything as an option for backup' +  Fore.RESET + Style.RESET_ALL)
    elif args.path:
        #print(f'You have chosen to backup "{args.path}"')
        dashboard = grafana.getDashboard(path=args.path, dashboard_uid='-1')
        github.commitDashboard(dashboard=dashboard, path=args.path)
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
                    github.commitDashboard(dashboard=dashboard, path=path)
                    #print('------------------------------------------------')
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    else:
        print(Fore.RED + Style.BRIGHT + 'You have to select either --path or --everything as an option for backup' + Fore.RESET + Style.RESET_ALL)
        
### Publish Command Section ###
elif args.command == 'publish':
    if args.commit_id and args.path:
        if args.overwrite: pass
        elif args.create_copy: pass
        else: 
            backup_file = github.downloadFileFromCommit(args.commit_id, args.path)
            grafana.installDashboard(dashboard_model=backup_file, path=args.path, 
                                     commit_oid=args.commit_id)
            
    elif args.everything:
        if args.overwrite: pass
        elif args.create_copy: pass
        else: pass
    else:
        print(Fore.RED + Style.BRIGHT + 
              'The following parameter combinations are allowed:' + 
              Fore.RESET + Style.RESET_ALL + 
              f'\n{publish_parameter_combinations}')
        
