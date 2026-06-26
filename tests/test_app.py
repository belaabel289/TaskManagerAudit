"""Integration test untuk endpoint Flask Task Manager.

Test ini memanggil endpoint HTTP secara end-to-end menggunakan Flask
test client (request -> routing -> business logic -> response),
berbeda dari unit test yang hanya menguji fungsi murni.
"""
import pytest

import app as app_module


@pytest.fixture
def client():
    """Sediakan Flask test client dengan storage yang bersih per test."""
    app_module.app.config["TESTING"] = True
    app_module.store = app_module.TaskStore()
    with app_module.app.test_client() as test_client:
        yield test_client


def test_create_task_returns_201(client):
    response = client.post("/tasks", json={"title": "Integrasi A"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "Integrasi A"


def test_create_task_without_title_returns_400(client):
    response = client.post("/tasks", json={"description": "tanpa judul"})
    assert response.status_code == 400


def test_list_tasks_returns_created_task(client):
    client.post("/tasks", json={"title": "Integrasi B"})
    response = client.get("/tasks")
    body = response.get_json()
    assert response.status_code == 200
    assert body["total"] == 1


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_complete_task_flow(client):
    """Skenario end-to-end.

    Buat task, tandai selesai, lalu verifikasi status.
    """
    created = client.post("/tasks", json={"title": "Integrasi C"}).get_json()
    response = client.patch(f"/tasks/{created['id']}/complete")
    assert response.status_code == 200
    assert response.get_json()["status"] == "done"


def test_update_task_priority(client):
    created = client.post("/tasks", json={"title": "Integrasi E"}).get_json()
    response = client.put(
        f"/tasks/{created['id']}", json={"priority": "high"}
    )
    assert response.status_code == 200
    assert response.get_json()["priority"] == "high"


def test_update_task_invalid_priority_returns_400(client):
    created = client.post("/tasks", json={"title": "Integrasi F"}).get_json()
    response = client.put(
        f"/tasks/{created['id']}", json={"priority": "urgent"}
    )
    assert response.status_code == 400


def test_delete_task_then_get_returns_404(client):
    created = client.post("/tasks", json={"title": "Integrasi D"}).get_json()
    delete_response = client.delete(f"/tasks/{created['id']}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404
