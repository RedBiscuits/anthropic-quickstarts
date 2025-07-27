"""
Session repository implementation with proper error handling and logging
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Session as SessionModel
from app.database.models import SessionStatus
from app.core.interfaces import SessionRepository
from app.core.validation import ValidationService
from app.core.exceptions import RepositoryError, ValidationError
from app.api.models.schemas import SessionCreate

logger = logging.getLogger(__name__)


class SQLAlchemySessionRepository(SessionRepository):
    """SQLAlchemy implementation of SessionRepository"""
    
    def __init__(self, db: DBSession, validation_service: ValidationService):
        self.db = db
        self.validation_service = validation_service
    
    def create(self, session_data: SessionCreate) -> SessionModel:
        """Create a new session with validation"""
        try:
            # Validate session data
            validation_result = self.validation_service.validate_session_name(session_data.name)
            if not validation_result.is_valid:
                raise ValidationError(validation_result.error_message, validation_result.field_name)
            
            # Create session
            session = SessionModel(
                name=session_data.name.strip(),
                status=SessionStatus.ACTIVE
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Created session: {session.id} with name: {session.name}")
            return session
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating session: {e}")
            raise RepositoryError(f"Failed to create session: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating session: {e}")
            raise RepositoryError(f"Unexpected error creating session: {str(e)}")
    
    def get_by_id(self, session_id: str) -> Optional[SessionModel]:
        """Get session by ID with validation"""
        try:
            # Validate session ID
            validation_result = self.validation_service.validate_session_id(session_id)
            if not validation_result.is_valid:
                logger.warning(f"Invalid session ID format: {session_id}")
                return None
            
            session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
            
            if session:
                logger.debug(f"Retrieved session: {session_id}")
            else:
                logger.debug(f"Session not found: {session_id}")
            
            return session
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving session {session_id}: {e}")
            raise RepositoryError(f"Failed to retrieve session: {str(e)}")
    
    def get_all(self) -> List[SessionModel]:
        """Get all sessions ordered by creation date"""
        try:
            sessions = self.db.query(SessionModel).order_by(SessionModel.created_at.desc()).all()
            logger.debug(f"Retrieved {len(sessions)} sessions")
            return sessions
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving sessions: {e}")
            raise RepositoryError(f"Failed to retrieve sessions: {str(e)}")
    
    def update(self, session_id: str, **kwargs) -> Optional[SessionModel]:
        """Update session with validation"""
        try:
            # Validate session ID
            validation_result = self.validation_service.validate_session_id(session_id)
            if not validation_result.is_valid:
                logger.warning(f"Invalid session ID format: {session_id}")
                return None
            
            session = self.get_by_id(session_id)
            if not session:
                logger.warning(f"Session not found for update: {session_id}")
                return None
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
                else:
                    logger.warning(f"Invalid field for session update: {key}")
            
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Updated session: {session_id}")
            return session
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating session {session_id}: {e}")
            raise RepositoryError(f"Failed to update session: {str(e)}")
    
    def delete(self, session_id: str) -> bool:
        """Delete session with validation"""
        try:
            # Validate session ID
            validation_result = self.validation_service.validate_session_id(session_id)
            if not validation_result.is_valid:
                logger.warning(f"Invalid session ID format: {session_id}")
                return False
            
            session = self.get_by_id(session_id)
            if not session:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
            
            self.db.delete(session)
            self.db.commit()
            
            logger.info(f"Deleted session: {session_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting session {session_id}: {e}")
            raise RepositoryError(f"Failed to delete session: {str(e)}") 