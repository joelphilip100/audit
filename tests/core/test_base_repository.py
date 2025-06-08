import pytest
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.core.base_repository import BaseRepository
from app.database import Base


class CreateSchema(BaseModel):
    name: str


class UpdateSchema(BaseModel):
    name: str


class FakeModel(Base):
    __tablename__ = "fake_table"
    fake_id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, nullable=False)


class FakeRepository(BaseRepository[FakeModel, CreateSchema, UpdateSchema]):
    pass


@pytest.fixture
def repo():
    return FakeRepository(FakeModel, "fake_id")


def test_get_all(repo, test_db):
    assert repo.get_all(test_db) == []


def test_get_all_with_data(repo, test_db):
    repo.create(FakeModel(name="John Doe"), test_db)
    repo.create(FakeModel(name="Jane Doe"), test_db)
    result = repo.get_all(test_db)
    assert result[0].name == "John Doe"
    assert result[1].name == "Jane Doe"


def test_create(repo, test_db):
    result = repo.create(FakeModel(name="Person 2"), test_db)
    assert result.name == "Person 2"


def test_create_duplicate(repo, test_db):
    repo.create(FakeModel(name="Person 3"), test_db)
    with pytest.raises(IntegrityError) as exc_info:
        repo.create(FakeModel(name="Person 3"), test_db)
    assert "UNIQUE constraint failed: fake_table.name" in str(exc_info.value)


def test_create_invalid_data(repo, test_db):
    with pytest.raises(IntegrityError) as exc_info:
        repo.create(FakeModel(name=None), test_db)
    assert "NOT NULL constraint failed: fake_table.name" in str(exc_info.value)


def test_update(repo, test_db):
    created_result = repo.create(FakeModel(name="Person 4"), test_db)
    created_result.name = "Person 5"
    result = repo.update(created_result, test_db)
    assert result.name == "Person 5"


def test_update_invalid_data(repo, test_db):
    created_result = repo.create(FakeModel(name="Person 6"), test_db)
    created_result.name = None
    with pytest.raises(IntegrityError) as exc_info:
        repo.update(created_result, test_db)
    assert "NOT NULL constraint failed: fake_table.name" in str(exc_info.value)


def test_update_without_changes(repo, test_db):
    created_result = repo.create(FakeModel(name="Person 7"), test_db)
    result = repo.update(created_result, test_db)
    assert result.name == "Person 7"


def test_update_unique_constraint(repo, test_db):
    repo.create(FakeModel(name="Person 8"), test_db)
    created_result = repo.create(FakeModel(name="Person 9"), test_db)
    created_result.name = "Person 8"
    with pytest.raises(IntegrityError) as exc_info:
        repo.update(created_result, test_db)
    assert "UNIQUE constraint failed: fake_table.name" in str(exc_info.value)


def test_delete(repo, test_db):
    created_result = repo.create(FakeModel(name="Person 10"), test_db)
    repo.delete(created_result, test_db)
    result = repo.get_by_field("fake_id", created_result.fake_id, test_db)
    assert result is None


def test_delete_not_found(repo, test_db):
    with pytest.raises(InvalidRequestError):
        repo.delete(FakeModel(fake_id=1000), test_db)


def test_get_by_field(repo, test_db):
    created_result = repo.create(FakeModel(name="Person 11"), test_db)
    result = repo.get_by_field("fake_id", created_result.fake_id, test_db)
    assert result.name == "Person 11"


def test_get_by_field_not_found(repo, test_db):
    result = repo.get_by_field("fake_id", 1000, test_db)
    assert result is None


def test_get_by_field_invalid_field(repo, test_db):
    with pytest.raises(AttributeError) as exc_info:
        repo.get_by_field("invalid_field", 1000, test_db)

    assert "FakeModel has no field 'invalid_field'" in str(exc_info.value)
