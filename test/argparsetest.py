import argparse

# create the top-level parser
parser = argparse.ArgumentParser(prog='PROG')
parser.add_argument('--foo', action='store_true', help='foo help')
subparsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')

# create the parser for the "command_a" command
parser_a = subparsers.add_parser('command_a', help='command_a help')
parser_a.add_argument('bar', type=int, help='bar help')

# create the parser for the "command_b" command
parser_b = subparsers.add_parser('command_b', help='command_b help')
parser_b.add_argument('--baz', choices='XYZ', help='baz help')

# parse some argument lists
#argv = ['--foo', 'command_b', '--baz', 'Z']
print(parser.parse_args())
'cshs users "users.json" --add admin Kevin --admin'