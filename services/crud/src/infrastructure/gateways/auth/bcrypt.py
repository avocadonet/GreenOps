import bcrypt
from application.auth.tokens.gateways import SecurityGateway


class BcryptSecurityGateway(SecurityGateway):
    encoding: str = "utf-8"

    def create_hashed_password(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode(self.encoding), bcrypt.gensalt()
        ).decode(self.encoding)

    def verify_passwords(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding),
        )
