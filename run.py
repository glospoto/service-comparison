#! /usr/bin/env python

from framework import ComparisonFramework
from utils.log import Logger

if __name__ == '__main__':
	log = Logger.get_instance()
	framework = ComparisonFramework()
	log.info('Runner', 'Framework starts.')
	framework.run()
