import hashlib


def deterministic_id(*args):
    """
    :param args: List of values to be used in generating a deterministic ID.
    :return: Deterministic hash based on input.
    """
    input_str = ''.join(list(map(lambda arg: arg, str(args))))
    return hashlib.md5(input_str.encode()).hexdigest()
