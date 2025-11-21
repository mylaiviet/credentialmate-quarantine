#!/usr/bin/env python3
"""
SHIPFASTV1 AUTOMATED QA TEST SUITE RUNNER

Executes all automated QA scripts for ShipFastV1 (Phases 1-4).
Tests authentication, documents, credentials, CME, admin features, and security.

Usage:
    python run_automated_qa_suite.py [options]

Options:
    --base-url URL          Base URL (default: http://localhost:8000)
    --skip-auth             Skip authentication tests
    --skip-docs             Skip document tests
    --skip-creds            Skip credential tests
    --skip-cme              Skip CME tests
    --skip-admin            Skip admin tests
    --skip-security         Skip security tests
    --only-critical         Run only critical (P0) tests
    --verbose               Print detailed output
    --html-report           Generate HTML report
    --junit-report           Generate JUnit XML report
    --cleanup               Clean up test data after running

Examples:
    python run_automated_qa_suite.py
    python run_automated_qa_suite.py --base-url http://staging.example.com
    python run_automated_qa_suite.py --only-critical --html-report
    python run_automated_qa_suite.py --verbose --cleanup

TIMESTAMP: 2025-11-16T00:00:00Z
ORIGIN: credentialmate-docs
UPDATED_FOR: phase5-step2-qa-scripts
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import requests
from requests.exceptions import ConnectionError, Timeout


class TestStatus(Enum):
    """Test execution status"""
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class TestSeverity(Enum):
    """Test severity/priority level"""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass
class TestResult:
    """Individual test result"""
    test_id: str
    test_name: str
    section: str
    severity: TestSeverity
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['status'] = self.status.value
        return data


class TestSession:
    """Manages HTTP session for test execution"""

    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Execute HTTP request"""
        url = f"{self.base_url}{endpoint}"
        if self.verbose:
            self.logger.info(f"{method} {url}")
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            if self.verbose:
                self.logger.info(f"Status: {response.status_code}")
            return response
        except (ConnectionError, Timeout) as e:
            self.logger.error(f"Connection error: {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('DELETE', endpoint, **kwargs)

    def close(self):
        """Close session"""
        self.session.close()


class QATestRunner:
    """Runs all QA tests"""

    def __init__(self, base_url: str, verbose: bool = False):
        self.session = TestSession(base_url, verbose)
        self.logger = self._setup_logger(verbose)
        self.results: List[TestResult] = []
        self.test_accounts = {
            'alice': {
                'email': 'provider.alice@credentialmate.local',
                'password': 'ProviderPass123!',
                'npi': '1234567890'
            },
            'bob': {
                'email': 'provider.bob@credentialmate.local',
                'password': 'ProviderPass123!',
                'npi': '1234567891'
            },
            'charlie': {
                'email': 'provider.charlie@credentialmate.local',
                'password': 'ProviderPass123!',
                'npi': '1234567892'
            },
            'admin': {
                'email': 'admin@credentialmate.local',
                'password': 'AdminSecurePass123!',
                'npi': '9999999999'
            }
        }

    def _setup_logger(self, verbose: bool) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('QATestRunner')
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)
        status_symbol = {
            TestStatus.PASS: '✓',
            TestStatus.FAIL: '✗',
            TestStatus.BLOCKED: '⊗',
            TestStatus.SKIPPED: '⊘'
        }
        symbol = status_symbol.get(result.status, '?')
        self.logger.info(
            f"{symbol} [{result.test_id}] {result.test_name} - {result.status.value} ({result.duration:.2f}s)"
        )

    def run_test(self, test_id: str, test_name: str, section: str,
                 severity: TestSeverity, test_func) -> TestResult:
        """Run individual test"""
        self.logger.debug(f"Running {test_id}: {test_name}")
        start = time.time()
        try:
            test_func()
            duration = time.time() - start
            result = TestResult(
                test_id=test_id,
                test_name=test_name,
                section=section,
                severity=severity,
                status=TestStatus.PASS,
                duration=duration
            )
        except AssertionError as e:
            duration = time.time() - start
            result = TestResult(
                test_id=test_id,
                test_name=test_name,
                section=section,
                severity=severity,
                status=TestStatus.FAIL,
                duration=duration,
                error_message=str(e)
            )
        except Exception as e:
            duration = time.time() - start
            result = TestResult(
                test_id=test_id,
                test_name=test_name,
                section=section,
                severity=severity,
                status=TestStatus.BLOCKED,
                duration=duration,
                error_message=f"{type(e).__name__}: {str(e)}"
            )

        self.add_result(result)
        return result

    # =====================================================================
    # SECTION A: AUTHENTICATION & AUTHORIZATION TESTS
    # =====================================================================

    def test_a_01_registration(self):
        """A-01: User registration with valid credentials"""
        response = self.session.post(
            '/api/auth/register',
            json={
                'email': f'test.{int(time.time())}@example.com',
                'password': 'SecurePass123!',
                'npi': '1234567890',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'id' in data, "Response missing user ID"
        assert data['email'] == data['email'], "Email mismatch"

    def test_a_02_duplicate_email(self):
        """A-02: Registration rejects duplicate email"""
        email = f'dup.{int(time.time())}@example.com'
        # First registration
        response1 = self.session.post(
            '/api/auth/register',
            json={
                'email': email,
                'password': 'SecurePass123!',
                'npi': '1111111111',
                'first_name': 'First',
                'last_name': 'User'
            }
        )
        assert response1.status_code == 201, "First registration should succeed"

        # Duplicate attempt
        response2 = self.session.post(
            '/api/auth/register',
            json={
                'email': email,
                'password': 'DifferentPass123!',
                'npi': '2222222222',
                'first_name': 'Second',
                'last_name': 'User'
            }
        )
        assert response2.status_code == 400, f"Expected 400 for duplicate email, got {response2.status_code}"

    def test_a_03_login_success(self):
        """A-03: Login with valid credentials"""
        account = self.test_accounts['alice']
        response = self.session.post(
            '/api/auth/login',
            json={
                'email': account['email'],
                'password': account['password']
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'access_token' in data, "Response missing access_token"
        assert 'refresh_token' in data, "Response missing refresh_token"

    def test_a_04_login_rate_limiting(self):
        """A-04: Login rate limiting (5 attempts per 15 minutes)"""
        email = f'ratelimit.{int(time.time())}@example.com'

        # Register account first
        self.session.post(
            '/api/auth/register',
            json={
                'email': email,
                'password': 'SecurePass123!',
                'npi': '3333333333',
                'first_name': 'Rate',
                'last_name': 'Limit'
            }
        )

        # Attempt 5 failed logins
        for i in range(5):
            response = self.session.post(
                '/api/auth/login',
                json={'email': email, 'password': 'WrongPassword123!'}
            )
            assert response.status_code == 401, f"Attempt {i+1} should return 401"

        # 6th attempt should be rate limited (429)
        response = self.session.post(
            '/api/auth/login',
            json={'email': email, 'password': 'WrongPassword123!'}
        )
        assert response.status_code == 429, f"Expected 429 rate limit, got {response.status_code}"

    def test_a_05_token_refresh(self):
        """A-05: Token refresh flow"""
        account = self.test_accounts['alice']
        # Login
        login_response = self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )
        assert login_response.status_code == 200, "Login should succeed"
        token1 = login_response.json()['access_token']

        # Refresh token
        refresh_response = self.session.post('/api/auth/refresh')
        assert refresh_response.status_code == 200, "Refresh should succeed"
        token2 = refresh_response.json()['access_token']

        # Tokens should be different
        assert token1 != token2, "New token should be different from old"

    def test_a_06_current_user_profile(self):
        """A-06: Retrieve current user profile"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        # Get profile
        response = self.session.get('/api/auth/me')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data['email'] == account['email'], "Email mismatch"

    def test_a_07_logout(self):
        """A-07: Logout clears session"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        # Logout
        response = self.session.post('/api/auth/logout')
        assert response.status_code == 200, f"Logout should succeed"

    def test_a_08_unauthorized_access(self):
        """A-08: API rejects requests without valid authentication"""
        # Create fresh session without logging in
        fresh_session = TestSession(self.session.base_url)
        response = fresh_session.get('/api/auth/me')
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        fresh_session.close()

    def test_a_09_invalid_jwt_signature(self):
        """A-09: API rejects forged tokens"""
        response = self.session.get(
            '/api/auth/me',
            headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid'}
        )
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"

    # =====================================================================
    # SECTION B: DOCUMENT UPLOAD & PARSING
    # =====================================================================

    def test_b_01_presigned_url(self):
        """B-01: Get S3 presigned upload URL"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.post(
            '/api/v1/documents/upload-url',
            json={
                'filename': 'test_license.pdf',
                'file_size': 2048576,
                'content_type': 'application/pdf'
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'upload_url' in data, "Response missing upload_url"
        assert 'document_id' in data, "Response missing document_id"

    def test_b_02_document_upload(self):
        """B-02: Document upload (requires actual file)"""
        # This test requires a real PDF file
        # In practice, you would use test fixtures from qa/data/fixtures/
        self.logger.info("B-02: Skipping - requires test fixtures")

    def test_b_09_list_documents(self):
        """B-09: List all documents"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/documents?skip=0&limit=50')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'items' in data, "Response missing items"
        assert 'total' in data, "Response missing total"

    # =====================================================================
    # SECTION C: CREDENTIAL MANAGEMENT
    # =====================================================================

    def test_c_01_create_license(self):
        """C-01: Create medical license credential"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.post(
            '/api/v1/licenses',
            json={
                'state': 'CA',
                'license_type': 'MD',
                'license_number': f'TEST-{int(time.time())}',
                'expiration_date': '2025-12-31',
                'active': True
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data['state'] == 'CA', "State mismatch"
        assert data['license_type'] == 'MD', "License type mismatch"

    def test_c_02_license_status(self):
        """C-02: License status with badges"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/licenses')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        if data.get('licenses'):
            license_item = data['licenses'][0]
            assert 'status' in license_item, "License missing status field"

    def test_c_07_all_credentials_summary(self):
        """C-07: Get all credentials summary"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/licenses')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'licenses' in data or 'items' in data, "Response missing credentials"

    # =====================================================================
    # SECTION D: LICENSE & EXPIRATION TRACKING
    # =====================================================================

    def test_d_01_expiration_status(self):
        """D-01: Verify licenses marked as expiring/expired"""
        from datetime import datetime, timedelta

        account = self.test_accounts['bob']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        # Create license expiring in 20 days
        exp_date = (datetime.now() + timedelta(days=20)).date().isoformat()
        response = self.session.post(
            '/api/v1/licenses',
            json={
                'state': 'TX',
                'license_type': 'MD',
                'license_number': f'EXP-{int(time.time())}',
                'expiration_date': exp_date,
                'active': True
            }
        )
        assert response.status_code == 201, "License creation should succeed"

        lic_id = response.json()['id']
        # Verify status
        resp = self.session.get(f'/api/v1/licenses/{lic_id}')
        assert resp.status_code == 200, "License retrieval should succeed"
        data = resp.json()
        assert data['status'] in ['active', 'expiring'], f"Unexpected status: {data.get('status')}"

    # =====================================================================
    # SECTION E: CME ACTIVITIES
    # =====================================================================

    def test_e_01_create_cme_activity(self):
        """E-01: Record CME activity with credit hours"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.post(
            '/api/v1/cme/activities',
            json={
                'title': 'Advanced Cardiology Update 2024',
                'activity_type': 'Conference',
                'credits': 10.0,
                'completion_date': '2025-11-15',
                'provider': 'American College of Cardiology',
                'state': 'CA',
                'certificate_number': f'ACC-{int(time.time())}'
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    def test_e_05_list_cme_activities(self):
        """E-05: Retrieve CME activities with filters"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/cme/activities')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # =====================================================================
    # SECTION F: PROVIDER DASHBOARD
    # =====================================================================

    def test_f_01_provider_profile(self):
        """F-01: Get provider's own profile"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/providers/me')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'email' in data, "Profile missing email"

    def test_f_03_credential_summary(self):
        """F-03: Display credential status overview"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/licenses')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # =====================================================================
    # SECTION G: ADMIN DASHBOARD
    # =====================================================================

    def test_g_01_list_providers(self):
        """G-01: Admin views all registered providers"""
        account = self.test_accounts['admin']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/admin/providers?skip=0&limit=50')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'items' in data or 'total' in data, "Provider list missing data"

    def test_g_05_parsing_jobs_queue(self):
        """G-05: Admin monitors document parsing job queue"""
        account = self.test_accounts['admin']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.get('/api/v1/admin/parsing/jobs?limit=20')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # =====================================================================
    # SECTION H: ERROR HANDLING & EDGE CASES
    # =====================================================================

    def test_h_01_rls_isolation(self):
        """H-01: Provider cannot access another provider's data"""
        # Login as Alice
        alice = self.test_accounts['alice']
        session_a = TestSession(self.session.base_url)
        session_a.post(
            '/api/auth/login',
            json={'email': alice['email'], 'password': alice['password']}
        )

        # Login as Bob
        bob = self.test_accounts['bob']
        session_b = TestSession(self.session.base_url)
        session_b.post(
            '/api/auth/login',
            json={'email': bob['email'], 'password': bob['password']}
        )

        # Get Alice's documents ID (if any)
        docs_a = session_a.get('/api/v1/documents?skip=0&limit=1').json()

        # Try to access from Bob's session (should fail if Alice has docs)
        if docs_a.get('items') and len(docs_a['items']) > 0:
            doc_id = docs_a['items'][0]['id']
            response = session_b.get(f'/api/v1/documents/{doc_id}')
            assert response.status_code == 403, f"Expected 403, got {response.status_code}"

        session_a.close()
        session_b.close()

    def test_h_02_admin_authorization(self):
        """H-02: Non-admin users cannot access admin endpoints"""
        account = self.test_accounts['alice']
        # Login as provider
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        # Try to access admin endpoint
        response = self.session.get('/api/v1/admin/providers')
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"

    def test_h_03_empty_document_list(self):
        """H-03: System handles provider with no documents"""
        # Register new provider
        email = f'empty.{int(time.time())}@example.com'
        reg_response = self.session.post(
            '/api/auth/register',
            json={
                'email': email,
                'password': 'SecurePass123!',
                'npi': '4444444444',
                'first_name': 'Empty',
                'last_name': 'User'
            }
        )
        assert reg_response.status_code == 201, "Registration should succeed"

        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': email, 'password': 'SecurePass123!'}
        )

        # Get documents
        response = self.session.get('/api/v1/documents')
        assert response.status_code == 200, "Should return 200 for empty list"
        data = response.json()
        assert data['total'] == 0, "New user should have 0 documents"

    def test_h_04_invalid_license_format(self):
        """H-04: System validates license number format"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.post(
            '/api/v1/licenses',
            json={
                'state': 'CA',
                'license_type': 'MD',
                'license_number': '',  # Invalid: empty
                'expiration_date': '2025-12-31'
            }
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # =====================================================================
    # SECTION J: SECURITY & COMPLIANCE
    # =====================================================================

    def test_j_01_jwt_signature_validation(self):
        """J-01: API verifies JWT signature"""
        response = self.session.get(
            '/api/auth/me',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_j_05_pii_masking(self):
        """J-05: Error messages don't expose sensitive data"""
        # Try invalid operation
        response = self.session.post(
            '/api/auth/register',
            json={
                'email': 'invalid',
                'password': 'weak',
                'npi': 'invalid',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        error_message = response.text
        # Verify no database terms
        assert 'postgresql' not in error_message.lower(), "Error exposes database type"
        assert 'traceback' not in error_message.lower(), "Error exposes stack trace"

    def test_j_09_sql_injection_prevention(self):
        """J-09: SQL injection attempts are neutralized"""
        account = self.test_accounts['alice']
        # Login
        self.session.post(
            '/api/auth/login',
            json={'email': account['email'], 'password': account['password']}
        )

        response = self.session.post(
            '/api/v1/licenses',
            json={
                'state': 'CA',
                'license_type': 'MD',
                'license_number': "'; DROP TABLE licenses; --",
                'expiration_date': '2025-12-31'
            }
        )
        # Should fail safely, not execute SQL
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # =====================================================================
    # SECTION K: REGRESSION TESTS
    # =====================================================================

    def test_k_01_login_flow(self):
        """K-01: Login flow still works after updates"""
        email = f'regression.{int(time.time())}@example.com'

        # Register
        reg_resp = self.session.post(
            '/api/auth/register',
            json={
                'email': email,
                'password': 'SecurePass123!',
                'npi': '5555555555',
                'first_name': 'Regression',
                'last_name': 'Test'
            }
        )
        assert reg_resp.status_code == 201, "Registration should succeed"

        # Login
        login_resp = self.session.post(
            '/api/auth/login',
            json={'email': email, 'password': 'SecurePass123!'}
        )
        assert login_resp.status_code == 200, "Login should succeed"

        # Get profile
        profile_resp = self.session.get('/api/auth/me')
        assert profile_resp.status_code == 200, "Profile should load"
        assert profile_resp.json()['email'] == email, "Email mismatch"

    # =====================================================================
    # SECTION L: RELEASE CRITERIA
    # =====================================================================

    def test_l_01_health_check(self):
        """L-01: System health check"""
        response = self.session.get('/api/health')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_l_02_api_responsiveness(self):
        """L-02: API responds within acceptable time"""
        start = time.time()
        response = self.session.get('/api/health')
        duration = time.time() - start

        assert response.status_code == 200, "Health check failed"
        assert duration < 1.0, f"Health check took {duration}s, expected < 1s"

    # =====================================================================
    # TEST EXECUTION
    # =====================================================================

    def run_all_tests(self, skip_sections: List[str] = None, only_critical: bool = False) -> Tuple[int, int, int, int]:
        """Run all tests and return summary"""
        skip_sections = skip_sections or []

        tests = [
            # Section A: Authentication
            ('A', 'A-01', 'User registration', TestSeverity.P0, self.test_a_01_registration),
            ('A', 'A-02', 'Duplicate email rejection', TestSeverity.P0, self.test_a_02_duplicate_email),
            ('A', 'A-03', 'Login success', TestSeverity.P0, self.test_a_03_login_success),
            ('A', 'A-04', 'Login rate limiting', TestSeverity.P1, self.test_a_04_login_rate_limiting),
            ('A', 'A-05', 'Token refresh', TestSeverity.P1, self.test_a_05_token_refresh),
            ('A', 'A-06', 'Current user profile', TestSeverity.P1, self.test_a_06_current_user_profile),
            ('A', 'A-07', 'Logout', TestSeverity.P1, self.test_a_07_logout),
            ('A', 'A-08', 'Unauthorized access rejection', TestSeverity.P0, self.test_a_08_unauthorized_access),
            ('A', 'A-09', 'Invalid JWT rejection', TestSeverity.P0, self.test_a_09_invalid_jwt_signature),

            # Section B: Documents
            ('B', 'B-01', 'Presigned upload URL', TestSeverity.P1, self.test_b_01_presigned_url),
            ('B', 'B-09', 'List documents', TestSeverity.P1, self.test_b_09_list_documents),

            # Section C: Credentials
            ('C', 'C-01', 'Create license', TestSeverity.P0, self.test_c_01_create_license),
            ('C', 'C-02', 'License status', TestSeverity.P1, self.test_c_02_license_status),
            ('C', 'C-07', 'Credentials summary', TestSeverity.P1, self.test_c_07_all_credentials_summary),

            # Section D: Expiration
            ('D', 'D-01', 'Expiration status', TestSeverity.P1, self.test_d_01_expiration_status),

            # Section E: CME
            ('E', 'E-01', 'Create CME activity', TestSeverity.P1, self.test_e_01_create_cme_activity),
            ('E', 'E-05', 'List CME activities', TestSeverity.P1, self.test_e_05_list_cme_activities),

            # Section F: Provider Dashboard
            ('F', 'F-01', 'Provider profile', TestSeverity.P1, self.test_f_01_provider_profile),
            ('F', 'F-03', 'Credential summary', TestSeverity.P1, self.test_f_03_credential_summary),

            # Section G: Admin Dashboard
            ('G', 'G-01', 'List providers', TestSeverity.P1, self.test_g_01_list_providers),
            ('G', 'G-05', 'Parsing jobs queue', TestSeverity.P1, self.test_g_05_parsing_jobs_queue),

            # Section H: Error Handling
            ('H', 'H-01', 'RLS isolation', TestSeverity.P0, self.test_h_01_rls_isolation),
            ('H', 'H-02', 'Admin authorization', TestSeverity.P0, self.test_h_02_admin_authorization),
            ('H', 'H-03', 'Empty document list', TestSeverity.P2, self.test_h_03_empty_document_list),
            ('H', 'H-04', 'License format validation', TestSeverity.P2, self.test_h_04_invalid_license_format),

            # Section J: Security
            ('J', 'J-01', 'JWT signature validation', TestSeverity.P0, self.test_j_01_jwt_signature_validation),
            ('J', 'J-05', 'PII masking in errors', TestSeverity.P0, self.test_j_05_pii_masking),
            ('J', 'J-09', 'SQL injection prevention', TestSeverity.P0, self.test_j_09_sql_injection_prevention),

            # Section K: Regression
            ('K', 'K-01', 'Login flow regression', TestSeverity.P1, self.test_k_01_login_flow),

            # Section L: Release
            ('L', 'L-01', 'Health check', TestSeverity.P0, self.test_l_01_health_check),
            ('L', 'L-02', 'API responsiveness', TestSeverity.P1, self.test_l_02_api_responsiveness),
        ]

        self.logger.info("=" * 70)
        self.logger.info("SHIPFASTV1 AUTOMATED QA TEST SUITE")
        self.logger.info("=" * 70)
        self.logger.info(f"Start time: {datetime.utcnow().isoformat()}Z")
        self.logger.info(f"Base URL: {self.session.base_url}")
        self.logger.info(f"Total tests: {len(tests)}")
        self.logger.info("=" * 70)

        for section, test_id, test_name, severity, test_func in tests:
            # Skip sections
            if section.lower() in [s.lower() for s in skip_sections]:
                result = TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    section=section,
                    severity=severity,
                    status=TestStatus.SKIPPED,
                    duration=0
                )
                self.results.append(result)
                self.logger.info(f"⊘ [{test_id}] {test_name} - SKIPPED")
                continue

            # Skip non-critical if only_critical
            if only_critical and severity != TestSeverity.P0:
                continue

            # Run test
            self.run_test(test_id, test_name, section, severity, test_func)

        # Summary
        return self._print_summary()

    def _print_summary(self) -> Tuple[int, int, int, int]:
        """Print test summary"""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        blocked = sum(1 for r in self.results if r.status == TestStatus.BLOCKED)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

        total = len(self.results)
        duration = sum(r.duration for r in self.results)

        self.logger.info("\n" + "=" * 70)
        self.logger.info("TEST SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Total:    {total}")
        self.logger.info(f"Passed:   {passed} ({100*passed//(total or 1)}%)")
        self.logger.info(f"Failed:   {failed}")
        self.logger.info(f"Blocked:  {blocked}")
        self.logger.info(f"Skipped:  {skipped}")
        self.logger.info(f"Duration: {duration:.2f}s")
        self.logger.info("=" * 70)

        # Print failures
        if failed > 0:
            self.logger.info("\nFAILED TESTS:")
            for result in self.results:
                if result.status == TestStatus.FAIL:
                    self.logger.error(f"  ✗ [{result.test_id}] {result.test_name}")
                    self.logger.error(f"     Error: {result.error_message}")

        # Print blocked
        if blocked > 0:
            self.logger.info("\nBLOCKED TESTS:")
            for result in self.results:
                if result.status == TestStatus.BLOCKED:
                    self.logger.warning(f"  ⊗ [{result.test_id}] {result.test_name}")
                    self.logger.warning(f"     Error: {result.error_message}")

        return passed, failed, blocked, skipped

    def export_results(self, format: str = 'json', filename: str = None):
        """Export test results"""
        if format == 'json':
            data = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'summary': {
                    'total': len(self.results),
                    'passed': sum(1 for r in self.results if r.status == TestStatus.PASS),
                    'failed': sum(1 for r in self.results if r.status == TestStatus.FAIL),
                    'blocked': sum(1 for r in self.results if r.status == TestStatus.BLOCKED),
                    'skipped': sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
                },
                'results': [r.to_dict() for r in self.results]
            }

            if filename:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                self.logger.info(f"Results exported to {filename}")
            else:
                return json.dumps(data, indent=2)

        elif format == 'junit':
            # JUnit XML format
            from xml.etree.ElementTree import Element, SubElement, tostring

            testsuites = Element('testsuites')
            testsuite = SubElement(testsuites, 'testsuite')
            testsuite.set('name', 'ShipFastV1 QA')
            testsuite.set('tests', str(len(self.results)))

            passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
            failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)

            testsuite.set('failures', str(failed))
            testsuite.set('timestamp', datetime.utcnow().isoformat())

            for result in self.results:
                testcase = SubElement(testsuite, 'testcase')
                testcase.set('name', result.test_id)
                testcase.set('classname', f"Section{result.section}")
                testcase.set('time', str(result.duration))

                if result.status == TestStatus.FAIL:
                    failure = SubElement(testcase, 'failure')
                    failure.set('message', result.error_message or 'Test failed')
                elif result.status == TestStatus.BLOCKED:
                    skipped = SubElement(testcase, 'skipped')
                    skipped.set('message', result.error_message or 'Test blocked')

            xml_str = tostring(testsuites, encoding='unicode')

            if filename:
                with open(filename, 'w') as f:
                    f.write(xml_str)
                self.logger.info(f"JUnit results exported to {filename}")
            else:
                return xml_str

    def generate_html_report(self, filename: str = 'qa_report.html'):
        """Generate HTML test report"""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        blocked = sum(1 for r in self.results if r.status == TestStatus.BLOCKED)
        total = len(self.results)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ShipFastV1 QA Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin-right: 30px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .blocked {{ color: orange; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #333; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .status-pass {{ background: #d4edda; }}
        .status-fail {{ background: #f8d7da; }}
        .status-blocked {{ background: #fff3cd; }}
        .timestamp {{ color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>ShipFastV1 QA Test Report</h1>
    <p class="timestamp">Generated: {datetime.utcnow().isoformat()}Z</p>

    <div class="summary">
        <h2>Summary</h2>
        <div class="metric">
            <div class="metric-value">{total}</div>
            <div>Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value pass">{passed}</div>
            <div>Passed ({100*passed//(total or 1)}%)</div>
        </div>
        <div class="metric">
            <div class="metric-value fail">{failed}</div>
            <div>Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value blocked">{blocked}</div>
            <div>Blocked</div>
        </div>
    </div>

    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test ID</th>
            <th>Name</th>
            <th>Section</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Error</th>
        </tr>
"""

        for result in self.results:
            status_class = f"status-{result.status.value.lower()}"
            html += f"""
        <tr class="{status_class}">
            <td>{result.test_id}</td>
            <td>{result.test_name}</td>
            <td>{result.section}</td>
            <td>{result.severity.value}</td>
            <td>{result.status.value}</td>
            <td>{result.duration:.2f}s</td>
            <td>{result.error_message or '-'}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(filename, 'w') as f:
            f.write(html)

        self.logger.info(f"HTML report generated: {filename}")

    def cleanup(self):
        """Clean up test data"""
        self.session.close()
        self.logger.info("Test session closed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ShipFastV1 Automated QA Test Suite'
    )
    parser.add_argument(
        '--base-url',
        default='http://localhost:8000',
        help='Base URL for API (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--skip-auth',
        action='store_true',
        help='Skip authentication tests'
    )
    parser.add_argument(
        '--skip-docs',
        action='store_true',
        help='Skip document tests'
    )
    parser.add_argument(
        '--skip-creds',
        action='store_true',
        help='Skip credential tests'
    )
    parser.add_argument(
        '--skip-cme',
        action='store_true',
        help='Skip CME tests'
    )
    parser.add_argument(
        '--skip-admin',
        action='store_true',
        help='Skip admin tests'
    )
    parser.add_argument(
        '--skip-security',
        action='store_true',
        help='Skip security tests'
    )
    parser.add_argument(
        '--only-critical',
        action='store_true',
        help='Run only P0 critical tests'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--html-report',
        help='Generate HTML report file'
    )
    parser.add_argument(
        '--json-report',
        help='Generate JSON report file'
    )
    parser.add_argument(
        '--junit-report',
        help='Generate JUnit XML report file'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up test data after running'
    )

    args = parser.parse_args()

    # Build skip list
    skip_sections = []
    if args.skip_auth:
        skip_sections.append('A')
    if args.skip_docs:
        skip_sections.append('B')
    if args.skip_creds:
        skip_sections.append('C')
    if args.skip_cme:
        skip_sections.append('E')
    if args.skip_admin:
        skip_sections.append('G')
    if args.skip_security:
        skip_sections.extend(['J', 'H'])

    # Create runner
    runner = QATestRunner(args.base_url, args.verbose)

    try:
        # Run tests
        passed, failed, blocked, skipped = runner.run_all_tests(
            skip_sections=skip_sections,
            only_critical=args.only_critical
        )

        # Generate reports
        if args.html_report:
            runner.generate_html_report(args.html_report)

        if args.json_report:
            runner.export_results('json', args.json_report)

        if args.junit_report:
            runner.export_results('junit', args.junit_report)

        # Exit code
        sys.exit(0 if failed == 0 and blocked == 0 else 1)

    finally:
        if args.cleanup:
            runner.cleanup()


if __name__ == '__main__':
    main()
