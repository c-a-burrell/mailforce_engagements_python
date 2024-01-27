import json
from time import sleep
from typing import BinaryIO

import requests

from mailforce import CONFIG, CONTENT_JSON
from mailforce.main import RESOURCES_PATH

MAX_RETRIES: int = 5
BACK_OFF_BASE: int = 1000
OAUTH_TOKEN: str = None


def issue_request(url: str, content_type: str,
                  body: str = None, form_data_file_path: str = None,
                  attempt: int = 1, method: str = 'POST') -> dict[str, any]:
    """
    Issues a basic request.
    :param url: URL to send the request to.
    :param content_type: Content type of the request body. This is ignored for `GET` requests.
    :param config: Mailforce Configurations
    :param body: Optional content to be included in the body of the request.
    :param form_data_file_path: Optional path to the file that contains the content that comprises the form data.
    :param attempt: Current number of attempts for the current request. Defaults to `1`.
    :param method: One of `POST`, `PUT`, `PATCH` or `GET`.
    :return: Response JSON.
    """
    if attempt > MAX_RETRIES:
        raise f'Attempt number {attempt} has exceeded the limit of {MAX_RETRIES} attempts.'
    _oauth_token()
    headers = _headers(content_type=content_type, content_encoding='gzip')
    if method == 'POST':
        response = requests.post(url=url, data=body, headers=headers) if body and len(body) > 0 \
            else requests.post(url=url, files=_from_form_data, headers=headers)
    elif method == 'PATCH':
        response = requests.patch(url=url, headers=headers, data=body)
    else:
        response = requests.get(url=url, headers=headers)
    status_code = response.status_code
    if 200 <= status_code < 300:
        return response.json()
    else:
        print(f'Response code is {status_code}. Reason is {response.text}')
        if status_code == 401:
            """ If we've failed on auth, refresh the token """
            _oauth_token(force_refresh=True)
        """ Increase  the current attempt count by one """
        current_attempt = attempt + 1
        sleep_millis = float(BACK_OFF_BASE * current_attempt)
        print(f'Attempt {current_attempt} of {MAX_RETRIES}. Sleeping for {sleep_millis} milliseconds.')
        sleep(sleep_millis)
        return issue_request(url=url,
                             content_type=content_type,
                             body=body,
                             form_data_file_path=form_data_file_path,
                             attempt=current_attempt)


def _headers(content_type: str, content_encoding: str = None) -> dict[str, str]:
    """ Generates basic headers."""
    headers: dict[str, str] = {
        'Content-Type': content_type,
        'Accept': 'application/json'
    }
    if content_encoding:
        headers['Content-Encoding'] = content_encoding
    if OAUTH_TOKEN:
        headers['Authorization'] = OAUTH_TOKEN
    return headers


def _from_form_data(file_path: str, file_type: str) -> dict[str, tuple[str, BinaryIO, str]]:
    """ Returns the request body stored in an external file """
    file_name: str = file_path.replace(RESOURCES_PATH, '')
    with open(file_path, 'rb') as f:
        form_data = {'upload_file': (file_name, f, file_type)}
    return form_data


def _oauth_token(force_refresh: bool = False):
    """ Inits the global OAUTH_TOKEN var if it hasn't been already, or if we are forcing a refresh """
    global OAUTH_TOKEN
    if not OAUTH_TOKEN or force_refresh:
        params: dict[str, str] = {
            'grant_type': 'refesh_token',
            'client_id': CONFIG.sf_client_id,
            'refresh_token': CONFIG.sf_refresh_token
        }
        response = issue_request(
            url=f'https://login.{CONFIG.sf_domain}/services/oauth2/token',
            body=json.dumps(params),
            content_type=CONTENT_JSON,
            attempt=1)
        OAUTH_TOKEN = f'Bearer {response["access_token"]}'
