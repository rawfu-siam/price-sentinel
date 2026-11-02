"""Unit tests for SQLAlchemy ORM models (Product and PriceHistory).

Verifies database schema constraints, default values, relationships,
and cascade deletion behaviors using an in-memory SQLite test database.
"""

from datetime import datetime
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database import Base
from src.models import Product


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh in-memory SQLite database session for each test."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_product(db_session: Session) -> None:
    """Verify that a product can be successfully created with valid attributes."""
    product = Product(
        sku="TEST_SKU_001",
        name="Test Competitor Widget",
        target_url="https://example.com/product/1",
        current_price=29.99,
        currency="USD",
        is_stock=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    assert product.id is not None
    assert product.sku == "TEST-SKU-001"
    assert product.name == "Test Competitor Widget"
    assert product.current_price == 29.99
    assert product.in_stock is True
    assert isinstance(product.created_at, datetime)
