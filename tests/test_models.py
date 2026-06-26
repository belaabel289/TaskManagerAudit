"""Unit test untuk logika bisnis di models.py.

Test ini tidak menyentuh HTTP/Flask sama sekali — murni menguji
fungsi dan class secara terisolasi (unit testing).
"""
import pytest

from models import (
    TaskStore,
    TaskValidationError,
    validate_task_data,
    filter_tasks,
)


def test_validate_task_data_valid_minimal():
    """Data minimal (hanya title) harus lolos validasi."""
    assert validate_task_data({"title": "Belajar QA"}) is True


def test_validate_task_data_missing_title_raises_error():
    """Tanpa title harus melempar TaskValidationError."""
    with pytest.raises(TaskValidationError):
        validate_task_data({"description": "tanpa judul"})


def test_validate_task_data_invalid_priority_raises_error():
    """Priority di luar low/medium/high harus ditolak."""
    with pytest.raises(TaskValidationError):
        validate_task_data({"title": "Tugas", "priority": "urgent"})


def test_taskstore_create_and_get():
    """Task yang dibuat harus bisa diambil kembali dengan id yang sama."""
    store = TaskStore()
    created = store.create({"title": "Tugas A"})
    fetched = store.get(created["id"])
    assert fetched["title"] == "Tugas A"
    assert fetched["status"] == "todo"


def test_taskstore_update_status():
    """Update status task harus tersimpan dan tervalidasi."""
    store = TaskStore()
    task = store.create({"title": "Tugas B"})
    updated = store.update(task["id"], {"status": "in_progress"})
    assert updated["status"] == "in_progress"


def test_taskstore_update_nonexistent_returns_none():
    """Update task yang tidak ada harus mengembalikan None, bukan error."""
    store = TaskStore()
    result = store.update(999, {"status": "done"})
    assert result is None


def test_taskstore_delete():
    """Task yang dihapus tidak boleh ditemukan lagi."""
    store = TaskStore()
    task = store.create({"title": "Tugas C"})
    assert store.delete(task["id"]) is True
    assert store.get(task["id"]) is None


def test_taskstore_mark_complete():
    """mark_complete harus mengubah status menjadi done."""
    store = TaskStore()
    task = store.create({"title": "Tugas D"})
    result = store.mark_complete(task["id"])
    assert result["status"] == "done"


def test_filter_tasks_by_status_and_keyword():
    """filter_tasks harus menggabungkan filter status + keyword dengan benar."""
    tasks = [
        {
            "id": 1, "title": "Belajar Flask", "description": "",
            "status": "todo", "priority": "high",
        },
        {
            "id": 2, "title": "Belajar Locust", "description": "",
            "status": "done", "priority": "low",
        },
        {
            "id": 3, "title": "Meeting", "description": "bahas Flask",
            "status": "todo", "priority": "medium",
        },
    ]
    result = filter_tasks(tasks, status="todo", keyword="flask")
    ids = sorted(t["id"] for t in result)
    assert ids == [1, 3]