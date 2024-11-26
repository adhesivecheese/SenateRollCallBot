from sqlalchemy import create_engine, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
db_name = config["DATABASE"].get("NAME")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_name}.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()


class Vote_Table(Base):
	__tablename__ = 'votes'
	id = Column(INTEGER(8), primary_key=True, unique=True)
	congress = Column(INTEGER(4))
	session = Column(INTEGER(4))
	vote_number = Column(INTEGER(6))

Base.metadata.create_all(bind=engine)
