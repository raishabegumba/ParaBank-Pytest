# """Comprehensive registration page tests covering all scenarios."""
# import pytest
# from playwright.sync_api import Page
# from src.pages.registration_page import RegistrationPage
# from src.utils.wait_helpers import WaitStrategy
# from src.fixtures.test_data_fixtures import security_test_data
# from src.fixtures.test_data_fixtures import user_test_data as user_test_data_fixture
# from src.fixtures.test_data_fixtures import boundary_test_data as boundary_test_data_fixture

# # Backwards/compat: these modules were written to sometimes be used as
# # fixtures (pytest would inject them) and sometimes as plain module data.
# # This test file expects `user_test_data` and `boundary_test_data` as fixtures,
# # so we alias them to fixture-style names.
# user_test_data = user_test_data_fixture
# boundary_test_data = boundary_test_data_fixture
# from src.config.settings import get_settings
# from src.config.logger import log


# @pytest.mark.ui
# @pytest.mark.registration
# @pytest.mark.smoke
# class TestRegistrationComprehensive:
#     """Comprehensive registration page test suite."""
    
#     @pytest.fixture(autouse=True)
#     def setup(self, page: Page):
#         """Setup test instance."""
#         self.registration_page = RegistrationPage(page)
#         self.registration_page.navigate_to_registration()
    
#     @pytest.mark.positive
#     def test_valid_registration(self, user_test_data):
#         """Test registration with valid data."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.complete_registration(
#             first_name=valid_user['first_name'],
#             last_name=valid_user['last_name'],
#             address=valid_user['address'],
#             city=valid_user['city'],
#             state=valid_user['state'],
#             zip_code=valid_user['zip_code'],
#             phone=valid_user['phone'],
#             ssn=valid_user['ssn'],
#             username="newuser123",
#             password="Password123!",
#             confirm_password="Password123!"
#         )
        
#         # Assert
#         self.registration_page.assert_registration_successful()
#         assert self.registration_page.is_registration_successful()
        
#         log.info("Valid registration test passed")
    
#     @pytest.mark.negative
#     @pytest.mark.parametrize("field_to_skip", [
#         "first_name", "last_name", "address", "city", 
#         "state", "zip_code", "phone", "ssn", 
#         "username", "password", "confirm_password"
#     ])
#     def test_missing_required_fields(self, field_to_skip, user_test_data):
#         """Test registration with missing required fields."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act - Skip one required field
#         if field_to_skip == "first_name":
#             self.registration_page.fill_personal_info(
#                 "", valid_user['last_name'], valid_user['address'],
#                 valid_user['city'], valid_user['state'], valid_user['zip_code'],
#                 valid_user['phone'], valid_user['ssn']
#             )
#         elif field_to_skip == "last_name":
#             self.registration_page.fill_personal_info(
#                 valid_user['first_name'], "", valid_user['address'],
#                 valid_user['city'], valid_user['state'], valid_user['zip_code'],
#                 valid_user['phone'], valid_user['ssn']
#             )
#         # ... similar logic for other fields
#         else:
#             # Fill all personal info normally
#             self.registration_page.fill_personal_info(
#                 valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#                 valid_user['city'], valid_user['state'], valid_user['zip_code'],
#                 valid_user['phone'], valid_user['ssn']
#             )
            
#             # Skip account info field
#             if field_to_skip == "username":
#                 self.registration_page.fill_account_info("", "Password123!", "Password123!")
#             elif field_to_skip == "password":
#                 self.registration_page.fill_account_info("newuser123", "", "Password123!")
#             elif field_to_skip == "confirm_password":
#                 self.registration_page.fill_account_info("newuser123", "Password123!", "")
        
#         self.registration_page.click_register_button()
        
#         # Assert
#         self.registration_page.assert_registration_failed()
#         assert not self.registration_page.is_registration_successful()
        
#         log.info(f"Missing required field test passed for: {field_to_skip}")
    
#     @pytest.mark.negative
#     @pytest.mark.parametrize("username,expected_error", [
#         ("", "Username is required"),
#         ("ab", "Username must be at least 3 characters"),
#         ("a" * 51, "Username must be less than 50 characters"),
#         ("john.doe", "Username already exists"),  # Assuming this username exists
#         ("user@name", "Username contains invalid characters"),
#         ("user name", "Username contains invalid characters")
#     ])
#     def test_username_validation(self, username, expected_error):
#         """Test username field validation."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info(username, "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Assert
#         self.registration_page.assert_registration_failed(expected_error)
        
#         log.info(f"Username validation test passed for: {username}")
    
#     @pytest.mark.negative
#     @pytest.mark.parametrize("password,confirm_password,expected_error", [
#         ("", "", "Password is required"),
#         ("pass", "", "Password must be at least 8 characters"),
#         ("Password123!", "DifferentPassword123!", "Passwords do not match"),
#         ("weakpass", "weakpass", "Password must contain uppercase letter"),
#         ("WEAKPASS", "WEAKPASS", "Password must contain lowercase letter"),
#         ("Weakpass", "Weakpass", "Password must contain digit"),
#         ("Weakpass123", "Weakpass123", "Password must contain special character")
#     ])
#     def test_password_validation(self, password, confirm_password, expected_error):
#         """Test password field validation."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info("newuser123", password, confirm_password)
#         self.registration_page.click_register_button()
        
#         # Assert
#         self.registration_page.assert_registration_failed()
        
#         log.info(f"Password validation test passed for: {password[:10]}...")
    
#     @pytest.mark.negative
#     @pytest.mark.parametrize("zip_code,expected_error", [
#         ("", "ZIP code is required"),
#         ("123", "ZIP code must be 5 digits"),
#         ("123456", "ZIP code must be 5 digits"),
#         ("abcde", "ZIP code must contain only digits"),
#         ("12a45", "ZIP code must contain only digits")
#     ])
#     def test_zip_code_validation(self, zip_code, expected_error):
#         """Test ZIP code field validation."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], zip_code,
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info("newuser123", "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Assert
#         self.registration_page.assert_registration_failed()
        
#         log.info(f"ZIP code validation test passed for: {zip_code}")
    
#     @pytest.mark.negative
#     @pytest.mark.parametrize("phone,expected_error", [
#         ("", "Phone number is required"),
#         ("123", "Phone number must be at least 10 digits"),
#         ("abc-123-4567", "Phone number must contain only digits and valid separators"),
#         ("555-123-45678", "Phone number format is invalid")
#     ])
#     def test_phone_validation(self, phone, expected_error):
#         """Test phone number field validation."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             phone, valid_user['ssn']
#         )
#         self.registration_page.fill_account_info("newuser123", "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Assert
#         self.registration_page.assert_registration_failed()
        
#         log.info(f"Phone validation test passed for: {phone}")
    
#     @pytest.mark.negative
#     @pytest.mark.parametrize("ssn,expected_error", [
#         ("", "SSN is required"),
#         ("123", "SSN must be 9 digits"),
#         ("1234567890", "SSN must be 9 digits"),
#         ("abc-45-6789", "SSN must contain only digits and valid separators"),
#         ("123-45-67890", "SSN format is invalid")
#     ])

#     def test_ssn_validation(self, ssn, expected_error):
#         """Test SSN field validation."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], ssn
#         )
#         self.registration_page.fill_account_info("newuser123", "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Assert
#         self.registration_page.assert_registration_failed()
        
#         log.info(f"SSN validation test passed for: {ssn}")
    
#     @pytest.mark.security
#     @pytest.mark.parametrize("malicious_input", security_test_data['xss_payloads'])
#     def test_registration_xss_protection(self, malicious_input):
#         """Test registration XSS protection."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             malicious_input, valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info("newuser123", "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Assert
#         page_content = self.registration_page.page.content()
#         assert "<script>" not in page_content.lower()
        
#         log.info(f"XSS protection test passed for: {malicious_input[:20]}...")
    
#     @pytest.mark.security
#     @pytest.mark.parametrize("sql_payload", security_test_data['sql_injection_payloads'])
#     def test_registration_sql_injection_protection(self, sql_payload):
#         """Test registration SQL injection protection."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info(sql_payload, "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Assert
#         assert not self.registration_page.is_registration_successful()
        
#         log.info(f"SQL injection protection test passed for: {sql_payload[:20]}...")
    
#     @pytest.mark.boundary
#     def test_registration_field_boundaries(self, boundary_test_data):
#         """Test registration field boundary conditions."""
#         # Test maximum length username
#         max_username = "a" * 50
#         valid_user = user_test_data['valid_user']
        
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info(max_username, "Password123!", "Password123!")
#         self.registration_page.click_register_button()
        
#         # Should either succeed or show appropriate error
#         result = self.registration_page.wait_for_registration_complete()
#         assert result, "Registration should complete (success or error)"
        
#         log.info("Registration boundary test passed")
    
#     @pytest.mark.ui
#     def test_registration_page_elements(self):
#         """Test all registration page elements are visible."""
#         # Assert
#         self.registration_page.assert_registration_page_loaded()
        
#         log.info("Registration page elements test passed")
    
#     @pytest.mark.ui
#     def test_form_validation_state(self):
#         """Test form validation state tracking."""
#         # Act
#         validation_state = self.registration_page.validate_required_fields()
        
#         # Assert
#         assert isinstance(validation_state, dict), "Should return validation state dictionary"
#         assert all(isinstance(value, bool) for value in validation_state.values()), "All values should be boolean"
        
#         log.info("Form validation state test passed")
    
#     @pytest.mark.ui
#     def test_password_match_validation(self):
#         """Test password match validation."""
#         # Arrange
#         self.registration_page.fill_account_info("newuser123", "Password123!", "DifferentPassword123!")
        
#         # Act
#         passwords_match = self.registration_page.validate_password_match()
        
#         # Assert
#         assert not passwords_match, "Passwords should not match"
        
#         log.info("Password match validation test passed")
    
#     @pytest.mark.ui
#     def test_clear_registration_form(self):
#         """Test clearing registration form."""
#         # Arrange - Fill form with data
#         valid_user = user_test_data['valid_user']
#         self.registration_page.fill_personal_info(
#             valid_user['first_name'], valid_user['last_name'], valid_user['address'],
#             valid_user['city'], valid_user['state'], valid_user['zip_code'],
#             valid_user['phone'], valid_user['ssn']
#         )
#         self.registration_page.fill_account_info("newuser123", "Password123!", "Password123!")
        
#         # Act
#         self.registration_page.clear_registration_form()
        
#         # Assert - Form should be empty
#         validation_state = self.registration_page.validate_required_fields()
#         assert not any(validation_state.values()), "All fields should be empty"
        
#         log.info("Clear registration form test passed")
    
#     @pytest.mark.ui
#     def test_username_availability_check(self):
#         """Test username availability checking."""
#         # Act
#         is_available = self.registration_page.is_username_available("brandnewuser123456")
        
#         # Assert - Should be available (assuming it doesn't exist)
#         assert isinstance(is_available, bool), "Should return boolean"
        
#         log.info("Username availability check test passed")
    
#     @pytest.mark.ui
#     def test_field_constraints_validation(self):
#         """Test field constraints validation."""
#         # Act
#         constraints = self.registration_page.validate_field_constraints()
        
#         # Assert
#         assert isinstance(constraints, dict), "Should return constraints dictionary"
#         expected_keys = ['zip_code_valid', 'phone_valid', 'ssn_valid', 'username_length_valid', 'password_strength_adequate']
#         assert all(key in constraints for key in expected_keys), "Should contain all constraint checks"
        
#         log.info("Field constraints validation test passed")
    
#     @pytest.mark.performance
#     def test_registration_performance(self, performance_metrics):
#         """Test registration performance."""
#         # Arrange
#         valid_user = user_test_data['valid_user']
        
#         # Act
#         performance_metrics.start_timer("registration")
#         self.registration_page.complete_registration(
#             first_name=valid_user['first_name'],
#             last_name=valid_user['last_name'],
#             address=valid_user['address'],
#             city=valid_user['city'],
#             state=valid_user['state'],
#             zip_code=valid_user['zip_code'],
#             phone=valid_user['phone'],
#             ssn=valid_user['ssn'],
#             username="perfuser123",
#             password="Password123!",
#             confirm_password="Password123!"
#         )
#         registration_complete = self.registration_page.wait_for_registration_complete()
#         performance_metrics.end_timer("registration")
        
#         # Assert
#         assert registration_complete, "Registration should complete within timeout"
        
#         # Check performance
#         registration_duration = performance_metrics.get_average("registration")
#         assert registration_duration < 5.0, f"Registration took {registration_duration}s, should be under 5s"
        
#         log.info(f"Registration performance test passed: {registration_duration:.2f}s")
    
#     @pytest.mark.ui
#     def test_navigation_to_login(self):
#         """Test navigation back to login page."""
#         # Act
#         self.registration_page.click_login_link()
        
#         # Assert
#         current_url = self.registration_page.get_url()
#         assert "index.htm" in current_url or "login" in current_url, "Should navigate to login page"
        
#         log.info("Navigation to login test passed")


# @pytest.mark.ui
# @pytest.mark.registration
# @pytest.mark.mobile
# class TestRegistrationMobile:
#     """Mobile-specific registration tests."""
    
#     def test_mobile_registration_responsive(self, mobile_page: Page):
#         """Test registration on mobile viewport."""
#         # Setup
#         registration_page = RegistrationPage(mobile_page)
#         registration_page.navigate_to_registration()
        
#         # Act
#         valid_user = {
#             'first_name': 'Mobile', 'last_name': 'User', 'address': '123 Mobile St',
#             'city': 'Mobile City', 'state': 'MC', 'zip_code': '12345',
#             'phone': '555-123-4567', 'ssn': '123-45-6789'
#         }
        
#         registration_page.fill_personal_info(**valid_user)
#         registration_page.fill_account_info("mobileuser123", "Password123!", "Password123!")
#         registration_page.click_register_button()
        
#         # Assert
#         registration_complete = registration_page.wait_for_registration_complete()
#         assert registration_complete, "Mobile registration should complete"
        
#         log.info("Mobile registration test passed")
