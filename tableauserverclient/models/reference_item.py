class ResourceReference:
    def __init__(self, id_, tag_name):
        self.id = id_
        self.tag_name = tag_name

    def __str__(self):
        return f"<ResourceReference id={self._id} tag={self._tag_name}>"

    __repr__ = __str__

    def __eq__(self, other: object) -> bool:
        if not hasattr(other, "id") or not hasattr(other, "tag_name"):
            return False
        return (self.id == other.id) and (self.tag_name == other.tag_name)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def tag_name(self):
        return self._tag_name

    @tag_name.setter
    def tag_name(self, value):
        self._tag_name = value
