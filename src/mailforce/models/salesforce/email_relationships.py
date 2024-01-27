from mailforce.models.salesforce.email_relationship import EmailRelationship


class EmailRelationships:
    """ Container that holds multiple email relationships for a single email. """
    def __init__(self, email_json: dict[str, any], salesforce_id: str, message_id: str, elastic_search_id: str):
        """
        :param email_json: JSON of the email from Elasticsearch,
        :param salesforce_id: Salesforce ID associated with this email.
        :param message_id: MessageID of this email.
        :param elastic_search_id: Elasticsearch Id associated with this email.
        """
        def email_relationship(email_address: str, relation: str):
            return EmailRelationship(email_address = email_address,
                                     salesforce_id=salesforce_id,
                                     message_id=message_id,
                                     elastic_search_id=elastic_search_id,
                                     relation=relation)
        to_emails: list[EmailRelationship] = list(map(lambda address: email_relationship(address,  'to'),
                                                      email_json.get('to.address', [])))
        from_emails: list[EmailRelationship] = list(map(lambda address: email_relationship(address,  'from'),
                                                        email_json['from.addresss']))
        cc_emails: list[EmailRelationship] = list(map(lambda address: email_relationship(address,  'from'),
                                                      email_json.get('cc.address', [])))
        self.email_relationships: list[EmailRelationship] = to_emails + from_emails + cc_emails
