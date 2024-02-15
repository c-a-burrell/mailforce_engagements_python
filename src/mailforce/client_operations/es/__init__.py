from elasticsearch import Elasticsearch

from mailforce import CONFIG

CLIENT: Elasticsearch = Elasticsearch(
            cloud_id=CONFIG.elastic_cloud_id,
            basic_auth=('elastic', CONFIG.elastic_password))
