class BaseTest:

    def navigate_to(self, page, url):
        page.goto(url)