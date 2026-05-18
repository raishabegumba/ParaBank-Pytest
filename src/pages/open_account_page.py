from src.pages.base_page import BasePage
from src.config.logger import log


class OpenAccountPage(BasePage):

    ACCOUNT_TYPE_SELECT = "#type"
    SOURCE_ACCOUNT_SELECT = "#fromAccountId"
    OPEN_BUTTON = "input[value='Open New Account']"

    OPEN_ACCOUNT_URL = "http://localhost:8080/parabank/openaccount.htm"

    def navigate_to_open_account(self):
        """Navigate to Open Account page (FIXED: absolute URL required)."""
        self.goto(self.OPEN_ACCOUNT_URL)
        self.assert_open_account_page_loaded()

    def assert_open_account_page_loaded(self):
        self.wait_for_element(self.ACCOUNT_TYPE_SELECT)
        self.wait_for_element(self.SOURCE_ACCOUNT_SELECT)
        self.wait_for_element(self.OPEN_BUTTON)
        log.info("Open Account page loaded successfully")

    def get_account_types(self):
        self.wait_for_element(self.ACCOUNT_TYPE_SELECT)
        return [
            t.strip()
            for t in self.page.locator(f"{self.ACCOUNT_TYPE_SELECT} option").all_text_contents()
            if t.strip()
        ]

    def get_source_accounts(self):
        self.wait_for_element(self.SOURCE_ACCOUNT_SELECT)
        return [
            a.strip()
            for a in self.page.locator(f"{self.SOURCE_ACCOUNT_SELECT} option").all_text_contents()
            if a.strip()
        ]

    def select_account_type(self, account_type: str):
        self.page.locator(self.ACCOUNT_TYPE_SELECT).select_option(label=account_type)
        log.info(f"Selected account type: {account_type}")

    def select_source_account(self, account: str):
        self.page.locator(self.SOURCE_ACCOUNT_SELECT).select_option(label=account)
        log.info(f"Selected source account: {account}")

    def click_open_new_account(self):
        self.click(self.OPEN_BUTTON)

    def is_account_opened_successfully(self) -> bool:
        return "Account Opened" in self.page.content()

    def simulate_account_opening_with_validation(self, account_type: str, source_account: str):
        """Full flow used by tests."""
        try:
            self.select_account_type(account_type)
            self.select_source_account(source_account)
            self.click_open_new_account()

            return {
                "success": self.is_account_opened_successfully(),
                "error_message": None if self.is_account_opened_successfully()
                else "Account creation failed"
            }

        except Exception as e:
            log.error(f"Account opening failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }