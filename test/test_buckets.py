import json
from unittest import TestCase

from models_email_account import EmailAccount, EmailEngagement


class TestBuckets(TestCase):
    def test_buckets(self):
        with open('./resources/buckets.json', 'r') as f:
            input_str = f.read()
            input_json = json.loads(input_str)
            buckets = EmailAccount(input_json, 'samantha@kunaico.com')
            self.assertEquals(4, len(buckets.emails_from))
            self.assertEquals(5, len(buckets.emails_to))
            self.assertEquals(2, len(buckets.emails_cc))
            self.assertEquals('samantha@kunaico.com', buckets.account)
            rep_bucket = buckets.emails_from[0]
        self.assertIsNotNone(rep_bucket)
        self.assertEquals(54, rep_bucket.count)
        self.assertEquals('from', rep_bucket.relationship)
        self.assertEquals('wexinc.com', rep_bucket.domain)
        self.assertEquals('venkatesh.joshi@wexinc.com', rep_bucket.email_address)
        self.assertEquals('2023-11-15 18:55', rep_bucket.latest_engagement_date)
        self.assertEquals('2023-03-02 15:34', rep_bucket.earliest_engagement_date)

    def test_email_to_csv(self):
        with open('./resources/single_email_valid_domain.json', 'r') as f:
            expected = 'natasa.trajkovic@visa.com,from,29,2023-05-11 16:52,2023-11-30 18:29'
            email_json = json.loads(f.read())
            email = EmailEngagement(email_json, 'from', 'samantha@kunaico.com')
            csv_row = email.to_csv_row()
            self.assertEquals(expected, csv_row)

    def test_bucket_to_csv(self):
        with open('./resources/buckets.json', 'r') as f:
            input_str = f.read()
            input_json = json.loads(input_str)
            buckets = EmailAccount(input_json, 'samantha@kunaico.com')
            csv_rows = buckets.to_csv_rows()
        self.assertEquals(12, len(csv_rows))




