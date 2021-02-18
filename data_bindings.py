
class Facet:
    def __init__(self, obj, field):
        self.obj = obj
        self.field = field

    def get(self):
        return getattr(self.obj, self.field)

    def set(self, value):
        setattr(self.obj, self.field, value)

class DataBindings:
    def __init__(self):
        self.__bindings = []

    def add_binding(self, source, destination):
        self.__bindings.append((source, destination))

    def push(self):
        for b in self.__bindings:
            b[1].set(b[0].get())
            
    def pull(self):
        for b in self.__bindings:
            b[0].set(b[1].get())
