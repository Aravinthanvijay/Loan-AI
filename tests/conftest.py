"""
Pytest fixtures shared across all test files.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_application_data():
    """Sample valid loan application data for testing."""
    return {
        "user_id": "user123",
        "full_name": "RAHUL KUMAR SHARMA",
        "age": 35,
        "pan_number": "ABCPA1234Z",
        "phone": "9876543210",
        "email": "rahul@example.com",
        "monthly_income": 75000.0,
        "employment_type": "salaried",
        "employer_name": "Infosys Limited",
        "years_employed": 5.0,
        "loan_amount": 500000.0,
        "loan_purpose": "personal",
        "existing_loans": 1,
        "existing_emi": 10000.0,
        "pan_document": {"file_path": "tests/fixtures/sample_pan.jpg", "filename": "pan.jpg", "file_type": "image/jpeg", "file_size": 50000},
        "salary_document": {"file_path": "tests/fixtures/sample_salary.jpg", "filename": "salary.jpg", "file_type": "image/jpeg", "file_size": 50000},
    }


@pytest.fixture
def blacklisted_application_data(sample_application_data):
    data = sample_application_data.copy()
    data["pan_number"] = "BLKST1234X"  # Blacklisted PAN
    return data


@pytest.fixture
def mock_db(monkeypatch):
    """Mock MongoDB operations."""
    mock = AsyncMock()
    monkeypatch.setattr("backend.db.repositories.blacklist_repo.BlacklistRepository.is_blacklisted",
                       AsyncMock(return_value=False))
    monkeypatch.setattr("backend.db.repositories.application_repo.ApplicationRepository.check_duplicate_application",
                       AsyncMock(return_value=False))
    return mock