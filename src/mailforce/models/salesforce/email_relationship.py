class EmailRelationship:
    """ Holds the relationship between an individual email and the email addresses associated with it. """
    def __init__(self, email_address: str, salesforce_id: str, message_id: str, elastic_search_id: str, relation: str):
        """
        :param email_address: Email address associated with this email.
        :param salesforce_id: Salesforce ID associated with this email.
        :param message_id: MessageID of this email.
        :param elastic_search_id: Elasticsearch Id associated with this email.
        :param relation: How this particular email address relates to this specific email.
        """
        self.email_address: str = email_address
        self.salesforce_id: str = salesforce_id
        self.message_id: str = message_id
        self.elastic_search_id: str = elastic_search_id
        self.relation: str = relation
