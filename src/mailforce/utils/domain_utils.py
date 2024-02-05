import os


def _get_domains() -> list:
    with open('../resources/domains.txt', 'r') as f:
        return list(map(lambda line: line.replace('\n', '').strip(), f.readlines()))


DOMAINS: list = _get_domains()


def is_valid_domain(domain: str) -> bool:
    """
    :param domain: Domain to be tested for validity.
    :return: Whether this domain is allow-listed.
    """
    return domain and domain in DOMAINS


def alphabetize_domains() -> list:
    """
    :return: List of alphabetized domains.
    """
    return sorted(DOMAINS)
