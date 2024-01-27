from mailforce.models import EMAIL_CSV_HEADER
from mailforce.models.email.engagement.email_engagement import EmailEngagement
from mailforce.utils.domain_utils import is_valid_domain
from mailforce.utils.hash_utils import deterministic_id


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
        return deterministic_id(self.account, all_emails)

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
