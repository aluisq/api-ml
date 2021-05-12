from fastapi import Form
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

now = datetime.now()
data = now.strftime("%d/%m/%Y, %H:%M:%S H")


class UserForm:

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        full_name: str = Form(...),
        email: str = Form(...)
       
    ):
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email