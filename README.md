[![Build Status](https://travis-ci.org/NCAR/HPCinstall.svg?branch=master)](https://travis-ci.org/NCAR/HPCinstall)

# HPCinstall

`HPCinstall` is a piece of software used to install other software in an HPC environment.
What it does is simply to run a given install script, but it will
help by automatize the clerical, tedious tasks, letting the script do only the complicated parts.
It interfaces and helps create modulefiles (particularly for [lmod](https://github.com/TACC/Lmod))
but it can be easily used also in a module-free environement.

See the [module and installation workflow](https://wiki.ucar.edu/display/csg/Module+and+installation+management+process)
currently in use at NCAR/CISL.

# Requirements

* python 2.7+ (it may work with 2.6 + `argparse`)
* bash (tested with v4.1 and v4.2, it should work with most versions)
* ssh (tested with OpenSSH v5.3 and v6.6, it should work with most versions)
* [lmod](https://github.com/TACC/Lmod)
or [module](http://modules.sourceforge.net/)
 (optional, tested with lmod v4.2 and v7.2, it should work with most versions)
* python `yaml` and `blessed` modules (distributed with HPCInstall itself, see subdirectories, so they are
not an external dependency)

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
The most useful one is `--csgteam` which will cause the installation to be system-wide.
The `--debug` and `--preserve` are useful for debugging issues, and the `--force` is a
convenience option to remove the target installation directory, because otherwise HPCInstall
will refuse to clobber it.

## Directives

Your script can and should communicate with HPCInstall some important matters, using _directives_ which are comments in the script of the form

```
#HPCI -n software_name     # software_name is what is under installation
#HPCI -v software_version  # software_version of what is under installation
#HPCI -a filename          # archive this file in the same way as the build logs
#HPCI -x export FOO=bar    # execute this line, preferred way to change the environment
#HPCI -l intel             # load these modules, prefferred way to do so
#HPCI -p python numpy      # load these modules, and signal they are prerequisites
#HPCI -o CLOBBER           # clobber (overwrite without deleting) the existing install directory
```

* All the directives, besides `-n` and `-v` can appear several times and they will be
 managed in the order they appear.

* The values set with `-n` and `-v` are usually used to construct the install
 directory and module directory (depending on how HPCInstalled has been configured, see
 the installation section below).

* The `-o` directive can be used to set options, at the moment only CLOBBER is supported. It is
 recommended that CLOBBER is not used unless strongly needed for particular use cases, and
 to make sure it is used only when needed, a confirmation message is asked twice.

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
 bullet. HPCInstall will run `module purge` before anything else, and therefore any desired module
 must be explicitly loaded. There is no directive for other module commands such as `reset` or
 `use` however they can be run in the `-x` directive when needed.
 Moreover, the `-p` can help creating the module for the software under installation, by
 setting the `$HPCI_MOD_PREREQ` environmental variable

* The directives are exectuted in the order they appear, so if there are dependent modules (or
 `module use` or other order-sensitive items, they are honored)

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

## Why one would want to use HPCInstall instead of a plain script?

* Convenience
 * :+1: The above script will have only two lines changed when a new version of my_code is
   released, namely the two lines specifying `1.2.3`
 * :rocket: Without the script doing anything, everything during the build process is
   automatically logged and stored alongside the install directory:
   environment variables, output/error logs, script used for install, etc.
 * :cloud: The install script is also pushed to a remote github repo (if HPCInstall is so configured at install time)
 * :smile: The install directory name (and related module directory and module name) are automatically generated
   using HPCInstall configuration, without the script needing to do anything.

* Simplification of tests and verifications
 * :sunglasses: Nothing will need to change in the script between a test install and a production install
   Just adding the `-c` command line argument the install will switch from test location
   to production location
 * :white_check_mark: Checksums, and file properties are automatically computed and logged each time a
   software is installed. The `hashdir` program is provided, to check if anybody changed anything when things
   do not work anymore

* Simply, the person doing the install can concentrate on the important things instead of the housekeeping.


## How to run HPCInstall, and the logs it creates

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
    produced by the script `build-mycode` itself. The suffix is the isoformat datetime of the run,
    to avoid clobbering in case of repeated builds (e.g. when debugging a build issue)
 - `hpci.fileinfo.log` with some information about the files it installed

If modules or environmental settings are created by the `-x`, `-l` and `-p` directives, their effect
is logged into the `hpci.env.log` and `hpci.modules.log`. If they are done in the body of the
script outside of a directive, they will not.

Note that in the `BUILD_DIR` tree, `HPCInstall` will also copy the script that ran, and anything
specified under the `-a` (archive) directive, for reproducibility.

## Production installations

The installations described above occur in a `test_installs` tree (configurable at the time `HPCInstall`
is installed or at runtime with the `HPCI_TEST_BASEPATH` environment
variable). When satisfied with the user-level test install, a site-wide install in a global path
may be desired. Since at NCAR this is done by the `csgteam` group which is different from root,
a `--csgteam` (abbreviated to `-c`) is available. Simply run:

```
hpcinstall -c build-mycode
```

and the same things as before will happen, just the directories will be the global ones (configured
at the time `HPCInstall` was installed)

## Notes and other features

* To verify the hash of an installation, checking if anybody has changed anything, run
 ```
hashdir -d /path/to/installed/directory
```
and compare its output to the one in `/path/to/installed/directory/BUILD_DIR/hpci.main.log`.
The `BUILD_DIR` directory is by default ignored by `hashdir` (and by `hpcinstall` at install
time). If the hashes differ, you may run hashdir with the `-v` option to investigate further.
It will output details about each single file, which you can diff from the ones obtained at
install time, which are stored in `/path/to/installed/directory/BUILD_DIR/hpci.fileinfo.log`.
You may also use hashdir `-i` and `-e` options to filter what exactly to hash.

* :star: The `--csgteam` (root) install is interactive!

* :sparkles: After a successful `--csgteam` (root) install, the script is committed and
  pushed to the remote `script_repo` as configured at the time `HPCInstall` was installed.

* :fire: Last, but not least, one **IMPORTANT CONSIDERATION ABOUT POSSIBLY
 INTERACTIVE SCRIPTS** :fire: The way `HPCInstall` talks to the subshell is
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

HPCInstall can be simply copied in a directory and invoked with fully qualified path, or
that directory can be put in the `$PATH`. However it needs to be configured for the
particular machine, and to do so it needs a `config.hpcinstall.yaml` file in the
installation directory.

The mandatory configuration options are:

* `scratch_tree`: The directory where temporary installs will happen is `scratch_tree/$USER` (can be
overriden by setting the `HPCI_TEST_BASEPATH` environment variable)

* `sw_install_dir`: The basepath of the tree where sofware will be installed
* `sw_install_struct`: The structure of the tree where sofware will be installed

* `mod_install_dir`: The directory tree where modules will be installed
* `mod_install_struct`: The structure of the tree where modules will be installed

There are additional optional configuration options, namely:

* `use_modules`: must be a boolean, if `False` will not do anything module-related (default: `True`)
* `python_cmd`: HPCInstall is written in python. If python is not in the `$PATH` or if the default
version is too old, another one can be specified here with fully qualified path.
* `script_repo`: if set to a directory, consider that directory as a clone of a repository where
all the install scripts will be preserved. After a successful production installation, add the install
script to that repository and push it
* `git_cmd`: fully qualified path of the git binary, to be run to preserve the install scripts per
previous bullet. If the git binary in the `$PATH` is new enough, no need to set this option.

The directory-related configuration options may use evironmental variables. See the `.yaml` files for some
examples.

# Release History

This section may become reduntant once github includes the tag message in their
[release page](https://github.com/NCAR/HPCinstall/releases) but for now, here it is, simply the output of
`git tag -n1`:

* v0.9            Initial release, decent enough to be installed on Yellowstone
* v0.9.1          now hpcinstall can self-install itself :-)
* v0.9.2          now enforcing clean slate in the environment
* v0.9.3          never push too early.... changing name because of that
* v0.9.4          Making sure the clean slate environment is usable, e.g. allowing to load modules
* v1.0            Several improvements, namely issues #23 #62 #63 #64 #65 (most important: proper parsing of names-with-slash and push-installscript-to-github
* v1.0.1          Wrong directory for modules on Yellowstone, otherwise identical to v1.0
* v1.0.2          Missing dependencies in the install script, otherwise identical to v1.0
* v1.0.3          Install script and config file for jellystone, otherwise identical to v1.0
* v1.0.4          Cheyenne settings, otherwise identical to v1.0
* v1.0rc          Many bugs fixed, large and small, changed the file format to directives
* v1.0rc2         Second release canditate, fixing some serious bugs
* v1.0rc3         Fixing issues for Yellowstone, caused by default python being v2.6
* v1.0rc4         wildcards for the archive directive, tcsh, datetime instead of PID, more moduledirs
* v1.0rc5         Swapping the order of directories for both modules and install: MPI first and COMPILER second
* v1.1            Several minor features added and bug fixes; better documenation; see the commit history for details
* v1.1.1          Made the use of modules optionally configurable at install time, and used that option for HPCFL
* v1.2            Using x-tunneling when `ssh`ing into localhost, fixed configuration file on Yellowstone, first open source release
