"""The module responsible for connecting to `GitHub`_."""

import schema

from .. import schema_type

_COMMON_TOKEN = {
    schema.Optional(
        "authentication_type", default=schema_type.DEFAULT_AUTHENTICATION
    ): schema.Or(
        schema_type.RAW,
        schema_type.FROM_FILE,
    ),
}
_TWO_FACTOR = {
    schema.Optional("two_factor_authentication"): schema_type.CALLABLE,
}
_USER_PASSWORD_PAIR = {
    "user": schema_type.NON_EMPTY_STR,
    "password": schema_type.NON_EMPTY_STR,
}
_USER_PASSWORD_PAIR.update(_COMMON_TOKEN)
_ACCESS_TOKEN = {
    # TODO : Probably don't allow spaces in access_token
    "access_token": schema_type.NON_EMPTY_STR,
}
_ACCESS_TOKEN.update(_COMMON_TOKEN)

_AUTHENTICATION_SCHEMA = schema.Schema(schema.Or(_USER_PASSWORD_PAIR, _ACCESS_TOKEN))


def validate(data):
    """Check if ``data`` describes `GitHub` authentication details.

    Args:
        data (dict[str, object]):
            A user / password pair, access token, or some other authentication method.

    Returns:
        TODO : Update this later.

    """
    return _AUTHENTICATION_SCHEMA.validate(data)
