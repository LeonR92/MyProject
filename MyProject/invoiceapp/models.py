from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

# Define the base class
Base = declarative_base()


class Invoice(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True)
    invoice_num = Column(String(120), unique=True, nullable=False)
    invoice_amount = Column(Float, nullable=False)
    sender_address = Column(String(255), nullable=False)
    receiver_address = Column(String(255), nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    payment_terms = Column(Integer, nullable=True)
    invoice_description = Column(Text, nullable=True)
    receiver = Column(String(120), nullable=True)
    invoice_status = Column(String(50), nullable=True)
    items = relationship("InvoiceItem", backref="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_item"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)


# Engine and session setup
engine = create_engine(
    "sqlite:///invoice.db", echo=True
)  # Change the connection string as needed
Session = sessionmaker(bind=engine)
session = Session()

# Create tables in the database
Base.metadata.create_all(engine)
