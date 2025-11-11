"""
Data Versioning & History Tracking System
NEVER DELETE DATA - Always keep history with versions
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import uuid

class ScheduleHistory(BaseModel):
    """Track every schedule change"""
    id: str
    user_email: str
    version: int
    frequency: str
    times: List[str]
    custom_days: Optional[List[str]] = None
    custom_interval: Optional[int] = None
    timezone: str
    paused: bool
    skip_next: bool
    changed_at: datetime
    changed_by: str  # system, user, admin
    change_reason: Optional[str] = None
    is_active: bool = True  # Current version or historical

class PersonalityHistory(BaseModel):
    """Track every personality change"""
    id: str
    user_email: str
    version: int
    personalities: List[Dict[str, Any]]
    rotation_mode: str
    changed_at: datetime
    changed_by: str
    is_active: bool = True

class ProfileHistory(BaseModel):
    """Track every profile update"""
    id: str
    user_email: str
    version: int
    name: str
    goals: str
    changed_at: datetime
    changed_by: str
    change_details: Dict[str, Any] = {}
    is_active: bool = True

class DataDeletion(BaseModel):
    """Track 'deleted' data (soft deletes only)"""
    id: str
    collection: str
    document_id: str
    document_data: Dict[str, Any]
    deleted_at: datetime
    deleted_by: str
    reason: Optional[str] = None
    can_restore: bool = True

class VersionTracker:
    """Manage data versioning and history"""
    
    def __init__(self, db):
        self.db = db
    
    async def save_schedule_version(
        self,
        user_email: str,
        schedule_data: Dict[str, Any],
        changed_by: str = "user",
        change_reason: Optional[str] = None
    ):
        """Save a new version of schedule"""
        # Get current version number
        latest = await self.db.schedule_history.find_one(
            {"user_email": user_email},
            sort=[("version", -1)]
        )
        
        version = (latest.get('version', 0) + 1) if latest else 1
        
        # Mark all previous versions as inactive
        await self.db.schedule_history.update_many(
            {"user_email": user_email, "is_active": True},
            {"$set": {"is_active": False}}
        )
        
        # Save new version
        history = ScheduleHistory(
            id=str(uuid.uuid4()),
            user_email=user_email,
            version=version,
            frequency=schedule_data.get('frequency', 'daily'),
            times=schedule_data.get('times', ['09:00']),
            custom_days=schedule_data.get('custom_days'),
            custom_interval=schedule_data.get('custom_interval'),
            timezone=schedule_data.get('timezone', 'UTC'),
            paused=schedule_data.get('paused', False),
            skip_next=schedule_data.get('skip_next', False),
            changed_at=datetime.now(timezone.utc),
            changed_by=changed_by,
            change_reason=change_reason,
            is_active=True
        )
        
        await self.db.schedule_history.insert_one(history.model_dump())
        return history.id, version
    
    async def save_personality_version(
        self,
        user_email: str,
        personalities: List[Dict],
        rotation_mode: str,
        changed_by: str = "user"
    ):
        """Save a new version of personalities"""
        # Get current version
        latest = await self.db.personality_history.find_one(
            {"user_email": user_email},
            sort=[("version", -1)]
        )
        
        version = (latest.get('version', 0) + 1) if latest else 1
        
        # Mark previous as inactive
        await self.db.personality_history.update_many(
            {"user_email": user_email, "is_active": True},
            {"$set": {"is_active": False}}
        )
        
        # Save new version
        history = PersonalityHistory(
            id=str(uuid.uuid4()),
            user_email=user_email,
            version=version,
            personalities=personalities,
            rotation_mode=rotation_mode,
            changed_at=datetime.now(timezone.utc),
            changed_by=changed_by,
            is_active=True
        )
        
        await self.db.personality_history.insert_one(history.model_dump())
        return history.id, version
    
    async def save_profile_version(
        self,
        user_email: str,
        name: str,
        goals: str,
        changed_by: str = "user",
        change_details: Optional[Dict] = None
    ):
        """Save a new version of profile"""
        latest = await self.db.profile_history.find_one(
            {"user_email": user_email},
            sort=[("version", -1)]
        )
        
        version = (latest.get('version', 0) + 1) if latest else 1
        
        await self.db.profile_history.update_many(
            {"user_email": user_email, "is_active": True},
            {"$set": {"is_active": False}}
        )
        
        history = ProfileHistory(
            id=str(uuid.uuid4()),
            user_email=user_email,
            version=version,
            name=name,
            goals=goals,
            changed_at=datetime.now(timezone.utc),
            changed_by=changed_by,
            change_details=change_details or {},
            is_active=True
        )
        
        await self.db.profile_history.insert_one(history.model_dump())
        return history.id, version
    
    async def soft_delete(
        self,
        collection: str,
        document_id: str,
        document_data: Dict,
        deleted_by: str = "user",
        reason: Optional[str] = None
    ):
        """Soft delete - never actually delete, just mark as deleted"""
        deletion = DataDeletion(
            id=str(uuid.uuid4()),
            collection=collection,
            document_id=document_id,
            document_data=document_data,
            deleted_at=datetime.now(timezone.utc),
            deleted_by=deleted_by,
            reason=reason,
            can_restore=True
        )
        
        await self.db.deleted_data.insert_one(deletion.model_dump())
        
        # Mark as inactive in original collection instead of deleting
        await self.db[collection].update_one(
            {"id": document_id},
            {"$set": {"active": False, "deleted_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return deletion.id
    
    async def get_schedule_history(self, user_email: str, limit: int = 50):
        """Get all schedule versions for a user"""
        history = await self.db.schedule_history.find(
            {"user_email": user_email},
            {"_id": 0}
        ).sort("version", -1).limit(limit).to_list(limit)
        
        # Convert datetime to ISO string
        for h in history:
            if isinstance(h.get('changed_at'), datetime):
                h['changed_at'] = h['changed_at'].isoformat()
        
        return history
    
    async def get_personality_history(self, user_email: str, limit: int = 50):
        """Get all personality versions for a user"""
        history = await self.db.personality_history.find(
            {"user_email": user_email},
            {"_id": 0}
        ).sort("version", -1).limit(limit).to_list(limit)
        
        for h in history:
            if isinstance(h.get('changed_at'), datetime):
                h['changed_at'] = h['changed_at'].isoformat()
        
        return history
    
    async def get_profile_history(self, user_email: str, limit: int = 50):
        """Get all profile versions for a user"""
        history = await self.db.profile_history.find(
            {"user_email": user_email},
            {"_id": 0}
        ).sort("version", -1).limit(limit).to_list(limit)
        
        for h in history:
            if isinstance(h.get('changed_at'), datetime):
                h['changed_at'] = h['changed_at'].isoformat()
        
        return history
    
    async def get_all_user_history(self, user_email: str):
        """Get complete change history for a user"""
        schedule_hist = await self.get_schedule_history(user_email, 100)
        personality_hist = await self.get_personality_history(user_email, 100)
        profile_hist = await self.get_profile_history(user_email, 100)
        
        return {
            "user_email": user_email,
            "schedule_versions": len(schedule_hist),
            "personality_versions": len(personality_hist),
            "profile_versions": len(profile_hist),
            "schedule_history": schedule_hist,
            "personality_history": personality_hist,
            "profile_history": profile_hist
        }
    
    async def restore_deleted(self, deletion_id: str):
        """Restore soft-deleted data"""
        deletion = await self.db.deleted_data.find_one({"id": deletion_id})
        
        if not deletion or not deletion.get('can_restore'):
            return False
        
        # Restore in original collection
        await self.db[deletion['collection']].update_one(
            {"id": deletion['document_id']},
            {
                "$set": {"active": True},
                "$unset": {"deleted_at": ""}
            }
        )
        
        # Mark deletion as restored
        await self.db.deleted_data.update_one(
            {"id": deletion_id},
            {"$set": {"can_restore": False, "restored_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return True
