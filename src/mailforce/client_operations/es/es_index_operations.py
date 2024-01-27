from elasticsearch import helpers

from mailforce.client_operations.es import CLIENT
from mailforce.models.domain.domain import Domain
from mailforce.models.domain.domains import Domains
from mailforce.models.email.account.email_account import EmailAccount
from mailforce.models.email.account.email_accounts import EmailAccounts
from mailforce.models.email.engagement.email_engagement import EmailEngagement
from mailforce.models.email.mapping.email_mapping import EmailMapping
from mailforce.models.message.message_role import MessageRole
from mailforce.models.message.message_roles import MessageRoles
from mailforce.models.message.message_roles_container import MessageRolesContainer
from mailforce.models.runtime_stats.runtime_stats import RuntimeStats
from mailforce.utils.date_utils import now

ACCOUNTS_STAT_INDEX: str = 'search-accounts_statistics_simple'
ACCOUNTS_ENGAGEMENTS_INDEX: str = 'search-accounts-engagements'
DOMAINS_ENGAGEMENTS_INDEX: str = 'search-domains-engagements'
RUNTIME_STATS_INDEX: str = 'search-runtime-stats'
MESSAGE_ROLES_INDEX: str = 'search-message-roles'
RIGHT_NOW: str = now()


def insert_runtime_stats(runtime_stats: RuntimeStats) -> bool:
    """ Inserts runtime stats into ES. The statistics consist of the counts of domains, email accounts,
    and to, from and cc'd emails processed.
    :param runtime_stats: Runtime statistics to be inserted.
    :return: Whether statistics were inserted into ES.
    """
    print('Updating Runtime Statistics.')
    doc = {
        'run_date': runtime_stats.run_date,
        'domains_processed': runtime_stats.domains_processed,
        'email_accounts_processed': runtime_stats.email_accounts_processed,
        'emails_processed': runtime_stats.emails_processed,
        'to_emails_processed': runtime_stats.to_emails_processed,
        'from_emails_processed': runtime_stats.from_emails_processed,
        'cc_emails_processed': runtime_stats.cc_emails_processed
    }
    response = CLIENT.index(index=RUNTIME_STATS_INDEX, document=doc)
    return True if response and response['result'] == 'created' else False


def insert_account_stats(email_accounts: EmailAccounts) -> bool:
    """ Inserts the email accounts statistics. This method only inserts the raw counts of to, from and cc'd.
    emails associated with the given account.
    :param email_accounts: Email Account Statistics to be updated.
    :return: Whether all account statistics have been updated.
    """
    print('Inserting Email Account Statistics.')

    def account_json(email_account: EmailAccount):
        return {
            '_op_type': 'index',
            '_index': ACCOUNTS_STAT_INDEX,
            '_id': email_account.id(),
            'doc': {
                'account': email_account.account,
                'emails_from_count': email_account.emails_from_count,
                'emails_to_count': email_account.emails_to_count,
                'emails_cc_count': email_account.emails_cc_count,
                'total_emails_count': email_account.total_email_count,
                'date': RIGHT_NOW
            }
        }

    return _perform_bulk_operations(email_accounts.accounts, account_json)


def insert_account_interactions(email_accounts: EmailAccounts) -> bool:
    """ Inserts a more granular accounting of specific relationships between the given email addresses
    and the account in question.
    :param email_accounts: Email Accounts Engagement data.
    :return: True if all Email Engagements for all accounts were inserted into ES.
    """
    print('Inserting Email Account Engagement Statistics.')

    def account_json(account: EmailAccount):
        def email_engagement_json(email: EmailEngagement):
            return {
                'relationship': email.relationship,
                'email_address': email.email_address,
                'count': email.count,
                'earliest_engagement_date': email.earliest_engagement_date,
                'latest_engagement_date': email.latest_engagement_date
            }

        return {
            '_op_type': 'index',
            '_index': ACCOUNTS_ENGAGEMENTS_INDEX,
            '_id': account.id(),
            'doc': {
                'account': account.account,
                'emails_from': list(map(email_engagement_json, account.emails_from)),
                'emails_to': list(map(email_engagement_json, account.emails_to)),
                'emails_cc': list(map(email_engagement_json, account.emails_cc)),
                'date': RIGHT_NOW
            }
        }

    return _perform_bulk_operations(email_accounts.accounts, account_json)


def insert_message_roles(message_roles_container: MessageRolesContainer):
    print('Inserting Message Roles')
    """ Inserts the relationships between associated message Ids and email addresses into ES.
    :param message_roles_container: Container holding all of the message roles.
    :return: Whether all message roles were inserted into ES.
    """

    def message_roles_json(message_roles: MessageRoles):
        def message_role_json(message_role: MessageRole):
            return {
                'email_address': message_role.email_address,
                'domain': message_role.domain,
                'role': message_role.role
            }

        return {
            '_op_type': 'index',
            '_index': MESSAGE_ROLES_INDEX,
            '_id': message_roles.id,
            'doc': {
                'message_id': message_roles.message_id,
                'message_roles': list(map(message_role_json, message_roles.roles)),
                'account': message_roles.account,
                'date': RIGHT_NOW
            }
        }

    return _perform_bulk_operations(message_roles_json, message_roles_container.message_roles)


def insert_domains_stats(domains: Domains) -> bool:
    """ Inserts domain level stats, namely for each email address associated with a domain how many emails were
    sent to or received from a registered Kunai account.
    :param domains: Domains to be inserted into ES.
    :return: Whether all domains were inserted.
    """
    print('Inserting Domain Level Engagement Statistics.')

    def domain_json(domain: Domain):
        def email_mapping_json(email_mapping: EmailMapping):
            return {
                'email_address': email_mapping.email_address,
                'first_contact_date': email_mapping.first_contact_date,
                'latest_contact_date': email_mapping.latest_contact_date,
                'from_count': email_mapping.from_count,
                'to_count': email_mapping.to_count,
                'cc_count': email_mapping.cc_count,
                'total_count': email_mapping.total
            }

        return {
            '_op_type': 'index',
            '_index': DOMAINS_ENGAGEMENTS_INDEX,
            '_id': domain.id(),
            'doc': {
                'date': RIGHT_NOW,
                'domain': domain.domain,
                'total_cc': domain.total_cc,
                'total_to': domain.total_to,
                'total_from': domain.total_from,
                'total_emails': domain.total_emails,
                'first_contact_date': domain.first_contact_date,
                'latest_contact_date': domain.latest_contact_date,
                'email_engagements': list(map(email_mapping_json, domain.email_mappings.values()))
            }
        }

    return _perform_bulk_operations(domains.domains.values(), domain_json)


def _perform_bulk_operations(json_list, mapping_function) -> bool:
    actions = list(map(mapping_function, json_list))
    response = helpers.parallel_bulk(CLIENT, actions=actions)
    failures = 0
    for success, info in response:
        if not success:
            print(f'A document failed to post: {info}')
            failures += 1
    return failures == 0
