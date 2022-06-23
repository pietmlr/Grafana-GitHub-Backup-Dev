import json


class Folder():

    def __init__(self, id, uid, title):
        if id is not None and uid is not None and title is not None:
            self.id = id
            self.uid = uid
            self.title = title
        else:
            raise Exception('Some attributes are None')

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)