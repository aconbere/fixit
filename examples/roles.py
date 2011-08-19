import fixit

from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'

    id                    = Column(Integer, primary_key=True)
    name                  = Column(String(64))
    short_name            = Column(String(64))
    default_boss_role_id  = Column(Integer)
    is_team_default       = Column(Boolean, default=True)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

roles = fixit.Table(Role)
roles.row("nfd").set(name            = "National Field Director",
                     short_name      = "nfd",
                     is_team_default = True,
                     )

roles.row("nrd").set(name                 = "National Regional Director",
                     short_name           = "nrd",
                     is_team_default      = True,
                     default_boss_role_id = roles.nfd.get("id")
                     )


roles.row("sd").set(name                 = "State Director",
                    short_name           = "sd",
                    is_team_default      = True,
                    default_boss_role_id = roles.nrd.get("id")
                    )

# This is a couple of the shortcuts available by design
# .f means from (from is a stupid keyword in python so I can't use it)
# it means inherit from a previous defined row or dict
#
# .set looks at *args as well as **kwargs and zips args with the column names
# So if you know what order the columns are in, you can just hand args to it
# that way. In this case this sets the Name of "fd" to Field Director
roles.row("fd").f(roles.sd).set(name = "Field Director")

fixit.setup(db_session, roles)

for role in db_session.query(Role).order_by("id").all():
    print "******"
    print role.name
    print role.short_name
    print role.default_boss_role_id
