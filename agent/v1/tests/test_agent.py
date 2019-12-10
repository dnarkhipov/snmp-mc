#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from agent.v1.agent import SNMPResponder


class TestSNMPAgent(TestCase):
    def setUp(self) -> None:
        self.agent: SNMPResponder = SNMPResponder(None)

    def test_run(self):
        self.assertIsInstance(self.agent, SNMPResponder)
