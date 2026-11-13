from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialProject
from app.schemas import FinancialProjectCreate


# 1. CREATE
def create_project(
    db: Session,
    project: FinancialProjectCreate
) -> FinancialProject:

    db_project = FinancialProject(
        project_name=project.project_name,
        client_name=project.client_name,
        budget=project.budget,
        revenue=project.revenue,
        expenditure=project.expenditure
    )

    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

    except Exception:
        db.rollback()
        raise

    return db_project


# 2. READ ALL
def get_projects(
    db: Session
) -> list[FinancialProject]:

    statement = select(FinancialProject)

    return list(db.scalars(statement).all())


# 3. READ ONE
def get_project(
    db: Session,
    project_id: int
) -> FinancialProject | None:

    statement = select(FinancialProject).where(
        FinancialProject.project_id == project_id
    )

    return db.scalar(statement)


# 4. UPDATE
def update_project(
    db: Session,
    project_id: int,
    updated_data: dict
) -> FinancialProject | None:

    db_project = get_project(db, project_id)

    if db_project is None:
        return None

    for field, value in updated_data.items():
        setattr(db_project, field, value)

    try:
        db.commit()
        db.refresh(db_project)

    except Exception:
        db.rollback()
        raise

    return db_project


# 5. DELETE
def delete_project(
    db: Session,
    project_id: int
) -> bool:

    db_project = get_project(db, project_id)

    if db_project is None:
        return False

    try:
        db.delete(db_project)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return True