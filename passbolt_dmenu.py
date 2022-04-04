#!/usr/bin/env python3

import sys
import os
import os.path as path
import subprocess
import shutil
import argparse
import json
import re

DMENU = shutil.which('dmenu')
PASSBOLT = shutil.which('passbolt')
NOTIFY_SEND = shutil.which('notify-send')
XCLIP = shutil.which('xclip')
GPG = shutil.which('gpg')

def dmenu(choices, args=[], path=DMENU):
    """
    Displays a menu with the given choices by executing dmenu
    with the provided list of arguments. Returns the selected choice
    or None if the menu was aborted.
    """
    dmenu = subprocess.Popen([path] + args,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    choice_lines = '\n'.join(map(str, choices))
    choice, errors = dmenu.communicate(choice_lines.encode('utf-8'))
    if dmenu.returncode not in [0, 1] \
       or (dmenu.returncode == 1 and len(errors) != 0):
        print("'{} {}' returned {} and error:\n{}"
              .format(path, ' '.join(args), dmenu.returncode,
                      errors.decode('utf-8')),
              file=sys.stderr)
        sys.exit(1)
    choice = choice.decode('utf-8').rstrip()
    return choice if choice in choices else None

def passbolt_command(args, path=PASSBOLT):
    passbolt = subprocess.Popen([path] + args,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    output, errors = passbolt.communicate()
    if passbolt.returncode not in [0, 1] \
       or (passbolt.returncode == 1 and len(errors) != 0):
        print("'{} {}' returned {} and error:\n{}"
              .format(path, ' '.join(args), passbolt.returncode,
                      errors.decode('utf-8')),
              file=sys.stderr)
        sys.exit(1)
    return output

def passbolt_resources():
    args = ["find", "--json"]
    return dict((item["uuid"], item) for item in json.loads(passbolt_command(args).decode('utf-8')))

def passbolt_password(id, path=GPG):
    args = ["-q"]
    gpg = subprocess.Popen([path] + args,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    output, errors = gpg.communicate(passbolt_command(["get", id]))
    if gpg.returncode not in [0, 1, 2] \
      or (gpg.returncode == 1 and len(errors) != 0):
       print("'{} {}' returned {} and error:\n{}"
             .format(path, ' '.join(args), gpg.returncode,
                     errors.decode('utf-8')),
             file=sys.stderr)
       sys.exit(1)
    return output.decode('utf-8')

def notify_send(message, path=NOTIFY_SEND):
    args = ["-u", "low", "Passolt", message]
    notify_send = subprocess.Popen([path] + args,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    notify_send.communicate()

def set_clipboard(value, value_type, path=XCLIP):
    args = ["-selection", "clipboard"]
    xclip = subprocess.Popen([path] + args,
                             stdin=subprocess.PIPE)
    output, errors = xclip.communicate(value.encode('utf-8'), 1)
    if xclip.returncode not in [0, 1] \
        or (xclip.returncode == 1 and len(errors) != 0):
         print("'{} {}' returned {} and error:\n{}"
               .format(path, ' '.join(args), xclip.returncode,
                       errors.decode('utf-8')),
               file=sys.stderr)
         sys.exit(1)
    notify_send("{} copied to clipboard".format(value_type))

def main():
    desc = ("A dmenu frontend to pass."
            " All passed arguments not listed below, are passed to dmenu."
            " If you need to pass arguments to dmenu which are in conflict"
            " with the options below, place them after --."
            " Requires xclip in default 'copy' mode.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-D', '--dmenu', dest="dmenu_bin", default=DMENU,
                        help=('The path to the dmenu binary. '
                              'Cannot find a default path to dmenu, '
                              'you must provide this option.'
                              if DMENU is None else 'Defaults to ' + DMENU))

    split_args = [[]]
    curr_args = split_args[0]
    for arg in sys.argv[1:]:
        if arg == "--":
            split_args.append([])
            curr_args = split_args[-1]
            continue
        curr_args.append(arg)

    args, unknown_args = parser.parse_known_args(args=split_args[0])

    error = False

    if error:
        sys.exit(1)

    dmenu_opts = unknown_args
    resources = passbolt_resources()
    choices = list(map(lambda item: "{} ({})".format(item["name"], item["uuid"]), resources.values()))
    choice = dmenu(choices, dmenu_opts, args.dmenu_bin)

    # Check if user aborted
    if choice is None:
        sys.exit(0)

    id_pattern = re.compile('.*\\(([^\\)]*)\\)$')
    m = id_pattern.match(choice)
    # Check if user aborted
    if m is None:
        sys.exit(0)

    selected_resource = resources[m.group(1)]

    attribute = dmenu(["password", "username", "url"], dmenu_opts, args.dmenu_bin)
    if attribute is None:
        sys.exit(0)
    elif attribute == "password":
        set_clipboard(passbolt_password(selected_resource["uuid"]), 'Password')
    elif attribute == "username":
        set_clipboard(selected_resource["username"], 'Username')
    elif attribute == "url":
        set_clipboard(selected_resource["uri"], 'URL')


if __name__ == "__main__":
    main()
