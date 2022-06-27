from config import Config
from github import GitHub
from grafana import Grafana


config = Config()
github = GitHub(config=config)
grafana = Grafana(config=config)

### Backup Command Section ###

# # for option everything on backup
# dashboards = grafana.getDashboards()
# for dashboard in dashboards:
#     github.commitDashboard(dashboard)
    
# # or more efficiently
# everything = 0
# for i in len(everything):
#     dashboard = grafana.getDashboard()
#     github.commitDashboard(dashboard)

# for option path on backup
path = 'folder 1/Praktikum'
dashboard = grafana.getDashboard(path=path)
github.commitDashboard(dashboard, path)


### Publish Command Section ###