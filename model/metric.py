"""
This class models a metric object. A metric is characterized by an extractor and (possibly) a collector. The collector
is to be considered as optional because some metrics may not need a collector (e.g. load-device)
"""


class Metric(object):
    def __init__(self, name, collector, extractor):
        self._name = name
        # NOTE: The following variables contain the name of the class and NOT the references to the objects!
        self._collector = collector
        self._extractor = extractor

    def __repr__(self):
        return 'Metric[name=%s, collector=%s, extractor=%s]' % (self._name, self._collector, self._extractor)

    '''
    Return the name of this metric.
    '''

    def get_name(self):
        return self._name

    '''
    Return the collector (if needed) associated to this metric.
    '''

    def get_collector(self):
        return self._collector

    '''
    Return the extractor associated to this extractor.
    '''

    def get_extractor(self):
        return self._extractor
