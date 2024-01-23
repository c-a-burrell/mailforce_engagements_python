from client_consts import CLIENT
from date_utils import now
from models_email_account import EmailAccount
from models_message_role import MessageRoles

INDEX: str = 'search-shinobi-email'
RUNTIME_STATS_INDEX: str = 'search-runtime-stats'
MIN_DATE: str = '2023-01-01'
MAX_DATE: str = '2023-12-30'
BATCH_SIZE: int = 2500


def get_last_runtime_date():
    """
    :return: Last runtime date if present else None
    """
    query = {
        "aggs": {
            "max_run_date": {"max": {"field": "run_date"}}
        }
    }
    results = _search(query, RUNTIME_STATS_INDEX)
    if results and 'aggregations' in results:
        return results['aggregations']['max_run_date']['value_as_string']
    else:
        return None


def get_emails_by_account(account: str, last_runtime_date: str = None) -> EmailAccount:
    """ Gets all the aggregated `to`, `from` and `cc` email addresses for the account in question.
    If no results are returned, then an alternate index will be searched.
    :param account:
    :param last_runtime_date: Last runtime date. If present, then all results posted after this date will be gotten.
    If not present, then all results in the index up until the present date will be fetched.
    :return: EmailAccount
    """
    results = _search_emails_by_account(account=account,
                                        last_runtime_date=last_runtime_date)
    hits = results['hits']['hits']
    master_email_account: EmailAccount = None
    while len(hits) > 0:
        print(f'Processing {len(hits)} email search results for account {account}')
        print(results.keys())
        for agg in results['aggregations'].keys():
            remaining_docs = results['aggregations'][agg]['sum_other_doc_count']
            if remaining_docs and remaining_docs > 0:
                print(
                    f'Warning - still {remaining_docs} more results for {agg} in account {account} for aggregation {agg}')
        if master_email_account is None:
            master_email_account = EmailAccount(results, account)
        else:
            email_account = EmailAccount(results, account)
            master_email_account.append_emails(email_account)
        last_index = len(hits) - 1
        search_after = hits[last_index]['sort'][0]
        results = _search_emails_by_account(account=account,
                                            last_runtime_date=last_runtime_date,
                                            search_after=search_after)
        hits = results['hits']['hits']
    return master_email_account


def search_accounts():
    """
    :return: All email accounts present in this index
    """
    query = {
        "aggs": {
            "account": {"terms": {"field": "account", "size": 10000}}},
        "query": {"query_string": {"query": "account:*"}},
        "collapse": {"field": "account"},
        "fields": ["account"],
        "_source": 'false'
    }
    return CLIENT.search(index=INDEX, body=query)


def get_message_roles(last_runtime_date: str = None) -> list[MessageRoles]:
    """
    :param last_runtime_date: Last runtime date. If present, then all results posted after this date will be gotten.
    If not present, then all results in the index up until the present date will be fetched.
    :return: All message roles across accounts.
    """
    response = _search_message_roles(last_runtime_date=last_runtime_date)
    hits = response['hits']['hits']
    all_hits = []
    while len(hits) > 0:
        all_hits += hits
        print(f'Processing {len(hits)} message roles search results')
        last_index = len(hits) - 1
        search_after = hits[last_index]['sort'][0]
        response = _search_message_roles(last_runtime_date=last_runtime_date, search_after=search_after)
        hits = response['hits']['hits']
    print(f'Processed {len(all_hits)} results.')
    return list(map(lambda message_role_json: MessageRoles(message_role_json['fields']), all_hits))


def _search_message_roles(last_runtime_date, search_after=None):
    query = {
        "size": BATCH_SIZE,
        "query": {
            "bool": {
                "must": [{"range": {"date": _date_aggs(last_runtime_date)}}]
            }
        },
        "sort": [
            {"date": {"order": "asc"}}
        ],
        "fields": ["account", "messageId", "cc.address", "to.address", "from.address"],
        "_source": "false"
    }
    return _search(query, INDEX, search_after)


def _search_emails_by_account(account, last_runtime_date, search_after=None):
    def group_by_aggs(field):
        return {
            'terms': {'field': field, 'size': 10000},
            'aggs': {
                'max_date': {'max': {'field': 'date'}},
                'min_date': {'min': {'field': 'date'}}
            }
        }

    query = {
        'size': BATCH_SIZE,
        'aggs': {
            'group_by_from': group_by_aggs('from.address'),
            'group_by_to': group_by_aggs('to.address'),
            'group_by_cc': group_by_aggs('cc.address')
        },
        'query': {
            'bool': {
                'must': [
                    {'term': {'account': account}},
                    {'range': {'date': _date_aggs(last_runtime_date)}}
                ]
            }
        },
        "sort": [
            {"date": {
                "order": "asc"
            }}
        ],
        '_source': 'false'
    }
    return _search(query, INDEX, search_after)


def _search(query, index, search_after=None):
    if search_after:
        query['search_after'] = [search_after]
    return CLIENT.search(index=index, body=query)


def _date_aggs(last_runtime_date=None):
    date_aggregation = {
        'format': "strict_date_optional_time"
    }
    if last_runtime_date:
        date_aggregation['gt'] = last_runtime_date
    else:
        date_aggregation['lte'] = now()
    return date_aggregation
