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

# Parse the arguments
args = parser.parse_args()

# Access parsed arguments
# if args.command == 'publish':
#   args.path


### Backup Command Section ###
if args.command == 'backup':
    print('Only folders with actual content will be backed-up')
    if args.path:
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
                    print('------------------------------------------------')

    elif args.path and args.everything:
        print(Fore.RED + Style.BRIGHT + 'You are allowed to select either path OR everything to for backup' +  Fore.RESET + Style.RESET_ALL)
    else:
        print(Fore.RED + Style.BRIGHT + 'You have to select either path or everything as an option to backup' + Fore.RESET + Style.RESET_ALL)


### Publish Command Section ###
#if args.command == 'publish':