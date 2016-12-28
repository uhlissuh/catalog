import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Item(Base):
    __tablename__ = 'item'
    id =  Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(350))
    category = Column(String(80), nullable = False)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
