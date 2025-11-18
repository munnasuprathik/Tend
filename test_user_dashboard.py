#!/usr/bin/env python3
"""
Comprehensive Test Script for Tend User Dashboard
Tests all user-facing features and endpoints
"""

import requests
import json
import time
import sys
from typing import Dict, Optional
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Test user email (change this to your test email)
TEST_EMAIL = "test@example.com"
TEST_NAME = "Test User"
TEST_GOALS = "Build a successful startup and achieve financial freedom"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def test_health_check():
    """Test 1: Health Check Endpoint"""
    print_header("TEST 1: Health Check Endpoint")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data.get('status', 'unknown')}")
            print_info(f"Database: {data.get('database', 'unknown')}")
            print_info(f"OpenAI: {data.get('openai', 'unknown')}")
            print_info(f"SMTP: {data.get('smtp', 'unknown')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            print_error(response.text)
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_login():
    """Test 2: Login (Magic Link)"""
    print_header("TEST 2: Login - Send Magic Link")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Login link sent: {data.get('message', '')}")
            print_info(f"User exists: {data.get('user_exists', False)}")
            return True, data.get('user_exists', False)
        elif response.status_code == 429:
            print_warning("Rate limit hit - waiting 60 seconds...")
            time.sleep(60)
            return test_login()
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(response.text)
            return False, False
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return False, False

def test_verify_token(token: str):
    """Test 3: Verify Token"""
    print_header("TEST 3: Verify Token")
    try:
        response = requests.post(
            f"{API_BASE}/auth/verify",
            json={"email": TEST_EMAIL, "token": token},
            timeout=10
        )
        if response.status_code == 200:
            print_success("Token verified successfully")
            return True
        else:
            print_error(f"Token verification failed: {response.status_code}")
            print_error(response.text)
            return False
    except Exception as e:
        print_error(f"Token verification error: {str(e)}")
        return False

def test_get_user():
    """Test 4: Get User Profile"""
    print_header("TEST 4: Get User Profile")
    try:
        response = requests.get(f"{API_BASE}/users/{TEST_EMAIL}", timeout=10)
        if response.status_code == 200:
            user = response.json()
            print_success("User profile retrieved")
            print_info(f"Name: {user.get('name', 'N/A')}")
            print_info(f"Active: {user.get('active', False)}")
            print_info(f"Streak: {user.get('streak_count', 0)} days")
            print_info(f"Total Messages: {user.get('total_messages_received', 0)}")
            return True, user
        elif response.status_code == 404:
            print_warning("User not found - needs onboarding")
            return False, None
        else:
            print_error(f"Get user failed: {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Get user error: {str(e)}")
        return False, None

def test_onboarding():
    """Test 5: Complete Onboarding"""
    print_header("TEST 5: Complete Onboarding")
    try:
        onboarding_data = {
            "email": TEST_EMAIL,
            "name": TEST_NAME,
            "goals": TEST_GOALS,
            "personalities": [
                {"type": "famous", "value": "Elon Musk"}
            ],
            "rotation_mode": "sequential",
            "schedule": {
                "frequency": "daily",
                "times": ["09:00"],
                "timezone": "UTC",
                "paused": False
            },
            "user_timezone": "UTC"
        }
        response = requests.post(
            f"{API_BASE}/onboarding",
            json=onboarding_data,
            timeout=10
        )
        if response.status_code == 200:
            print_success("Onboarding completed successfully")
            return True
        else:
            print_error(f"Onboarding failed: {response.status_code}")
            print_error(response.text)
            return False
    except Exception as e:
        print_error(f"Onboarding error: {str(e)}")
        return False

def test_generate_message():
    """Test 6: Generate Message Preview"""
    print_header("TEST 6: Generate Message Preview")
    try:
        message_data = {
            "goals": TEST_GOALS,
            "personality": {"type": "famous", "value": "Elon Musk"},
            "user_name": TEST_NAME
        }
        response = requests.post(
            f"{API_BASE}/generate-message",
            json=message_data,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Message generated successfully")
            print_info(f"Message preview: {data.get('message', '')[:100]}...")
            print_info(f"Used fallback: {data.get('used_fallback', False)}")
            return True, data.get('message', '')
        elif response.status_code == 429:
            print_warning("Rate limit hit - waiting 60 seconds...")
            time.sleep(60)
            return test_generate_message()
        else:
            print_error(f"Generate message failed: {response.status_code}")
            print_error(response.text)
            return False, None
    except Exception as e:
        print_error(f"Generate message error: {str(e)}")
        return False, None

def test_send_now():
    """Test 7: Send Instant Motivation"""
    print_header("TEST 7: Send Instant Motivation")
    try:
        response = requests.post(
            f"{API_BASE}/send-now/{TEST_EMAIL}",
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Instant motivation sent")
            print_info(f"Message: {data.get('message', '')}")
            return True
        elif response.status_code == 429:
            print_warning("Rate limit hit - waiting 60 seconds...")
            time.sleep(60)
            return test_send_now()
        else:
            print_error(f"Send now failed: {response.status_code}")
            print_error(response.text)
            return False
    except Exception as e:
        print_error(f"Send now error: {str(e)}")
        return False

def test_get_message_history():
    """Test 8: Get Message History"""
    print_header("TEST 8: Get Message History")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/message-history",
            params={"limit": 10},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            print_success(f"Retrieved {len(messages)} messages")
            if messages:
                latest = messages[0]
                print_info(f"Latest message: {latest.get('subject', 'N/A')}")
                print_info(f"Sent at: {latest.get('sent_at', 'N/A')}")
            return True, messages
        else:
            print_error(f"Get message history failed: {response.status_code}")
            return False, []
    except Exception as e:
        print_error(f"Get message history error: {str(e)}")
        return False, []

def test_get_goals():
    """Test 9: Get User Goals"""
    print_header("TEST 9: Get User Goals")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/goals",
            timeout=10
        )
        if response.status_code == 200:
            goals = response.json()
            print_success(f"Retrieved {len(goals)} goals")
            for goal in goals[:3]:  # Show first 3
                print_info(f"Goal: {goal.get('title', 'N/A')} - Active: {goal.get('active', False)}")
            return True, goals
        else:
            print_error(f"Get goals failed: {response.status_code}")
            return False, []
    except Exception as e:
        print_error(f"Get goals error: {str(e)}")
        return False, []

def test_create_goal():
    """Test 10: Create Goal"""
    print_header("TEST 10: Create Goal")
    try:
        goal_data = {
            "title": "Test Goal - Learn Python",
            "description": "Master Python programming in 30 days",
            "mode": "personality",
            "personality_id": "Elon Musk",
            "schedules": [
                {
                    "type": "daily",
                    "times": ["10:00"],
                    "timezone": "UTC",
                    "active": True
                }
            ],
            "active": True,
            "category": "Learning",
            "priority": "high"
        }
        response = requests.post(
            f"{API_BASE}/users/{TEST_EMAIL}/goals",
            json=goal_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Goal created: {data.get('goal', {}).get('title', 'N/A')}")
            return True, data.get('goal', {}).get('id')
        else:
            print_error(f"Create goal failed: {response.status_code}")
            print_error(response.text)
            return False, None
    except Exception as e:
        print_error(f"Create goal error: {str(e)}")
        return False, None

def test_get_analytics():
    """Test 11: Get User Analytics"""
    print_header("TEST 11: Get User Analytics")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/analytics",
            timeout=10
        )
        if response.status_code == 200:
            analytics = response.json()
            print_success("Analytics retrieved")
            print_info(f"Streak: {analytics.get('streak_count', 0)} days")
            print_info(f"Total Messages: {analytics.get('total_messages', 0)}")
            print_info(f"Favorite Personality: {analytics.get('favorite_personality', 'N/A')}")
            print_info(f"Average Rating: {analytics.get('avg_rating', 'N/A')}")
            return True, analytics
        else:
            print_error(f"Get analytics failed: {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Get analytics error: {str(e)}")
        return False, None

def test_get_achievements():
    """Test 12: Get User Achievements"""
    print_header("TEST 12: Get User Achievements")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/achievements",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            achievements = data.get('achievements', [])
            print_success(f"Retrieved {len(achievements)} achievements")
            for ach in achievements[:5]:  # Show first 5
                print_info(f"Achievement: {ach.get('name', 'N/A')}")
            return True, achievements
        else:
            print_error(f"Get achievements failed: {response.status_code}")
            return False, []
    except Exception as e:
        print_error(f"Get achievements error: {str(e)}")
        return False, []

def test_update_user():
    """Test 13: Update User Profile"""
    print_header("TEST 13: Update User Profile")
    try:
        update_data = {
            "name": f"{TEST_NAME} (Updated)",
            "goals": f"{TEST_GOALS} - Updated at {datetime.now().isoformat()}"
        }
        response = requests.put(
            f"{API_BASE}/users/{TEST_EMAIL}",
            json=update_data,
            timeout=10
        )
        if response.status_code == 200:
            print_success("User profile updated")
            return True
        else:
            print_error(f"Update user failed: {response.status_code}")
            print_error(response.text)
            return False
    except Exception as e:
        print_error(f"Update user error: {str(e)}")
        return False

def test_get_streak_status():
    """Test 14: Get Streak Status"""
    print_header("TEST 14: Get Streak Status")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/streak-status",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Streak status retrieved")
            print_info(f"Current Streak: {data.get('current_streak', 0)} days")
            print_info(f"Last Message Date: {data.get('last_message_date', 'N/A')}")
            return True
        else:
            print_error(f"Get streak status failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get streak status error: {str(e)}")
        return False

def test_get_personalities():
    """Test 15: Get Available Personalities"""
    print_header("TEST 15: Get Available Personalities")
    try:
        # Test famous personalities
        response = requests.get(f"{API_BASE}/famous-personalities", timeout=10)
        if response.status_code == 200:
            personalities = response.json()
            print_success(f"Retrieved {len(personalities)} famous personalities")
            print_info(f"Sample: {', '.join(personalities[:5])}")
        
        # Test tone options
        response = requests.get(f"{API_BASE}/tone-options", timeout=10)
        if response.status_code == 200:
            tones = response.json()
            print_success(f"Retrieved {len(tones)} tone options")
            print_info(f"Sample: {', '.join(tones[:5])}")
        
        return True
    except Exception as e:
        print_error(f"Get personalities error: {str(e)}")
        return False

def test_rate_limiting():
    """Test 16: Test Rate Limiting"""
    print_header("TEST 16: Test Rate Limiting")
    print_info("Attempting 6 login requests in quick succession...")
    success_count = 0
    rate_limited = False
    
    for i in range(6):
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": f"ratelimit_test_{i}@example.com"},
                timeout=5
            )
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                print_warning(f"Request {i+1}: Rate limited (expected)")
                break
            time.sleep(0.5)
        except Exception as e:
            print_error(f"Request {i+1} error: {str(e)}")
    
    if rate_limited:
        print_success("Rate limiting is working correctly!")
        return True
    else:
        print_warning(f"Rate limiting not triggered (got {success_count} successful requests)")
        return False

def test_weekly_analytics():
    """Test 17: Get Weekly Analytics"""
    print_header("TEST 17: Get Weekly Analytics")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/analytics/weekly",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Weekly analytics retrieved")
            print_info(f"Period: {data.get('period', 'N/A')}")
            return True
        else:
            print_error(f"Get weekly analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get weekly analytics error: {str(e)}")
        return False

def test_monthly_analytics():
    """Test 18: Get Monthly Analytics"""
    print_header("TEST 18: Get Monthly Analytics")
    try:
        response = requests.get(
            f"{API_BASE}/users/{TEST_EMAIL}/analytics/monthly",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Monthly analytics retrieved")
            print_info(f"Period: {data.get('period', 'N/A')}")
            return True
        else:
            print_error(f"Get monthly analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get monthly analytics error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("  Tend User Dashboard - Comprehensive Test Suite")
    print("="*60)
    print(f"{Colors.RESET}\n")
    
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test email: {TEST_EMAIL}")
    print_info(f"Test name: {TEST_NAME}\n")
    
    results = {}
    
    # Test 1: Health Check
    results['health_check'] = test_health_check()
    time.sleep(1)
    
    # Test 2: Login
    login_success, user_exists = test_login()
    results['login'] = login_success
    time.sleep(1)
    
    # Test 3: Get User (or Onboard if new)
    user_success, user = test_get_user()
    results['get_user'] = user_success
    
    if not user_success:
        print_warning("User doesn't exist - running onboarding...")
        results['onboarding'] = test_onboarding()
        time.sleep(1)
        user_success, user = test_get_user()
        results['get_user'] = user_success
    
    time.sleep(1)
    
    # Test 4: Generate Message
    results['generate_message'] = test_generate_message()[0]
    time.sleep(2)
    
    # Test 5: Send Now
    results['send_now'] = test_send_now()
    time.sleep(2)
    
    # Test 6: Message History
    results['message_history'] = test_get_message_history()[0]
    time.sleep(1)
    
    # Test 7: Get Goals
    results['get_goals'] = test_get_goals()[0]
    time.sleep(1)
    
    # Test 8: Create Goal
    results['create_goal'] = test_create_goal()[0]
    time.sleep(1)
    
    # Test 9: Analytics
    results['analytics'] = test_get_analytics()[0]
    time.sleep(1)
    
    # Test 10: Achievements
    results['achievements'] = test_get_achievements()[0]
    time.sleep(1)
    
    # Test 11: Update User
    results['update_user'] = test_update_user()
    time.sleep(1)
    
    # Test 12: Streak Status
    results['streak_status'] = test_get_streak_status()
    time.sleep(1)
    
    # Test 13: Personalities
    results['personalities'] = test_get_personalities()
    time.sleep(1)
    
    # Test 14: Weekly Analytics
    results['weekly_analytics'] = test_weekly_analytics()
    time.sleep(1)
    
    # Test 15: Monthly Analytics
    results['monthly_analytics'] = test_monthly_analytics()
    time.sleep(1)
    
    # Test 16: Rate Limiting
    results['rate_limiting'] = test_rate_limiting()
    time.sleep(2)
    
    # Print Summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    print(f"\n{Colors.BOLD}Total Tests: {total_tests}{Colors.RESET}")
    print_success(f"Passed: {passed_tests}")
    if failed_tests > 0:
        print_error(f"Failed: {failed_tests}")
    
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.RESET}")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status}{Colors.RESET} - {test_name}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}\n")
    
    if failed_tests == 0:
        print_success("🎉 All tests passed! Dashboard is working correctly.")
    else:
        print_warning(f"⚠️  {failed_tests} test(s) failed. Please review the errors above.")
    
    return failed_tests == 0

if __name__ == "__main__":
    # Check if custom email provided
    if len(sys.argv) > 1:
        TEST_EMAIL = sys.argv[1]
        print_info(f"Using custom test email: {TEST_EMAIL}")
    
    success = main()
    sys.exit(0 if success else 1)

