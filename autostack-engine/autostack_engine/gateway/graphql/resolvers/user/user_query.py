import os
import platform
import strawberry
import structlog
from typing import Optional


logger = structlog.get_logger()

# Define output types for your queries
@strawberry.type
class UserResponse:
    fullname: str

@strawberry.type
class UserQuery:
    @strawberry.field
    async def fetch_user_details(
        self
    ) -> Optional[UserResponse]:
        """Return the logged in user's fullname"""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                # Windows implementation
                import ctypes
                GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
                NameDisplay = 3
                
                size = ctypes.pointer(ctypes.c_ulong(0))
                GetUserNameEx(NameDisplay, None, size)
                
                name_buffer = ctypes.create_unicode_buffer(size.contents.value)
                GetUserNameEx(NameDisplay, name_buffer, size)
                
                return UserResponse(fullname=name_buffer.value) if username else None
                
            elif system in ["linux", "darwin"]:  # darwin is macOS
                # Unix-like systems implementation
                import pwd
                user_info = pwd.getpwuid(os.getuid())
                fullname = user_info.pw_gecos.split(',')[0]  # Get the full name part before any commas
                return UserResponse(fullname=fullname) if fullname else None
                
            else:
                # Fallback for other systems
                import getpass
                username = getpass.getuser()
                return UserResponse(fullname=username)
                
        except Exception as e:
            # Log the error and return None or a default value
            print(f"Error fetching user details: {e}")
            return None
    
        
    