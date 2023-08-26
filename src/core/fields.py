class Field:
    def __init__(self, source, *args, **kwargs):
        self.source = source
        self.args = args
        self.kwargs = kwargs


class ReferenceField(Field):
    def __init__(self, mapper, source, pk="id", *args, **kwargs):
        self.pk = pk
        self.mapper = mapper
        super().__init__(source, *args, **kwargs)


class MethodField(Field):
    def __init__(self, source=None, *args, **kwargs):
        self.source = source
