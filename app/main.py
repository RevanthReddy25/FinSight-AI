from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.schemas import FinancialProjectAnalytics

from app import crud
from app.database import get_db

from app.schemas import (
    FinancialProjectCreate,
    FinancialProjectResponse,
    FinancialProjectUpdate,
)


app = FastAPI(
    title="FinSight-AI API",
    description="Financial Project Management API",
    version="2.0.0"
)


# CREATE: Add a new financial project
@app.post(
    "/projects/",
    response_model=FinancialProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    project: FinancialProjectCreate,
    db: Session = Depends(get_db)
):
    return crud.create_project(db, project)


# READ: Retrieve all financial projects
@app.get(
    "/projects/",
    response_model=list[FinancialProjectResponse]
)
def read_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)


# READ: Retrieve one financial project
@app.get(
    "/projects/{project_id}",
    response_model=FinancialProjectResponse
)
def read_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial project not found"
        )

    return project


# UPDATE: Modify an existing financial project
@app.patch(
    "/projects/{project_id}",
    response_model=FinancialProjectResponse
)
def update_project(
    project_id: int,
    project: FinancialProjectUpdate,
    db: Session = Depends(get_db)
):
    updated_data = project.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not updated_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided for updating"
        )

    updated_project = crud.update_project(
        db,
        project_id,
        updated_data
    )

    if updated_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial project not found"
        )

    return updated_project


# DELETE: Remove a financial project
@app.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_project(db, project_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial project not found"
        )

    return None

@app.get(
    "/projects/{project_id}/analytics",
    response_model=FinancialProjectAnalytics
)
def read_project_analytics(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return services.get_project_analytics(project)