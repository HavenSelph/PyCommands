"""
MIT License

Copyright (c) 2020 Haven Selph

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# ============== Impots ==============
from shlex import split

# ==============  Main  ==============
class Command:
  def __init__(self, fn, name=None, aliases=None):
    self.name = name or fn.__name__
    self.aliases = aliases or []
    self.fn = fn

  def __call__(self, *args, **kwargs):
    return self.fn(*args, **kwargs)

  @property
  def all_names(self):
    return self.name, *self.aliases


# ============= Storage =============
class Commands(dict):
  def __init__(self, not_found: str='{} was not recognized.', argmismatch: str='{} takes {} arguments but {} were given.'):
    """
    Initializes a new command storage object. Check docs for more info.
    Check docs for all instance variables to interact with module more closely.

    not_found: The text to be sent back when a command is not found
      {0} - The command attempted

    argmismatch: The text to be sent back when a command is issue with an invalid amount of arguments.
      {0} - The command attempted
      {1} - The amount of arguments required
      {2} - The amount of arguments passed
    """
    self.flag = (not_found, argmismatch)
    super().__init__()

  def _add_command(self, command):
    """DO NOT USE UNLESS YOU KNOW HOW. WILL LIKELY BREAK COMMAND."""
    for cmd_name in command.all_names:
      if cmd_name in self:
        raise ValueError(f'Name or alias assigned to function {command.fn.__name__} is duplicate: {cmd_name}')
      self[cmd_name] = command
    
  def add_command(self, name=None, aliases=None):
    """
    Addes a new command to the object. Check docs for more info.

    name: The name that the command will use.
    aliases: The other names the command can be called with.
    """
    def inner_fn(fn):
      self._add_command(Command(fn, name, aliases))
      return fn
    return inner_fn

  def execute(self, user_input):
    """
    Auto parsing function to execute commands. Check docs for more info.

    user_input: A string for the parser to parse.
    """
    self.command, *args = self.parse(user_input or 'no_input')
    if self.command.lower() in self:
      try:
        rtrn = self[self.command].fn(*args)
      except TypeError:
        return (False, self.flag[1].format(self.command, self[self.command].fn.__code__.co_argcount, len(args)))
      else:
        return True, rtrn
    else:
      return False, self.flag[0].format(self.command)
  
  @staticmethod
  def parse(string):
    if (string=='no_input'):
      return '',''
    return split(string)
