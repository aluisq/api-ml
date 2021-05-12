from fastapi import Form
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

now = datetime.now()
data = now.strftime("%d/%m/%Y, %H:%M:%S H")


class UpdateUser:

    def __init__(
        self,
        username: str = Form(...),
        newUsername: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        full_name: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        role: Optional[str] = Form(None),
        status: Optional[str] = Form(None)
       
    ):
        self.username = username
        self.newUsername = newUsername
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.status = status