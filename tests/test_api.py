def sample_project():
    return {
        "project_name": "Investment Analytics",
        "client_name": "XYZ Financial Services",
        "budget": "750000.00",
        "revenue": "680000.00",
        "expenditure": "420000.00"
    }


# TEST 1: CREATE PROJECT
def test_create_project(client):

    response = client.post(
        "/projects/",
        json=sample_project()
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_name"] == "Investment Analytics"
    assert data["client_name"] == "XYZ Financial Services"
    assert data["budget"] == "750000.00"
    assert data["project_id"] > 0


# TEST 2: GET ALL PROJECTS
def test_get_all_projects(client):

    client.post("/projects/", json=sample_project())

    response = client.get("/projects/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


# TEST 3: GET PROJECT BY ID
def test_get_project_by_id(client):

    create_response = client.post(
        "/projects/",
        json=sample_project()
    )

    project_id = create_response.json()["project_id"]

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 200
    assert response.json()["project_id"] == project_id


# TEST 4: UPDATE PROJECT
def test_update_project(client):

    create_response = client.post(
        "/projects/",
        json=sample_project()
    )

    project_id = create_response.json()["project_id"]

    update_data = {
        "revenue": "800000.00"
    }

    response = client.patch(
        f"/projects/{project_id}",
        json=update_data
    )

    assert response.status_code == 200
    assert response.json()["revenue"] == "800000.00"


# TEST 5: DELETE PROJECT
def test_delete_project(client):

    create_response = client.post(
        "/projects/",
        json=sample_project()
    )

    project_id = create_response.json()["project_id"]

    response = client.delete(
        f"/projects/{project_id}"
    )

    assert response.status_code == 204

    # Verify that the project no longer exists
    get_response = client.get(
        f"/projects/{project_id}"
    )

    assert get_response.status_code == 404


# TEST 6: PROJECT NOT FOUND
def test_project_not_found(client):

    response = client.get("/projects/99999")

    assert response.status_code == 404


# TEST 7: NEGATIVE BUDGET VALIDATION
def test_negative_budget(client):

    project_data = sample_project()
    project_data["budget"] = "-5000.00"

    response = client.post(
        "/projects/",
        json=project_data
    )

    assert response.status_code == 422


# TEST 8: EMPTY UPDATE VALIDATION
def test_empty_update(client):

    create_response = client.post(
        "/projects/",
        json=sample_project()
    )

    project_id = create_response.json()["project_id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={}
    )

    assert response.status_code == 422

def test_get_empty_projects(client):

    response = client.get("/projects/")

    assert response.status_code == 200
    assert response.json() == []

def test_update_nonexistent_project(client):

    response = client.patch(
        "/projects/99999",
        json={"revenue": "500000.00"}
    )

    assert response.status_code == 404

def test_delete_nonexistent_project(client):

    response = client.delete("/projects/99999")

    assert response.status_code == 404

def test_invalid_project_id(client):

    response = client.get("/projects/invalid")

    assert response.status_code == 422
