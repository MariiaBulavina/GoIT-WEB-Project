from fastapi import Request, Depends, HTTPException, status

from src.database.models import UserRole, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):

        if user.user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN"
            )