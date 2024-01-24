from models.email.engagement.email_engagement import EmailEngagement
from utils.date_utils import get_earliest_date, get_latest_date


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

