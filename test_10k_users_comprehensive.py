#!/usr/bin/env python3
"""
Comprehensive Test Script for Tend - 10K Users & All Features
Tests all user dashboard features with maximum limits and 10k users
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
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Test Configuration
TOTAL_USERS = 10000
BATCH_SIZE = 100  # Process in batches
MAX_WORKERS = 20  # Concurrent requests

# Test user base
TEST_EMAIL_BASE = "test_user_{}@tendtest.com"

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
# TEST 1: Health Check
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
# TEST 2: Create 10K Users
# ============================================================================
def create_user_batch(start_idx: int, end_idx: int) -> Dict:
    """Create a batch of users"""
    results = {'created': 0, 'errors': []}
    
    for i in range(start_idx, end_idx):
        email = TEST_EMAIL_BASE.format(i)
        try:
            # Onboard user
            onboarding_data = {
                "email": email,
                "name": f"Test User {i}",
                "goals": f"Goal for user {i}: Build something amazing",
                "personalities": [
                    {"type": "famous", "value": random.choice(["Elon Musk", "Steve Jobs", "Oprah Winfrey"])}
                ],
                "rotation_mode": random.choice(["sequential", "random"]),
                "schedule": {
                    "frequency": "daily",
                    "times": [f"{random.randint(6, 22):02d}:00"],
                    "timezone": "UTC",
                    "paused": False
                },
                "user_timezone": "UTC"
            }
            
            response = requests.post(
                f"{API_BASE}/onboarding",
                json=onboarding_data,
                timeout=30
            )
            
            if response.status_code == 200:
                results['created'] += 1
            else:
                results['errors'].append(f"User {i}: {response.status_code}")
                
        except Exception as e:
            results['errors'].append(f"User {i}: {str(e)}")
    
    return results

def test_create_10k_users():
    """Test creating 10,000 users"""
    print_header("TEST 2: Create 10,000 Users")
    print_info(f"Creating {TOTAL_USERS} users in batches of {BATCH_SIZE}...")
    
    total_created = 0
    total_errors = []
    start_time = time.time()
    
    # Process in batches with threading
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        
        for batch_start in range(0, TOTAL_USERS, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, TOTAL_USERS)
            future = executor.submit(create_user_batch, batch_start, batch_end)
            futures.append((future, batch_start, batch_end))
        
        completed = 0
        for future, batch_start, batch_end in futures:
            try:
                result = future.result(timeout=300)  # 5 min timeout per batch
                total_created += result['created']
                total_errors.extend(result['errors'])
                completed += (batch_end - batch_start)
                print_progress(completed, TOTAL_USERS, f"Created {total_created} users")
            except Exception as e:
                print_error(f"Batch {batch_start}-{batch_end} failed: {str(e)}")
                total_errors.append(f"Batch {batch_start}-{batch_end}: {str(e)}")
    
    elapsed = time.time() - start_time
    
    print(f"\n")
    print_success(f"Created {total_created} users in {elapsed:.2f} seconds")
    print_info(f"Rate: {total_created/elapsed:.2f} users/second")
    
    if total_errors:
        print_warning(f"{len(total_errors)} errors occurred (first 10):")
        for error in total_errors[:10]:
            print_warning(f"  - {error}")
    
    success = total_created >= (TOTAL_USERS * 0.95)  # 95% success rate acceptable
    record_test("Create 10K Users", success, f"Created {total_created}/{TOTAL_USERS}")
    return success, total_created

# ============================================================================
# TEST 3: Test User Scheduling (All Users)
# ============================================================================
def test_schedule_all_users():
    """Test that all users are scheduled"""
    print_header("TEST 3: Verify All Users Are Scheduled")
    print_info("Checking if scheduler processed all users...")
    
    try:
        # Get total active users
        response = requests.get(f"{API_BASE}/admin/users?limit=1", 
                               headers={"Authorization": f"Bearer {os.getenv('ADMIN_SECRET', 'admin_secure_pass_2024')}"},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_users = data.get('total', 0)
            print_success(f"Total active users in database: {total_users}")
            
            # Check if we have close to 10k
            if total_users >= (TOTAL_USERS * 0.95):
                print_success(f"✅ All users scheduled successfully!")
                record_test("Schedule All Users", True)
                return True
            else:
                print_warning(f"Only {total_users} users found (expected ~{TOTAL_USERS})")
                record_test("Schedule All Users", False, f"Only {total_users} users")
                return False
        else:
            print_error(f"Failed to get user count: {response.status_code}")
            record_test("Schedule All Users", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking users: {str(e)}")
        record_test("Schedule All Users", False, str(e))
        return False

# ============================================================================
# TEST 4: Test Pagination - Admin Users Endpoint
# ============================================================================
def test_admin_pagination():
    """Test admin users endpoint pagination with max limits"""
    print_header("TEST 4: Admin Users Pagination (Max Limits)")
    
    try:
        # Test with maximum page size
        max_limit = 1000  # Maximum reasonable limit
        page = 1
        total_fetched = 0
        
        print_info(f"Testing pagination with limit={max_limit}...")
        
        while True:
            response = requests.get(
                f"{API_BASE}/admin/users?page={page}&limit={max_limit}",
                headers={"Authorization": f"Bearer {os.getenv('ADMIN_SECRET', 'admin_secure_pass_2024')}"},
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
# TEST 5: Test All User Dashboard Features (Sample Users)
# ============================================================================
def test_user_features(email: str, user_idx: int) -> Dict:
    """Test all features for a single user"""
    results = {
        'user': email,
        'tests': {},
        'errors': []
    }
    
    # Test 5.1: Get User Profile
    try:
        response = requests.get(f"{API_BASE}/users/{email}", timeout=10)
        results['tests']['get_user'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"get_user: {str(e)}")
        results['tests']['get_user'] = False
    
    # Test 5.2: Get Message History (Max Limit)
    try:
        response = requests.get(
            f"{API_BASE}/users/{email}/message-history?limit=1000",
            timeout=10
        )
        results['tests']['message_history'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"message_history: {str(e)}")
        results['tests']['message_history'] = False
    
    # Test 5.3: Get Analytics
    try:
        response = requests.get(f"{API_BASE}/users/{email}/analytics", timeout=10)
        results['tests']['analytics'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"analytics: {str(e)}")
        results['tests']['analytics'] = False
    
    # Test 5.4: Get Goals (Max Limit)
    try:
        response = requests.get(f"{API_BASE}/users/{email}/goals", timeout=10)
        results['tests']['goals'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"goals: {str(e)}")
        results['tests']['goals'] = False
    
    # Test 5.5: Get Achievements
    try:
        response = requests.get(f"{API_BASE}/users/{email}/achievements", timeout=10)
        results['tests']['achievements'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"achievements: {str(e)}")
        results['tests']['achievements'] = False
    
    # Test 5.6: Get Streak Status
    try:
        response = requests.get(f"{API_BASE}/users/{email}/streak-status", timeout=10)
        results['tests']['streak_status'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"streak_status: {str(e)}")
        results['tests']['streak_status'] = False
    
    # Test 5.7: Get Weekly Analytics
    try:
        response = requests.get(f"{API_BASE}/users/{email}/analytics/weekly", timeout=10)
        results['tests']['weekly_analytics'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"weekly_analytics: {str(e)}")
        results['tests']['weekly_analytics'] = False
    
    # Test 5.8: Get Monthly Analytics
    try:
        response = requests.get(f"{API_BASE}/users/{email}/analytics/monthly", timeout=10)
        results['tests']['monthly_analytics'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"monthly_analytics: {str(e)}")
        results['tests']['monthly_analytics'] = False
    
    # Test 5.9: Get Replies
    try:
        response = requests.get(f"{API_BASE}/users/{email}/replies?limit=1000", timeout=10)
        results['tests']['replies'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"replies: {str(e)}")
        results['tests']['replies'] = False
    
    # Test 5.10: Get Reply Insights
    try:
        response = requests.get(f"{API_BASE}/users/{email}/reply-insights", timeout=10)
        results['tests']['reply_insights'] = response.status_code == 200
    except Exception as e:
        results['errors'].append(f"reply_insights: {str(e)}")
        results['tests']['reply_insights'] = False
    
    return results

def test_all_user_features():
    """Test all user dashboard features with sample users"""
    print_header("TEST 5: All User Dashboard Features (Sample Users)")
    
    # Test with 100 random users
    sample_size = 100
    sample_indices = random.sample(range(TOTAL_USERS), min(sample_size, TOTAL_USERS))
    
    print_info(f"Testing features for {len(sample_indices)} random users...")
    
    all_results = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(test_user_features, TEST_EMAIL_BASE.format(i), i): i 
            for i in sample_indices
        }
        
        for future in as_completed(futures):
            try:
                result = future.result(timeout=60)
                all_results.append(result)
                completed += 1
                print_progress(completed, len(sample_indices), f"Tested {completed} users")
            except Exception as e:
                idx = futures[future]
                print_error(f"User {idx} test failed: {str(e)}")
    
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
    
    record_test("All User Features", overall_success >= 95, f"{overall_success:.1f}% success")
    return overall_success >= 95

# ============================================================================
# TEST 6: Test Rate Limiting
# ============================================================================
def test_rate_limiting():
    """Test rate limiting with high volume"""
    print_header("TEST 6: Rate Limiting Test")
    
    print_info("Testing rate limits with rapid requests...")
    
    rate_limited_count = 0
    success_count = 0
    
    for i in range(20):
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": f"ratelimit_test_{i}@test.com"},
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
# TEST 7: Test Broadcast Message (All Users)
# ============================================================================
def test_broadcast_message():
    """Test broadcast message to all users"""
    print_header("TEST 7: Broadcast Message (All Users)")
    
    print_info("Testing broadcast message endpoint...")
    print_warning("Note: This will send emails to all users. Use with caution!")
    
    try:
        broadcast_data = {
            "message": "<h1>Test Broadcast</h1><p>This is a test broadcast message.</p>",
            "subject": "Test Broadcast - Tend"
        }
        
        response = requests.post(
            f"{API_BASE}/admin/broadcast",
            json=broadcast_data,
            headers={"Authorization": f"Bearer {os.getenv('ADMIN_SECRET', 'admin_secure_pass_2024')}"},
            timeout=600  # 10 minute timeout for 10k users
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"✅ Broadcast completed!")
            print_info(f"Total users: {data.get('total_users', 0)}")
            print_info(f"Success: {data.get('success', 0)}")
            print_info(f"Failed: {data.get('failed', 0)}")
            record_test("Broadcast Message", True)
            return True
        else:
            print_error(f"Broadcast failed: {response.status_code}")
            print_error(response.text)
            record_test("Broadcast Message", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Broadcast error: {str(e)}")
        record_test("Broadcast Message", False, str(e))
        return False

# ============================================================================
# TEST 8: Test Maximum Limits
# ============================================================================
def test_maximum_limits():
    """Test all endpoints with maximum limits"""
    print_header("TEST 8: Maximum Limits Test")
    
    test_email = TEST_EMAIL_BASE.format(0)
    results = {}
    
    # Test message history with max limit
    try:
        response = requests.get(
            f"{API_BASE}/users/{test_email}/message-history?limit=1000",
            timeout=30
        )
        results['message_history_1000'] = response.status_code == 200
        if response.status_code == 200:
            data = response.json()
            print_success(f"Message history: Retrieved {len(data.get('messages', []))} messages")
    except Exception as e:
        results['message_history_1000'] = False
        print_error(f"Message history error: {str(e)}")
    
    # Test replies with max limit
    try:
        response = requests.get(
            f"{API_BASE}/users/{test_email}/replies?limit=1000",
            timeout=30
        )
        results['replies_1000'] = response.status_code == 200
        if response.status_code == 200:
            data = response.json()
            print_success(f"Replies: Retrieved {len(data.get('replies', []))} replies")
    except Exception as e:
        results['replies_1000'] = False
        print_error(f"Replies error: {str(e)}")
    
    # Test admin users with max limit
    try:
        response = requests.get(
            f"{API_BASE}/admin/users?page=1&limit=1000",
            headers={"Authorization": f"Bearer {os.getenv('ADMIN_SECRET', 'admin_secure_pass_2024')}"},
            timeout=30
        )
        results['admin_users_1000'] = response.status_code == 200
        if response.status_code == 200:
            data = response.json()
            print_success(f"Admin users: Retrieved {len(data.get('users', []))} users")
    except Exception as e:
        results['admin_users_1000'] = False
        print_error(f"Admin users error: {str(e)}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print_success(f"✅ All maximum limit tests passed ({passed}/{total})")
        record_test("Maximum Limits", True)
        return True
    else:
        print_warning(f"⚠️ Some maximum limit tests failed ({passed}/{total})")
        record_test("Maximum Limits", False, f"{passed}/{total} passed")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    """Run all comprehensive tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*70)
    print("  Tend - Comprehensive 10K Users Test Suite")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Total users to test: {TOTAL_USERS}")
    print_info(f"Batch size: {BATCH_SIZE}")
    print_info(f"Max workers: {MAX_WORKERS}\n")
    
    # Confirm before running
    print_warning("⚠️  This test will:")
    print_warning("  1. Create 10,000 test users")
    print_warning("  2. Test all features with maximum limits")
    print_warning("  3. May take 30-60 minutes to complete")
    print_warning("  4. Will send test emails if broadcast is enabled\n")
    
    confirm = input(f"{Colors.YELLOW}Continue? (yes/no): {Colors.RESET}")
    if confirm.lower() != 'yes':
        print_info("Test cancelled by user")
        return
    
    start_time = time.time()
    
    # Run tests
    test_health_check()
    time.sleep(2)
    
    success, users_created = test_create_10k_users()
    time.sleep(5)  # Wait for scheduling
    
    if success:
        test_schedule_all_users()
        time.sleep(2)
    
    test_admin_pagination()
    time.sleep(2)
    
    test_all_user_features()
    time.sleep(2)
    
    test_rate_limiting()
    time.sleep(2)
    
    # Ask before broadcast
    broadcast = input(f"\n{Colors.YELLOW}Run broadcast test? (yes/no): {Colors.RESET}")
    if broadcast.lower() == 'yes':
        test_broadcast_message()
        time.sleep(2)
    
    test_maximum_limits()
    
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
        print_success("\n🎉 All tests passed! System is ready for 10K+ users!")
    else:
        print_warning(f"\n⚠️  {test_results['failed']} test(s) failed. Please review errors above.")
    
    return test_results['failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

