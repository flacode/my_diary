from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationToken(PasswordResetTokenGenerator):
    """ Generate a one time login token with the user's slug_field, state and timestamp."""
    def _make_hash_value(self, user, timestamp):
        return str(user.slug_field) + str(user.is_active) + str(timestamp)


class PasswordResetToken(PasswordResetTokenGenerator):
    """Generate a one time password reset token. """
    def _make_hash_value(self, user, timestamp):
        return str(user.slug_field) + str(user.password) + str(timestamp)


ACTIVATIONTOKEN = AccountActivationToken()
PASSWORDRESETTOKEN = PasswordResetToken()
