"""Modul model dan logika bisnis untuk Task Manager.

Berisi penyimpanan task (in-memory), validasi data, dan fungsi
pencarian/filter yang dipisah dari layer Flask agar mudah diuji
secara unit (tanpa perlu HTTP client).
"""

VALID_PRIORITIES = ("low", "medium", "high")
VALID_STATUSES = ("todo", "in_progress", "done")


class TaskValidationError(Exception):
    """Dilempar saat data task yang dikirim user tidak valid."""


class TaskStore:
    """Penyimpanan task in-memory dengan operasi CRUD dasar."""

    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def create(self, data):
        validate_task_data(data)
        task_id = self._next_id
        task = {
            "id": task_id,
            "title": data["title"].strip(),
            "description": data.get("description", "").strip(),
            "priority": data.get("priority", "medium"),
            "status": data.get("status", "todo"),
        }
        self._tasks[task_id] = task
        self._next_id += 1
        return task

    def get(self, task_id):
        return self._tasks.get(task_id)

    def list_all(self):
        return list(self._tasks.values())

    def update(self, task_id, data):
        task = self._tasks.get(task_id)
        if task is None:
            return None

        if "title" in data:
            if not data["title"] or not data["title"].strip():
                raise TaskValidationError("title tidak boleh kosong")
            task["title"] = data["title"].strip()

        if "description" in data:
            task["description"] = data["description"].strip()

        if "priority" in data:
            if data["priority"] not in VALID_PRIORITIES:
                raise TaskValidationError("priority tidak valid")
            task["priority"] = data["priority"]

        if "status" in data:
            if data["status"] not in VALID_STATUSES:
                raise TaskValidationError("status tidak valid")
            task["status"] = data["status"]

        return task

    def delete(self, task_id):
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def mark_complete(self, task_id):
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task["status"] = "done"
        return task


def validate_task_data(data):
    """Validasi payload pembuatan task.

    Fungsi ini sengaja dibuat dengan beberapa percabangan agar dapat
    dipakai sebagai contoh perhitungan Cyclomatic Complexity.
    """
    if not isinstance(data, dict):
        raise TaskValidationError("payload harus berupa object JSON")

    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        raise TaskValidationError("title wajib diisi dan berupa string")

    priority = data.get("priority", "medium")
    if priority not in VALID_PRIORITIES:
        raise TaskValidationError(
            "priority harus salah satu dari: " + ", ".join(VALID_PRIORITIES)
        )

    status = data.get("status", "todo")
    if status not in VALID_STATUSES:
        raise TaskValidationError(
            "status harus salah satu dari: " + ", ".join(VALID_STATUSES)
        )

    return True


def filter_tasks(tasks, status=None, priority=None, keyword=None):
    """Filter daftar task berdasarkan status, priority, dan/atau kata kunci.

    Beberapa percabangan independen di sini juga representatif untuk
    pengukuran Cyclomatic Complexity pada laporan audit.
    """
    result = tasks

    if status is not None:
        result = [t for t in result if t["status"] == status]

    if priority is not None:
        result = [t for t in result if t["priority"] == priority]

    if keyword:
        keyword_lower = keyword.lower()
        filtered = []
        for task in result:
            in_title = keyword_lower in task["title"].lower()
            in_desc = keyword_lower in task.get("description", "").lower()
            if in_title or in_desc:
                filtered.append(task)
        result = filtered

    return result
