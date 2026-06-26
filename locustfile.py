"""Locust load test untuk Task Manager API.

Mensimulasikan pengguna yang membuat, membaca, mengupdate, dan
menyelesaikan task -- merepresentasikan pola pemakaian nyata,
bukan cuma satu endpoint statis.
"""

import random

from locust import HttpUser, task, between


class TaskManagerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.created_ids = []

    @task(3)
    def list_tasks(self):
        self.client.get("/tasks")

    @task(2)
    def create_task(self):
        response = self.client.post(
            "/tasks",
            json={
                "title": f"Task {random.randint(1, 100000)}",
                "priority": random.choice(["low", "medium", "high"]),
            },
        )
        if response.status_code == 201:
            self.created_ids.append(response.json()["id"])

    @task(2)
    def get_task(self):
        if self.created_ids:
            task_id = random.choice(self.created_ids)
            self.client.get(f"/tasks/{task_id}")

    @task(1)
    def complete_task(self):
        if self.created_ids:
            task_id = random.choice(self.created_ids)
            self.client.patch(f"/tasks/{task_id}/complete")
