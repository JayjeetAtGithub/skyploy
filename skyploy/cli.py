"""
skyploy - An end-to-end automated deployment tool for SkyhookDM.

Usage:
  skyploy run
  skyploy grafana
  skyploy fs
  skyploy -h | --help
  skyploy --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  skyploy run

Note: 
  This tool should be only used with `sudo`.

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/JayjeetAtGithub/skyploy
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import skyploy.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items(): 
        if hasattr(skyploy.commands, k) and v:
            module = getattr(skyploy.commands, k)
            skyploy.commands = getmembers(module, isclass)
            command = [command[1] for command in skyploy.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
