"""Aplikasi Task Manager berbasis Flask.

Endpoint:
    GET    /tasks            -> daftar task (bisa difilter via query param)
    POST   /tasks             -> buat task baru
    GET    /tasks/<id>        -> detail satu task
    PUT    /tasks/<id>        -> update task
    DELETE /tasks/<id>        -> hapus task
    PATCH  /tasks/<id>/complete -> tandai task selesai
"""
from flask import Flask, jsonify, request

from models import TaskStore, TaskValidationError, filter_tasks

app = Flask(__name__)
store = TaskStore()


@app.route("/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    priority = request.args.get("priority")
    keyword = request.args.get("q")

    tasks = store.list_all()
    tasks = filter_tasks(
        tasks, status=status, priority=priority, keyword=keyword
    )
    return jsonify(tasks=tasks, total=len(tasks))


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    try:
        task = store.create(data)
    except TaskValidationError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = store.get(task_id)
    if task is None:
        return jsonify(error="Task tidak ditemukan"), 404
    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    try:
        task = store.update(task_id, data)
    except TaskValidationError as exc:
        return jsonify(error=str(exc)), 400
    if task is None:
        return jsonify(error="Task tidak ditemukan"), 404
    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    deleted = store.delete(task_id)
    if not deleted:
        return jsonify(error="Task tidak ditemukan"), 404
    return jsonify(message="Task berhasil dihapus")


@app.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    task = store.mark_complete(task_id)
    if task is None:
        return jsonify(error="Task tidak ditemukan"), 404
    return jsonify(task)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)