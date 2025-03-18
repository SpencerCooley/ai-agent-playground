from enum import Enum

class RoleEnum(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    customer = "customer"
    user = "user"