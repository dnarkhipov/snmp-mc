import argparse
import json
import sys
from pathlib import Path

from .version import ABOUT


def read_settings(override_args=None):

    parser = argparse.ArgumentParser(
        prog='snmp-agent',
        description=ABOUT,
        usage='%(prog)s [options]',
        conflict_handler='resolve',
    )

    parser.add_argument(
        '-h', '--help',
        action='help',
        help='Print this help text and exit')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=ABOUT,
        help='Print version and exit'
    )

    # region common
    grp_common = parser.add_argument_group('common')
    grp_common.add_argument(
        '--config',
        default='config.json',
        dest='cfg_file',
        help='Full path to configuration file'
    )
    # end region

    # region logging
    grp_logging = parser.add_argument_group('logging')
    grp_logging.add_argument(
        '--log-file',
        default='agent.log',
        dest='log_file',
        help='Full path to log file'
    )
    grp_logging.add_argument(
        '--log-level',
        choices=['FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'],
        default='DEBUG',
        dest='log_level',
        type=lambda s: s.upper(),
        help='One of the predefined levels for logging'
    )
    grp_logging.add_argument(
        '--log-maxsize-mb',
        default=50,
        dest='log_maxmb',
        help='Maximum log size in Mb, default 50'
    )
    grp_logging.add_argument(
        '--log-backup-count',
        default=3,
        dest='log_backup_count',
        help='Log files are rotated log-backup-count times before being removed, default 3'
    )
    grp_logging.add_argument(
        '--console-logging',
        action='store_true',
        default=True,
        dest='console_logging',
        help='Write log messages to console (additionally to the other logging destinations)'
    )
    grp_logging.add_argument(
        '--console-log-level',
        choices=['FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'],
        default='INFO',
        dest='console_log_level',
        type=lambda s: s.upper(),
        help='One of the predefined levels for console logging'
    )
    # endregion

    # region DB
    grp_db = parser.add_argument_group('db')
    grp_db.add_argument(
        '--db-url',
        dest='db_url',
        default='',
        help='Database connect string: username:password@host:port/database'
    )
    grp_db.add_argument(
        '--db-debug',
        action='store_true',
        default=False,
        dest='db_debug',
        help='Debug database engine'
    )
    # endregion

    # region SNMP
    grp_api = parser.add_argument_group('snmp')
    grp_api.add_argument(
        '--snmp-bind',
        dest='snmp_bind',
        default='127.0.0.1:4161',
        help='Listen for SNMP packets at this network address, default 127.0.0.1:4161'
    )
    # http://snmplabs.com/snmpresponder/configuration/snmpresponderd.html#snmp-usm-auth-protocol
    grp_api.add_argument(
        '--snmp-auth-protocol',
        choices=['NONE', 'MD5', 'SHA', 'SHA224', 'SHA256', 'SHA384', 'SHA512'],
        default='SHA',
        dest='snmp_auth_protocol',
        type=lambda s: s.upper(),
        help="SNMPv3 message authentication protocol to use. Valid values are: 'NONE', 'MD5', 'SHA', 'SHA224', 'SHA256', 'SHA384', 'SHA512'."
    )
    # http://snmplabs.com/snmpresponder/configuration/snmpresponderd.html#snmp-usm-priv-protocol
    grp_api.add_argument(
        '--snmp-priv-protocol',
        choices=['NONE', 'DES', 'AES', 'AES192', 'AES256', 'AES192BLMT', 'AES256BLMT', '3DES'],
        default='AES',
        dest='snmp_priv_protocol',
        type=lambda s: s.upper(),
        help="SNMPv3 message encryption protocol to use. Valid values are: 'NONE', 'DES', 'AES', 'AES192', 'AES256', 'AES192BLMT', 'AES256BLMT', '3DES'."
    )
    grp_api.add_argument(
        '--snmp-user',
        default=list(),
        action='append',
        dest='snmp_user',
        help='SNMPv3 user. Template: "user-name:auth-key:encryption-key"'
    )
    # endregion

    if override_args is not None:
        settings = parser.parse_args(override_args)
    else:
        cmd_line_args = sys.argv[1:]
        cmd_line_opts = parser.parse_args(cmd_line_args)
        cfg_file = Path(cmd_line_opts.cfg_file)

        if cfg_file.exists():
            try:
                with cfg_file.open() as json_file:
                    cfg = list()
                    for (key, value) in json.load(json_file).items():
                        if type(value) == list:
                            cfg.extend([f"--{key}={list_value}" for list_value in value])
                        else:
                            cfg.append(f"--{key}={value}")
            except Exception as e:
                parser.error(f"Can't load json configuration file {cfg_file}: {e}")
        elif any('--config' in p for p in cmd_line_args):
            parser.error(f"Configuration file {cfg_file} does not exist.")
        else:
            cfg = []

        # параметры командной строки имеют приоритет перед конфигурационным файлом
        settings = parser.parse_args(cfg + cmd_line_args)

    return parser, settings
