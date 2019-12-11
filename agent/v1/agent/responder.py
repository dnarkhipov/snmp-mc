import asyncio
import logging
from argparse import Namespace

from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import engine as snmp_engine, config as snmp_cfg
from pysnmp.entity.rfc3413 import cmdrsp, context


SnmpSecurityLevel = {0: "noAuthNoPriv", 1:"authNoPriv", 2:"authPriv"}
SnmpAuthProtocol = {
    "NONE": snmp_cfg.usmNoAuthProtocol,
    "MD5": snmp_cfg.usmHMACMD5AuthProtocol,
    "SHA": snmp_cfg.usmHMACSHAAuthProtocol,
    "SHA224": snmp_cfg.usmHMAC128SHA224AuthProtocol,
    "SHA256": snmp_cfg.usmHMAC192SHA256AuthProtocol,
    "SHA384": snmp_cfg.usmHMAC256SHA384AuthProtocol,
    "SHA512": snmp_cfg.usmHMAC384SHA512AuthProtocol
}

SnmpPrivacyProtocol = {
    "NONE": snmp_cfg.usmNoPrivProtocol,
    "DES": snmp_cfg.usmDESPrivProtocol,
    "AES": snmp_cfg.usmAesCfb128Protocol,
    "AES192": snmp_cfg.usmAesCfb192Protocol,
    "AES256": snmp_cfg.usmAesCfb256Protocol,
    "AES192BLMT": snmp_cfg.usmAesBlumenthalCfb192Protocol,
    "AES256BLMT": snmp_cfg.usmAesBlumenthalCfb256Protocol,
    "3DES": snmp_cfg.usm3DESEDEPrivProtocol
}


LOGGER_TAG = 'snmp-resp'


class SnmpResponder(object):
    """
    SnmpResponder serve the custom MIB.
    """
    _snmpEngine: snmp_engine = None

    # asyncio main loop
    _loop: asyncio.events.AbstractEventLoop = None

    _logger: logging.Logger = None

    def __init__(self, settings: Namespace, mib_objects):
        """
        @param settings: agent global settings
        @param mib_objects: a list of MibObject tuples that this agent will serve
        """

        self._logger = settings.logger

        # Get the event loop for this thread
        self._loop = asyncio.get_event_loop()

        # loop.add_signal_handler(signal.SIGTERM, handler, loop)

        # Create SNMP engine with autogenernated engineID and pre-bound to socket transport dispatcher
        self._snmpEngine = snmp_engine.SnmpEngine()

        # Transport setup: UDP over IPv4
        snmp_cfg.addTransport(
            self._snmpEngine,
            udp.domainName,
            udp.UdpTransport().openServerMode(tuple(settings.snmp_bind.split(sep=":", maxsplit=1)))
        )
        self._logger.info(f'[{LOGGER_TAG}] SNMP listening interface: {settings.snmp_bind}')

        # SNMPv3/USM setup

        for usr in settings.snmp_user:
            u_name, *u_keys = usr.split(sep=":", maxsplit=2)
            sec_level_id = len(u_keys)
            sec_level = SnmpSecurityLevel[sec_level_id]

            if sec_level_id:
                auth_key = u_keys[0]
                auth_protocol = SnmpAuthProtocol.get(settings.snmp_auth_protocol, SnmpAuthProtocol['NONE'])
                if sec_level_id > 1:
                    priv_key = u_keys[1]
                    priv_protocol = SnmpPrivacyProtocol.get(settings.snmp_priv_protocol, SnmpPrivacyProtocol['NONE'])
                else:
                    priv_key = None
                    priv_protocol = SnmpPrivacyProtocol['NONE']
            else:
                auth_key = None
                auth_protocol = SnmpAuthProtocol['NONE']
                priv_key = None
                priv_protocol = SnmpPrivacyProtocol['NONE']

            snmp_cfg.addV3User(
                self._snmpEngine, u_name,
                auth_protocol, auth_key,
                priv_protocol, priv_key
            )
            self._logger.debug('[%s] New user registered: <%s><%s><%s%s>' % (LOGGER_TAG, u_name, sec_level,
                                                                      (f"{auth_key}({settings.snmp_auth_protocol})" if auth_key else ""),
                                                                      (f":{priv_key}({settings.snmp_priv_protocol})" if priv_key else "")
                                                                      ))
            snmp_cfg.addVacmUser(self._snmpEngine, 3, u_name, sec_level, (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

        # Get default SNMP context this SNMP engine serves
        self.snmpContext = context.SnmpContext(self._snmpEngine)

        # Register SNMP Applications at the SNMP engine for particular SNMP context
        cmdrsp.GetCommandResponder(self._snmpEngine, self.snmpContext)
        cmdrsp.SetCommandResponder(self._snmpEngine, self.snmpContext)
        cmdrsp.NextCommandResponder(self._snmpEngine, self.snmpContext)
        cmdrsp.BulkCommandResponder(self._snmpEngine, self.snmpContext)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self):
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()


