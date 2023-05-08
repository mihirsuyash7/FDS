# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from datetime import datetime
from sqlalchemy import create_engine

Base=declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'
    id=Column(Integer, primary_key=True)        # Creating Column for ID
    type=Column(String(10), nullable=True)      # Creating Column for Transaction Type
    amount=Column(Float, nullable=True)         # Creating Column for Amount
    nameOrig=Column(String(15), nullable=True)  # Creating Column for Sender's Account Number
    oldbalanceOrig=Column(Float, nullable=True) # Creating Column for Old Balance of Sender's Account
    newbalanceOrig=Column(Float, nullable=True) # Creating Column for New Balance of Sender's Account
    nameDest=Column(String(15), nullable=True)  # Creating Column for Receiver's Account Number
    oldbalanceDest=Column(Float, nullable=True) # Creating Column for Old Balance of Receiver's Account
    newbalanceDest=Column(Float, nullable=True) # Creating Column for New Balance of Receiver's Account
    date_time=Column(DateTime, nullable=True)   # Creating Column for Date of Transaction
    is_Fraud=Column(Integer, nullable=True)     # Creating Column for Fraudulent Transaction Prediction

    def __str__(self):
        return self.type

engine=create_engine('sqlite:///project.sqlite')
Base.metadata.create_all(engine)

