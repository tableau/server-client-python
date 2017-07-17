"""Target class meant to abstract mappings to other objects"""
class Target():
    def __init__(self, id, target_type):
        self.id = id
        self.target_type = target_type

    def __repr__(self):
        return "<Target#{id}, {target_type}>"

    def get_type(self):
        return self.target_type

    def get_id(self):
        return self.id
