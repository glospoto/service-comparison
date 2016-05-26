import subprocess
from subprocess import PIPE

"""
This class implements an instance of a docker container. In the framework, each docker instance represents a router.
"""


class Docker(object):
    def __init__(self, name, image, opts):
        self._name = name
        self._image = image
        self._opts = opts

    '''
    Return the name of the Docker instance.
    '''

    def get_name(self):
        return self._name

    '''
    This method runs docker create command.
    '''

    def create(self):
        cmd = 'sudo docker create --name=%s %s -i %s' % (self._name, self._opts, self._image)
        cmd_debug = 'sudo docker create --name=%s %s --tty --interactive -i %s' % (self._name, self._opts, self._image)
        subprocess.Popen(cmd_debug, shell=True, stdout=PIPE, stderr=PIPE).communicate()

    '''
    This method runs docker start command.
    '''

    def start(self):
        cmd = 'sudo docker start %s' % self._name
        subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()

    '''
    Add a new interface to this docker instance.
    '''
    def add_interface(self):
        pass

    '''
    This method runs docker stop command.
    '''

    def stop(self):
        cmd = 'sudo docker stop %s' % self._name
        subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()

    '''
    This method runs docker rm command.
    '''

    def remove(self):
        cmd = 'sudo docker rm %s' % self._name
        subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()


"""
This class models a linux bridge. It is used in the environment built on top of Docker to create link between each
pair of router interfaces (remember that each docker instance represents a router).
"""


class Bridge(object):
    def __init__(self, name):
        # The name of the bridge
        self._name = name

    '''
    Attach an interface to this bridge.
    '''

    def attach(self, interface):
        pass

    '''
    Delete this bridge.
    '''

    def destroy(self):
        pass
