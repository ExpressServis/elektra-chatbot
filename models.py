from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    ean = Column(String)
    name = Column(String)
    url = Column(String)
    image = Column(String)
    category = Column(String)
    price = Column(String)

class Knowledge(Base):
    __tablename__ = "knowledge"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    content = Column(Text)

def create_tables():
    Base.metadata.create_all(bind=engine)
