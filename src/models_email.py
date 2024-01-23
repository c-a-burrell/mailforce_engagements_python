class EmailMessageRelationship:
    """ Holds data concerning a single relation between an email address and an email message. """
    def __init__(self, message_id: str, email_address: str, relation: str):
        """
        :param message_id: Email Message ID.
        :param email_address: Email Address.
        :param relation: Relation between email address and email message.
        """
        self.email_address: str = email_address
        self.relation: str = relation
        self.message_id: str = message_id


class EmailRelationships:
    """ Holds relationships between multiple email addresses and a single email message id. """
    def __init__(self, message_id: list[str], from_address: list[str], to_addresses: list[str],
                 cc_addresses: list[str]):
        """
        :param message_id: Email Message ID.
        :param from_address: The email address that originated this email.
        :param to_addresses: All the email addresses that this email was sent directly to.
        :param cc_addresses: All the email addresses that this email was cc'd to.
        """
        def _get_relationships(values: list[str], relationship: str, email_message_id: str):
            return list(map(lambda value: EmailMessageRelationship(email_message_id, value, relationship), values))

        self.message_id: str = message_id[0]
        self.to_addresses: list[EmailMessageRelationship] = _get_relationships(to_addresses, 'to',
                                                                               self.message_id)
        self.cc_addresses: list[EmailMessageRelationship] = _get_relationships(cc_addresses, 'cc',
                                                                               self.message_id)
        self.from_address = EmailMessageRelationship(self.message_id, from_address[0], 'from')
