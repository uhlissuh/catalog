import sys
import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    name = Column(String(80), nullable = False)
    id =  Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)

class Item(Base):
    __tablename__ = 'items'
    name = Column(String(80), nullable = False)
    id =  Column(Integer, primary_key = True)
    description = Column(String(250))
    category = Column(String(80), nullable = False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
