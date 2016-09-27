import threading

"""
Singleton thread-safe implementation
"""


class Singleton(type):
	__singleton_lock = threading.Lock()
	__singleton_instance = None

	# Using @classmethod decorator, the method instance is inherited by all subclasses
	@classmethod
	def get_instance(cls):
		print '@@@', cls
		if not cls.__singleton_instance:
			with cls.__singleton_lock:
				if not cls.__singleton_instance:
					cls.__singleton_instance = cls()
		return cls.__singleton_instance
