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

