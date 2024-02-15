from datetime import datetime

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
ALT_DATE_FORMAT = '%Y-%m-%d %H:%M'


# 2023-11-15T18:55:34.000Z
def to_simple_date_string(date_str: str) -> str:
    """ Generates a simplified date string from one that is formatted like `1969-08-03T15:15:15.000Z`.
    :param date_str: Input date string.
    :return: Date string in `YYYY-mm-dd HH:MM` format.
    """
    stripped_string = date_str.split('.')[0]
    the_date = datetime.strptime(stripped_string, DATE_FORMAT)
    return the_date.strftime(ALT_DATE_FORMAT)


def get_latest_date(first_date_str: str, second_date_str: str) -> str:
    """ Gets the latest of the two dates.
    :param first_date_str: First date to be compared.
    :param second_date_str: Second date to be compared.
    :return: latest of the two dates.
    """
    (first_date, second_date) = _get_formatted_date_strings(first_date_str, second_date_str)
    return first_date_str if first_date and first_date > second_date else second_date_str


def get_earliest_date(first_date_str, second_date_str) -> str:
    """ Gets the earliest of the two dates.
        :param first_date_str: First date to be compared.
        :param second_date_str: Second date to be compared.
        :return: earliest of the two dates.
        """
    (first_date, second_date) = _get_formatted_date_strings(first_date_str, second_date_str)
    return first_date_str if first_date and first_date < second_date else second_date_str


def now():
    """
    :return: Current date in YYYY-mm-DD'T'HH:MM:SS format
    """
    return datetime.now().strftime(DATE_FORMAT)


def _get_formatted_date_strings(first_date_str: str, second_date_str: str) -> (str, str):
    return (datetime.strptime(first_date_str, ALT_DATE_FORMAT),
            datetime.strptime(second_date_str, ALT_DATE_FORMAT)) if first_date_str \
        else (None, datetime.strptime(second_date_str, ALT_DATE_FORMAT))
