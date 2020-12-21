from dataclasses import dataclass, asdict

from validate_email import validate_email


@dataclass
class BaseDataclass:
    def __post_init__(self):
        if not self.validate():
            raise ValueError('Wrong Types')

    def validate(self) -> bool:
        for field_name, field in self.__dataclass_fields__.items():
            actual_type = type(getattr(self, field_name))
            if field.type != actual_type:
                return False
        return True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SignIn(BaseDataclass):
    email: str
    password: str

    def __post_init__(self):
        if not self.validate_email(self.email):
            raise ValueError('Not valid email')

    @staticmethod
    def validate_email(email: str) -> bool:
        return validate_email(email)


@dataclass
class SignUp(BaseDataclass):
    email: str
    password: str
    repeat_password: str

    def __post_init__(self):
        if not self.validate_password(self.password, self.repeat_password):
            raise ValueError('Password Not equal')
        if not self.validate_email(self.email):
            raise ValueError('Email invalid')

    @staticmethod
    def validate_email(email: str) -> bool:
        return validate_email(email)

    @staticmethod
    def validate_password(password: str, repeat_password: str) -> bool:
        return password == repeat_password
