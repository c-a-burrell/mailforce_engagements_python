import json
import tempfile

from redis import Redis

from mailforce import CONFIG, CONTENT_JSON, CONTENT_CSV
from mailforce.client.aws.aws_s3_client import get_file
from mailforce.client.sf.salesforce_client import issue_request
from mailforce.models.salesforce.create_bulk_api_response import CreateBulkApiResponse

REDIS: Redis = Redis(host=CONFIG.redis_host,
                     port=CONFIG.redis_port,
                     username=CONFIG.redis_username,
                     password=CONFIG.redis_password,
                     db=CONFIG.redis_db)


def _bulk_insert(api_version: str, job_mapping: dict[str, str], file_path: str, attempt: int):
    create_bulk_api_response: CreateBulkApiResponse = _create_batch_job(api_version, job_mapping)
    batch_job_id: str = create_bulk_api_response.batch_job_id
    content_url: str = create_bulk_api_response.content_url
    update_linking_table_response = _bulk_update(url=content_url,
                                                 file_path=file_path,
                                                 attempt=attempt)
    success: bool = update_linking_table_response['success']
    if success:
        url: str = f'https://${CONFIG.sf_domain}/services/data/${api_version}/jobs/ingest/${batch_job_id}'
        body: str = json.dumps({'state': 'Upload Complete'})
        return issue_request(url=url,
                             method='PATCH',
                             body=body,
                             content_type=CONTENT_JSON,
                             attempt=1)
    else:
        """ Need to write to storage...."""
        print('BULK Api Update failed.')


def _create_batch_job(api_version: str, job_mapping: dict[str, str]) -> CreateBulkApiResponse:
    """ Creates the Bulk Batch Job. """
    url = f'https://{CONFIG.sf_domain}/services/data/{api_version}/jobs/ingest'
    response = issue_request(url=url,
                             body=json.dumps(job_mapping),
                             content_type=CONTENT_JSON,
                             attempt=1)
    return CreateBulkApiResponse(response)


def _bulk_update(url: str, file_path: str, attempt: int) -> dict[str, any]:
    """ Performs a bulk update of the Linking Relationships table. """
    return issue_request(url=url,
                         content_type=CONTENT_CSV,
                         form_data_file_path=file_path,
                         attempt=attempt)


def _bulk_update_from_external(bucket: str, key: str, api_key: str, job_mapping: dict[str, str]) -> dict[
    str, any]:
    """
    Update the Linking table using a file path, needed for remediation
    :param bucket: Path to bucket.
    :param key: Path to file at bucket, including any folders.
    :return: Result of updating the linking table.
    """
    result: dict[str, any] = None
    try:
        content: str = get_file(bucket, key)
        temp = tempfile.NamedTemporaryFile()
        temp.write(content)
        result = _bulk_insert(file_path=temp.name, attempt=1,
                              api_version=api_key,
                              job_mapping=job_mapping)
        temp.close()
    except Exception as e:
        print(f'Exception when updating linking table from file {bucket}/{key}: {str(e)}')
    finally:
        return result


def _write_to_temp(header: str, content: list[str]):
    content: list[str] = list(header) + content
    content_string: str = '/n'.join(content)
    temp = tempfile.NamedTemporaryFile()
    temp.write(content_string)
    return temp
