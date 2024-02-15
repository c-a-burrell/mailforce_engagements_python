# Mailforce Engagements Python
This project queries Elasticsearch for all unique domains, then queries Elasticsearch again for an aggregated listing of all email interactions for those domains

# Output
The following data is output to Elasticsearch:
<details>
<summary> Data output to ES</summary>

**Email Address Engagement**

For each email address that has interacted with that account, the following is compiled:
* Email address
* Domain name
* Earliest engagement date
* Most recent engagement date
* Count (number of interactions)
* Engagement role, which is one of the following:
  * `To`
  * `From`
  * `CC`
The data points that are written to the `'search-accounts-engagements` Elasticsearch index contains a listing of all the email addresses separated by role.

The data points that are written to the`ACCOUNTS_STAT_INDEX` Elasticsearch index contains a raw count of all the email addresses for any given role.

**Domain Level Interactions**

For each TLD that has interacted with that account, the following is compiled:
* Domain name
* Earliest engagement date
* Most recent engagement date
* Count (number of interactions)

All the above data points are written to the `search-domains-engagements` Elasticsearch index.

**Individual Email Message Relationships**

For each individual email message belonging to an account, the following is compiled on a per-email address basis:
* Email Address
* Engagement role, which is one of the following:
  * `To`
  * `From`
  * `CC`
* Message Id
These are written to the `search-message-roles` Elasticsearch index.

**Runtime Statistics**

After evey successful execution the following is published to the `search-runtime-stats` 
Elasticsearch index:
* Execution date
* Number of email accounts processed
* Number of domains processed
* Number of individual emails processed
As a part of normal operations, this script will query this index first in order to derive the latest run date
that it can use as a lower exclusive bound for purposes of performing its Elasticsearch queries. If this index is empty,
it will use the present date as an upper **inclusive** bound.
</details>

## Prerequisites
* Python 3 (Best installed with Homebrew)

## Installation
```commandline
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Executing
### Local Execution
This project is designed to be run as a Lambda function, but can be executed as a standalone script:
```commandline
python3 ./main.py
```
In order to run this locally, you will need to copy over the secret values from the Function's environmental variables 
into the mapping in `src/resources/local_setup.json` *before* executing the above command. As of `05 February 2024`, the
following values are required to be set in either the local setup file or the function's environment variables:

| Key              | Description                                 |
|------------------|---------------------------------------------|
| ELASTIC_PASSWORD | API Password needed to access Elasticsearch |
| ELASTIC_CLOUD_ID | API Endpoint to Elasticsearch               |



### Lambada Payload
It should be noted that the normal JSON payload of the trigger for this function will be an empty mapping:
```json
{}
```
However, if it is desired that emails from a specific date are needed (for backfilling purposes), then it can be 
specified as follows:
```json
{"from_date": "2024-01-01T00:00"}
```
Also, if it is desired that only certain accounts be considered (useful in  the case of backfilling individual accounts),
then they need to be provided:
```json
{
  "from_date": "2024-01-01T00:00",
  "backfilled_accounts": ["kunai-jim", "kunai-joe"]
}
```
Similarly, if we want to *exclude* accounts:
```json
{"exclude_accounts": ["kunai-jim", "kunai-joe"]}
```
Note that you can specify accounts to both backfill *and* exclude. 
* The default behavior if *no* accounts are provided to be backfilled is to process *all* accounts present, 
  but *only* from the point of the last runtimne date. 
* If accounts are specified to be backfilled, then *only* those accounts will be processed from the very first entry 
  found in ES for them. However, the runtime date will not be recorded (but all other data will be) so as to avoid data inconsistency issues.
## Notes
* Each top-level object is stored in its relevant index with a deterministically generated identifier that
so that the same Email Address Engagement, Domain Level Interaction or Individual Email Message Relationship
harvested on two different occasions will *not* be stored in the index twice.