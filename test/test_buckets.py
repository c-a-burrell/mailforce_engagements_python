import json
from unittest import TestCase

from mailforce.models import EmailAccount
from mailforce.models import EmailEngagement


class TestBuckets(TestCase):
    def test_buckets(self):
        with open('./resources/buckets.json', 'r') as f:
            input_str = f.read()
            input_json = json.loads(input_str)
            buckets = EmailAccount(input_json, 'samantha@kunaico.com')
            self.assertEqual(4, len(buckets.emails_from))
            self.assertEqual(5, len(buckets.emails_to))
            self.assertEqual(2, len(buckets.emails_cc))
            self.assertEqual('samantha@kunaico.com', buckets.account)
            rep_bucket = buckets.emails_from[0]
        self.assertIsNotNone(rep_bucket)
        self.assertEqual(54, rep_bucket.count)
        self.assertEqual('from', rep_bucket.relationship)
        self.assertEqual('wexinc.com', rep_bucket.domain)
        self.assertEqual('venkatesh.joshi@wexinc.com', rep_bucket.email_address)
        self.assertEqual('2023-11-15 18:55', rep_bucket.latest_engagement_date)
        self.assertEqual('2023-03-02 15:34', rep_bucket.earliest_engagement_date)

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
        self.assertEqual(12, len(csv_rows))

    def  test_id(self):
        with open('./resources/buckets.json', 'r') as f:
            input_str = f.read()
            input_json = json.loads(input_str)
            buckets_1 = EmailAccount(input_json, 'samantha@kunaico.com')
            buckets_2 =  EmailAccount(input_json, 'samantha@kunaico.com')
            print(buckets_1.id())
            self.assertEqual(buckets_2.id(), buckets_1.id())




