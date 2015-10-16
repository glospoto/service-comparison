import importlib, sys


def for_name(class_name, *args, **kwargs):
    # Divide the module into a list.
    # E.g.: model.services.configuration.x.xConfigurator -> [model, services, configuration, x, xConfigurator]
    parts = class_name.split('.')  # Create a module less the name of the class
    # E.g.: model.services.configuration.x
    module = ".".join(parts[:-1])
    # Import the module
    # E.g.: import model.services.configuration.x
    m = importlib.import_module(module)
    # Take the class inside module m (see above)
    class_name = getattr(m, parts[len(parts) - 1])
    # Create an instance of the class
    # E.g.: it is the same of
    # from model.services.configuration.x import xConfigurator
    # configurator = xConfigurator()
    class_instance = class_name(*args, **kwargs)
    return class_instance

