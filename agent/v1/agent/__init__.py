__all__ = ['main', 'SNMPResponder']

import logging
import logging.handlers
import sys
from pathlib import Path

from .responder import SNMPResponder
from .config import (
    read_settings
)
from .version import ABOUT


AGENT_ID = '52303b6d-1462-4468-918e-2c1b90af7871'
LOGGER_TAG = 'core'

def start_agent():
    parser, settings = read_settings()

    logger = logging.getLogger(f'snmp-agent-{AGENT_ID}')

    logger.setLevel(logging.getLevelName(settings.log_level))
    # lh = logging.handlers.WatchedFileHandler(settings.log_file)
    lh = logging.handlers.RotatingFileHandler(filename=settings.log_file,
                                              maxBytes=settings.log_maxmb * 1024 * 1024,
                                              backupCount=settings.log_backup_count)
    lh.setFormatter(logging.Formatter('%(asctime)s [%(process)d] [%(thread)d] [%(levelname)s] %(message)s'))
    lh.setLevel(logging.getLevelName(settings.log_level))
    logger.addHandler(lh)

    if settings.db_debug:
        # Debug sqlalchemy library
        dbl = logging.getLogger('sqlalchemy')
        dbl.setLevel(logging.DEBUG)
        # dblh = logging.handlers.WatchedFileHandler(os.path.join(os.path.dirname(settings.log_file), 'db-debug.log'))
        dblh = logging.handlers.RotatingFileHandler(filename=Path(settings.log_file).parent.joinpath('db-debug.log'),
                                                    maxBytes=settings.log_maxmb * 1024 * 1024,
                                                    backupCount=settings.log_backup_count)
        dblh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        dbl.addHandler(dblh)

    # if True:
    #     # Debug pysnmp library
    #
    #     from pysnmp import debug
    #
    #     debug.setLogger(debug.Debug('io', loggerName='snmp-debug'))
    #     snmpl = logging.getLogger('snmp-debug')
    #     snmpl.setLevel(logging.DEBUG)
    #     snmplh = logging.handlers.RotatingFileHandler(filename=Path(settings.log_file).parent.joinpath('snmp-debug.log'),
    #                                                 maxBytes=settings.log_maxmb * 1024 * 1024,
    #                                                 backupCount=settings.log_backup_count)
    #     snmplh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    #     snmpl.addHandler(snmplh)

    if settings.console_logging:
        lhc = logging.StreamHandler()
        lhc.setFormatter(logging.Formatter('%(asctime)s [%(process)d] [%(thread)d] [%(levelname)s] %(message)s'))
        lhc.setLevel(logging.getLevelName(settings.console_log_level))
        logger.addHandler(lhc)

    settings.agent_id = AGENT_ID
    settings.logger = logger

    logger.info(f'[{LOGGER_TAG}] Starting {ABOUT} ...')
    with SNMPResponder(settings, None) as srv:
        srv.run()


def main():
    try:
        start_agent()
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user\n')
