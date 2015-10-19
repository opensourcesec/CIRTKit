# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

import pkgutil
import inspect

from lib.common.out import print_warning
from lib.common.abstracts import Module, Integration


def load_modules():
    # Import modules package.
    import modules

    moduleDict = dict()

    # Walk recursively through all modules and packages.
    for loader, module_name, ispkg in pkgutil.walk_packages(modules.__path__, modules.__name__ + '.'):
        # If current item is a package, skip.
        if ispkg:
            pass
        else:
            # Try to import the module, otherwise skip.
            try:
                module = __import__(module_name, globals(), locals(), ['dummy'], -1)
            except ImportError as e:
                print_warning("Something wrong happened while importing the module {0}: {1}".format(module_name, e))
                continue

            # Walk through all members of currently imported modules.
            for member_name, member_object in inspect.getmembers(module):
                # Check if current member is a class.
                if inspect.isclass(member_object):
                    # Yield the class if it's a subclass of Module.
                    if issubclass(member_object, Module) and member_object is not Module:
                        moduleDict[member_object.cmd] = dict(obj=member_object, description=member_object.description)

    return moduleDict


def load_integrations():
    import integrations

    integrationDict = {}
    # Walk recursively through all modules and packages.
    for loader, integration_name, ispkg in pkgutil.walk_packages(integrations.__path__, integrations.__name__ + '.'):
        # If current item is a package, skip.
        if ispkg:
            pass
        else:
            # Try to import the module, otherwise skip.
            try:
                module = __import__(integration_name, globals(), locals(), ['dummy'], -1)
            except ImportError as e:
                print_warning("Error occurred while loading the integration {0}: {1}".format(integration_name, e))
                continue

            # Walk through all members of currently imported modules.
            for member_name, member_object in inspect.getmembers(module):
                # Check if current member is a class.
                if inspect.isclass(member_object):
                    # Yield the class if it's a subclass of Module.
                    if issubclass(member_object, Integration) and member_object is not Integration:
                        integrationDict[member_object.cmd] = dict(obj=member_object, description=member_object.description)

    return integrationDict


def load_scripts():
    import scripts
    scriptDict = dict()

    return scriptDict


__modules__ = load_modules()
__integrations__ = load_integrations()
__scripts__ = load_scripts()
