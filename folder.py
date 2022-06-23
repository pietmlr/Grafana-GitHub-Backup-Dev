class Folder(object):
    def __init__(self, id, uid, title):
        self.id = id
        self.uid = uid
        self.title = title
        
    @property
    def id(self):
        return self.id

    @id.setter
    def id(self, value):
        self.id = value

    @id.deleter
    def id(self):
        del self.id
        
    @property
    def uid(self):
        return self.uid

    @uid.setter
    def uid(self, value):
        self.uid = value

    @uid.deleter
    def uid(self):
        del self.uid
        
    @property
    def title(self):
        return self.title

    @title.setter
    def title(self, value):
        self.title = value

    @title.deleter
    def title(self):
        del self.title