## NOTICE
> **This is no longer maintained, I will not add any new features, and likely won't be able to answer questions, sorry.**

# PyCommands
A simple and easy-to-use module that streamlines the whole user-input side of your script!

### Key Features
- Allows functions to be linked to a custom command and alias. 
- Parses user input and allows the passing of function arguments `<command> arg1 arg2 "arg 3"`.
- Custom error messages for missing parameters and commands that don't exist.

### Installing
```
Linux/Windows:
pip install PyCommandsTool
```

### Example
(*This example will only work in Windows due to the 'cls' command.*)
```python
from PyCommandsTool import Commands


cmd = Commands()

@cmd.add_command(name='clearscreen', aliases=['cls','clear',])
def clear_screen():
    system('cls')


while True:
    try:
        x = cmd.execute(input('>>>'))
        if not x[0]:  # execute returns false in zeroth position if command not found or execution failed
            print(x[1])  # execute returns the flag for secific error
        else:
            pass  # here you could do something when a function is completed successfully
    except KeyboardInterrupt:
        print('Ctrl + C')
        print('Closing app...')
        break
```
The above program will allow you too enter anything you want but will return 'command not found' errors until you enter either `clearscreen` `cls` or `clear`. This module is very simple to use, I wish you luck on finding more out. Check links for more in-depth documentation.
