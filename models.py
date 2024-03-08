from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///carwash.db')
db_session = scoped_session(sessionmaker(bind=engine))

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    cars = relationship("Car", back_populates="customer")

class Car(Base):
    __tablename__ = 'car'
    id = Column(Integer, primary_key=True)
    year = Column(String)
    make = Column(String)
    model = Column(String)
    license_plate = Column(String, unique=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship("Customer", back_populates="cars")

def init_db():
    Base.metadata.create_all(bind=engine)
