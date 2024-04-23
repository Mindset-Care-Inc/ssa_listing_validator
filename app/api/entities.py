from dataclasses import dataclass, field

# Define a data class representing a User
@dataclass
class User:
    user_name: str = field(default=None)
    response_msg: str = field(default=None)