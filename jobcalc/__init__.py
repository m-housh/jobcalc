# -*- coding: utf-8 -*-

import os
import logging
import sys
from .utils import bool_from_env_string

debug = bool_from_env_string(
    os.environ.get('DEBUG', os.environ.get('JOBCALC_DEBUG', 'false'))
)

if debug is True:  # pragma: no cover
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(levelname)s - (%(filename)s::%(funcName)s):msg: %(message)s'
    )
else:  # pragma: no cover
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

logger = logging.getLogger(__name__)
logger.debug('In debug mode.')


__author__ = 'Michael Housh'
__email__ = 'mhoush@houshhomeenergy.com'
__version__ = '0.0.1'
