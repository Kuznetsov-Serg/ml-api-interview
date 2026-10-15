from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(36), index=True, unique=True)
    input_data = Column(JSON)
    prediction = Column(Integer)
    probability = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

async def get_db_session(database_url: str = None):
    from app.config import get_settings
    url = database_url or get_settings().DATABASE_URL
    engine = create_async_engine(url, pool_size=10, max_overflow=20, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine, session_factory

async def save_prediction(db_engine, session_factory, request_id, input_data, prediction):
    async with session_factory() as session:
        record = PredictionRecord(
            request_id=request_id,
            input_data=input_data,
            prediction=prediction["prediction"],
            probability=prediction["probability"]
        )
        session.add(record)
        await session.commit()