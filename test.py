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

class RoleData(fixit.Table):
    columns = ["name", "short_name", "default_boss_role_id", "is_team_default"]

roles = RoleData()
roles.row("nfd").set(name            = "National Field Director",
                     short_name      = "nfd",
                     is_team_default = True
                     )

roles.row("nrd").set(name                 = "National Regional Director",
                     short_name           = "nrd",
                     is_team_default      = True,
                     default_boss_role_id = roles.nfd.id
                     )

roles.row("sd").set(name                 = "State Director",
                    short_name           = "sd",
                    is_team_default      = True,
                    default_boss_role_id = roles.nrd.id
                    )

for role in roles.rows:
    r = Role(**dict(role))
    db_session.add(r)
    db_session.commit()
    role.id = r.id

for role in db_session.query(Role).all():
    print "******"
    print role.name
    print role.short_name
    print role.default_boss_role_id
