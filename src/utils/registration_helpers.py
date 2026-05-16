class RegistrationHelpers:
    """High-level registration workflows."""

    @staticmethod
    def register_user(page_obj, user_data):
        page_obj.navigate_to_registration()
        page_obj.fill_personal_info(
            user_data["first_name"],
            user_data["last_name"],
            user_data["address"],
            user_data["city"],
            user_data["state"],
            user_data["zip_code"],
            user_data["phone"],
            user_data["ssn"]
        )
        page_obj.fill_account_info(
            user_data["username"],
            user_data["password"],
            user_data["confirm_password"]
        )
        page_obj.click_register_button()