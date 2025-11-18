#!/usr/bin/env python3
"""
Comprehensive Test Script for Tend - All Features
Tests all user dashboard features, admin features, and scalability (10k users)
"""

import requests
import json
import time
import sys
import os
import random
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BASE_URL}/api"

# Test Configuration
TOTAL_USERS = 10000  # For scalability tests
BATCH_SIZE = 100
MAX_WORKERS = 20
TEST_EMAIL_BASE = "test_user_{}@tendtest.com"
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")  # For single user tests

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_progress(current: int, total: int, message: str = ""):
    percent = (current / total) * 100
    bar_length = 50
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\r{Colors.CYAN}[{bar}] {percent:.1f}% - {message}{Colors.RESET}", end='', flush=True)

# Test Results
test_results = {
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'errors': []
}

def record_test(name: str, success: bool, error: str = None):
    test_results['total_tests'] += 1
    if success:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
        if error:
            test_results['errors'].append(f"{name}: {error}")

# ============================================================================
# SECTION 1: Basic Health & System Tests
# ============================================================================

def test_health_check():
    """Test backend health check"""
    print_header("TEST 1: Backend Health Check")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data.get('status', 'unknown')}")
            print_info(f"Database: {data.get('database', 'unknown')}")
            print_info(f"OpenAI: {data.get('openai', 'unknown')}")
            print_info(f"SMTP: {data.get('smtp', 'unknown')}")
            record_test("Health Check", True)
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            record_test("Health Check", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        record_test("Health Check", False, str(e))
        return False

# ============================================================================
# SECTION 2: User Dashboard Features
# ============================================================================

def test_user_profile(email: str):
    """Test getting user profile"""
    try:
        response = requests.get(f"{API_BASE}/users/{email}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"User profile retrieved: {data.get('email', 'N/A')}")
            return True
        return False
    except Exception as e:
        print_error(f"User profile error: {str(e)}")
        return False

def test_message_history(email: str, limit: int = 50):
    """Test getting message history"""
    try:
        response = requests.get(
            f"{API_BASE}/users/{email}/message-history?limit={limit}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('messages', []))
            print_success(f"Message history: {count} messages")
            return True
        return False
    except Exception as e:
        print_error(f"Message history error: {str(e)}")
        return False

def test_user_analytics(email: str):
    """Test getting user analytics"""
    try:
        response = requests.get(f"{API_BASE}/users/{email}/analytics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Analytics retrieved: {data.get('average_rating', 'N/A')} avg rating")
            return True
        return False
    except Exception as e:
        print_error(f"Analytics error: {str(e)}")
        return False

def test_streak_status(email: str):
    """Test getting streak status"""
    try:
        response = requests.get(f"{API_BASE}/users/{email}/streak-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Streak status: {data.get('streak_count', 0)} days")
            return True
        return False
    except Exception as e:
        print_error(f"Streak status error: {str(e)}")
        return False

def test_goals(email: str):
    """Test getting user goals"""
    try:
        response = requests.get(f"{API_BASE}/users/{email}/goals", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('goals', []))
            print_success(f"Goals: {count} goals")
            return True
        return False
    except Exception as e:
        print_error(f"Goals error: {str(e)}")
        return False

def test_replies(email: str):
    """Test getting email replies"""
    try:
        response = requests.get(f"{API_BASE}/users/{email}/replies?limit=50", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('replies', []))
            print_success(f"Replies: {count} replies")
            return True
        return False
    except Exception as e:
        print_error(f"Replies error: {str(e)}")
        return False

def test_generate_message():
    """Test message generation"""
    print_header("TEST 2: Message Generation")
    try:
        payload = {
            "goals": "Build a successful startup",
            "personality": {
                "type": "tone",
                "value": "inspiring"
            },
            "name": "Test User"
        }
        response = requests.post(
            f"{API_BASE}/generate-message",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Message generated: {len(data.get('message', ''))} chars")
            record_test("Generate Message", True)
            return True
        else:
            print_error(f"Generate message failed: {response.status_code}")
            record_test("Generate Message", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Generate message error: {str(e)}")
        record_test("Generate Message", False, str(e))
        return False

def test_all_user_features_single():
    """Test all user dashboard features for a single user"""
    print_header("TEST 3: All User Dashboard Features (Single User)")
    print_info(f"Testing with email: {TEST_EMAIL}")
    
    results = {}
    results['profile'] = test_user_profile(TEST_EMAIL)
    results['message_history'] = test_message_history(TEST_EMAIL, 1000)
    results['analytics'] = test_user_analytics(TEST_EMAIL)
    results['streak'] = test_streak_status(TEST_EMAIL)
    results['goals'] = test_goals(TEST_EMAIL)
    results['replies'] = test_replies(TEST_EMAIL)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print_success(f"✅ All user features passed ({passed}/{total})")
        record_test("All User Features", True)
        return True
    else:
        print_warning(f"⚠️ Some user features failed ({passed}/{total})")
        record_test("All User Features", False, f"{passed}/{total} passed")
        return False

# ============================================================================
# SECTION 3: Admin Dashboard Features
# ============================================================================

def get_admin_headers():
    """Get admin authentication headers"""
    admin_secret = os.getenv('ADMIN_SECRET', 'admin_secure_pass_2024')
    return {"Authorization": f"Bearer {admin_secret}"}

def test_admin_users():
    """Test admin users endpoint"""
    print_header("TEST 4: Admin Users Endpoint")
    try:
        response = requests.get(
            f"{API_BASE}/admin/users?page=1&limit=50",
            headers=get_admin_headers(),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('users', []))
            total = data.get('total', 0)
            print_success(f"Admin users: {count} users (Total: {total})")
            record_test("Admin Users", True)
            return True
        else:
            print_error(f"Admin users failed: {response.status_code}")
            record_test("Admin Users", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Admin users error: {str(e)}")
        record_test("Admin Users", False, str(e))
        return False

def test_admin_stats():
    """Test admin stats endpoint"""
    try:
        response = requests.get(
            f"{API_BASE}/admin/stats",
            headers=get_admin_headers(),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Admin stats retrieved")
            return True
        return False
    except Exception as e:
        print_error(f"Admin stats error: {str(e)}")
        return False

def test_admin_logs():
    """Test admin logs endpoints"""
    print_header("TEST 5: Admin Logs Endpoints")
    results = {}
    
    # Activity logs
    try:
        response = requests.get(
            f"{API_BASE}/admin/logs/activity?page=1&limit=50",
            headers=get_admin_headers(),
            timeout=10
        )
        results['activity'] = response.status_code == 200
    except:
        results['activity'] = False
    
    # System events
    try:
        response = requests.get(
            f"{API_BASE}/admin/logs/system-events?page=1&limit=50",
            headers=get_admin_headers(),
            timeout=10
        )
        results['system'] = response.status_code == 200
    except:
        results['system'] = False
    
    # API analytics
    try:
        response = requests.get(
            f"{API_BASE}/admin/logs/api-analytics?page=1&limit=50",
            headers=get_admin_headers(),
            timeout=10
        )
        results['api'] = response.status_code == 200
    except:
        results['api'] = False
    
    # Unified logs
    try:
        response = requests.get(
            f"{API_BASE}/admin/logs/unified?page=1&limit=50",
            headers=get_admin_headers(),
            timeout=10
        )
        results['unified'] = response.status_code == 200
    except:
        results['unified'] = False
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print_success(f"✅ All log endpoints passed ({passed}/{total})")
        record_test("Admin Logs", True)
        return True
    else:
        print_warning(f"⚠️ Some log endpoints failed ({passed}/{total})")
        record_test("Admin Logs", False, f"{passed}/{total} passed")
        return False

# ============================================================================
# SECTION 4: Scalability Tests (10k Users)
# ============================================================================

def create_test_user(user_idx: int) -> bool:
    """Create a single test user"""
    email = TEST_EMAIL_BASE.format(user_idx)
    try:
        # Clerk sync (simulated)
        clerk_data = {
            "clerk_user_id": f"clerk_test_{user_idx}",
            "email": email,
            "name": f"Test User {user_idx}",
            "image_url": None
        }
        requests.post(f"{API_BASE}/auth/clerk-sync", json=clerk_data, timeout=5)
        
        # Onboarding
        onboarding_data = {
            "email": email,
            "name": f"Test User {user_idx}",
            "goals": f"Test goal for user {user_idx}",
            "personalities": [
                {
                    "id": "test_personality",
                    "type": "tone",
                    "value": "inspiring",
                    "active": True
                }
            ],
            "rotation_mode": "sequential",
            "schedule": {
                "frequency": "daily",
                "times": ["09:00"],
                "timezone": "America/New_York",
                "paused": False
            },
            "user_timezone": "America/New_York"
        }
        response = requests.post(f"{API_BASE}/onboarding", json=onboarding_data, timeout=10)
        return response.status_code == 200
    except:
        return False

def test_create_10k_users():
    """Test creating 10k users"""
    print_header("TEST 6: Create 10K Users (Scalability)")
    print_warning("This will create 10,000 test users. This may take 10-20 minutes.")
    
    confirm = input(f"{Colors.YELLOW}Continue? (yes/no): {Colors.RESET}")
    if confirm.lower() != 'yes':
        print_info("Test skipped")
        return False, 0
    
    created = 0
    failed = 0
    
    print_info(f"Creating {TOTAL_USERS} users in batches of {BATCH_SIZE}...")
    
    for batch_start in range(0, TOTAL_USERS, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TOTAL_USERS)
        print_progress(batch_start, TOTAL_USERS, f"Batch {batch_start//BATCH_SIZE + 1}")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(create_test_user, i): i 
                for i in range(batch_start, batch_end)
            }
            
            for future in as_completed(futures):
                if future.result():
                    created += 1
                else:
                    failed += 1
    
    print(f"\n")
    print_success(f"Created {created} users")
    if failed > 0:
        print_warning(f"Failed: {failed} users")
    
    record_test("Create 10K Users", created >= TOTAL_USERS * 0.95, f"{created}/{TOTAL_USERS}")
    return created >= TOTAL_USERS * 0.95, created

def test_user_features_batch(email: str, user_idx: int) -> Dict:
    """Test all features for a single user"""
    results = {
        'user': email,
        'tests': {},
        'errors': []
    }
    
    tests = [
        ('profile', lambda: requests.get(f"{API_BASE}/users/{email}", timeout=10).status_code == 200),
        ('message_history', lambda: requests.get(f"{API_BASE}/users/{email}/message-history?limit=1000", timeout=10).status_code == 200),
        ('analytics', lambda: requests.get(f"{API_BASE}/users/{email}/analytics", timeout=10).status_code == 200),
        ('goals', lambda: requests.get(f"{API_BASE}/users/{email}/goals", timeout=10).status_code == 200),
        ('streak', lambda: requests.get(f"{API_BASE}/users/{email}/streak-status", timeout=10).status_code == 200),
        ('replies', lambda: requests.get(f"{API_BASE}/users/{email}/replies?limit=1000", timeout=10).status_code == 200),
    ]
    
    for test_name, test_func in tests:
        try:
            results['tests'][test_name] = test_func()
        except Exception as e:
            results['errors'].append(f"{test_name}: {str(e)}")
            results['tests'][test_name] = False
    
    return results

def test_all_user_features_batch():
    """Test all user features with sample users"""
    print_header("TEST 7: All User Features (Batch - 100 Users)")
    
    sample_size = 100
    sample_indices = random.sample(range(TOTAL_USERS), min(sample_size, TOTAL_USERS))
    
    print_info(f"Testing features for {len(sample_indices)} random users...")
    
    all_results = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(test_user_features_batch, TEST_EMAIL_BASE.format(i), i): i 
            for i in sample_indices
        }
        
        for future in as_completed(futures):
            try:
                result = future.result(timeout=60)
                all_results.append(result)
                completed += 1
                print_progress(completed, len(sample_indices), f"Tested {completed} users")
            except Exception as e:
                print_error(f"User test failed: {str(e)}")
    
    print(f"\n")
    
    # Analyze results
    feature_tests = {}
    total_tests = 0
    passed_tests = 0
    
    for result in all_results:
        for test_name, success in result['tests'].items():
            if test_name not in feature_tests:
                feature_tests[test_name] = {'passed': 0, 'failed': 0}
            total_tests += 1
            if success:
                feature_tests[test_name]['passed'] += 1
                passed_tests += 1
            else:
                feature_tests[test_name]['failed'] += 1
    
    print_info("Feature Test Results:")
    for feature, stats in feature_tests.items():
        total = stats['passed'] + stats['failed']
        success_rate = (stats['passed'] / total * 100) if total > 0 else 0
        status = "✅" if success_rate >= 95 else "⚠️" if success_rate >= 80 else "❌"
        print(f"  {status} {feature}: {stats['passed']}/{total} ({success_rate:.1f}%)")
    
    overall_success = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print_success(f"Overall: {passed_tests}/{total_tests} tests passed ({overall_success:.1f}%)")
    
    record_test("All User Features Batch", overall_success >= 95, f"{overall_success:.1f}% success")
    return overall_success >= 95

def test_admin_pagination():
    """Test admin pagination with max limits"""
    print_header("TEST 8: Admin Pagination (Max Limits)")
    
    try:
        max_limit = 1000
        page = 1
        total_fetched = 0
        
        print_info(f"Testing pagination with limit={max_limit}...")
        
        while True:
            response = requests.get(
                f"{API_BASE}/admin/users?page={page}&limit={max_limit}",
                headers=get_admin_headers(),
                timeout=30
            )
            
            if response.status_code != 200:
                print_error(f"Pagination failed at page {page}: {response.status_code}")
                record_test("Admin Pagination", False, f"Page {page} failed")
                return False
            
            data = response.json()
            users = data.get('users', [])
            total_fetched += len(users)
            
            print_info(f"Page {page}: Fetched {len(users)} users (Total: {total_fetched})")
            
            if len(users) < max_limit:
                break
            
            page += 1
            
            if page > 20:  # Safety limit
                print_warning("Reached safety limit of 20 pages")
                break
        
        print_success(f"✅ Pagination works! Fetched {total_fetched} users across {page} pages")
        record_test("Admin Pagination", True)
        return True
        
    except Exception as e:
        print_error(f"Pagination test error: {str(e)}")
        record_test("Admin Pagination", False, str(e))
        return False

# ============================================================================
# SECTION 5: Rate Limiting & Security
# ============================================================================

def test_rate_limiting():
    """Test rate limiting"""
    print_header("TEST 9: Rate Limiting")
    
    print_info("Testing rate limits with rapid requests...")
    
    rate_limited_count = 0
    success_count = 0
    
    for i in range(20):
        try:
            response = requests.post(
                f"{API_BASE}/generate-message",
                json={
                    "goals": "Test",
                    "personality": {"type": "tone", "value": "inspiring"}
                },
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
                print_warning(f"Request {i+1}: Rate limited (expected)")
                break
                
            time.sleep(0.1)
        except Exception as e:
            print_error(f"Request {i+1} error: {str(e)}")
    
    if rate_limited_count > 0:
        print_success(f"✅ Rate limiting works! Blocked after {success_count} requests")
        record_test("Rate Limiting", True)
        return True
    else:
        print_warning(f"Rate limiting not triggered ({success_count} successful)")
        record_test("Rate Limiting", False, "Not triggered")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all comprehensive tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*70)
    print("  Tend - Comprehensive Test Suite (All Features)")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test email: {TEST_EMAIL}")
    print_info(f"Max workers: {MAX_WORKERS}\n")
    
    start_time = time.time()
    
    # Basic tests
    test_health_check()
    time.sleep(1)
    
    # User dashboard tests
    test_generate_message()
    time.sleep(1)
    test_all_user_features_single()
    time.sleep(1)
    
    # Admin dashboard tests
    test_admin_users()
    time.sleep(1)
    test_admin_stats()
    time.sleep(1)
    test_admin_logs()
    time.sleep(1)
    
    # Scalability tests (optional)
    print_header("Scalability Tests (10K Users)")
    print_warning("These tests will create 10,000 test users and may take 20-30 minutes.")
    scalability = input(f"{Colors.YELLOW}Run scalability tests? (yes/no): {Colors.RESET}")
    
    if scalability.lower() == 'yes':
        success, users_created = test_create_10k_users()
        time.sleep(5)
        
        if success:
            test_admin_pagination()
            time.sleep(2)
            test_all_user_features_batch()
            time.sleep(2)
    
    # Rate limiting
    test_rate_limiting()
    
    # Print Summary
    elapsed = time.time() - start_time
    print_header("FINAL TEST SUMMARY")
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}")
    print(f"  Total Tests: {test_results['total_tests']}")
    print_success(f"  Passed: {test_results['passed']}")
    if test_results['failed'] > 0:
        print_error(f"  Failed: {test_results['failed']}")
    
    success_rate = (test_results['passed'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}")
    print(f"{Colors.BOLD}Total Time: {elapsed/60:.2f} minutes{Colors.RESET}")
    
    if test_results['errors']:
        print(f"\n{Colors.YELLOW}Errors (first 10):{Colors.RESET}")
        for error in test_results['errors'][:10]:
            print_warning(f"  - {error}")
    
    if test_results['failed'] == 0:
        print_success("\n🎉 All tests passed!")
    else:
        print_warning(f"\n⚠️  {test_results['failed']} test(s) failed. Please review errors above.")
    
    return test_results['failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

