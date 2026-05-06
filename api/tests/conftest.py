"""Test fixtures and utilities."""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

from main import app
from db.database import Base, get_db
from models import User, Domain, DomainAccess, APIKey


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestingSessionLocal() as session:
        yield session
        # Rollback after test
        await session.rollback()
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    """Create a test client with database override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        keycloak_id="test-keycloak-id",
        email="test@example.com",
        full_name="Test User",
        roles=["KM_VIEWER"],
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session):
    """Create a test admin user."""
    user = User(
        keycloak_id="admin-keycloak-id",
        email="admin@example.com",
        full_name="Admin User",
        roles=["KM_ADMIN"],
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_domain(db_session, test_user):
    """Create a test domain."""
    domain = Domain(
        name="Test Domain",
        description="A test domain",
        embedding_model="text-embedding-004",
        embedding_dimension=768,
        created_by=test_user.id
    )
    db_session.add(domain)
    await db_session.commit()
    await db_session.refresh(domain)
    return domain


@pytest.fixture
def mock_jwt_token():
    """Return a mock JWT token for testing."""
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.mock"


@pytest.fixture
def mock_user_payload():
    """Return mock JWT payload for testing."""
    return {
        "sub": "test-keycloak-id",
        "email": "test@example.com",
        "realm_access": {
            "roles": ["KM_VIEWER"]
        }
    }


@pytest.fixture
def mock_admin_payload():
    """Return mock admin JWT payload for testing."""
    return {
        "sub": "admin-keycloak-id",
        "email": "admin@example.com",
        "realm_access": {
            "roles": ["KM_ADMIN"]
        }
    }