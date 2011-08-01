from types import FunctionType

def setup(session, *tables):
    for table in tables:
        Model = table.model
        for row in table.rows:
            item = Model(**dict(row))
            session.add(item)
            session.commit()
            row.id = item.id

class Table(object):
    def __init__(self):
        self.rows = []

    def row(self, name):
        row = Row(self.columns)
        self.rows.append(row)
        setattr(self, name, row)
        return row

    def __iter__(self):
        for r in self.rows:
            yield dict(r)

class Row(object):
    def __init__(self, columns):
        self.columns = columns
        self.values = {}

    def set(self, *args, **kwargs):
        values = dict(zip(self.columns, args))
        values.update(kwargs)
        self.values.update(values)
        return self

    def f(self, data):
        if isinstance(data, Table):
            self.values.update(row.values)
        else:
            self.values.update(data)
        return self

    @property
    def id(self):
        def lazy():
            return self.values.get('id')
        return lazy

    @id.setter
    def id(self, id):
        self.values['id'] = id

    def __iter__(self):
        for k,v in self.values.iteritems():
            if isinstance(v, FunctionType):
                yield k, v()
            else:
                yield k, v
