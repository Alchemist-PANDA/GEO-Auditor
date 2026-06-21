from fastapi import HTTPException, status

class GEOException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class EntityNotFoundException(GEOException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with id {entity_id} not found"
        )

class InsufficientPermissionsException(GEOException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient workspace permissions"
        )

class PromptLimitExceededException(GEOException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace prompt limit exceeded. Please upgrade or delete existing prompts."
        )
