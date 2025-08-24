"""Testing patterns and fixtures."""

from typing import List
from ..db_manager import Pattern


def get_testing_patterns() -> List[Pattern]:
    """Get testing-related patterns."""
    return [
        Pattern(
            name="pytest_fixture_factory",
            language="python",
            pattern_type="testing",
            code_snippet="""
@pytest.fixture
def user_factory():
    def _create_user(name="Test User", email="test@example.com"):
        return User(name=name, email=email)
    return _create_user

def test_user_creation(user_factory):
    user = user_factory(name="John Doe")
    assert user.name == "John Doe"
""",
            usage_context="Factory fixtures for test data creation",
            dependencies=["pytest"],
            success_count=30
        ),
        Pattern(
            name="mock_service_pattern",
            language="python",
            pattern_type="testing",
            code_snippet="""
from unittest.mock import Mock, patch

class MockAPIService:
    def __init__(self):
        self.responses = {}
    
    def set_response(self, endpoint, response):
        self.responses[endpoint] = response
    
    def get(self, endpoint):
        return self.responses.get(endpoint, {"error": "Not found"})

def test_api_integration(mock_service):
    mock_service.set_response("/users", {"users": [{"id": 1, "name": "Test"}]})
    result = mock_service.get("/users")
    assert len(result["users"]) == 1
""",
            usage_context="Mock services for isolated testing",
            dependencies=["unittest.mock"],
            success_count=25
        ),
        Pattern(
            name="test_builder_pattern",
            language="python",
            pattern_type="testing",
            code_snippet="""
class UserBuilder:
    def __init__(self):
        self.data = {
            'name': 'Default User',
            'email': 'default@example.com',
            'age': 25
        }
    
    def with_name(self, name):
        self.data['name'] = name
        return self
    
    def with_email(self, email):
        self.data['email'] = email
        return self
    
    def with_age(self, age):
        self.data['age'] = age
        return self
    
    def build(self):
        return User(**self.data)

# Usage
user = UserBuilder().with_name("John").with_age(30).build()
""",
            usage_context="Builder pattern for test object creation",
            dependencies=[],
            success_count=22
        ),
        Pattern(
            name="parametrized_tests",
            language="python",
            pattern_type="testing",
            code_snippet="""
@pytest.mark.parametrize("input_value,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("MiXeD", "MIXED")
])
def test_uppercase_function(input_value, expected):
    assert uppercase(input_value) == expected

@pytest.mark.parametrize("user_data", [
    {"name": "John", "age": 25},
    {"name": "Jane", "age": 30},
    {"name": "Bob", "age": 35}
])
def test_user_validation(user_data):
    user = User(**user_data)
    assert user.is_valid()
""",
            usage_context="Parametrized testing for multiple test cases",
            dependencies=["pytest"],
            success_count=28
        ),
        Pattern(
            name="database_test_fixtures",
            language="python",
            pattern_type="testing",
            code_snippet="""
@pytest.fixture(scope="session")
def test_database():
    # Create test database
    db = create_test_db()
    yield db
    # Cleanup
    db.close()
    os.remove("test.db")

@pytest.fixture
def db_session(test_database):
    # Start transaction
    session = test_database.begin()
    yield session
    # Rollback transaction
    session.rollback()
""",
            usage_context="Database fixtures with proper cleanup",
            dependencies=["pytest"],
            success_count=26
        ),
        Pattern(
            name="api_test_client",
            language="python",
            pattern_type="testing",
            code_snippet="""
class APITestClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, endpoint, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)
    
    def post(self, endpoint, data=None, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", json=data, **kwargs)
    
    def authenticate(self, token):
        self.session.headers.update({"Authorization": f"Bearer {token}"})

@pytest.fixture
def api_client():
    return APITestClient()
""",
            usage_context="HTTP API testing client",
            dependencies=["requests", "pytest"],
            success_count=24
        )
    ]