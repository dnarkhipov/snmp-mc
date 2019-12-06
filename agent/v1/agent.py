#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
import asyncio, signal


logging.basicConfig(level=logging.INFO)

# def handler(loop):
#     loop.remove_signal_handler(signal.SIGTERM)
#     loop.stop()

# Get the event loop for this thread
loop = asyncio.get_event_loop()

# loop.add_signal_handler(signal.SIGTERM, handler, loop)

# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4
config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode(('127.0.0.1', 4161))
)

# SNMPv3/USM setup

# user: usr-md5-des, auth: MD5, priv DES
config.addV3User(
    snmpEngine, 'usr-md5-des',
    config.usmHMACMD5AuthProtocol, 'authkey1',
    config.usmDESPrivProtocol, 'privkey1'
)
# user: usr-sha-none, auth: SHA, priv NONE
config.addV3User(
    snmpEngine, 'usr-sha-none',
    config.usmHMACSHAAuthProtocol, 'authkey1'
)
# user: usr-sha-none, auth: SHA, priv AES
config.addV3User(
    snmpEngine, 'usr-sha-aes128',
    config.usmHMACSHAAuthProtocol, 'authkey1',
    config.usmAesCfb128Protocol, 'privkey1'
)

# Allow full MIB access for each user at VACM
config.addVacmUser(snmpEngine, 3, 'usr-md5-des', 'authPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))
config.addVacmUser(snmpEngine, 3, 'usr-sha-none', 'authNoPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))
config.addVacmUser(snmpEngine, 3, 'usr-sha-aes128', 'authPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

# Get default SNMP context this SNMP engine serves
snmpContext = context.SnmpContext(snmpEngine)

# Register SNMP Applications at the SNMP engine for particular SNMP context
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

# Run asyncio main loop
try:
    loop.run_forever()
finally:
    loop.close()
