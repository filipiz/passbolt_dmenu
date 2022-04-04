# passbolt_dmenu
A dmenu frontend to passbolt with clipboard functionality.

This project is kindly inspired on [passdmenu](https://github.com/klaasb/passdmenu).

## Dependencies

* [dmenu](https://tools.suckless.org/dmenu/)
* Gnupg v2
* xclip
* libnotify-bin
* passbolt_cli


ATTENTION. It requires a feature not yet merged on [official passbolt_cli](https://github.com/passbolt/passbolt_cli).  
While [my pull request](https://github.com/passbolt/passbolt_cli/pull/53) is not accepted, to make this program to work, you will
need to install my fork of passbolt_cli available on [https://github.com/filipiz/passbolt_cli](https://github.com/filipiz/passbolt_cli)

Simply follow same installation instruction from official passbolt_cli.

## Instalation

Copy the repository

```
git clone https://github.com/filipiz/passbolt_dmenu.git

```

Make a symbolic link on your $PATH

```
cd passbolt_dmenu
ln -s $(pwd)/passbolt_dmenu.py /usr/local/bin/passbolt_dmenu
```


## Usage

All arguments are passed to dmenu.

```
passbolt_dmenu -c -i -l 5 -m 0 -nb "#383034" -nf "#EBEBEB" -sb "#FF5252" -sf "#FFFFFF" -fn "Bitstream Vera Sans"
```


