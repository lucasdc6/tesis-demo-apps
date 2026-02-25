from locust import HttpUser, task, between


class WordPressUser(HttpUser):
    host = "http://wordpress.localhost"
    weight = 3
    wait_time = between(1, 3)

    @task(4)
    def homepage(self):
        self.client.get("/")

    @task(2)
    def hello_world_post(self):
        self.client.get("/?p=1", name="/?p=[id]")

    @task(2)
    def rest_api_posts(self):
        self.client.get("/wp-json/wp/v2/posts")

    @task(1)
    def rest_api_pages(self):
        self.client.get("/wp-json/wp/v2/pages")

    @task(1)
    def login_page(self):
        self.client.get("/wp-login.php")


class RedmineUser(HttpUser):
    host = "http://redmine.localhost"
    weight = 2
    wait_time = between(1, 4)

    @task(3)
    def homepage(self):
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


class WagtailUser(HttpUser):
    host = "http://wagtail.localhost"
    weight = 2
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
