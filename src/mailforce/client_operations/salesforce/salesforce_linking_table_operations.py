import json
import tempfile

from mailforce import MailforceConfigurations, CONFIG, CONTENT_JSON, CONTENT_CSV
from mailforce.client.aws.aws_s3_client import get_file
from mailforce.client.sf.salesforce_client import issue_request
from mailforce.models.salesforce.create_bulk_api_response import CreateBulkApiResponse
from mailforce.models.salesforce.email_relationships import EmailRelationships

JOB_MAPPING: dict[str, str] = {'object': 'Need this', 'contentType': 'CSV', 'operation': 'insert', 'lineEnding': "LF"}
LINKING_TABLE_API_VERSION: str = ''
HEADER: str = 'address,relation,messageId'


def update_linking_table(email_relationships: EmailRelationships, secrets: MailforceConfigurations) -> dict[str, any]:
    """
    Updates the linking table object in Salesforce.
    :param email_relationships: Container holding email relationships.
    :param secrets: Instance that contains SF configurations.
    :return: Result of updating the linking table.
    """
    result: dict[str, any] = None
    try:
        filepath = _write_linking_relationships(email_relationships)
        result = _update_linking_table(file_path=filepath.name, attempt=1)
        filepath.close()
    except Exception as e:
        print(f'Caught unexpected exception while updating linking relationships: {str(e)}')
    finally:
        return result


def update_linking_table_from_external(bucket: str, key: str, config: MailforceConfigurations) -> dict[str, any]:
    """
    Update the Linking table using a file path, needed for remediation
    :param bucket: Path to bucket.
    :param key: Path to file at bucket, including any folders.
    :param config: Instance that contains SF configurations.
    :return: Result of updating the linking table.
    """
    result: dict[str, any] = None
    try:
        content: str = get_file(bucket, key)
        temp = tempfile.NamedTemporaryFile()
        temp.write(content)
        result = _update_linking_table(file_path=temp.name, attempt=1)
        temp.close()
    except Exception as e:
        print(f'Exception when updating linking table from file {bucket}/{key}: {str(e)}')
    finally:
        return result


def _update_linking_table(file_path: str, attempt: int) -> dict[str, any]:
    """ Updates the Linking Table object in SF using the Bulk API. """
    create_bulk_api_response: CreateBulkApiResponse = _create_batch_job()
    batch_job_id: str = create_bulk_api_response.batch_job_id
    content_url: str = create_bulk_api_response.content_url
    update_linking_table_response = _bulk_update_linking_table(url=content_url,
                                                               file_path=file_path,
                                                               attempt=attempt)
    success: bool = update_linking_table_response['success']
    if success:
        url: str = f'https://${CONFIG.sf_domain}/services/data/${LINKING_TABLE_API_VERSION}/jobs/ingest/${batch_job_id}'
        body: str = json.dumps({'state': 'Upload Complete'})
        return issue_request(url=url,
                             method='PATCH',
                             body=body,
                             content_type=CONTENT_JSON,
                             attempt=1)
    else:
        """ Need to write to storage...."""
        print('BULK Api Update failed.')


def _create_batch_job() -> CreateBulkApiResponse:
    """ Creates the Bulk Batch Job. """
    url = f'https://{CONFIG.sf_domain}/services/data/{LINKING_TABLE_API_VERSION}/jobs/ingest'
    response = issue_request(url=url,
                             body=json.dumps(JOB_MAPPING),
                             content_type=CONTENT_JSON,
                             attempt=1)
    return CreateBulkApiResponse(response)


def _bulk_update_linking_table(url: str, file_path: str, attempt: int) \
        -> dict[str, any]:
    """ Performs a bulk update of the Linking Relationships table. """
    return issue_request(url=url,
                         content_type=CONTENT_CSV,
                         form_data_file_path=file_path,
                         attempt=attempt)


def _write_linking_relationships(email_relationships: EmailRelationships):
    """ Writes these linking relationships to a temp file so that they can be uploaded using the bulk API. """
    content: list[str] = [HEADER] + list(map(lambda x: f'{x.email_address},{x.relation},{x.message_id}',
                                             email_relationships.email_relationships))
    content_string: str = '/n'.join(content)
    temp = tempfile.NamedTemporaryFile()
    temp.write(content_string)
    return temp
