class Field:
    def __init__(self, source, *args, **kwargs):
        self.source = source


class ReferenceField(Field):
    def __init__(self, source, pk="id", *args, **kwargs):
        self.pk = pk
        super().__init__(source, *args, **kwargs)


class MethodField(Field):
    def __init__(self, source=None, *args, **kwargs):
        self.source = source
