from mailforce.client_operations.salesforce import REDIS, _write_to_temp, _bulk_insert, \
    _bulk_update_from_external

EMAIL_API_VERSION: str = ''
EMAIL_THREAD_API_VERSION: str = ''
EMAIL_THREAD_API_MODEL_NAME: str = 'EmailThread'
REDIS_EMAIL_THREAD_CACHE: str = 'emailThreadCache'
JOB_MAPPING: dict[str, str] = {'object': 'EmailThread', 'contentType': 'CSV', 'operation': 'insert', 'lineEnding': "LF"}
HEADER: str = 'Email_Thread_ID__c'


def preprocess_email_threads(email_jsons: dict[str, any]) -> list[dict[str, any]]:
    """
    :param email_jsons: Email JSONS from ES
    :return: All the email JSONS that have not been previously cached
    """

    def email_thread_is_not_cached(email_json: dict[str, any], cached_ids: list[str]) -> bool:
        """
        :param email_json:
        :param cached_ids: All the IDs that have been cached in Redis.
        :return: True if this email Id is *not* cached.
        """
        email_thread_id = email_json.get('messageId', ())
        return email_thread_id[0] not in cached_ids if len(email_thread_id) > 0 else False

    cached_ids_from_redis: list[str] = REDIS.hkeys(name=REDIS_EMAIL_THREAD_CACHE)
    emails = email_jsons['hits']['hits']
    return list(filter(lambda x: email_thread_is_not_cached(x, cached_ids_from_redis), emails))


def update_email_threads(email_thread_ids: list[str]) -> dict[str, any]:
    """
    Updates the linking table object in Salesforce.
    :param email_thread_ids: List of email thread Ids.
    :return: Result of updating the linking table.
    """
    result: dict[str, any] = None
    try:
        file_path = _write_email_threads_to_local(email_thread_ids)
        result = _bulk_insert(file_path=file_path.name, attempt=1,
                              api_version=EMAIL_THREAD_API_VERSION,
                              job_mapping=JOB_MAPPING)
        file_path.close()
    except Exception as e:
        print(f'Caught unexpected exception while updating linking relationships: {str(e)}')
    finally:
        return result


def _write_email_threads_to_local(email_thread_ids: list[str]):
    """ Writes these email threads to a temp file so that they can be uploaded using the bulk API. """
    content: list[str] = list(HEADER) + email_thread_ids
    return _write_to_temp(header=HEADER, content=content)


def update_email_threads_from_external(bucket: str, key: str) -> dict[str, any]:
    """
    Update the Email Threads using a file path, needed for remediation
    :param bucket: Path to bucket.
    :param key: Path to file at bucket, including any folders.
    :return: Result of updating the linking table.
    """
    return _bulk_update_from_external(bucket=bucket, key=key,
                                      api_key=EMAIL_THREAD_API_VERSION,
                                      job_mapping=JOB_MAPPING)
