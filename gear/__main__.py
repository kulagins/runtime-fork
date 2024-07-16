import sys
from gear.Cli import Cli

if __name__ == '__main__':
    cli = Cli()
    cli.start(sys.argv[1:])
