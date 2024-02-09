from mailforce.client_operations.salesforce import _bulk_insert, _write_to_temp, _bulk_update_from_external
from mailforce.models.salesforce.email_relationships import EmailRelationships

JOB_MAPPING: dict[str, str] = {'object': 'EmailMessageRelation', 'contentType': 'CSV', 'operation': 'insert',
                               'lineEnding': "LF"}
LINKING_TABLE_API_VERSION: str = ''
HEADER: str = 'address,relation,messageId'


def update_linking_table(email_relationships: EmailRelationships) -> dict[str, any]:
    """
    Updates the linking table object in Salesforce.
    :param email_relationships: Container holding email relationships.
    :return: Result of updating the linking table.
    """
    result: dict[str, any] = None
    try:
        file_path = _write_linking_relationships_to_local(email_relationships)
        result = _bulk_insert(file_path=file_path.name, attempt=1,
                              api_version=LINKING_TABLE_API_VERSION, job_mapping=JOB_MAPPING)
        file_path.close()
    except Exception as e:
        print(f'Caught unexpected exception while updating linking relationships: {str(e)}')
    finally:
        return result


def update_linking_table_from_external(bucket: str, key: str) -> dict[str, any]:
    """
    Update the Linking table using a file path, needed for remediation
    :param bucket: Path to bucket.
    :param key: Path to file at bucket, including any folders.
    :return: Result of updating the linking table.
    """
    return _bulk_update_from_external(bucket=bucket, key=key,
                                      api_key=LINKING_TABLE_API_VERSION,
                                      job_mapping=JOB_MAPPING)


def _write_linking_relationships_to_local(email_relationships: EmailRelationships):
    """ Writes these linking relationships to a temp file so that they can be uploaded using the bulk API. """
    content: list[str] = list(map(lambda x: f'{x.email_address},{x.relation},{x.message_id}',
                                  email_relationships.email_relationships))
    return _write_to_temp(header=HEADER, content=content)
