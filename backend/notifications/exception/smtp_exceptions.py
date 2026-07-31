class SMTPError(Exception):
    pass


class SMTPConnectionError(SMTPError):
    pass


class SMTPAuthError(SMTPError):
    pass


class SMTPRecipientError(SMTPError):
    pass


class SMTPSendError(SMTPError):
    pass
