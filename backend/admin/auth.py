from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
import bcrypt

from admin.database import AsyncSessionLocal
from auth.models.items import UserModel


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            print("DEBUG LOGIN: Missing username or password", flush=True)
            return False

        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(
                (UserModel.username == username) | (UserModel.email == username)
            )
            result = await session.execute(stmt)
            user = result.scalars().first()

            if not user:
                print(
                    f"DEBUG LOGIN: User '{username}' not found in database", flush=True
                )
                return False

            print(
                f"DEBUG LOGIN: Found user '{user.username}', role='{user.role}', is_active={user.is_active}",
                flush=True,
            )

            if user.role != "admin":
                print("DEBUG LOGIN: User is not an admin", flush=True)
                return False

            if not user.is_active:
                print("DEBUG LOGIN: User is not active", flush=True)
                return False

            pwd_ok = verify_password(password, user.password_hash)
            print(f"DEBUG LOGIN: Password verification result: {pwd_ok}", flush=True)

            if pwd_ok:
                request.session.update(
                    {"user_id": user.id, "username": user.username, "role": user.role}
                )
                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if not user_id or role != "admin":
            return False

        return True
