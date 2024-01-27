from mailforce.models.salesforce.email_relationships import EmailRelationships


class InsertEmailResponse:
    """ Holds the response of call to insert email in Salesforce. """
    def __init__(self, response_json: dict[str, any], email_json: dict[str, any]):
        """
        :param response_json: Response from Salesforce.
        :param email_json: Email as obtained from Elasticsearch.
        """
        self.salesforce_id: str = response_json['id']
        self.elastic_search_id: str = email_json['_id']
        self.message_id = email_json['messageId']
        self.email_json: dict[str, any] = email_json
        self.email_relationships: EmailRelationships = EmailRelationships(email_json=email_json,
                                                                          elastic_search_id=self.elastic_search_id,
                                                                          message_id=self.message_id,
                                                                          salesforce_id=self.message_id)

