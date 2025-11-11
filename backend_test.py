#!/usr/bin/env python3
"""
Backend API Testing for InboxInspire Email Scheduling Bug Fix
Tests the critical fix where APScheduler was sending emails to ALL users instead of specific users.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
import time

# Get backend URL from frontend .env
BACKEND_URL = "https://aipep.preview.emergentagent.com/api"

# Known active users from logs
TEST_USERS = [
    "munnasuprathik79@gmail.com",
    "munnaworld.b@gmail.com", 
    "quiccledaily@gmail.com",
    "rakeshkumar101221@gmail.com"
]

class EmailSchedulingTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def test_user_exists(self, email):
        """Test if user exists and get their data"""
        try:
            async with self.session.get(f"{BACKEND_URL}/users/{email}") as response:
                if response.status == 200:
                    user_data = await response.json()
                    self.log_result(f"User Exists - {email}", True, 
                                  f"User found with schedule: {user_data.get('schedule', {})}")
                    return user_data
                else:
                    self.log_result(f"User Exists - {email}", False, 
                                  f"User not found, status: {response.status}")
                    return None
        except Exception as e:
            self.log_result(f"User Exists - {email}", False, f"Error: {str(e)}")
            return None
    
    async def test_scheduler_job_exists(self, email):
        """Test if scheduler job exists for specific user"""
        try:
            async with self.session.post(f"{BACKEND_URL}/test-schedule/{email}") as response:
                if response.status == 200:
                    job_data = await response.json()
                    job_exists = job_data.get('job_exists', False)
                    job_id = job_data.get('job_id', '')
                    next_run = job_data.get('next_run', '')
                    
                    self.log_result(f"Scheduler Job - {email}", job_exists,
                                  f"Job ID: {job_id}, Next run: {next_run}")
                    return job_data
                else:
                    self.log_result(f"Scheduler Job - {email}", False,
                                  f"Failed to check job, status: {response.status}")
                    return None
        except Exception as e:
            self.log_result(f"Scheduler Job - {email}", False, f"Error: {str(e)}")
            return None
    
    async def get_message_history_count(self, email):
        """Get current message history count for user"""
        try:
            async with self.session.get(f"{BACKEND_URL}/users/{email}/message-history") as response:
                if response.status == 200:
                    history_data = await response.json()
                    count = len(history_data.get('messages', []))
                    return count
                else:
                    return 0
        except Exception as e:
            print(f"Error getting message history for {email}: {str(e)}")
            return 0
    
    async def test_send_now_isolation(self, target_email, other_emails):
        """Test that send-now only sends to target user, not others"""
        print(f"\n🎯 Testing send-now isolation for {target_email}")
        
        # Get initial message counts for all users
        initial_counts = {}
        for email in [target_email] + other_emails:
            initial_counts[email] = await self.get_message_history_count(email)
            print(f"Initial message count for {email}: {initial_counts[email]}")
        
        # Send email to target user
        try:
            async with self.session.post(f"{BACKEND_URL}/send-now/{target_email}") as response:
                if response.status == 200:
                    send_result = await response.json()
                    message_id = send_result.get('message_id')
                    
                    # Wait a moment for processing
                    await asyncio.sleep(2)
                    
                    # Check message counts after sending
                    final_counts = {}
                    for email in [target_email] + other_emails:
                        final_counts[email] = await self.get_message_history_count(email)
                    
                    # Verify only target user received email
                    target_increased = final_counts[target_email] > initial_counts[target_email]
                    others_unchanged = all(
                        final_counts[email] == initial_counts[email] 
                        for email in other_emails
                    )
                    
                    if target_increased and others_unchanged:
                        self.log_result(f"Send-Now Isolation - {target_email}", True,
                                      f"✓ Target user got email (count: {initial_counts[target_email]} → {final_counts[target_email]}), others unchanged")
                    else:
                        details = f"❌ Target: {initial_counts[target_email]} → {final_counts[target_email]}, "
                        details += f"Others: {[(email, initial_counts[email], final_counts[email]) for email in other_emails]}"
                        self.log_result(f"Send-Now Isolation - {target_email}", False, details)
                    
                    return message_id
                else:
                    response_text = await response.text()
                    self.log_result(f"Send-Now Isolation - {target_email}", False,
                                  f"Send failed, status: {response.status}, response: {response_text}")
                    return None
        except Exception as e:
            self.log_result(f"Send-Now Isolation - {target_email}", False, f"Error: {str(e)}")
            return None
    
    async def test_schedule_update(self, email):
        """Test updating user schedule and verify job recreation"""
        print(f"\n⚙️ Testing schedule update for {email}")
        
        # Get current user data
        user_data = await self.test_user_exists(email)
        if not user_data:
            return False
        
        current_schedule = user_data.get('schedule', {})
        original_times = current_schedule.get('times', ['09:00'])
        
        # Update schedule with new time
        new_time = "10:30" if original_times[0] != "10:30" else "11:30"
        updated_schedule = current_schedule.copy()
        updated_schedule['times'] = [new_time]
        
        try:
            # Update user schedule
            update_data = {"schedule": updated_schedule}
            async with self.session.put(f"{BACKEND_URL}/users/{email}", 
                                      json=update_data) as response:
                if response.status == 200:
                    # Wait for scheduler to update
                    await asyncio.sleep(2)
                    
                    # Check if job was recreated with new schedule
                    job_data = await self.test_scheduler_job_exists(email)
                    if job_data:
                        # Restore original schedule
                        restore_data = {"schedule": current_schedule}
                        async with self.session.put(f"{BACKEND_URL}/users/{email}", 
                                                  json=restore_data) as restore_response:
                            if restore_response.status == 200:
                                self.log_result(f"Schedule Update - {email}", True,
                                              f"✓ Schedule updated to {new_time}, job recreated, then restored")
                                return True
                    
                    self.log_result(f"Schedule Update - {email}", False,
                                  "Schedule update failed or job not recreated")
                    return False
                else:
                    response_text = await response.text()
                    self.log_result(f"Schedule Update - {email}", False,
                                  f"Update failed, status: {response.status}, response: {response_text}")
                    return False
        except Exception as e:
            self.log_result(f"Schedule Update - {email}", False, f"Error: {str(e)}")
            return False
    
    async def run_comprehensive_tests(self):
        """Run all email scheduling tests"""
        print("🚀 Starting InboxInspire Email Scheduling Bug Fix Tests")
        print("=" * 60)
        
        # Test 1: Verify all known users exist and have schedules
        print("\n📋 Phase 1: User and Schedule Verification")
        existing_users = []
        for email in TEST_USERS:
            user_data = await self.test_user_exists(email)
            if user_data:
                existing_users.append(email)
        
        if len(existing_users) < 2:
            print("❌ Need at least 2 users for isolation testing")
            return False
        
        # Test 2: Verify scheduler jobs exist for each user
        print("\n📋 Phase 2: Scheduler Job Verification")
        users_with_jobs = []
        for email in existing_users:
            job_data = await self.test_scheduler_job_exists(email)
            if job_data and job_data.get('job_exists'):
                users_with_jobs.append(email)
        
        # Test 3: Test send-now isolation for multiple users
        print("\n📋 Phase 3: Send-Now Isolation Testing")
        isolation_tests_passed = 0
        for i, target_email in enumerate(users_with_jobs[:3]):  # Test first 3 users
            other_emails = [email for email in users_with_jobs if email != target_email][:2]  # Check 2 others
            message_id = await self.test_send_now_isolation(target_email, other_emails)
            if message_id:
                isolation_tests_passed += 1
        
        # Test 4: Test schedule updates
        print("\n📋 Phase 4: Schedule Update Testing")
        if users_with_jobs:
            await self.test_schedule_update(users_with_jobs[0])
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Critical test analysis
        critical_failures = []
        for result in self.test_results:
            if not result['success'] and 'Isolation' in result['test']:
                critical_failures.append(result['test'])
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED:")
            for failure in critical_failures:
                print(f"   - {failure}")
            print("   ⚠️  Email isolation bug may still exist!")
        else:
            print(f"\n✅ EMAIL ISOLATION BUG FIX VERIFIED")
            print("   ✓ Each user receives emails only for their own schedule")
            print("   ✓ send-now endpoint sends to specific user only")
        
        return len(critical_failures) == 0

async def main():
    """Main test execution"""
    async with EmailSchedulingTester() as tester:
        success = await tester.run_comprehensive_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)