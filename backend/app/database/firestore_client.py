"""
Firestore Database Client
Production client for Google Cloud Firestore with safe fallback for local offline prototyping.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("memorybox.database")


class FirestoreClient:
    def __init__(self):
        self.client = None
        self._is_mock = False
        self._mock_memories: Dict[str, Dict[str, Any]] = {}
        self._mock_sessions: Dict[str, Dict[str, Any]] = {}
        self._mock_custodians: Dict[str, Dict[str, Any]] = {}
        self._mock_users: Dict[str, Dict[str, Any]] = {}
        self._mock_otps: Dict[str, Dict[str, Any]] = {}
        self._mock_audit_logs: List[Dict[str, Any]] = []
        self._initialize()

    def _initialize(self):
        try:
            from google.cloud import firestore
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("FIREBASE_PROJECT_ID")
            if project_id and (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CREDENTIALS_PATH")):
                self.client = firestore.Client(project=project_id)
                logger.info(f"Connected to Cloud Firestore project: {project_id}")
            else:
                try:
                    # Attempt Application Default Credentials (Cloud Run environment)
                    self.client = firestore.Client()
                    logger.info("Connected to Cloud Firestore via Application Default Credentials.")
                except Exception as adc_err:
                    logger.warning(f"ADC not detected ({adc_err}). Enabling high-performance MemoryVault local repository.")
                    self._is_mock = True
        except Exception as e:
            logger.warning(f"Firestore SDK initialization error ({e}). Using resilient in-memory datastore.")
            self._is_mock = True

    # --- Memory Operations ---

    async def save_memory(self, memory_dict: Dict[str, Any]) -> str:
        memory_id = memory_dict.get("id")
        if not memory_id:
            import uuid
            memory_id = f"mem_{uuid.uuid4().hex[:12]}"
            memory_dict["id"] = memory_id

        if not self._is_mock and self.client:
            try:
                doc_ref = self.client.collection("memories").document(memory_id)
                doc_ref.set(memory_dict, merge=True)
                return memory_id
            except Exception as e:
                logger.error(f"Firestore save error: {e}. Falling back to resilient storage.")

        # Fallback / Local
        self._mock_memories[memory_id] = memory_dict
        return memory_id

    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        if not self._is_mock and self.client:
            try:
                doc_ref = self.client.collection("memories").document(memory_id)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore get error: {e}")

        return self._mock_memories.get(memory_id)

    async def list_memories(
        self,
        user_id: str,
        era: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        if not self._is_mock and self.client:
            try:
                from google.cloud.firestore import FieldFilter
                query = self.client.collection("memories").where(filter=FieldFilter("user_id", "==", user_id))
                if era and era != "All":
                    query = query.where(filter=FieldFilter("era", "==", era))
                docs = query.order_by("created_at", direction="DESCENDING").limit(limit).stream()
                results = [d.to_dict() for d in docs]
                if tag:
                    results = [r for r in results if tag in r.get("tags", [])]
                return results
            except Exception as e:
                logger.warning(f"Firestore list error: {e}. Reading from local memory store.")

        # Fallback
        results = [m for m in self._mock_memories.values() if m.get("user_id") == user_id]
        if era and era != "All":
            results = [r for r in results if r.get("era") == era]
        if tag:
            results = [r for r in results if tag in r.get("tags", [])]
        results.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return results[:limit]

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        if not self._is_mock and self.client:
            try:
                doc_ref = self.client.collection("memories").document(memory_id)
                doc = doc_ref.get()
                if doc.exists and doc.to_dict().get("user_id") == user_id:
                    doc_ref.delete()
                    return True
                return False
            except Exception as e:
                logger.error(f"Firestore delete error: {e}")

        if memory_id in self._mock_memories and self._mock_memories[memory_id].get("user_id") == user_id:
            del self._mock_memories[memory_id]
            return True
        return False

    # --- Interview Session Operations ---

    async def save_interview_session(self, session_dict: Dict[str, Any]) -> str:
        session_id = session_dict["session_id"]
        if not self._is_mock and self.client:
            try:
                self.client.collection("interview_sessions").document(session_id).set(session_dict)
                return session_id
            except Exception as e:
                logger.error(f"Firestore save session error: {e}")

        self._mock_sessions[session_id] = session_dict
        return session_id

    async def get_interview_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self._is_mock and self.client:
            try:
                doc = self.client.collection("interview_sessions").document(session_id).get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore get session error: {e}")

        return self._mock_sessions.get(session_id)

    async def update_interview_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        updates["updated_at"] = datetime.utcnow()
        if not self._is_mock and self.client:
            try:
                self.client.collection("interview_sessions").document(session_id).update(updates)
                return True
            except Exception as e:
                logger.error(f"Firestore update session error: {e}")

        if session_id in self._mock_sessions:
            self._mock_sessions[session_id].update(updates)
            return True
        return False

    async def delete_interview_session(self, session_id: str) -> bool:
        if not self._is_mock and self.client:
            try:
                self.client.collection("interview_sessions").document(session_id).delete()
                return True
            except Exception as e:
                logger.error(f"Firestore delete session error: {e}")

        if session_id in self._mock_sessions:
            del self._mock_sessions[session_id]
            return True
        return False

    # --- Governance: Custodian & Legacy Handover ---

    async def save_custodian(self, user_id: str, custodian_dict: Dict[str, Any]) -> bool:
        if not self._is_mock and self.client:
            try:
                self.client.collection("custodians").document(user_id).set(custodian_dict)
                return True
            except Exception as e:
                logger.error(f"Firestore custodian save error: {e}")

        self._mock_custodians[user_id] = custodian_dict
        return True

    async def get_custodian(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self._is_mock and self.client:
            try:
                doc = self.client.collection("custodians").document(user_id).get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore custodian get error: {e}")

        return self._mock_custodians.get(user_id)

    # --- User Management (Firebase Auth + Firestore) ---

    async def save_user(self, uid: str, user_dict: Dict[str, Any]) -> str:
        if not self._is_mock and self.client:
            try:
                self.client.collection("users").document(uid).set(user_dict, merge=True)
                return uid
            except Exception as e:
                logger.error(f"Firestore save user error: {e}")

        self._mock_users[uid] = user_dict
        return uid

    async def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        if not self._is_mock and self.client:
            try:
                doc = self.client.collection("users").document(uid).get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore get user error: {e}")

        return self._mock_users.get(uid)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        clean_email = email.strip().lower()
        if not self._is_mock and self.client:
            try:
                from google.cloud.firestore import FieldFilter
                docs = self.client.collection("users").where(
                    filter=FieldFilter("email", "==", clean_email)
                ).limit(1).stream()
                for d in docs:
                    return d.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore query email error: {e}")

        for u in self._mock_users.values():
            if u.get("email", "").strip().lower() == clean_email:
                return u
        return None

    async def update_user(self, uid: str, updates: Dict[str, Any]) -> bool:
        if not self._is_mock and self.client:
            try:
                self.client.collection("users").document(uid).update(updates)
                return True
            except Exception as e:
                logger.error(f"Firestore update user error: {e}")

        if uid in self._mock_users:
            self._mock_users[uid].update(updates)
            return True
        return False

    # --- Dual-Channel 2FA OTP Storage ---

    async def save_otp(self, uid: str, otp_data: Dict[str, Any]) -> bool:
        if not self._is_mock and self.client:
            try:
                self.client.collection("otps").document(uid).set(otp_data)
                return True
            except Exception as e:
                logger.error(f"Firestore save OTP error: {e}")

        self._mock_otps[uid] = otp_data
        return True

    async def get_otp(self, uid: str) -> Optional[Dict[str, Any]]:
        if not self._is_mock and self.client:
            try:
                doc = self.client.collection("otps").document(uid).get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore get OTP error: {e}")

        return self._mock_otps.get(uid)

    async def delete_otp(self, uid: str) -> bool:
        if not self._is_mock and self.client:
            try:
                self.client.collection("otps").document(uid).delete()
                return True
            except Exception as e:
                logger.error(f"Firestore delete OTP error: {e}")

        if uid in self._mock_otps:
            del self._mock_otps[uid]
            return True
        return False

    # --- Audit Logging ---

    async def log_audit_event(self, user_id: str, action: str, resource_id: str, metadata: Optional[Dict[str, Any]] = None):
        event = {
            "user_id": user_id,
            "action": action,
            "resource_id": resource_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        if not self._is_mock and self.client:
            try:
                self.client.collection("audit_logs").add(event)
                return
            except Exception as e:
                logger.error(f"Firestore audit log error: {e}")

        self._mock_audit_logs.append(event)


# Global singleton instance
db_client = FirestoreClient()
