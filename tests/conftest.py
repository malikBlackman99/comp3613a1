from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models
from app.database import get_session
from app.main import app
from app.models.user import User


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine) -> Iterator[Session]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_engine) -> Iterator[TestClient]:
    original_overrides = app.dependency_overrides.copy()

    def override_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture
def accounts(db_session: Session) -> dict[str, User]:
    landlord = User(
        username="landlord-test",
        email="landlord-test@example.com",
        password="not-used",
        role="regular_user",
    )
    student = User(
        username="student-test",
        email="student-test@example.com",
        password="not-used",
        role="regular_user",
    )
    admin = User(
        username="admin-test",
        email="admin-test@example.com",
        password="not-used",
        role="admin",
    )
    db_session.add_all([landlord, student, admin])
    db_session.commit()
    for user in (landlord, student, admin):
        db_session.refresh(user)
    return {"landlord": landlord, "student": student, "admin": admin}
