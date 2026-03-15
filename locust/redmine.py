from locust import HttpUser, task, between


class RedmineUser(HttpUser):
    """
    Simula un usuario navegando Redmine.
    Ejecutar con: --host=http://redmine.localhost
    """

    wait_time = between(1, 4)

    @task(3)
    def homepage(self):
        # Redirige a /login si no está autenticado; genera trazas de todos modos
        self.client.get("/", name="/")

    @task(2)
    def login_page(self):
        self.client.get("/login")

    @task(2)
    def projects(self):
        self.client.get("/projects")

    @task(1)
    def issues(self):
        self.client.get("/issues")
