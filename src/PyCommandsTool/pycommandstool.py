# Copyright Haven Selph 2022, MIT License, see LICENSE.md file for more info.
import inspect
# from parser import *


class Command:
    def __init__(self, funct: callable, names: list[str, ...] or tuple[str, ...], does: str=None, help_msg: str=None) -> None:
        """
        Generates a new command object to be used in Commands.

        :param funct: Function to be called when calling this object.
        :param names: All names for this object to be referred to as.
        :param does: A short description of what this command does.
        :param help_msg: A long description of what this command does.
        """
        self.__funct = funct
        self.__names = names
        self.does = does
        self.help_msg = help_msg

    @property
    def funct(self) -> callable:
        """Returns the function of this command."""
        return self.__funct

    @property
    def parameters(self) -> list[str, ...] or tuple[str, ...]:
        """Returns all parameters of this commands function as a tuple."""
        return [arg[0] for arg in inspect.signature(self.funct).parameters]

    @property
    def names(self) -> list[str, ...] or tuple[str, ...]:
        """Returns all names of this command."""
        return self.__names

    @property
    def name(self) -> str:
        """Returns names[0] of this command."""
        return self.__names[0]

    def usage(self, name: str=None, aliases_sep: str=" | ", aliases_wrap: list[str, str] or tuple[str, str]=("<",">"), param_sep: str=" | ", param_wrap: list[str, str] or tuple[str, str]=("<",">"), setup: str="|{name}: {does}\n|{parameters}") -> str:
        """
        Generate a string to show command usage dynamically. Use setup to customize how it looks.
        Example Setup String: "{name}: {does}\n{parameters}"

        {name} = name parameter

        {aliases} = self.names (does not include name, and formatted using provided parameters)

        {parameters} = self.parameters (formatted using provided parameters)

        {does} = self.does

        {help_msg} = self.help_msg


        :param name: Which name to use as the main name of the command. Defaults to commands main name.
        :param aliases_sep: Text to place between each alias.
        :param aliases_wrap: Tuple where [0] is placed on the left and [1] on the right of each alias.
        :param param_sep: Text to place between each parameter.
        :param param_wrap: Tuple where [0] is placed on the left and [1] on the right of each alias.
        :param setup: Custom setup for string.


        :return: Returns a generated string based on parameters passed.
        """
        name = name if name in self.names else self.name
        parameters = param_sep.join([param_wrap[0] + param + param_wrap[1] for param in self.parameters])
        aliases = aliases_sep.join([aliases_wrap[0] + str(_name) + aliases_wrap[1] for _name in self.names if _name!=name])
        return setup.format(
            name=name,
            aliases=aliases or "",
            does=self.does or "",
            parameters=parameters,
            help_msg=self.help_msg or ""
        )

    def __call__(self, *args, **kwargs):
        return self.funct(*args, **kwargs)


class Commands(dict):
    def __init__(self, /, register_help_command: bool=True, register_exit_command: bool=True, register_aliases_command: bool=True) -> None:
        """Create a commands dictionary to register commands to."""
        self.names_no_aliases = []

        if register_help_command:
            self.__help_command = self.add_command("help", "info", does="Displays information on a provided command, or all registered commands.")(self.__help_command)

        if register_exit_command:
            self.add_command("exit", "quit", does="Exits the script using Python's built-in 'exit()' method.")(exit)

        if register_aliases_command:
            self.__aliases = self.add_command("aliases", "names", does="Displays all names pointing to a provided command.")(self.__aliases)
        super().__init__()

    def __help_command(self, command: str=None) -> None:
        if command:
            setup = "Command: {name} - {does}" if self.get(command).does else "Command: {name}"
            setup += "\nParameters: {parameters}" if len(self.get(command).parameters)>0 else "\nParameters: [no parameters]"
            setup += "\n{help_msg}" if self.get(command).parameters else ""
            print(self.get(command).usage(command, param_sep=" ", param_wrap=("[", "]"), setup=setup), end="\n" * 2)
        else:
            for command in self.names_no_aliases:
                setup = "Command: {name} - {does}" if self.get(command).does else "Command: {name}"
                setup += "\nParameters: {parameters}" if len(self.get(command).parameters)>0 else "\nParameters: [no parameters]"
                setup += "\n{help_msg}" if self.get(command).parameters else ""
                print(self.get(command).usage(command, param_sep=" ", param_wrap=("[","]"), setup=setup), end="\n"*2)

    def __aliases(self, command: str):
        setup = "Command: {name}"
        setup += "Aliases: {aliases}" if len(self.get(command).names)>1 else "Aliases: Command has no aliases."
        print(self.get(command).usage(aliases_sep=", ", aliases_wrap=("",""), setup="Command: {name}\nAliases: {aliases}"), end="\n"*2)

    def __add_command(self, command: Command) -> Command:
        for name in command.names:
            if name in self:
                raise self.CommandExists(name)
            else:
                self[name] = command
        self.names_no_aliases.append(command.name)
        return command

    def add_command(self, *names: str, does: str=None, help_msg: str=None) -> callable:
        def wrapper(funct: callable) -> Command:
            return self.__add_command(Command(funct, names, does=does, help_msg=help_msg))

        return wrapper

    def execute(self, text: str) -> any:
        _out = self.parse_string(text)
        return self.execute_no_parse(*_out[0], **_out[1])

    def execute_no_parse(self, *args, **kwargs) -> any:
        if not args:
            raise self.CommandNotFound("No command provided.")
        else:
            if args[0] in self:
                return self.get(args[0])(*args[1:], **kwargs)
            else:
                raise self.CommandNotFound(f"Command '{args[0]}' not found.")

    @classmethod
    def parse_string(cls, string: str="") -> tuple[list, dict]:
        try:
            _out = parse(string)
        except Tokenizer.UnexpectedToken as er:
            raise cls.ParseError(repr(er))
        except Tokenizer.UnexpectedEOF as er:
            raise cls.ParseError(repr(er))
        return _out

    def get(self, key) -> Command:  # Included so I can typehint .get()
        return self[key]

    class PyCommandsToolException(Exception):
        """A generic exception to be inherited by all custom exceptions in PyCommandsTool."""
        def __init__(self, *values: str) -> None:
            super().__init__(*values)

    class CommandExists(PyCommandsToolException):
        """An exception thrown when a command name provided is already registered to the Commands object."""

    class CommandNotFound(PyCommandsToolException):
        """An exception thrown when a command name does not exist."""

    class ParseError(PyCommandsToolException):
        """An exception thrown when parse cannot properly interpret a string passed to it."""


if __name__ == "__main__":
    cmd = Commands()

    @cmd.add_command("add", "sum", does="Adds two numbers together.")
    def add(a, b):
        print(a + b)

    while True:
        try:
            cmd.execute(input(">>> "))
        except cmd.PyCommandsToolException as e:
            print(e)
