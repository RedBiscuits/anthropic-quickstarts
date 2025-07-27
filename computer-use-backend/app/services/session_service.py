"""
Session service implementing business logic and orchestration
"""
import logging
from typing import List, Optional
from datetime import datetime

from app.core.interfaces import SessionRepository, EventPublisher
from app.core.validation import ValidationService
from app.core.exceptions import ServiceError, ValidationError, RepositoryError
from app.api.models.schemas import SessionCreate, SessionResponse, SessionDetail
from app.database.models import Session as SessionModel, Message

logger = logging.getLogger(__name__)


class SessionService:
    """Service for session management business logic"""
    
    def __init__(
        self, 
        session_repository: SessionRepository,
        validation_service: ValidationService,
        event_publisher: Optional[EventPublisher] = None
    ):
        self.session_repository = session_repository
        self.validation_service = validation_service
        self.event_publisher = event_publisher
    
    async def create_session(self, session_data: SessionCreate) -> SessionResponse:
        """Create a new session with business logic"""
        try:
            logger.info(f"Creating session with name: {session_data.name}")
            
            # Business logic: Check for duplicate session names (optional)
            # This could be enhanced to prevent duplicate names if needed
            
            # Create session via repository
            session = self.session_repository.create(session_data)
            
            # Convert to response model
            response = SessionResponse(
                id=session.id,
                name=session.name,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=0
            )
            
            # Publish event if publisher is available
            if self.event_publisher:
                await self.event_publisher.publish_session_created(session)
            
            logger.info(f"Successfully created session: {session.id}")
            return response
            
        except ValidationError as e:
            logger.warning(f"Validation error creating session: {e}")
            raise
        except RepositoryError as e:
            logger.error(f"Repository error creating session: {e}")
            raise ServiceError(f"Failed to create session: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise ServiceError(f"Unexpected error creating session: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session by ID with business logic"""
        try:
            logger.debug(f"Retrieving session: {session_id}")
            
            session = self.session_repository.get_by_id(session_id)
            if not session:
                logger.debug(f"Session not found: {session_id}")
                return None
            
            # Convert to response model
            response = SessionResponse(
                id=session.id,
                name=session.name,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=0  # This could be calculated from messages
            )
            
            return response
            
        except RepositoryError as e:
            logger.error(f"Repository error retrieving session {session_id}: {e}")
            raise ServiceError(f"Failed to retrieve session: {str(e)}")
    
    def get_all_sessions(self) -> List[SessionResponse]:
        """Get all sessions with business logic"""
        try:
            logger.debug("Retrieving all sessions")
            
            sessions = self.session_repository.get_all()
            
            # Convert to response models
            responses = []
            for session in sessions:
                response = SessionResponse(
                    id=session.id,
                    name=session.name,
                    status=session.status,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    message_count=0  # This could be calculated from messages
                )
                responses.append(response)
            
            logger.debug(f"Retrieved {len(responses)} sessions")
            return responses
            
        except RepositoryError as e:
            logger.error(f"Repository error retrieving sessions: {e}")
            raise ServiceError(f"Failed to retrieve sessions: {str(e)}")
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session with business logic"""
        try:
            logger.info(f"Deleting session: {session_id}")
            
            # Business logic: Check if session can be deleted
            session = self.session_repository.get_by_id(session_id)
            if not session:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
            
            # Additional business rules could be added here
            # e.g., prevent deletion of active sessions with ongoing tasks
            
            success = self.session_repository.delete(session_id)
            
            if success:
                logger.info(f"Successfully deleted session: {session_id}")
            else:
                logger.warning(f"Failed to delete session: {session_id}")
            
            return success
            
        except RepositoryError as e:
            logger.error(f"Repository error deleting session {session_id}: {e}")
            raise ServiceError(f"Failed to delete session: {str(e)}")
    
    def update_session_status(self, session_id: str, status: str) -> Optional[SessionResponse]:
        """Update session status with business logic"""
        try:
            logger.info(f"Updating session {session_id} status to: {status}")
            
            # Business logic: Validate status transition
            if not self._is_valid_status_transition(session_id, status):
                logger.warning(f"Invalid status transition for session {session_id}: {status}")
                raise ValidationError(f"Invalid status transition to: {status}")
            
            session = self.session_repository.update(session_id, status=status)
            if not session:
                return None
            
            # Convert to response model
            response = SessionResponse(
                id=session.id,
                name=session.name,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=0
            )
            
            logger.info(f"Successfully updated session {session_id} status to: {status}")
            return response
            
        except RepositoryError as e:
            logger.error(f"Repository error updating session {session_id}: {e}")
            raise ServiceError(f"Failed to update session: {str(e)}")
    
    def _is_valid_status_transition(self, session_id: str, new_status: str) -> bool:
        """Validate status transition business rules"""
        # This could implement complex business rules for status transitions
        # For now, we'll allow any valid status
        valid_statuses = ['active', 'completed', 'error', 'cancelled']
        return new_status in valid_statuses 