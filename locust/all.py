from locust import HttpUser, task, between, events

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--wordpress-url",
        type=str,
        env_var="WORDPRESS_URL",
        default="http://wordpress.localhost",
        help="Wordpress url"
    )
    parser.add_argument(
        "--redmine-url",
        type=str,
        env_var="REDMINE_URL",
        default="http://redmine.localhost",
        help="Redmine url"
    )
    parser.add_argument(
        "--wagtail-url",
        type=str,
        env_var="WAGTAIL_URL",
        default="http://wagtail.localhost",
        help="Wagtail url"
    )

@events.test_start.add_listener
def _(environment, **kwargs):
    WordPressUser.host = environment.parsed_options.wordpress_url
    RedmineUser.host = environment.parsed_options.redmine_url
    WagtailUser.host = environment.parsed_options.wagtail_url


class WordPressUser(HttpUser):
    host = "http://wordpress.localhost"
    weight = 3
    wait_time = between(1, 3)

    @task(4)
    def homepage(self):
        self.client.get("/", name=f"{self.host}/")

    @task(2)
    def hello_world_post(self):
        self.client.get("/?p=1", name=f"{self.host}/?p=[id]")

    @task(2)
    def rest_api_posts(self):
        self.client.get("/wp-json/wp/v2/posts", name=f"{self.host}/wp-json/wp/v2/posts")

    @task(1)
    def rest_api_pages(self):
        self.client.get("/wp-json/wp/v2/pages", name=f"{self.host}/wp-json/wp/v2/pages")

    @task(1)
    def login_page(self):
        self.client.get("/wp-login.php", name=f"{self.host}/wp-login.php")


class RedmineUser(HttpUser):
    host = "http://redmine.localhost"
    weight = 2
    wait_time = between(1, 4)

    @task(3)
    def homepage(self):
        self.client.get("/", name=f"{self.host}/")

    @task(2)
    def login_page(self):
        self.client.get("/login", name=f"{self.host}/login")

    @task(2)
    def projects(self):
        self.client.get("/projects", name=f"{self.host}/projects")

    @task(1)
    def issues(self):
        self.client.get("/issues", name=f"{self.host}/issues")


class WagtailUser(HttpUser):
    host = "http://wagtail.localhost"
    weight = 2
    wait_time = between(1, 3)

    @task(4)
    def homepage(self):
        self.client.get("/", name=f"{self.host}/")

    @task(3)
    def breads(self):
        self.client.get("/breads/", name=f"{self.host}/breads/")

    @task(2)
    def blog(self):
        self.client.get("/blog/", name=f"{self.host}/blog/")

    @task(1)
    def locations(self):
        self.client.get("/locations/", name=f"{self.host}/locations/")
