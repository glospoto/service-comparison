from abc import ABCMeta, abstractmethod

from mako.lookup import TemplateLookup

from utils.file import File
from utils.fs import FileSystem
from utils.log import Logger


class FactoryTemplate(object):
    __instance = None

    def __init__(self):
        self._template = None

    '''
    Return an instance of this class.
    '''

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = FactoryTemplate()
        return cls.__instance

    '''
    Return an instance of ZebraTemplate class.
    '''

    def create_zebra_template(self):
        self._template = ZebraTempate()
        return self._template

    '''
    Return an instance of OspfTemplate class.
    '''

    def create_ospf_template(self, subnets, loopback=None):
        self._template = OspfTempate(subnets, loopback)
        return self._template

    '''
    Return an instance of GoBgpTemplate class.
    '''

    def create_gobgp_template(self, local_loopback_address, peer_loopback_addresses):
        self._template = GoBgpTempate(local_loopback_address, peer_loopback_addresses)
        return self._template

    '''
    Return an instance of GoBgpTemplate class.
    '''

    def create_bagpipebgp_template(self, local_address, peer_address):
        self._template = BagPipeBgpTempate(local_address, peer_address)
        return self._template


"""
This class implements a wrapper
"""


class Template(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # Logging
        self._log = Logger.get_instance()
        # The FileSystem handler
        self._fs = FileSystem.get_instance()
        # Mako template engine
        self._template = TemplateLookup(directories=[self._fs.get_template_folder()])

    '''
    Abstract method to generate configuration file (typically for traditional routing protocol).
    '''

    @abstractmethod
    def generate(self):
        pass


"""
This class implements a template generator for Zebra.
"""


class ZebraTempate(Template):
    def __init__(self):
        Template.__init__(self)

    '''
    Generate the configuration file with respect to this object.
    '''

    def generate(self):
        # Get the Zebra template
        self._log.debug(self.__class__.__name__, 'Starting to load the template for Zebra configuration file.')
        zebra_template = self._template.get_template('zebra.mako')
        # Now save the file into a file inside tmp folder
        self._log.debug(self.__class__.__name__, 'Creating the file in which saving the Zebra configuration file.')
        zebra_file = File(self._fs.get_tmp_folder(), 'zebra.conf')
        zebra_file.write(zebra_template.render())
        self._log.debug(self.__class__.__name__, 'Storing the Zebra configuration file.')
        zebra_file.save()
        self._log.debug(self.__class__.__name__, 'Zebra configuration file has been successfully stored.')

        # Do the same for daemons file
        self._log.debug(self.__class__.__name__, 'Starting to load the template for Zebra daemons configuration file.')
        daemons_template = self._template.get_template('daemons.mako')
        # Now save the file into a file inside tmp folder
        self._log.debug(self.__class__.__name__,
                        'Creating the file in which saving the Zebra daemons configuration file.')
        daemons_file = File(self._fs.get_tmp_folder(), 'daemons')
        daemons_file.write(daemons_template.render())
        self._log.debug(self.__class__.__name__, 'Storing the Zebra daemons configuration file.')
        daemons_file.save()
        self._log.debug(self.__class__.__name__, 'Zebra daemons configuration file has been successfully stored.')


"""
This class implements a template generator for OSPF.
"""


class OspfTempate(Template):
    def __init__(self, subnets, loopback=None):
        Template.__init__(self)
        # The subnets to put into ospf.mako template
        self._subnets = subnets
        # The loopback
        self._loopback = loopback

    '''
    Generate the configuration file with respect to this object.
    '''

    def generate(self):
        # Get the OSPF template
        self._log.debug(self.__class__.__name__, 'Starting to load the template for OSPF configuration file.')
        ospf_template = self._template.get_template('ospfd.mako')
        # Now save the file into a file inside tmp folder
        self._log.debug(self.__class__.__name__, 'Creating the file in which saving the OSPF configuration file.')
        ospf_file = File(self._fs.get_tmp_folder(), 'ospfd.conf')
        ospf_file.write(
            ospf_template.render(
                subnets=self._subnets,
                loopback=self._loopback
            )
        )
        self._log.debug(self.__class__.__name__, 'Storing the OSPF configuration file.')
        ospf_file.save()
        self._log.debug(self.__class__.__name__, 'OSPF configuration file has been successfully stored.')


"""
This class implements a template generator for GoBGP.
"""


class GoBgpTempate(Template):
    def __init__(self, local_loopback_address, remote_loopback_addresses):
        Template.__init__(self)
        # The local loopback IP address, namely the router currently configured
        self._local_loopback_address = local_loopback_address
        # The peer's loopback IP address
        self._remote_loopback_addresses = remote_loopback_addresses

    '''
    Generate the configuration file with respect to this object.
    '''

    def generate(self):
        """ Get the BGP template (in this implementation we use both BoBGP and BagPipeBGP) """
        # GoBGP configuration
        self._log.debug(self.__class__.__name__, 'Starting to load the template for GoBGP configuration file.')
        gobgp_template = self._template.get_template('gobgp.mako')
        # Now save the file into a file inside tmp folder
        self._log.debug(self.__class__.__name__, 'Creating the file in which saving the GoBGP configuration file.')
        gobgp_file = File(self._fs.get_tmp_folder(), 'gobgp.conf')
        gobgp_file.write(
            gobgp_template.render(
                my_loopback_address=self._local_loopback_address,
                peer_loopback_addresses=self._remote_loopback_addresses
            )
        )
        self._log.debug(self.__class__.__name__, 'Storing the GoBGP configuration file.')
        gobgp_file.save()
        self._log.debug(self.__class__.__name__, 'GoBGP configuration file has been successfully stored.')
        """
        # BagPipeBGP configuration
        self._log.debug(self.__class__.__name__,
                        'Starting to load the template for BagPipeBGP configuration file.')
        bagpipebgp_template = self._template.get_template('bgp.mako')
        # Now save the file into a file inside tmp folder
        self._log.debug(self.__class__.__name__,
                        'Creating the file in which saving the BagPipeBGP configuration file.')
        bagpipebgp_file = File(self._fs.get_tmp_folder(), 'bgp.conf')
        bagpipebgp_file.write(bagpipebgp_template.render())
        self._log.debug(self.__class__.__name__, 'Storing the BagPipeBGP configuration file.')
        bagpipebgp_file.save()
        self._log.debug(self.__class__.__name__, 'BagPipeBGP configuration file has been successfully stored.')
        """

"""
This class implements a template generator for BagPipeBGP.
"""


class BagPipeBgpTempate(Template):
    def __init__(self, local_address, peer_address):
        Template.__init__(self)
        # The local IP address, namely the router currenctly configured
        self._local_address = local_address
        # The peer's loopback IP address
        self._peer_address = peer_address

    '''
    Generate the configuration file with respect to this object.
    '''

    def generate(self):
        # BagPipeBGP configuration
        self._log.debug(self.__class__.__name__,
                        'Starting to load the template for BagPipeBGP configuration file.')
        bagpipebgp_template = self._template.get_template('bgp.mako')
        # Now save the file into a file inside tmp folder
        self._log.debug(self.__class__.__name__,
                        'Creating the file in which saving the BagPipeBGP configuration file.')
        bagpipebgp_file = File(self._fs.get_tmp_folder(), 'bgp.conf')
        bagpipebgp_file.write(
            bagpipebgp_template.render(
                my_address=self._local_address,
                peer_address=self._peer_address
            )
        )
        self._log.debug(self.__class__.__name__, 'Storing the BagPipeBGP configuration file.')
        bagpipebgp_file.save()
        self._log.debug(self.__class__.__name__, 'BagPipeBGP configuration file has been successfully stored.')