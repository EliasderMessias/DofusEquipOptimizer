from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schema import Base

engine = create_engine('sqlite:///DofusItems.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def get_session():
    return Session()