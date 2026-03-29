from application.auth.tokens.gateways import SecurityGateway


def test_security_gateway_happy_path(security_gateway: SecurityGateway):
    raw_password = "<PASSWORD>"

    hashed_password = security_gateway.create_hashed_password(password=raw_password)

    assert security_gateway.verify_passwords(raw_password, hashed_password)


def test_security_gateway_wrong_password(security_gateway: SecurityGateway):
    raw_password = "<PASSWORD>"
    hashed_password = security_gateway.create_hashed_password(password=raw_password)
    another_raw_password = "<PASSWORD2>"

    assert (
        security_gateway.verify_passwords(another_raw_password, hashed_password)
        is False
    )
