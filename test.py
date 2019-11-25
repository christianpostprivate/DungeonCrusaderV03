# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 12:28:04 2019

@author: Christian
"""

import logging
import importlib
importlib.reload(logging)
import sys

print(logging.__version__)
logging.basicConfig(format="%(message)s",level=logging.DEBUG,stream=sys.stdout)
#logger = logging.getLogger(__name__)
logger = logging.getLogger("")
#logger.setLevel(logging.INFO)

logger.info('Start reading database')
# read database here
records = {'john': 55, 'tom': 66}
logger.debug('Records: %s', records)
logger.info('Updating records ...')
# update records here
logger.info('Finish updating records')