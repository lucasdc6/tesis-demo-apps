from locust import HttpUser, task, between


class WagtailUser(HttpUser):
    """
    Simula un usuario navegando Wagtail (bakerydemo).
    Ejecutar con: --host=http://wagtail.localhost
    """

    wait_time = between(1, 3)

    @task(4)
    def homepage(self):
        self.client.get("/")

    @task(3)
    def breads(self):
        self.client.get("/breads/")

    @task(2)
    def blog(self):
        self.client.get("/blog/")

    @task(1)
    def locations(self):
        self.client.get("/locations/")
