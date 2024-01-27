class CreateBulkApiResponse:
    """ Holds the response from  the Salesforce Create Bulk Job API. """
    def __init__(self, response_json: dict[str, any]):
        """
        :param response_json: Response from call to Salesforce.
        """
        self.batch_job_id: str = response_json['id']
        self.content_url: str = response_json['contentUrl']