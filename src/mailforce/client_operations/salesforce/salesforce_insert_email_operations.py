import json

from mailforce import MailforceConfigurations, CONTENT_JSON
from mailforce.client.sf.salesforce_client import issue_request
from mailforce.models.salesforce.insert_email_response import InsertEmailResponse

EMAIL_API_VERSION: str = ''
EMAIL_API_MODEL_NAME: str = ''


def insert_email(email_json: dict[str, any], config: MailforceConfigurations, attempt: int = 1) -> InsertEmailResponse:
    """
    Inserts the email JSON via the Salesforce API.
    :param email_json: Email JSON to insert.
    :param config: Mailforce Configurations.
    :param attempt: The number of the current attempt. The default is `1`.
    :return: Object that holds the response from Salesforce as well as Email Relationship mappings for
            further processing.
    """
    url: str = f'https://${config.sf_domain}/services/data/${EMAIL_API_VERSION}/{EMAIL_API_MODEL_NAME}'
    response: dict[str, any] = issue_request(url=url,
                                             method='POST',
                                             body=json.dumps(email_json),
                                             content_type=CONTENT_JSON,
                                             attempt=1)
    success: bool = response.get('success', False)
    return InsertEmailResponse(response_json=response, email_json=email_json) if success \
        else insert_email(email_json, config, attempt + 1)
