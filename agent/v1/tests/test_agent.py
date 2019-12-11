#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
import json

from agent.v1.agent import SnmpResponder


class TestSNMPResponder(TestCase):
    def setUp(self) -> None:
        pass
        # self.agent: SNMPResponder = SNMPResponder(settings=None, mib_objects=None)

    def test_snmp_usr_list(self):
        t = '["usr-sha-aes128:authkey1:privkey1", "usr-md5-none:authkey1"]'
        r = json.loads(t)
        self.assertEqual(len(r), 2)
