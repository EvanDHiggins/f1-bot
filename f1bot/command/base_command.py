from .command_registry import CommandRegistrar

class Command(metaclass=CommandRegistrar):
    pass
