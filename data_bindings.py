
class ConversionAdapter:
    def __init__(self, push, pull):
        self.push = push
        self.pull = pull

NopAdapter = ConversionAdapter(push=lambda x: x, pull=lambda x: x)
FloatToInt = ConversionAdapter(push=lambda x: int(x), pull=lambda x: float(x))

class Binding:
    def __init__(self, getter, setter = lambda: None):
        self.getter = getter
        self.setter = setter
        
    def get(self):
        return self.getter()
    
    def set(self, value):
        self.setter(value)

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

    def add_binding(self, source, destination, conversion = NopAdapter):
        self.__bindings.append((source, destination, conversion))

    def push(self):
        for b in self.__bindings:
            b[1].set(b[2].push(b[0].get()))
            
    def pull(self):
        for b in self.__bindings:
            b[0].set(b[2].pull(b[1].get()))
