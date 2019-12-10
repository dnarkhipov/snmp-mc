import asyncio
import logging
from argparse import Namespace

from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context


LOGGER_TAG = 'snmp-resp'


class SNMPResponder(object):
    """
    SNMPResponder serve the custom MIB.
    """
    _snmpEngine: engine = None

    # asyncio main loop
    _loop: asyncio.events.AbstractEventLoop = None

    _logger: logging.Logger = None

    def __init__(self, settings: Namespace, mib_objects):
        """
        @param mib_objects:  a list of MibObject tuples that this agent will serve
        """

        self._logger = settings.logger

        # Get the event loop for this thread
        self._loop = asyncio.get_event_loop()

        # loop.add_signal_handler(signal.SIGTERM, handler, loop)

        # Create SNMP engine with autogenernated engineID and pre-bound to socket transport dispatcher
        self._snmpEngine = engine.SnmpEngine()

        # Transport setup: UDP over IPv4
        config.addTransport(
            self._snmpEngine,
            udp.domainName,
            udp.UdpTransport().openServerMode(tuple(settings.snmp_bind.split(sep=":", maxsplit=1)))
        )
        self._logger.info(f'[{LOGGER_TAG}] SNMP listening interface: {settings.snmp_bind}')

        # SNMPv3/USM setup

        # user: usr-sha-none, auth: SHA, priv AES
        config.addV3User(
            self._snmpEngine, 'usr-sha-aes128',
            config.usmHMACSHAAuthProtocol, 'authkey1',
            config.usmAesCfb128Protocol, 'privkey1'
        )

        config.addVacmUser(self._snmpEngine, 3, 'usr-sha-aes128', 'authPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

        # Get default SNMP context this SNMP engine serves
        self.snmpContext = context.SnmpContext(self._snmpEngine)

        # Register SNMP Applications at the SNMP engine for particular SNMP context
        cmdrsp.GetCommandResponder(self._snmpEngine, self.snmpContext)
        cmdrsp.SetCommandResponder(self._snmpEngine, self.snmpContext)
        cmdrsp.NextCommandResponder(self._snmpEngine, self.snmpContext)
        cmdrsp.BulkCommandResponder(self._snmpEngine, self.snmpContext)
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self):
        pass


