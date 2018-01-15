from sqlalchemy import create_engine, Column, Table, ForeignKey,  DateTime, String, Integer,func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

from scrapy.utils.project import get_project_settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """    
    return create_engine(get_project_settings().get("CONNECTION_STRING"))

def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class BucscraperDB(DeclarativeBase):
    __tablename__ = "article_table"

    id = Column(Integer, primary_key=True)
    date = Column('date', DateTime(timezone=True), server_default=func.now())
    text = Column('text', Text())
    link = Column('link', String)
    