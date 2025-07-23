from sqlalchemy import JSON, Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

Base = declarative_base()


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    time = Column(Integer, nullable=False, index=True)  # Unix timestamp
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    avg = Column(Float, nullable=False)
    sale = Column(Float, nullable=False)
    meta = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Stock(ticker='{self.ticker}', time={self.time}, high={self.high}, low={self.low})>"


engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def get_session():
    return Session()

