import json
import unittest
from unittest import TestCase

import pytest

from models.email.engagement.email_engagement import EmailEngagement
from utils.domain_utils import is_valid_domain, alphabetize_domains


class TestDomainUtils(TestCase):

    def test_positive(self):
        self._test_domain('valid', True)

    def test_negative(self):
        self._test_domain('invalid', False)

    def _test_domain(self, prefix: str, is_valid: bool):
        filename = f"./resources/single_email_{prefix}_domain.json"
        with open(filename, 'r') as f:
            email_json = json.loads(f.read())
            email = EmailEngagement(email_json, 'from', 'account')
            valid_domain = is_valid_domain(email.domain)
            self.assertEquals(is_valid, valid_domain)

    @pytest.mark.skip(reason='Function written only for test')
    @unittest.skip('Function written only for test')
    def test_alpha(self):
        alphabetized = alphabetize_domains()
        print(alphabetized)