[![Build Status](https://travis-ci.com/NCAR/HPCinstall.svg?token=ZoVz2xMBgzXK6oqcK3qN&branch=master)](https://travis-ci.com/NCAR/HPCinstall)

# HPCinstall

`HPCinstall` is a piece of software used to install other software in an HPC environment.
What it does is simply to run a given install script, but it will
help by automatize the clerical, tedious tasks, letting the script do only the complicated parts.
It interfaces and helps create modulefiles (particularly for [lmod](https://github.com/TACC/Lmod))
but it can be easily used also in a module-free environement

See the [module and installation workflow](https://wiki.ucar.edu/display/csg/Module+and+installation+management+process)
currently in use at NCAR/CISL.

# Features
 
Some of the features of `HPCinstall` are: 
* :rocket: automatic log of everything (environment, log, script used for install, etc) 
* :+1: automatic archive of the logs in the install directory
* :smile: automatic generation of the install directory name (and module name) from
 the name and version of the software to be compiled and the loaded compiler/mpi modules (if appropriate).
 The structure of this directories names can be configured with the
 `sw_install_struct` and `mod_install_struct` config properties
* :white_check_mark: checksum verification of the installation (at install time and post-mortem with `hashdir`)
* :beer: and more
 
# Use

HPCInstall is simply invoked as

```
hpcinstall [options] filename
```

where `filename` is the build/install script for the software to be installed

## Command line options

The CLI options for HPCInstall are just a few:

```
usage: hpcinstall [-h] [-c] [-f] [-d] [-p] install-software-ver

positional arguments:
  install-software-ver  script in the current directory which does the build
                        and install (do not use './', relative nor fully
                        qualified paths)

optional arguments:
  -h, --help            show this help message and exit
  -c, --csgteam         Install as csgteam (default: False)
  -f, --force           Force overwrite of existing install (default: False)
  -d, --debug           Debug mode i.e. more verbose output (default: False)
  -p, --preserve        Preserve current environment - not valid with
                        --csgteam (default: False)
```
The most useful one is `--csgteam` which will cause the installation to be system-wide. The `--debug` and `--preserve` are useful for debugging issues, and the `--force` is a convenience option to remove the target installation directory, because otherwise HPCInstall will refuse to clobber it.

## Directives

Your script can and should communicate with HPCInstall some important matters, using _directives_ which are comments in the script of the form

```
#HPCI -n software_name     # software_name is what is under installation
#HPCI -v software_version  # software_version of what is under installation
#HPCI -a filename          # archive this file in the same way as the build logs
#HPCI -x export FOO=bar    # execute this line, preferred way to change the environment
#HPCI -l intel             # load these modules, prefferred way to do so
#HPCI -p python numpy      # load these modules, and signal they are prerequisites
```

* All the directives, besides `-n` and `-v` can appear several times and they will be
 managed in the order they appear.

* The values set with `-n` and `-v` are usually used to construct the install
 directory and module directory (depending on how HPCInstalled has been configured, see
 the installation section below). 
 
* The values set with `-a` is a file that will be copied in the directory with installation logs,
 useful, e.g. to preserve a tarballs or other scripts (however use of [here
 document](https://en.wikipedia.org/wiki/Here_document) is recommended)
 
* Whatever follows `-x` is executed verbatim in the shell before invoking the script.
 It could be simply included in the script instead of using this directive, however
 using the directive will inform HPCInstall that these things will change the environment,
 and that can be extremely useful especially when sourcing third part files (because HPCInstall
 will automatically store the environment *after* running the `-x` commands, but *before*
 anything else in the script is exectuted)
 
* The `-l` and `-p` directives simply load the specified modules (without the need to write
 `module load`) and will inform HPCInstall that the environment has changed, like in the previous
 bullet. Moreover, the `-p` can help creating the module for the software under installation, by
 setting the `$HPCI_MOD_PREREQ` environmental variable

## Environmental variables

HPCInstall will set the following environmental variables:

```
HPCI_SW_DIR        # where to install the software
HPCI_SW_NAME       # software_name of the sw being installed
HPCI_SW_VERSION    # software_version of the sw being installed
HPCI_MOD_DIR       # directory where to create module, generic
HPCI_MOD_DIR_IDEP  # directory where to create module, if compiler independant
HPCI_MOD_DIR_CDEP  # directory where to create module, if compiler dependant
HPCI_MOD_PREREQ    # module prerequisite
```

These environmental variables should be used by the install script. Depending on how `hpcinstall`
has been installed, these environmental variables can use the loaded modules (e.g. compiler)
to build the appropriate directory structure, e.g. for where to install the software
or where to create the modules. This can happen only if `HPCInstall` knows about the loaded
modules, i.e. if they are loaded via a directive and not in the body of the script.
 
## Putting everything together

And here is an example install script using directives and environmental variables, similar to
the `build-mycode-example` present in the repository. It can have any name. Only `bash`
scripts are officially supported, and the recommended way to use anything non-bash is
to have it in a [here  document](https://en.wikipedia.org/wiki/Here_document) or in a
separate file, and invoke it from bash, as opposed to have a shebang for anything non-bash.

```
#!/bin/bash
#HPCI -n my_code
#HPCI -v 1.2.3
#HPCI -a ../my_code-1.2.3.tgz
#HPCI -l ncarenv
#HPCI -l gnu                # modules can be loaded on same line or multiple lines 
#HPCI -p netcdf             # even if they are prerequisite modules, however, the order
#HPCI -p ncl                # of their dependency must be respected
#HPCI -p another_module
#HPCI -p yet many other modules here

# terminate this script immediately should anything go wrong
set -e

./configure --prefix=$HPCI_SW_DIR
make
make install

# Create the module directory, if needed
# if this were compiler-independent module $HPCI_MOD_DIR_IDEP would have been used
mkdir -p $HPCI_MOD_DIR_CDEP/$HPCI_SW_NAME/

# Create the module with the following template
cat << EOF > $HPCI_MOD_DIR_CDEP/$HPCI_SW_NAME/${HPCI_SW_VERSION}.lua
require("posix")

whatis("$HPCI_SW_NAME v$HPCI_SW_VERSION")

help([[
This module loads my_code.
See http://my_code.example.com/ for details.
]])

local verpath = "$HPCI_SW_DIR"                    -- specific version path
local binpath = pathJoin(verpath, "bin")          -- internal python libs
-- similarly for includes or others

prepend_path("PATH", binpath)

prereq($HPCI_MOD_PREREQ)
EOF
```

## What does this buy us?

* list of advantages
* minimal change for new code
* including pushing to ys-install-script

## Running it

Simply run something like `hpcinstall build-mycode`. The `build-mycode` script does
not need to be executable, but will be made so by `HPCInstall` itself.
You should see an output similar to:

```
Saving environment status in hpci.env.log... Done.
Saving module list in hpci.modules.log... Done.

On 2017-02-16T13:37:22.883029 ddvento
called HPCinstall from /path/to/hpcinstall.py
invoked as /path/to/hpcinstall build-mycode

Setting environmental variables:
HPCI_SW_DIR       = /glade/scratch/ddvento/test_installs/my_code/1.2.3/gnu/4.8.2/
HPCI_SW_NAME      = my_code
HPCI_SW_VERSION   = 1.2.3
HPCI_MOD_DIR      = /glade/scratch/ddvento/test_installs/modulefiles/
HPCI_MOD_DIR_IDEP = /glade/scratch/ddvento/test_installs/modulefiles/idep/
HPCI_MOD_DIR_CDEP = /glade/scratch/ddvento/test_installs/modulefiles/gnu/
HPCI_MOD_PREREQ   = "netcdf","ncl"
Running ./build-mycode-example...
Value of SOMETHING=3
This script pretends to be installing
my_code version v1.2.3 in /glade/scratch/ddvento/test_installs/my_code/1.2.3/gnu/4.8.2/.
And modules in one of /glade/scratch/ddvento/test_installs/modulefiles/
or /glade/scratch/ddvento/test_installs/modulefiles/gnu/
or /glade/scratch/ddvento/test_installs/modulefiles/idep/
using prerequisite module "netcdf","ncl"
PRETENDING TO BE RUNNING: ./configure --prefix=/glade/scratch/ddvento/test_installs/my_code/1.2.3/gnu/4.8.2/
PRETENDING TO BE RUNNING: make and make install
Done running ./build-mycode-example - exited with code 0
For more details about this code, see URL: http://www.example.com
Hashdir: d41d8cd98f00b204e9800998ecf8427e /glade/scratch/ddvento/test_installs/my_code/1.2.3/gnu/4.8.2
Connection to localhost closed.
```

Note the line that says:

```
Done running ./build-mycode-example - exited with code 0
```

:star: `HPCInstall` simply run the `bash` script as is, and by default bash scripts keep running even in case
of errors. It is strongly recommended to use `set -e` as the example does, to force bash to stop when an error
is encountered, in order to prevent partially failed builds to install.

## Log files

From the previous run, the following logs will be created in the running directory and will also be
copied in the install directory in the `BUILD_DIR` subdirectory. Such a directory will be
automatically created by `HPCInstall`.

 - `hpci.env.log`: contains the list of all the environment variables in the
    system, right before the script started executing
 - `hpci.modules.log`: contains the list of all the loaded modules, right before
    the script is executed
 - `hpci.main.log`: contains a log of what happened, including the checksum of the installed directory
 - `hpci.build-mycode-example-20170216T133722.log`: contains the stdout and stderr
    produced by the script `build-mycode` itself. The suffix is the time of the run, to avoid
    clobbering in case of repeated builds (e.g. when debugging a build issue)
 - `hpci.fileinfo.log` with some information about the files it installed

If modules or environmental settings are created by the `-x`, `-l` and `-p` directives, their effect
is logged into the `hpci.env.log` and `hpci.modules.log`. If they are done in the body of the
script outside of a directive, they will be not.

Note that in the `BUILD_DIR` tree, `HPCInstall` will also copy the script that ran, and anything
specified under the `-a` (archive) directive, for reproducibility.

## More

 - note that it has not done anything with `/glade/scratch/ddvento/test_installs/modulefiles/`
 (other than setting the env var)
5. A real install will need to do something, so let's put the following into `build-zlib-1.2.8`
(only `bash` ufficially supported, however the bash
script can call another script in `tcsh`, `python`, `R` or whatever -- in such case, remember to
use the `#HPCI -a other_script.tcsh` to preserve
that other script, since `HPCInstall` does not try to guess what your script is doing):
 ```
#!/usr/bin/env bash
#
# Loading the latest GNU compiler and our wrappers
# No other (default or otherwise) modules are loaded
#HPCI -x ml gnu
#HPCI -x module load ncarcompilers
#
# Storing the tarball
#HPCI -a ../zlib-1.2.8.tar.gz

./configure --prefix=$HPCI_SW_DIR
make && make install
```

6. run `hpcinstall build-zlib-1.2.8  -a ../zlib-1.2.8.tar.gz` and [go playing in the hallway](http://www.xkcd.com/303/)

7. If one among the last lines of the log is different from `Done running ./build-zlib-1.2.8 - exited with code 0`,
figure out what was wrong, and go back to previous bullet.

8. Run  `cat hpci.main.log` and look at the content of `$HPCI_SW_DIR` directory, which for me on Laramie is
`/picnic/scratch/ddvento/test_installs/zlib/1.2.8/gnu/6.2.0/` (this is where everything should be installed,
but **only** if the build script described at the bullet 5. uses `$HPCI_SW_DIR` as prefix)

9. Run some program using this version of zlib (ideally making that program a test case for
[shark](https://github.com/NCAR/shark/)).
If everything is fine, you may install globally by running `HPCinstall` as csgteam
(or as yourself, if you have writing permissions) by using the `--csgteam` option:
 ```
hpcinstall -c build-zlib-1.2.8 -a ../zlib-1.2.8.tar.gz
```
 If you are running this as a test, beware! **THIS WILL INSTALL in /glade/apps/opt !!!!!**
 (or wherever the default, user-visible install directory is on that system -- this is chosen at
 install time with a line in `config.hpcinstall.yaml`)
 So do it for a piece of software for which is appropriate (if directory exists, `HPCinstall`
 will not clobber, but you might want to play safe and use a strange name instead)
 
10. :fire: To verify the hash of an installation, checking if anybody has changed anything, run
 ```
hashdir -d /path/to/installed/directory
```
and compare its output to the one in `/path/to/installed/directory/BUILD_DIR/hpci.main.log`.
The `BUILD_DIR` directory is by default ignored by `hashdir` (and by `hpcinstall` at install
time). If the hashes differ, you may run hashdir with the `-v` option to investigate further.
It will output details about each single file, which you can diff from the ones obtained at
install time, which are stored in `/path/to/installed/directory/BUILD_DIR/hpci.fileinfo.log`.
You may also use hashdir `-i` and `-e` options to filter what exactly to hash.

# Notes
 1. The install directory is automatically generated and contains the name and version of the
 compiler module loaded, per our policies. If no compiler is loaded, only software name and
 version would be used, such in `/glade/apps/opt/zlib/1.2.8/`, which is the policy for
 non-compiled stuff, such as pure-python (non compiled) libraries. It is now possible to
 change the base path of test installs from `/glade/scratch/$USER/test_installs` to a
 custom path by setting the `INSTALL_TEST_BASEPATH` environment variable before running `HPCinstall`.

 2. The modules are specified as comments in file `build-zlib-1.2.8`. This is needed for
 `HPCinstall` to correctly generate the `hpci.modules.log` file and (especially) to correctly
 generate the install directory as `/glade/apps/opt/zlib/1.2.8/gnu/4.8.2` (note the automatic
 use of the loaded module). If you are ok with not having both of these features, you may load
 the modules in any other way you want (e.g. command line before invoking, or executable
 `module such-and-such` in the script), and everything else will work just fine --
 **HOWEVER THIS IS NOT RECOMMENDED PRACTICE**, ask Sidd for details.

 3. The install directory should not exist, to prevent involuntary clobbering. Use the
 `--force` option to allow `HPCinstall` to clobber previous builds. Note that the path
 is not currently cleaned up before rerunning the install script, so manually cleaning
 may still be desired.

 4. The string (20161116T114509 in this case) at the end of the install script log
 `hpci.build-zlib-1.2.8-20161116T114509.txt` is the shortened isoformat of the date
 and time when the script ran, in this case 2016 Nov 16th at Time 11:45:09
 It is added to avoid deleting the log from previous attempts, so one can compare the
 current erros with the previous one(s) in case of failures, to see if any progress
 has been made. To reduce clutter, the other logs (modules, env, etc) are clobbered
 because tend to have more obvious content and not error messages.

 5. The csgteam install is interactive! It may ask a bunch of questions. We may need
 to discuss in the group meeting whether or not this is desired, it can be easily
 changed if appropriate, as well as if we want the script to know about picnic and whatsnot

 6. :bangbang: :bangbang: Last, but not least, one **IMPORTANT CONSIDERATION ABOUT POSSIBLY
 INTERACTIVE SCRIPTS** :bangbang: :bangbang: The way `HPCInstall` talks to the subshell is
 such that you could miss a question and the installation may seem to hang. This happens for
 example when running `unzip` which will print something like 
 ```replace directory/file? [y]es, [n]o, [A]ll, [N]one, [r]ename:```
 if the content of the file you are unzipping will clobber existing ones. This is very
 complicated to fix (see https://github.com/NCAR/HPCinstall/issues/72 for details), but a
 easy workaround is to just hit enter if the installation will seem to hang. The enter will
 flush the buffer and show the question, however a caveat is that it may also accept the
 default choice which might not be what you want. See if the program you are running has a
 non-interactive option (e.g. `unzip -o`)

## Installation

HPCInstall can be simply copied in a directory and invoked with fully qualified path. Or
that directory can be put in the `$PATH`. Strictly speaking that ends the installation.
However there is configuration to be done, and it must be done by creating a
`config.hpcinstall.yaml` file in the installation directory. See the ones for the machines
I work on for some examples, probably later I will describe more.
