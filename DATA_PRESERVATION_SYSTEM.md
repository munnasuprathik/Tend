# InboxInspire - Complete Data Preservation & Versioning System

## 🔒 Core Principle: NEVER DELETE DATA

**Everything is preserved. Forever. With complete history.**

---

## 📊 What's Tracked & Preserved

### 1. **Schedule History** (`schedule_history` collection)
Every time a user changes their schedule, we save:
- ✅ Frequency (daily/weekly/monthly/custom)
- ✅ Exact times (can be multiple)
- ✅ Custom days (for weekly patterns)
- ✅ Custom intervals
- ✅ Timezone (full IANA timezone name)
- ✅ Paused status
- ✅ Skip next flag
- ✅ Version number
- ✅ Changed timestamp
- ✅ Changed by (user/admin/system)
- ✅ Change reason
- ✅ Active status (only latest is active)

**Example:**
```json
{
  "id": "uuid",
  "user_email": "user@example.com",
  "version": 5,
  "frequency": "daily",
  "times": ["09:00", "18:00"],
  "timezone": "America/New_York",
  "paused": false,
  "changed_at": "2025-11-11T17:30:00Z",
  "changed_by": "user",
  "change_reason": "Updated morning time",
  "is_active": true
}
```

### 2. **Personality History** (`personality_history` collection)
Every personality change tracked:
- ✅ Complete personalities array
- ✅ Each personality (type, value, active status)
- ✅ Rotation mode
- ✅ Version number
- ✅ Change timestamp
- ✅ Changed by

### 3. **Profile History** (`profile_history` collection)
Every profile update:
- ✅ Name changes
- ✅ Goals updates
- ✅ Version number
- ✅ Change details (what changed)
- ✅ Timestamp

### 4. **Soft Deletes** (`deleted_data` collection)
"Deleted" data is never deleted:
- ✅ Original collection name
- ✅ Complete document data
- ✅ Deletion timestamp
- ✅ Deleted by (user/admin)
- ✅ Reason for deletion
- ✅ Can restore flag
- ✅ Ability to restore anytime

---

## 🔄 How Versioning Works

### Automatic Version Creation

**When user updates schedule:**
1. Current version marked as `is_active: false`
2. New version created with `version: N+1`
3. New version marked as `is_active: true`
4. Old version preserved forever in history

**When user updates personalities:**
1. Previous personalities saved with version number
2. New set becomes active version
3. Complete history maintained

**When user updates profile:**
1. Previous name/goals saved
2. New values become active
3. Change details tracked

---

## 🚫 Soft Delete System

### How It Works

**Traditional Delete:**
```javascript
// ❌ OLD WAY - Data lost forever
db.collection.delete_one({id: "123"})
```

**Soft Delete:**
```javascript
// ✅ NEW WAY - Data preserved
await version_tracker.soft_delete(
  collection="users",
  document_id="123",
  document_data={...full_document...},
  deleted_by="admin",
  reason="User requested account closure"
)
```

**What Happens:**
1. Document copied to `deleted_data` collection
2. Original document marked `active: false`
3. Deletion metadata saved (who, when, why)
4. Can be restored anytime
5. Original data never touched

---

## 📡 API Endpoints

### View Version History

#### Schedule History
```
GET /api/users/{email}/history/schedule?limit=50
```

Response:
```json
{
  "user_email": "user@example.com",
  "versions": 12,
  "history": [
    {
      "version": 12,
      "frequency": "daily",
      "times": ["09:00"],
      "timezone": "America/New_York",
      "changed_at": "2025-11-11T17:30:00Z",
      "is_active": true
    },
    {
      "version": 11,
      "frequency": "daily",
      "times": ["08:00"],
      "timezone": "America/New_York",
      "changed_at": "2025-11-10T10:15:00Z",
      "is_active": false
    }
  ]
}
```

#### Personality History
```
GET /api/users/{email}/history/personalities?limit=50
```

#### Profile History
```
GET /api/users/{email}/history/profile?limit=50
```

#### Complete History
```
GET /api/users/{email}/history/complete
```
Returns ALL history for a user (schedule + personalities + profile)

### Manage Soft Deletes

#### View Deleted Data
```
GET /api/admin/deleted-data?limit=100
```

Returns all soft-deleted items that can be restored

#### Restore Deleted Data
```
POST /api/admin/restore/{deletion_id}
```

Restores soft-deleted data back to active status

---

## 🔧 Technical Implementation

### When Data Is Saved

**Onboarding:**
- ✅ Initial schedule (version 1)
- ✅ Initial personalities (version 1)
- ✅ Initial profile (version 1)

**Profile Update:**
```python
# Automatically saves version before updating
@api_router.put("/users/{email}")
async def update_user(email, updates):
    # Save history BEFORE updating
    if 'schedule' in updates:
        await version_tracker.save_schedule_version(...)
    
    # Then update actual data
    await db.users.update_one(...)
```

**Delete Operation:**
```python
# Instead of deleting, soft delete
await version_tracker.soft_delete(
    collection="users",
    document_id=user_id,
    document_data=user,
    deleted_by="admin",
    reason="Policy violation"
)
```

---

## 💾 Database Collections

| Collection | Purpose | Size Estimate |
|------------|---------|---------------|
| `schedule_history` | All schedule changes | ~500 bytes per version |
| `personality_history` | All personality changes | ~1KB per version |
| `profile_history` | All profile updates | ~300 bytes per version |
| `deleted_data` | Soft-deleted items | Variable (full document) |

**Storage Efficiency:**
- Only deltas stored (what changed)
- Old versions compressed
- Indexed for fast queries
- Automatic cleanup of very old versions (optional)

---

## 📈 Use Cases

### 1. **User Support**
"Why did my schedule change?"
- View complete schedule history
- See exact times/timezones for each version
- Identify when change happened

### 2. **Debugging**
"Emails not sending at right time?"
- Check schedule history
- Verify timezone changes
- See if user paused/unpaused

### 3. **Compliance**
"User wants data report"
- Export complete history
- Show all changes made
- Provide audit trail

### 4. **Analytics**
"How often do users change schedules?"
- Query version counts
- Analyze change patterns
- Track frequency adjustments

### 5. **Recovery**
"User accidentally deleted account"
- Find in deleted_data
- Restore with one click
- All data intact

---

## 🔍 Querying History

### MongoDB Queries

**Get user's current schedule:**
```javascript
db.schedule_history.findOne({
  user_email: "user@example.com",
  is_active: true
})
```

**Get all schedule versions:**
```javascript
db.schedule_history.find({
  user_email: "user@example.com"
}).sort({version: -1})
```

**Find when timezone changed:**
```javascript
db.schedule_history.find({
  user_email: "user@example.com",
  change_reason: /timezone/i
})
```

**Get deleted users:**
```javascript
db.deleted_data.find({
  collection: "users",
  can_restore: true
})
```

---

## ✅ Benefits

### For Users
- ✅ Can see their complete change history
- ✅ Account recovery if accidentally deleted
- ✅ Transparency in data handling
- ✅ Peace of mind (nothing lost)

### For Admins
- ✅ Complete audit trail
- ✅ Easy debugging
- ✅ Compliance support
- ✅ Restore capabilities

### For Business
- ✅ GDPR compliance (data portability)
- ✅ User behavior insights
- ✅ No data loss scenarios
- ✅ Professional data management

---

## 🔐 Privacy & Compliance

### GDPR Compliance
- ✅ **Right to access**: User can see all their history
- ✅ **Right to portability**: Export complete history
- ✅ **Right to erasure**: Soft delete (can be hard deleted if required)
- ✅ **Audit trail**: Every change logged

### Data Retention
- Active versions: Forever
- Inactive versions: Configurable (default: forever)
- Deleted data: 90 days before permanent deletion (configurable)

---

## 📊 Monitoring Version Growth

**Check version counts:**
```sql
-- Users with most schedule changes
db.schedule_history.aggregate([
  {$group: {
    _id: "$user_email",
    versions: {$sum: 1}
  }},
  {$sort: {versions: -1}},
  {$limit: 10}
])
```

**Storage usage:**
```sql
db.schedule_history.stats()
db.personality_history.stats()
db.profile_history.stats()
```

---

## 🚀 Future Enhancements

- [ ] Version diff viewer (show what changed)
- [ ] Rollback to specific version
- [ ] Automatic version cleanup (>100 versions)
- [ ] Export history as JSON/CSV
- [ ] Visual timeline of changes
- [ ] Compare two versions side-by-side

---

## ✅ Email Sending Status

### FIXED Issues:
1. ✅ **Async/await problem solved**
   - Created `create_email_job()` wrapper function
   - Properly handles async code from synchronous scheduler
   - Uses new event loop for each job

2. ✅ **User-specific emails working**
   - Each user gets their own scheduled job
   - Emails sent only to intended recipient
   - Timezone-aware scheduling

3. ✅ **Tracking integrated**
   - Every scheduled email logged
   - System events tracked
   - Version history saved

### Email Schedule Storage:
- ✅ Frequency stored with each version
- ✅ Timezone stored with each version
- ✅ Exact times stored (can be multiple)
- ✅ Custom patterns preserved
- ✅ Pause/unpause history tracked

---

**Summary: Every piece of data, every change, every schedule update - PRESERVED FOREVER with complete version history.** 📦💾

Nothing is ever truly deleted. Everything can be restored. Complete transparency.
