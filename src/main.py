import os

from models.domain.domains import Domains
from utils.date_utils import now
from client.es.index_client import insert_account_stats, insert_runtime_stats, insert_account_interactions, \
    insert_domains_stats, insert_message_roles
from client.es.search_client import get_emails_by_account, search_accounts, get_message_roles, get_last_runtime_date
from models.email.account.email_accounts import EmailAccounts, EmailAccount
from models.message.message_roles_container import MessageRolesContainer
from models.runtime_stats.models_runtime_stats import RuntimeStats

RESOURCES_PATH = './resources'
ACCOUNTS_PATH = f'{RESOURCES_PATH}/accounts'
DOMAINS_PATH = f'{RESOURCES_PATH}/domains'
USE_ACCOUNTS_FILE = False
WRITE_LOCAL_FILES = False


def main(event, context):
    response = _get_response(event, context)
    try:
        from_date = event['from_date'] if 'from_date' in event else None
        runtime_stats = _collect(from_date)
        response['runtime_stats'] = str(runtime_stats)
    except Exception as e:
        response['error'] = str(e)
    finally:
        return response


def _get_response(event, context):
    return {
        "body": {
            "event": event,
            "context": {
                "activationId": context.activation_id,
                "apiHost": context.api_host,
                "apiKey": context.api_key,
                "deadline": context.deadline,
                "functionName": context.function_name,
                "functionVersion": context.function_version,
                "namespace": context.namespace,
                "requestId": context.request_id,
            },
        }
    }


def _collect(from_date: str = None):
    last_runtime_date = from_date if from_date else get_last_runtime_date()
    print(f'Using last runtime date of {last_runtime_date}')
    accounts = _get_accounts_from_file() if USE_ACCOUNTS_FILE else _get_accounts_from_es()
    email_accounts = _get_email_accounts(last_runtime_date, accounts)
    domains = _get_domains(email_accounts)
    message_roles = get_message_roles()
    message_roles_container = MessageRolesContainer(message_roles)
    _write_to_local(email_accounts, domains, message_roles_container)
    runtime_stats = _write_to_es(email_accounts, domains, message_roles_container)
    print('Done')
    return runtime_stats


def _get_email_accounts(last_runtime_date: str, accounts: list[str]) -> EmailAccounts:
    email_accounts = EmailAccounts()
    for account in accounts:
        email_account = get_emails_by_account(account=account, last_runtime_date=last_runtime_date)
        email_accounts.add_account(email_account)
    return email_accounts


def _get_accounts_from_file():
    with open(f'{os.getcwd()}/resources/accounts.txt', 'r') as f:
        accounts = list(map(lambda line: line.replace('\n', '').strip(), f.readlines()))
        return list(filter(lambda account: '#' not in account, accounts))


def _get_accounts_from_es():
    query_result = search_accounts()
    return list(map(lambda hit: hit['fields']['account'][0], query_result['hits']['hits']))


def _write_to_local(email_accounts: EmailAccounts, domains: Domains, message_roles_container: MessageRolesContainer):
    if WRITE_LOCAL_FILES:
        for email_account in email_accounts.accounts:
            _write_account(email_account.account, email_account)
        _write_account_stats(email_accounts)
        _write_domains_file(domains)
        _write_message_roles(message_roles_container)


def _write_to_es(email_accounts: EmailAccounts, domains: Domains, message_roles_container: MessageRolesContainer):
    insert_account_stats(email_accounts)
    insert_account_interactions(email_accounts)
    insert_domains_stats(domains)
    insert_message_roles(message_roles_container)
    runtime_stats = RuntimeStats(run_date=now(), email_accounts=email_accounts, domains=domains)
    insert_runtime_stats(runtime_stats)
    return runtime_stats


def _write_account(account: str, email_account: EmailAccount):
    if email_account:
        filename = f'{ACCOUNTS_PATH}/{account}.csv'
        print(f'Writing account {account} to {filename}')
        with open(filename, 'w') as f:
            f.writelines(list(map(lambda row: f'{row}\n', email_account.to_csv_rows())))


def _get_domains(email_accounts: EmailAccounts):
    domains = Domains()
    for email_account in email_accounts.accounts:
        all_rows = email_account.emails_cc + email_account.emails_to + email_account.emails_from
        for email in all_rows:
            domains.add_email(email)
    return domains


def _write_domains_file(domains: Domains):
    for domain in domains.domains.values():
        output_file_path = f'{DOMAINS_PATH}/{domain.domain}.csv'
        with open(output_file_path, 'w') as f:
            f.writelines(domain.to_csv())
    print(f'Wrote {len(domains.domains)} files to {DOMAINS_PATH}')
    return domains


def _write_account_stats(email_accounts: EmailAccounts):
    output_file_path = f'{RESOURCES_PATH}/account_stats.csv'
    with open(output_file_path, 'w') as f:
        f.writelines(email_accounts.to_csv_rows())
    print(f'Wrote stats for {len(email_accounts.accounts)} accounts to {output_file_path}')


def _write_message_roles(message_roles_container: MessageRolesContainer):
    output_file_path = f'{RESOURCES_PATH}/message_roles.csv'
    with open(output_file_path, 'w') as f:
        f.writelines(message_roles_container.to_csv_rows())
    print(f'Wrote stats for {len(message_roles_container.message_roles)} message roles to {output_file_path}')


if __name__ == "__main__":
    _collect(None)
