class Sort:
    def __init__(self, field, direction):
        self.field = field
        self.direction = direction

    def __str__(self):
        return f"{self.field}:{self.direction}"
