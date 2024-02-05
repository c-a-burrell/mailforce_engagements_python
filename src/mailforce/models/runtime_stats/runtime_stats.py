from mailforce.models.domain.domains import Domains
from mailforce.models.email.account.email_accounts import EmailAccounts


class RuntimeStats:
    """ Class that holds all the statistics for a given run. """

    def __init__(self, run_date: str, domains: Domains, email_accounts: EmailAccounts,
                 start_time: float, end_time: float):
        """
        :param run_date: Date of processing run.
        :param domains: All domains processed during this run.
        :param email_accounts: All Email accounts processed during this run.
        """
        accounts = email_accounts.accounts
        self.run_date: str = run_date
        self.email_accounts_processed: int = len(email_accounts.accounts)
        self.domains_processed: int = len(domains.domains)
        self.cc_emails_processed: int = sum(list(map(lambda account: len(account.emails_cc), accounts)))
        self.to_emails_processed: int = sum(list(map(lambda account: len(account.emails_to), accounts)))
        self.from_emails_processed: int = sum(list(map(lambda account: len(account.emails_from), accounts)))
        self.start_time: float = start_time
        self.end_time: float = end_time
        self.emails_processed: int = self.to_emails_processed + self.cc_emails_processed + self.from_emails_processed

    def set_times(self, start_time: float, end_time: float):
        self.start_time = start_time
        self.end_time = end_time

    def elapsed_time(self):
        def proper_round(num, dec=0):
            num = str(num)[:str(num).index('.') + dec + 2]
            if num[-1] >= '5':
                return float(num[:-2 - (not dec)] + str(int(num[-2 - (not dec)]) + 1))
            return float(num[:-1])
        seconds = self.end_time - self.start_time
        if seconds < 60:
            return f'{seconds} seconds.'
        else:
            minutes = proper_round(seconds / 60)
            seconds = proper_round(seconds % 60)
            return f'{minutes} minutes, {seconds} seconds.'

    def __str__(self):
        return (f'Run Date: {self.run_date}\nAccounts: {self.email_accounts_processed}'
                f'\nDomains: {self.domains_processed}\nCC Emails: {self.cc_emails_processed}\n'
                f'To Emails: {self.to_emails_processed}\nFrom Emails: {self.from_emails_processed}\n'
                f'Start Time: {self.start_time}\nEnd Time:{self.end_time}\n'
                f'Elapsed Time (Seconds):{self.elapsed_time()}')
