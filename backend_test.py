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