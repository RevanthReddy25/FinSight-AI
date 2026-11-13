from unittest.mock import Mock, patch

import pytest

from app.crud import (
    create_project,
    update_project,
    delete_project
)

from app.schemas import FinancialProjectCreate


# Common test data
def sample_project():
    return FinancialProjectCreate(
        project_name="Test Project",
        client_name="Test Client",
        budget="100000.00",
        revenue="80000.00",
        expenditure="50000.00"
    )


# TEST 1: CREATE - DATABASE FAILURE
def test_create_project_rollback():

    db = Mock()
    db.commit.side_effect = Exception("Database failure")

    with pytest.raises(Exception, match="Database failure"):
        create_project(db, sample_project())

    db.rollback.assert_called_once()


# TEST 2: UPDATE - DATABASE FAILURE
def test_update_project_rollback():

    db = Mock()
    db.commit.side_effect = Exception("Database failure")

    existing_project = Mock()

    with patch(
        "app.crud.get_project",
        return_value=existing_project
    ):

        with pytest.raises(Exception, match="Database failure"):
            update_project(
                db,
                1,
                {"revenue": 90000}
            )

    db.rollback.assert_called_once()


# TEST 3: DELETE - DATABASE FAILURE
def test_delete_project_rollback():

    db = Mock()
    db.commit.side_effect = Exception("Database failure")

    existing_project = Mock()

    with patch(
        "app.crud.get_project",
        return_value=existing_project
    ):

        with pytest.raises(Exception, match="Database failure"):
            delete_project(db, 1)

    db.rollback.assert_called_once()