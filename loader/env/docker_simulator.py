import subprocess
from subprocess import PIPE

from utils.process import Process
from utils.patterns.observer import Observable

"""
This class implements an instance of a docker container. In the framework, each docker instance 
represents a router.
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
		cmd_debug = 'sudo docker create --name=%s %s --tty --interactive -i %s' % (
			self._name, self._opts, self._image)
		process = Process()
		process.execute(cmd_debug)
		process.communicate()
		# subprocess.Popen(cmd_debug, shell=True, stdout=PIPE, stderr=PIPE).communicate()

	'''
	This method runs docker start command.
	'''

	def start(self):
		cmd = 'sudo docker start %s' % self._name
		process = Process()
		process.execute(cmd)
		process.communicate()
		# subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()

	'''
	This method runs docker stop command.
	'''

	def stop(self):
		cmd = 'sudo docker stop %s' % self._name
		process = Process()
		process.execute(cmd)
		process.communicate()
		# subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()

	'''
	This method runs docker rm command.
	'''

	def remove(self):
		cmd = 'sudo docker rm %s' % self._name
		process = Process()
		process.execute(cmd)
		process.communicate()
		# subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()


"""
This class wraps the "docker network" command. It is used in the environment built on top of Docker 
to create link between each pair of router interfaces (remember that each docker instance 
represents a router).
"""


class Bridge(Observable):
	def __init__(self, name):
		Observable.__init__(self)
		# The name of the bridge
		self._name = name

	'''
	Return the name of this bridge
	'''

	def get_name(self):
		return self._name

	'''
	Create a new bridge (wraps docker network)
	'''

	def create(self, subnet):
		cmd = 'sudo docker network create -d bridge --subnet %s %s' % (subnet, self._name)
		process = Process()
		process.execute(cmd)
		process.communicate()
		
		'''
		Notify obverser (DockerEnvironment) in order to allow it to start a sniffer over
		this bridge
		'''
		self.notify_all('bridge')

	'''
	Connect two Docker instances to this bridge (wraps docker connect).
	'''

	def connect(self, source_node, destination_node):
		cmd_source_node = 'sudo docker network connect %s %s' % (self._name, source_node)
		cmd_destination_node = 'sudo docker network connect %s %s' % (self._name, destination_node)

		process_source = Process()
		process_source.execute(cmd_source_node)
		process_source.communicate()

		process_destination = Process()
		process_destination.execute(cmd_destination_node)
		process_destination.communicate()

	'''
	Delete this bridge.
	'''

	def destroy(self):
		cmd = 'sudo docker network rm %s' % self._name

		process = Process()
		process.execute(cmd)
		process.communicate()
