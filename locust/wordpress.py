from locust import HttpUser, task, between


class WordPressUser(HttpUser):
    """
    Simula un usuario navegando WordPress.
    Ejecutar con: --host=http://wordpress.localhost
    """

    wait_time = between(1, 3)

    @task(4)
    def homepage(self):
        self.client.get("/")

    @task(2)
    def hello_world_post(self):
        # WordPress siempre crea el post "Hello World!" con ID 1
        self.client.get("/?p=1", name="/?p=[id]")

    @task(2)
    def rest_api_posts(self):
        # La REST API genera trazas con consultas a la base de datos
        self.client.get("/wp-json/wp/v2/posts")

    @task(1)
    def rest_api_pages(self):
        self.client.get("/wp-json/wp/v2/pages")

    @task(1)
    def login_page(self):
        self.client.get("/wp-login.php")
