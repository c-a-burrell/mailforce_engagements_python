from mailforce.models.domain.domain import Domain
from mailforce.models.email.engagement.email_engagement import EmailEngagement


class Domains:
    """ Holds all the domains processed during the current run."""
    def __init__(self):
        self.domains: dict[str, Domain] = {}

    def add_email(self, email: EmailEngagement):
        """
        Adds an Email instance to this Domains Instance. If this email belongs to a Domain that is not already present,
        then a new Domain is created. Otherwise, the existing domain is updated.
        :param email: Email to be added.
        """
        domain: str = email.domain
        if domain not in self.domains:
            self.domains[domain] = Domain(domain)
        self.domains[domain].add_email(email)
