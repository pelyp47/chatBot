from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#database create and connect
engine = create_engine('sqlite:///database/data.db')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    token = Column(String, primary_key = True)
    name = Column(String)
    track_id = Column(String)
    support_id = Column(Integer, ForeignKey("supports.id"))


class Support(Base):
    __tablename__ = "supports"
    id = Column(Integer, primary_key = True)
    name = Column(String)



Base.metadata.create_all(engine)

#session create
Session = sessionmaker(bind=engine)
session = Session()


