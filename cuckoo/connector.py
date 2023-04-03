""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

from connectors.core.connector import Connector, get_logger, ConnectorError
from .operations import Cuckoo

logger = get_logger("cuckoo")


class CuckooConn(Connector):
    def execute(self, config, operation, params, **kwargs):
        logger.debug("Invoking Cuckoo execute()")
        try:
            cuckoo = Cuckoo(config)
            operations = {
                'submit_file':cuckoo.detonate_file,
                'submit_url': cuckoo.submit_url,
                'get_report': cuckoo.get_report
            }
            operation = operations.get(operation)
            return operation(params)
        except Exception as Err:
            logger.exception("Exception in execute function: {} ".format(str(Err)))
            raise ConnectorError(str(Err))

    def check_health(self, config):
        cuckoo = Cuckoo(config)
        return cuckoo._check_health()
