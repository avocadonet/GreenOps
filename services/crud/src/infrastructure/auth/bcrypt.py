import bcrypt

from application.auth.tokens.dtos import PasswordDto
from application.auth.tokens.gateways import SecurityGateway


class BcryptSecurityGateway(SecurityGateway):
    encoding = "utf-8"

    def create_salt(self) -> str:
        return ""

    def create_hashed_password(self, password: str) -> PasswordDto:
        hashed = bcrypt.hashpw(password.encode(self.encoding), bcrypt.gensalt())
        return PasswordDto(hashed_password=hashed.decode(self.encoding), salt="")

    def verify_passwords(
        self, plain_password: str, hashed_password: PasswordDto
    ) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.hashed_password.encode(self.encoding),
        )
