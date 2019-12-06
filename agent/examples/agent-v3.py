"""
http://snmplabs.com/pysnmp/examples/v3arch/asyncio/agent/cmdrsp/snmp-versions.html#multiple-snmp-usm-users

$ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost:1161 .1.3.6
$ snmpwalk -v3 -u usr-sha-none -l authNoPriv -a SHA -A authkey1 localhost:1161 .1.3.6
$ snmpwalk -v3 -u usr-sha-aes128 -l authPriv -a SHA -A authkey1 -x AES -X privkey1 localhost:1161 .1.3.6
"""

from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
import asyncio

# Get the event loop for this thread
loop = asyncio.get_event_loop()

# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4
config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode(('127.0.0.1', 1161))
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
loop.run_forever()
