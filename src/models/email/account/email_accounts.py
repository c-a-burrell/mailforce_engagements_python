from models import ACCOUNTS_CSV_HEADER
from models.email.account.email_account import EmailAccount


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




