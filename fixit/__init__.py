from types import FunctionType

class Table(object):
    """
    An abstract representation of a sqlalchemy table
    """

    def __init__(self, model):
        self.rows = []
        self.model = model
        self.columns = self.model.__table__.columns.keys()

    def row(self, name):
        row = Row(self.columns)
        self.rows.append(row)
        setattr(self, name, row)
        return row

    def after_insert(self, item, session):
        """
        Called after a row has been inserted
        """
        pass

    def after_create(self, session):
        """
        Called after all rows have been inserted
        """
        pass

class Row(object):
    def __init__(self, columns):
        self.columns = list(columns)
        self.columns.remove("id")
        self.values = {}
        self._item = None

    def __repr__(self):
        return str(self.values)

    def set(self, **kwargs):
        self.values.update(kwargs)
        return self

    def f(self, data):
        if isinstance(data, Row):
            self.values.update(data.values)
        else:
            self.values.update(data)
        return self

    def get(self, key):
        val = self.values.get(key)
        if isinstance(val, FunctionType):
            return val
        else:
            return lambda: self.values.get(key)

    def to_dict(self):
        return dict([(k, self.get(k)()) for k in self.values.keys()])

def setup(session, *tables):
    for table in tables:
        for row in table.rows:
            try:
                item = table.model(**row.to_dict())
                session.add(item)
                session.flush()
                row.values["id"] = item.id
                row._item = item
                table.after_insert(item, session)

#                for column in table.columns + ["id"]:
#                    value = getattr(item, column)
#                    if value:
#                        row.values[column] = value
            except AttributeError, why:
                raise AttributeError("You have a misconfigured row\n%s\n%s" % (row, why))
        table.after_create(session)
    session.commit()
