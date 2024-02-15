from mailforce.models.email.engagement.email_engagement import EmailEngagement
from mailforce.models.email.mapping.email_mapping import EmailMapping
from mailforce.utils.date_utils import get_earliest_date, get_latest_date
from mailforce.utils.hash_utils import deterministic_id

DOMAIN_CSV_HEADER: str = ('email_address,cc Email Count,from Email Count,to Email Count,First Contact Date,'
                          'Last Contact Date,Total Emails')


class Domain:
    """ Holds all the email data for a single domain. """

    # noinspection PyTypeChecker
    def __init__(self, domain: str):
        """
        :param domain: Name of domain.
        """
        self.email_mappings: dict = {}
        self.domain: str = domain
        self.total_cc: int = 0
        self.total_from: int = 0
        self.total_to: int = 0
        self.total_emails: int = 0
        self.first_contact_date: str = None
        self.latest_contact_date: str = None

    def id(self) -> str:
        """
        :return: Deterministic ID based on the following:
         - the domain name
         - the first contact date
         - the last contact date
         - the total number of emails associated with this domain
         - a concatenation of all the email addresses associated with this domain
        """
        email_mappings: str = '+'.join(sorted(self.email_mappings.keys()))
        return deterministic_id(self.domain, self.first_contact_date, self.latest_contact_date, self.total_emails,
                                 email_mappings)

    def add_email(self, email: EmailEngagement):
        """ Adds an Email to this domain and updates the following:
            * `from`, `to` and `cc` counts,
            * The earliest engagement date if the one present in the email object is earlier than the existing one;
            * The latest engagement date if the one present in the email object is later than the existing one; and,
            * The total email count
        If a mapping for this email address is not present, one will be created. Otherwise, the existing email mapping
        will be amended. If the emails domain is different from what is present, no update will occur.
        :param email: Email to be added.
        """
        if self.domain == email.domain:
            self._adjust_counts(email)
            self._add_email_mapping(email)
            self._adjust_dates(email)
        else:
            print(f'Domain mismatch between present:added {self.domain}:{email.domain}')

    def _adjust_dates(self, email: EmailEngagement):
        self.first_contact_date = get_earliest_date(self.first_contact_date, email.earliest_engagement_date)
        self.latest_contact_date = get_latest_date(self.latest_contact_date, email.latest_engagement_date)

    def _add_email_mapping(self, email: EmailEngagement):
        email_address: str = email.email_address
        if email_address not in self.email_mappings:
            self.email_mappings[email_address] = EmailMapping(email)
        else:
            self.email_mappings[email_address].add_email(email)

    def _adjust_counts(self, email: EmailEngagement):
        self.total_emails += email.count
        if email.relationship == 'cc':
            self.total_cc += email.count
        elif email.relationship == 'to':
            self.total_to += email.count
        else:
            self.total_from += email.count

    def to_csv(self) -> list[str]:
        """
        :return: CSV Row
        """
        first_row: str = f'{self.domain},{self.total_cc},{self.total_from},{self.total_to},{self.first_contact_date},{self.latest_contact_date},{self.total_emails}'
        rows: map = map(lambda email_mapping: email_mapping.to_csv_row(), self.email_mappings.values())
        return list(map(lambda row: f'{row}\n', [DOMAIN_CSV_HEADER, first_row] + list(rows)))

