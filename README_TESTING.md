# User Dashboard Testing Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install requests
```

### 2. Configure Test Email
Edit `test_user_dashboard.py` and change:
```python
TEST_EMAIL = "your-test-email@example.com"
TEST_NAME = "Your Name"
```

Or pass it as argument:
```bash
python test_user_dashboard.py your-email@example.com
```

### 3. Start Backend Server
```bash
cd backend
python run.py
```

### 4. Run Tests
```bash
python test_user_dashboard.py
```

---

## What Gets Tested

The script tests **18 different features**:

### Core Features
1. ✅ **Health Check** - Backend health status
2. ✅ **Login** - Magic link authentication
3. ✅ **Get User** - Retrieve user profile
4. ✅ **Onboarding** - Complete user setup (if new user)
5. ✅ **Generate Message** - Preview message generation
6. ✅ **Send Now** - Instant motivation email
7. ✅ **Message History** - View past messages
8. ✅ **Get Goals** - List user goals
9. ✅ **Create Goal** - Add new goal
10. ✅ **Analytics** - User statistics
11. ✅ **Achievements** - Unlocked achievements
12. ✅ **Update User** - Modify profile
13. ✅ **Streak Status** - Current streak info
14. ✅ **Personalities** - Available personalities
15. ✅ **Weekly Analytics** - 7-day reports
16. ✅ **Monthly Analytics** - 30-day reports
17. ✅ **Rate Limiting** - Verify rate limits work

---

## Test Output

The script provides:
- ✅ **Color-coded results** (green=pass, red=fail)
- ✅ **Detailed information** for each test
- ✅ **Summary report** at the end
- ✅ **Success rate** percentage

### Example Output:
```
✅ Health check passed: healthy
✅ Login link sent
✅ User profile retrieved
✅ Message generated successfully
...
```

---

## Customization

### Change Base URL
```python
BASE_URL = "http://localhost:8000"  # Change to your server URL
```

### Adjust Test Data
```python
TEST_EMAIL = "your-email@example.com"
TEST_NAME = "Your Name"
TEST_GOALS = "Your goals here"
```

### Skip Specific Tests
Comment out test calls in `main()` function:
```python
# results['rate_limiting'] = test_rate_limiting()  # Skip this test
```

---

## Troubleshooting

### Connection Errors
- Make sure backend server is running
- Check `BASE_URL` is correct
- Verify firewall/network settings

### Rate Limiting
- If rate limited, script waits 60 seconds automatically
- Adjust rate limits in `backend/server.py` if needed

### Authentication Issues
- Make sure test email is valid
- Check magic link email if login fails
- Verify token if using manual verification

### Timeout Errors
- Increase timeout values in test functions
- Check server performance
- Verify database connectivity

---

## Advanced Usage

### Test Specific Feature Only
Modify `main()` to run only one test:
```python
def main():
    results['health_check'] = test_health_check()
    # Only test health check
```

### Continuous Testing
Add loop for continuous testing:
```python
while True:
    main()
    time.sleep(300)  # Wait 5 minutes
```

### Export Results
Add JSON export:
```python
import json
with open('test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## Expected Results

### All Tests Should Pass If:
- ✅ Backend server is running
- ✅ Database is connected
- ✅ OpenAI API key is valid
- ✅ SMTP is configured
- ✅ Test email is accessible

### Common Failures:
- **404 errors**: User doesn't exist (onboarding will run)
- **429 errors**: Rate limiting working (expected)
- **500 errors**: Server/database issues
- **Timeout**: Slow API responses

---

## Integration with CI/CD

Add to your CI pipeline:
```yaml
# .github/workflows/test.yml
- name: Run Dashboard Tests
  run: |
    python test_user_dashboard.py test@example.com
```

---

## Notes

- Tests are **non-destructive** (won't delete data)
- Some tests create test data (goals, etc.)
- Rate limiting test intentionally triggers limits
- All tests use the same test email

---

## Support

If tests fail:
1. Check backend logs
2. Verify environment variables
3. Test endpoints manually with curl
4. Review error messages in test output

