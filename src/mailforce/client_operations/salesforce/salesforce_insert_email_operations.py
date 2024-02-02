import json

from mailforce import MailforceConfigurations, CONTENT_JSON
from mailforce.client.sf.salesforce_client import issue_request
from mailforce.client_operations.salesforce import REDIS
from mailforce.models.salesforce.insert_email_response import InsertEmailResponse

EMAIL_API_VERSION: str = ''
EMAIL_API_MODEL_NAME: str = ''
REDIS_EMAIL_CACHE: str = 'emailIdCache'


def preprocess_emails(email_jsons: dict[str, any]) -> list[dict[str, any]]:
    """
    :param email_jsons: Email JSONS from ES
    :return: All the email JSONS that have not been previously cached
    """
    def email_is_not_cached(email_json: dict[str, any], cached_ids: list[str]) -> bool:
        """
        :param email_json:
        :param cached_ids: All the IDs that have been cached in Redis.
        :return: True if this email Id is *not* cached.
        """
        email_id = email_json.get('messageId', None)
        return email_id not in cached_ids

    cached_ids_from_redis: list[str] = REDIS.hkeys(name=REDIS_EMAIL_CACHE)
    emails = email_jsons['hits']['hits']
    return list(filter(lambda x: email_is_not_cached(x, cached_ids_from_redis), emails))


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


def update_cache(insert_email_response: InsertEmailResponse) -> bool:
    """
    :param insert_email_response: Object that holds the response from Salesforce as well as Email Relationship mappings for
            further processing.
    :return: Whether update was successful
    """
    return REDIS.hset(name=REDIS_EMAIL_CACHE,
                      key=insert_email_response.message_id,
                      value=insert_email_response.salesforce_id) > 0
