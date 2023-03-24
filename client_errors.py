from pysteamauth.errors import SteamError, custom_error_exception


class ServiceUnavailable(SteamError):
    pass


class RateLimitExceeded(SteamError):
    pass


class TwoFactorCodeMismatch(SteamError):
    pass


custom_error_exception({
    20: ServiceUnavailable,
    84: RateLimitExceeded,
    88: TwoFactorCodeMismatch
})
