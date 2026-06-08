"""Database configuration for TimescaleDB telemetry ingestion."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def init_db() -> None:
    """Create telemetry tables and Timescale hypertables when available."""
    from backend.models.telemetry import BatteryTelemetry, ECGTelemetry, GlucoseTelemetry
    from backend.models.doctor import Doctor
    from backend.models.patient import Patient

    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        try:
            connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        except Exception:
            pass

        for table in (
            ECGTelemetry.__tablename__,
            GlucoseTelemetry.__tablename__,
            BatteryTelemetry.__tablename__,
        ):
            try:
                connection.exec_driver_sql(
                    f"SELECT create_hypertable('{table}', 'timestamp', if_not_exists => TRUE);"
                )
            except Exception:
                # SQLite/local Postgres without TimescaleDB can still run the demo.
                pass

    print("Database tables created")


def get_db():
    """FastAPI dependency for a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
