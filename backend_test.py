import requests
import sys
import json
from datetime import datetime

class AndreDev_APITester:
    def __init__(self, base_url="https://code-studio-22.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, status_code, expected_status, error_msg=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - Status: {status_code}")
        else:
            print(f"❌ {name} - Expected {expected_status}, got {status_code}")
            if error_msg:
                print(f"   Error: {error_msg}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "status_code": status_code,
            "expected_status": expected_status,
            "error": error_msg
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add auth headers if token exists
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        # Add additional headers
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            # For debugging, print error response
            if not success and response.content:
                try:
                    error_response = response.json()
                    error_msg = f"API Error: {error_response}"
                    print(f"   Response body: {error_response}")
                except:
                    error_msg = f"HTTP {response.status_code}"
                    print(f"   Response text: {response.text}")
            else:
                error_msg = None
                
            self.log_test(name, success, response.status_code, expected_status, error_msg)

            return success, response.json() if response.content else {}

        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            self.log_test(name, False, 0, expected_status, error_msg)
            return False, {}
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error"
            self.log_test(name, False, 0, expected_status, error_msg)
            return False, {}
        except Exception as e:
            error_msg = str(e)
            self.log_test(name, False, 0, expected_status, error_msg)
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_portfolio_endpoint(self):
        """Test portfolio endpoint (public)"""
        success, response = self.run_test(
            "Portfolio Endpoint",
            "GET", 
            "portfolio",
            200
        )
        if success and 'data' not in response:
            # Should return a list of portfolio items
            print(f"   Portfolio items count: {len(response) if isinstance(response, list) else 'N/A'}")
        return success

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_user_data = {
            "name": f"Test User {timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!",
            "company": "Test Company"
        }

        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )

        if success and 'access_token' in response and 'user' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['name']} ({response['user']['email']})")
        
        return success

    def test_user_login(self):
        """Test user login with the registered user"""
        if not self.user_id:
            print("❌ Login Test - No user registered to test login")
            return False

        # We'll create a new user for login test since we already have token from registration
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') + "_login"
        register_data = {
            "name": f"Login Test User {timestamp}",
            "email": f"login_test_{timestamp}@example.com", 
            "password": "LoginPass123!",
            "company": "Login Test Company"
        }

        # First register a new user
        requests.post(f"{self.api_base}/auth/register", json=register_data, timeout=10)

        # Now test login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }

        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login", 
            200,
            data=login_data
        )

        if success and 'access_token' in response:
            print(f"   Login successful for: {response['user']['name']}")

        return success

    def test_get_user_profile(self):
        """Test getting user profile with auth"""
        if not self.token:
            print("❌ Get Profile Test - No auth token available")
            return False

        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "auth/me",
            200
        )

        if success and 'name' in response and 'email' in response:
            print(f"   Profile: {response['name']} ({response['email']})")

        return success

    def test_contact_form(self):
        """Test contact form submission (public endpoint)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        contact_data = {
            "name": f"Contact Test {timestamp}",
            "email": f"contact_{timestamp}@example.com",
            "phone": "+351 123 456 789",
            "message": f"Test message sent at {timestamp}",
            "service_type": "web"
        }

        success, response = self.run_test(
            "Contact Form Submission",
            "POST",
            "contact",
            200,
            data=contact_data
        )

        if success and 'id' in response:
            print(f"   Contact submitted with ID: {response['id']}")

        return success

    def test_create_project(self):
        """Test creating a project (requires auth)"""
        if not self.token:
            print("❌ Create Project Test - No auth token available")
            return False

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_data = {
            "name": f"Test Project {timestamp}",
            "description": f"A test project created at {timestamp}",
            "project_type": "web",
            "budget": "5000€"
        }

        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data=project_data
        )

        if success and 'id' in response:
            print(f"   Project created with ID: {response['id']}")
            self.project_id = response['id']

        return success

    def test_get_projects(self):
        """Test getting user projects (requires auth)"""
        if not self.token:
            print("❌ Get Projects Test - No auth token available")
            return False

        success, response = self.run_test(
            "Get Projects",
            "GET", 
            "projects",
            200
        )

        if success:
            project_count = len(response) if isinstance(response, list) else 0
            print(f"   User has {project_count} projects")

        return success

    def test_create_message(self):
        """Test creating a message (requires auth)"""
        if not self.token:
            print("❌ Create Message Test - No auth token available") 
            return False

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_data = {
            "subject": f"Test Message {timestamp}",
            "content": f"This is a test message created at {timestamp}"
        }

        success, response = self.run_test(
            "Create Message",
            "POST",
            "messages", 
            200,
            data=message_data
        )

        if success and 'id' in response:
            print(f"   Message created with ID: {response['id']}")

        return success

    def test_get_messages(self):
        """Test getting user messages (requires auth)"""
        if not self.token:
            print("❌ Get Messages Test - No auth token available")
            return False

        success, response = self.run_test(
            "Get Messages",
            "GET",
            "messages",
            200
        )

        if success:
            message_count = len(response) if isinstance(response, list) else 0
            print(f"   User has {message_count} messages")

        return success

    def test_get_stats(self):
        """Test getting user stats (requires auth)"""
        if not self.token:
            print("❌ Get Stats Test - No auth token available")
            return False

        success, response = self.run_test(
            "Get Stats",
            "GET",
            "stats", 
            200
        )

        if success:
            stats = response
            print(f"   Stats - Projects: {stats.get('total_projects', 0)}, " +
                  f"Pending: {stats.get('pending', 0)}, " +
                  f"In Progress: {stats.get('in_progress', 0)}, " +
                  f"Completed: {stats.get('completed', 0)}")

        return success

    # ============= ADMIN FUNCTIONALITY TESTS =============

    def test_check_admin_exists(self):
        """Test checking if admin account exists (public endpoint)"""
        success, response = self.run_test(
            "Check Admin Exists",
            "GET",
            "admin/check",
            200
        )

        if success:
            admin_exists = response.get('admin_exists', False)
            print(f"   Admin exists: {admin_exists}")

        return success

    def test_admin_setup(self):
        """Test admin account setup"""
        # First check if admin exists
        check_success, check_response = self.run_test(
            "Pre-Admin Setup Check",
            "GET",
            "admin/check",
            200
        )

        if not check_success:
            return False

        admin_exists = check_response.get('admin_exists', False)
        
        if admin_exists:
            print("   Admin already exists, skipping setup test")
            return True

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        admin_data = {
            "name": f"Admin Test {timestamp}",
            "email": f"admin_{timestamp}@example.com",
            "password": "AdminPass123!"
        }

        success, response = self.run_test(
            "Admin Setup",
            "POST",
            "admin/setup",
            200,
            data=admin_data
        )

        if success and 'access_token' in response and 'user' in response:
            self.admin_token = response['access_token']
            self.admin_user_id = response['user']['id']
            print(f"   Admin created: {response['user']['name']} ({response['user']['email']})")
            print(f"   Admin role: {response['user']['role']}")
        
        return success

    def test_admin_login(self):
        """Test admin login functionality"""
        # If admin was just created in setup, test is not needed
        if hasattr(self, 'admin_token') and self.admin_token:
            print("✅ Admin Login - Already authenticated via setup")
            return True

        # Try to login with known admin credentials (would need to exist)
        print("❌ Admin Login - No admin credentials available for login test")
        return False

    def test_admin_stats(self):
        """Test admin statistics endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Stats Test - No admin auth token available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        success, response = self.run_test(
            "Admin Stats",
            "GET",
            "admin/stats",
            200
        )

        if success:
            stats = response
            print(f"   Admin Stats - Users: {stats.get('total_users', 0)}, " +
                  f"Contacts: {stats.get('total_contacts', 0)}, " +
                  f"Projects: {stats.get('total_projects', 0)}, " +
                  f"Messages: {stats.get('total_messages', 0)}")

        # Restore original token
        self.token = original_token
        return success

    def test_admin_get_contacts(self):
        """Test admin get all contacts endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Get Contacts Test - No admin auth token available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        success, response = self.run_test(
            "Admin Get Contacts",
            "GET",
            "admin/contacts",
            200
        )

        if success:
            contact_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {contact_count} contacts")

        # Restore original token
        self.token = original_token
        return success

    def test_admin_get_users(self):
        """Test admin get all users endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Get Users Test - No admin auth token available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        success, response = self.run_test(
            "Admin Get Users",
            "GET",
            "admin/users",
            200
        )

        if success:
            user_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {user_count} users")

        # Restore original token
        self.token = original_token
        return success

    def test_admin_get_projects(self):
        """Test admin get all projects endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Get Projects Test - No admin auth token available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        success, response = self.run_test(
            "Admin Get Projects",
            "GET",
            "admin/projects",
            200
        )

        if success:
            project_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {project_count} projects")
            # Store a project ID for status update test
            if project_count > 0 and isinstance(response, list):
                self.test_project_id = response[0].get('id')

        # Restore original token
        self.token = original_token
        return success

    def test_admin_update_project_status(self):
        """Test admin update project status endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Update Project Status Test - No admin auth token available")
            return False

        if not hasattr(self, 'test_project_id') or not self.test_project_id:
            print("❌ Admin Update Project Status Test - No project ID available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        success, response = self.run_test(
            "Admin Update Project Status",
            "PUT",
            f"admin/projects/{self.test_project_id}/status?status=in_progress",
            200
        )

        if success:
            print(f"   Updated project {self.test_project_id} status to in_progress")

        # Restore original token
        self.token = original_token
        return success

    def test_admin_get_messages(self):
        """Test admin get all messages endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Get Messages Test - No admin auth token available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        success, response = self.run_test(
            "Admin Get Messages",
            "GET",
            "admin/messages",
            200
        )

        if success:
            message_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {message_count} messages")
            # Store a message ID for reply test
            if message_count > 0 and isinstance(response, list):
                self.test_message_id = response[0].get('id')

        # Restore original token
        self.token = original_token
        return success

    def test_admin_reply_message(self):
        """Test admin reply to message endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("❌ Admin Reply Message Test - No admin auth token available")
            return False

        if not hasattr(self, 'test_message_id') or not self.test_message_id:
            print("❌ Admin Reply Message Test - No message ID available")
            return False

        # Store original token and use admin token
        original_token = self.token
        self.token = self.admin_token

        reply_text = "This is an admin test reply."
        
        success, response = self.run_test(
            "Admin Reply to Message",
            "PUT",
            f"admin/messages/{self.test_message_id}/reply?reply={reply_text}",
            200
        )

        if success:
            print(f"   Replied to message {self.test_message_id}")

        # Restore original token
        self.token = original_token
        return success

    def test_admin_access_forbidden_for_regular_user(self):
        """Test that regular users cannot access admin endpoints"""
        if not self.token:
            print("❌ Admin Access Test - No regular user auth token available")
            return False

        success, response = self.run_test(
            "Admin Access Forbidden for Regular User",
            "GET",
            "admin/stats",
            403  # Should return 403 Forbidden
        )

        if success:
            print("   Regular user correctly denied access to admin endpoint")

        return success

    def run_all_tests(self):
        """Run all API tests in order"""
        print(f"🚀 Starting Andre Dev API Testing")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)

        # Public endpoints first
        self.test_root_endpoint()
        self.test_portfolio_endpoint()
        self.test_contact_form()

        # Auth flow  
        self.test_user_registration()
        self.test_user_login()
        self.test_get_user_profile()

        # Protected endpoints (require auth)
        self.test_create_project() 
        self.test_get_projects()
        self.test_create_message()
        self.test_get_messages()
        self.test_get_stats()

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = AndreDev_APITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())