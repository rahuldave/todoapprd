# test_app.py
from unittest.mock import patch

from flask import json


def test_index(client):
    with patch("todoapp.app.render_template") as mock_render_template:
        mock_render_template.return_value = "mocked todos.html"
        response = client.get("/")
        assert response.status_code == 200
        assert b"mocked todos.html" in response.data


def test_manage_todos_get(client):
    response = client.get("/todos")
    data = json.loads(response.data)

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["task"] == "Task 1"
    assert data[0]["done"] == 0
    assert data[1]["task"] == "Task 2"
    assert data[1]["done"] == 1


def test_manage_todos_post(client):
    response = client.post("/todos", json={"task": "New Task", "category_id": 1})
    data = json.loads(response.data)

    assert response.status_code == 201
    assert data is not None
    assert isinstance(data, int)  # Check if response is an integer (last inserted ID)


def test_manage_categories_get(client):
    response = client.get("/categories")
    data = json.loads(response.data)

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == "Work"
    assert data[1]["name"] == "Home"


def test_manage_categories_post(client):
    response = client.post("/categories", json={"name": "New Category"})
    data = json.loads(response.data)

    assert response.status_code == 201
    assert data is not None
    assert isinstance(data, int)  # Check if response is an integer (last inserted ID)


def test_toggle_todo(client):
    response = client.post("/toggle-todo/1")
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data is True  # Check if the task is marked as done

    # Check if the task is actually updated in the database
    response = client.get("/todos")
    todos = json.loads(response.data)
    assert todos[0]["done"] == 1  # Check if the 'done' status is updated
