# Copyright Haven Selph 2022, MIT License, see LICENSE.md file for more info.
from shlex import split
import inspect


class Command:
    def __init__(self, funct, names: tuple or list, does):
        self.funct = funct
        self.names = names or [funct.__name__]
        self.args = inspect.getfullargspec(funct)
        self.does = does
        self.help_msg = self.usage

    def run(self, *args, **kwargs):
        try:
            return [0, self.funct(args, kwargs)]
        except Exception as e:
            return [1, e]

    def set_help_msg(self, msg, show_aliases=False, show_usage=False):
        if show_aliases:
            self.help_msg = self.usage if show_usage else "" + "\nNames: " + " | ".join(self.names) + msg
        else:
            self.help_msg = self.usage if show_usage else "" + msg

    @property
    def usage(self, name: str = None):
        if not name:
            name = self.name
        params = "|"
        if not self.params:
            params = "| this command does not take any parameters"
        for param in self.params:
            params += f" <{param}>  "

        return f"| {name}: {self.does}" + "\n" + params

    @property
    def params(self):
        return inspect.signature(self.funct).parameters

    @property
    def name(self):
        return self.names[0]


class Commands(dict):
    class CommandExists(TypeError):
        pass

    class NoSuchCommand(KeyError):
        pass

    class ParseError(SyntaxError):
        pass

    class NoValidInput(ParseError):
        pass

    class OperatorError(ParseError):
        pass

    class ListError(ParseError):
        pass

    class PositionalPlacementError(ParseError):
        pass

    def __init__(self, *,
                 no_such_command_flag: str = "{0} is not a command.",
                 no_valid_input_flag: str = "No valid input was passed.",
                 operator_error_flag: str = "Value must not be separated with spaces: x=y not x = y",
                 list_error_flag: str = "Improperly formatted list argument! Should look like: [value1,value2,etc.]",
                 positional_placement_error_flag: str = "Positional argument follows keyword argument.",
                 register_help_command=True, register_exit_command=True, register_aliases_command=True):
        self.commands_no_aliases = []
        self.NoSuchCommandFlag = no_such_command_flag
        self.NoValidInputFlag = no_valid_input_flag
        self.OperatorErrorFlag = operator_error_flag
        self.ListErrorFlag = list_error_flag
        self.PositionalPlacementErrorFlag = positional_placement_error_flag
        if register_help_command:
            self.__add_command(
                Command(self.__help_command, ["help", "info"], does="prints out available commands, and their arguments")
            )
        if register_aliases_command:
            self.__add_command(
                Command(self.__aliases, ["names", "aliases"], does="returns all names for a given command")
            )
        if register_exit_command:
            self.__add_command(
                Command(exit, ["exit"], does="exits the program using exit()")
            )
        super().__init__()

    def __add_command(self, command):
        for name in command.names:
            if name in self:
                raise self.CommandExists(
                    f"Name or alias assigned to function {command.funct.__name__} is duplicate: {name}"
                )
            else:
                self[name] = command
        self.commands_no_aliases.append(command.names[0])

    def add_command(self, *names, does=None):
        def inner_fn(funct):
            self.__add_command(Command(funct, names, does or "No information provided for this command"))
            return funct

        return inner_fn

    def __help_command(self, command=None):
        if command:
            print(self[command].help_msg)
        else:
            print("List of available commands: ")
            for command in self.commands_no_aliases:
                print(self[command].usage, end="\n" * 2)

    def __aliases(self, command):
        try:
            if self[command]:
                pass
        except self.NoSuchCommand:
            return 1
        print(f"Registered aliases for {command}")
        print(", ".join(self[command].names))

    def execute(self, user_input):
        command, kwargs = self.parse(user_input)
        if command[0] in self.keys():
            return 0, self[command[0]].funct(*command[1:], **kwargs), command[0], command[1:], kwargs
        else:
            raise self.NoSuchCommand(self.NoSuchCommandFlag.format(command[0]))

    def execute_no_parse(self, cmd: str, *args, **kwargs):
        if cmd == "":
            raise self.NoValidInput(self.NoValidInputFlag)
        if cmd in self.keys():
            return 0, self[cmd](args, kwargs), cmd, args, kwargs

    def parse(self, value=None):
        if not value:
            raise self.NoValidInput(
                "No valid input was received"
            )
        args = []
        kwargs = {}
        for argument in split(value):
            if "=" in argument:
                if argument == "=" and args:
                    raise self.OperatorError(
                        self.OperatorErrorFlag
                    )
                a, b = argument.split("=")
                if b[0] == "#" and b[1:].isnumeric() and args:
                    kwargs[a] = int(b[1:])
                elif [b for check in ["[", "(", ")", "]"] if (check in b)] and args:
                    if (b[0] == "[" and b[-1] == "]") or (b[0] == "(" and b[-1] == ")"):
                        kwargs[a] = b.replace("[", "").replace("(", "").replace("]", "").replace(")", "").split(",")
                else:
                    kwargs[a] = b
            elif [argument for check in ["[", "(", ")", "]"] if (check in argument)] and args:
                if (argument[0] == "[" and argument[-1] == "]") or (argument[0] == "(" and argument[-1] == ")"):
                    args.append(argument.replace("[", "").replace("(", "").replace("]", "").replace(")", "").split(","))
                else:
                    raise self.ListError(
                        self.ListErrorFlag
                    )

            elif argument[0] == "#" and argument[1:].isnumeric() and kwargs == {} and args:
                args.append(int(argument[1:]))
            else:
                if kwargs == {}:
                    args.append(argument)
                else:
                    raise self.PositionalPlacementError(
                        self.PositionalPlacementErrorFlag
                    )
        if not args:
            raise self.NoValidInput(
                self.NoValidInputFlag
            )
        return [args, kwargs]