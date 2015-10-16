import shutil
import os

"""
This class models the framework filesystem, storing the organization of the folders used for keeping information.
"""


class FileSystem(object):

    __instance = None

    def __init__(self):
        """ Define here all folders of the framework """
        # Root folder
        self._root_folder = os.getcwd()
        # Simulations folder
        self._simulations_folder = os.path.abspath("simulations/")
        # TMP folder
        self._tmp_folder = os.path.abspath("tmp/")
        # Current simulation folder
        self._current_simulation_folder = None
        # Current working directory
        self._current_working_folder = self._root_folder

    '''
    Return an instance of this class in accord with the Singleton pattern.
    '''
    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = FileSystem()
        return cls.__instance

    """ Methods for retrieving application's folders """

    '''
    Return the framework root folder.
    '''
    def get_root_folder(self):
        return self._root_folder

    '''
    Return the simulation folder.
    '''
    def get_simulations_folder(self):
        return self._simulations_folder

    '''
    Return the simulation folder (it seems a duplicate of the previous method: check it!)
    '''
    def get_current_simulation_folder(self):
        return self._simulations_folder

    '''
    Return the path to the framewok temporary folder.
    '''
    def get_tmp_folder(self):
        return self._tmp_folder

    '''
    Return the current framework working folder.
    '''
    def get_current_working_folder(self):
        return self._current_working_folder

    """ Methods for operating over application's folders """

    '''
    Set the current working directory to the root folder.
    '''
    def root(self):
        os.chdir(self._root_folder)
        # Set the current working folder to the root folder
        self._current_working_folder = self._root_folder

    '''
    Change directory, placing into path.
    '''
    def cd(self, path):
        if path.startswith('~'):
            os.chdir(os.path.expanduser(path))
        else:
            os.chdir(path)
        # Set the current working folder to the new path
        self._current_working_folder = os.getcwd()

    '''
    Join one or more paths into a single one. This one will become the current working directory.
    '''
    def join(self, path, *paths):
        self._current_working_folder = os.path.join(path, *paths)
        return self._current_working_folder

    '''
    Copy source into destination.
    '''
    @staticmethod
    def copy(source, destination):
        if source.startswith('~'):
            source = os.path.expanduser(source)
        if destination.startswith('~'):
            destination = os.path.expanduser(destination)
        shutil.copy(source, destination)

    '''
    Delete path.
    '''
    @staticmethod
    def delete(path):
        os.remove(path)
