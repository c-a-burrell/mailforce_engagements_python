from date_utils import get_earliest_date, get_latest_date, to_simple_date_string
from domain_utils import is_valid_domain
from hash_utils import deterministic_id

EMAIL_CSV_HEADER: str = 'email_address,relation,count,first_contact,most_recent_contact'
ACCOUNTS_CSV_HEADER: str = 'account,emails_from_count,emails_to_count,emails_cc_count,total_emails_count'


class EmailAccount:
    """ This class holds all the emails for an individual account. """
    def __init__(self, results_json: dict[str, any], account: str):
        """
        :param results_json: JSON dict holding email data.
        :param account: account name.
        """

        def _process_emails(email_list: list, relationship: str) -> list[EmailEngagement]:
            unfiltered: list = list(map(lambda email: EmailEngagement(email_json=email, relationship=relationship,
                                                                      account=account), email_list))
            return list(filter(lambda email: is_valid_domain(email.domain), unfiltered))

        aggregations: dict[str, any] = results_json['aggregations']
        cc_emails: list[dict[str, any]] = aggregations['group_by_cc']['buckets']
        to_emails: list[dict[str, any]] = aggregations['group_by_to']['buckets']
        from_emails: list[dict[str, any]] = aggregations['group_by_from']['buckets']
        self.account: str = account
        self.emails_cc: list[EmailEngagement] = _process_emails(cc_emails, 'cc')
        self.emails_to: list[EmailEngagement] = _process_emails(to_emails, 'to')
        self.emails_from: list[EmailEngagement] = _process_emails(from_emails, 'from')
        self.emails_to_count: int = len(self.emails_to)
        self.emails_from_count: int = len(self.emails_from)
        self.emails_cc_count: int = len(self.emails_cc)
        self.total_email_count = self.emails_to_count + self.emails_cc_count + self.emails_from_count

    def id(self):
        """
        :return: Deterministic ID based on the IDs of all the underlying Email Engagements and the
        account name
        """
        def emails_set_str(emails: list[EmailEngagement]) -> str:
            return ''.join(list(sorted(set(map(lambda engagement: engagement.id, emails)))))

        all_emails: str = (f'{emails_set_str(self.emails_to)}'
                           f'{emails_set_str(self.emails_from)}'
                           f'{emails_set_str(self.emails_cc)}')
        return deterministic_id(self.account,all_emails)

    def to_csv_rows(self, include_account: bool = None) -> list[str]:
        """
        :param include_account: Whether the account is to be included as a part of the output.
        :return: CSV formatted string with header.
        """
        header: str = f'account,{EMAIL_CSV_HEADER}' if include_account else EMAIL_CSV_HEADER
        all_emails: list[EmailEngagement] = self.emails_to + self.emails_cc + self.emails_from
        if include_account:
            all_emails = sorted(all_emails, key=lambda email: email.account)
        return [header] + list(map(lambda email: email.to_csv_row(include_account), all_emails))

    def to_account_csv_row(self) -> str:
        """
        :return: CSV of account-level info
        """
        return f'{self.account},{self.emails_to_count},{self.emails_from_count},{self.emails_cc_count},{self.total_email_count}'

    def append_emails(self, emails):
        """ Adds all the emails to this one.
        :param emails: Emails to be added.
        """
        if emails:
            self.emails_cc += emails.emails_cc
            self.emails_to += emails.emails_to
            self.emails_from += emails.emails_from


class EmailAccounts:
    """ Holds multiple accounts for processing. """
    def __init__(self):
        self.accounts: list[EmailAccount] = []

    def add_account(self, account: EmailAccount):
        """ Adds an account to the internal list
        :param account: Account to be added
        """
        if account:
            self.accounts.append(account)

    def to_csv_rows(self) -> list[str]:
        """
        :return: CSV Row for all accounts.
        """
        all_accounts = map(lambda account: f'{account.to_account_csv_row()}\n', self.accounts)
        header_row = [f'{ACCOUNTS_CSV_HEADER}\n']
        return header_row + list(all_accounts)


class EmailEngagement:
    """ This class holds all the data for a specific email engagement. """
    def __init__(self, email_json: dict[str, any], relationship: str, account: str):
        """
        :param email_json: JSON dict holding email data.
        :param relationship: Whether this email was sent to, from or received as a cc.
        :param account: Name of account.
        """
        min_date: str = to_simple_date_string(email_json['min_date']['value_as_string'])
        max_date: str = to_simple_date_string(email_json['max_date']['value_as_string'])
        self.earliest_engagement_date: str = min_date
        self.latest_engagement_date: str = max_date
        self.email_address: str = email_json['key']
        self.domain: str = self.email_address.split('@')[1]
        self.count: int = email_json['doc_count']
        self.relationship: str = relationship
        self.account: str = account
        self.id: str = deterministic_id(self.email_address, self.relationship, self.account,
                                        min_date, max_date)

    def to_csv_row(self, add_account: bool = False) -> str:
        """
        :param add_account: Whether to add the account to the CSV output.
        :return: CSV output.
        """
        min_date: str = self.earliest_engagement_date
        max_date: str = self.latest_engagement_date
        csv_row: str = f'{self.email_address},{self.relationship},{self.count},{min_date},{max_date}'
        return f'{self.account},{csv_row}' if add_account else csv_row


class EmailMapping:
    """ This class holds all the engagement data for a single email address across all registered accounts. """
    def __init__(self, email: EmailEngagement):
        """
        :param email: Email instance that serves as a base for this mapping.
        """
        self.email_address: str = email.email_address
        self.first_contact_date: str = email.earliest_engagement_date
        self.latest_contact_date: str = email.latest_engagement_date
        self.cc_count: int = email.count if email.relationship == 'cc' else 0
        self.to_count: int = email.count if email.relationship == 'to' else 0
        self.from_count: int = email.count if email.relationship == 'from' else 0
        self.total: int = email.count

    def add_email(self, email: EmailEngagement):
        """ Adds an Email to this Email Mapping and updates the following:
            * `from`, `to` and `cc` counts,
            * The earliest engagement date if the one present in the email object is earlier than the existing one;
            * The latest engagement date if the one present in the email object is later than the existing one; and,
            * The total email count
        If for some reason there is an email address mismatch between the one that this mapping was initalized with and
        the one that is being added, the existing mapping will not be updated.
         :param email: Email to be added.
        """
        if email.email_address == self.email_address:
            self._adjust_counts(email)
            self._adjust_dates(email)
        else:
            print(f'Email mismatch between present:added {self.email_address}:{email.email_address}')

    def _adjust_dates(self, email):
        self.first_contact_date = get_earliest_date(self.first_contact_date, email.earliest_engagement_date)
        self.latest_contact_date = get_latest_date(self.latest_contact_date, email.latest_engagement_date)

    def _adjust_counts(self, email):
        self.total += email.count
        if email.relationship == 'cc':
            self.cc_count += email.count
        elif email.relationship == 'to':
            self.to_count += email.count
        else:
            self.from_count += email.count

    def to_csv_row(self) -> str:
        """
        :return: CSV row representing the current Email Account.
        """
        cc_count: int = self.cc_count
        to_count: int = self.to_count
        from_count: int = self.from_count
        total: int = self.total
        first_contact_date: str = self.first_contact_date
        last_contact_date: str = self.latest_contact_date
        return (f'{self.email_address},{cc_count},{from_count},{to_count},{first_contact_date},{last_contact_date}'
                f',{total}')

