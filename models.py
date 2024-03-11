from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, backref

Base = declarative_base()

# Configure your database URI here
DATABASE_URI = 'sqlite:///carwash.db'
engine = create_engine(DATABASE_URI, echo=True)

# Scoped session to ensure thread safety
db_session = scoped_session(sessionmaker(bind=engine))

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    phone = Column(String(64))
    email = Column(String(128), unique=True)
    cars = relationship("Car", backref="customer", lazy='dynamic')

    def __repr__(self):
        return f"<Customer(name={self.name}, email={self.email})>"

class Car(Base):
    __tablename__ = "car"
    id = Column(Integer, primary_key=True)
    year = Column(String(4))
    make = Column(String(128))
    model = Column(String(128))
    license_plate = Column(String(64), unique=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))

    def __repr__(self):
        return f"<Car(make={self.make}, model={self.model}, license_plate={self.license_plate})>"

def init_db():
    # In a production setting, it's important to appropriately manage database migrations.
    # For this simple example, we're directly creating the tables based on models.
    Base.metadata.create_all(bind=engine)

def shutdown_session(exception=None):
    db_session.remove()