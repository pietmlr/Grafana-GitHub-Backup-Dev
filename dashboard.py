class Dashboard:
    """
    Simple Dashboard structure for storing and retrieving fundamental Dashboard data 
    """

    def __init__(self, grafana_api_reponse: dict):
        self.grafana_api_response = grafana_api_reponse

    def isDashboard(self, dashboard: dict) -> bool:
        return True if dashboard['type'] == 'dash-db' else False
    
    # From http://localhost:3000/api/search?folderIds=
    def getRootFolder(self) -> list:
        # root_folder = []
        # for dashboard in self.grafana_api_response:
        #     if self.isDashboard(dashboard):
        #         if 'folderTitle' in dashboard:
        #             root_folder.append(dashboard['folderTitle'])
        #         else:
        #             root_folder.append('General')
        #     else:
        #         root_folder.append('-1')
        return [dashboard['folderTitle'] if 'folderTitle' in dashboard else 'General' if self.isDashboard(dashboard) else '-1' for dashboard in self.grafana_api_response]

    # From http://localhost:3000/api/search?folderIds=
    def getDashboardUid(self) -> list:
        """
        Returns:
            list: A List containing every dashboards uid, folders are marked with '-1'
        """
        return [dashboard['uid'] if self.isDashboard(dashboard) else '-1' for dashboard in self.grafana_api_response]

    def getDashboardTitle(self) -> list:
        return [dashboard['title'] for dashboard in self.grafana_api_response]