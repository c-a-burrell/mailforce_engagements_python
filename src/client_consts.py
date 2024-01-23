from elasticsearch import Elasticsearch

ELASTIC_PASSWORD: str = 'cJksFDtj6E1I7KmRyL2ahB4L'
CLOUD_ID: str = 'Shinobi_Document_Store:dXMtd2VzdC0xLmF3cy5mb3VuZC5pbzo0NDMkODVhYjQ2MzIzN2QyNGE3YWFiNDgyODRiOWJkMzI3YTckOWFmMWUwYTBjMzI3NDA2ODkzNzI4YmU0MjY3NWFkOTI='

CLIENT: Elasticsearch = Elasticsearch(
    cloud_id=CLOUD_ID,
    basic_auth=('elastic', ELASTIC_PASSWORD))