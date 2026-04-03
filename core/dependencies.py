from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from core.security import get_current_user, require_role
from model.user import User

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(require_role("admin"))]
