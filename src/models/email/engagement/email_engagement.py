from utils.date_utils import to_simple_date_string
from utils.hash_utils import deterministic_id


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
