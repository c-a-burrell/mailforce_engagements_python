class MessageRole:
    """ Holds the relationships between a given message ID in a specified account and an email address. """
    def __init__(self, account: str, message_id: str, email_address: str, role: str):
        """
        :param account: Name of the account.
        :param message_id: ID of the email message.
        :param email_address: Email address.
        :param role: Relationship between the given email address and the message ID, namely whether it originated,
        directly received or was a CC recipient of the email.
        """
        self.account: str = account
        self.message_id: str = message_id
        self.email_address: str = email_address
        self.role: str = role
        self.domain: str = self.email_address.split('@')[1]

    def to_csv_row(self):
        """
        :return: CSV representation of this object.
        """
        return f'{self.account},{self.message_id},{self.email_address},{self.role}'
