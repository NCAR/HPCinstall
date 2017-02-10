[![Build Status](https://travis-ci.com/NCAR/HPCinstall.svg?token=ZoVz2xMBgzXK6oqcK3qN&branch=master)](https://travis-ci.com/NCAR/HPCinstall)

# HPCinstall

`HPCinstall` is a piece of software used to install other software in an HPC environment.
What it does is simply to run a given install script, but it will
help by automatize the clerical, tedious tasks, letting the script do only the complicated parts.
It interfaces and helps create modulefiles (particularly for [lmod](https://github.com/TACC/Lmod))
but it can be easily used also in a module-free environement

See the [module and installation workflow](https://wiki.ucar.edu/display/csg/Module+and+installation+management+process)
currently in use at NCAR/CISL.

## Features
 
Some of the features of `HPCinstall` are: 
* :rocket: automatic log of everything (environment, log, script used for install, etc) 
* :+1: automatic archive of the logs in the install directory
* :smile: automatic generation of the install directory name (and module name) from
 the name and version of the software to be compiled and the loaded compiler/mpi modules (if appropriate).
 The structure of this directories names can be configured with the
 `sw_install_struct` and `mod_install_struct` config properties
* checksum verification of the installation (at install time and post-mortem with `hashdir`)
* and more
 
It is easier to show how it achieves these goals with an example

## Use example - zlib v1.2.8

1. :point_right: Download the software to be installed. This could be part of the script, but I prefer
to manually run `wget http://zlib.net/zlib-1.2.8.tar.gz` (because the build may fail
and need to re-run several times and I don't want to redownload the source several times)
2. Untar the tarball and cd into the directory. 
3. Create a file named `build-name-version`, e.g by running `touch build-zlib-1.2.8`.
3. :+1: Load the `hpcinstall` module (or clone the trunk and specify full path) 
4. :collision: Run `hpcinstall build-zlib-1.2.8` :collision: You will get the
`ERROR: Either or both the '#HPCI -u URL' and '#HPCI -a source.tgz' must be provided`
4. :hand: You **have to** specify either or both the `-a`, or `-u` directive to document which
source code you are using (`-u` is recommended
*only* for software that you did not manually download a source archive, such as ones
that you install with `pip install` or `git clone`)
5. Run `echo "#HPCI -a ../zlib-1.2.8.tar.gz" > build-zlib-1.2.8` (to create that directive
into the file) and run again `hpcinstall build-zlib-1.2.8`
4. The install script `build-zlib-1.2.8` we created is almost empty, so it does nothing,
but `HPCinstall` still does something with it. The output of running
`hpcinstall build-zlib-1.2.8` should be something like (if the terminal supports it, it'll
use colored output):

```
Saving environment status in hpci.env.log... Done.
Saving module list in hpci.modules.log... Done.

On 2017-02-10T11:44:27.494285 ddvento
called HPCinstall from /glade/u/home/ddvento/github/HPCinstall/yellowstone/hpcinstall.py
invoked as /glade/u/home/ddvento/github/HPCinstall/yellowstone/hpcinstall build-zlib-1.2.8

Setting environmental variables:
HPCI_SW_DIR       = /glade/scratch/ddvento/test_installs/zlib/1.2.8/
HPCI_SW_NAME      = zlib
HPCI_SW_VERSION   = 1.2.8
HPCI_MOD_DIR      = /glade/scratch/ddvento/test_installs/modulefiles/
HPCI_MOD_DIR_IDEP = /glade/scratch/ddvento/test_installs/modulefiles/idep/
HPCI_MOD_DIR_CDEP = /glade/scratch/ddvento/test_installs/modulefiles/
HPCI_MOD_PREREQ   = 
Running ./build-zlib-1.2.8...
Done running ./build-zlib-1.2.8 - exited with code 0
Archiving file: /glade/u/home/ddvento/github/HPCinstall/zlib-1.2.8.tar.gz
Hashdir: d41d8cd98f00b204e9800998ecf8427e /glade/scratch/ddvento/test_installs/zlib/1.2.8
Connection to localhost closed.
```

 Let's look at what `HPCinstall` has done in the current directory:
 ```
  ddvento@yslogin6 /glade/u/home/ddvento/github/HPCinstall/yellowstone $ ls -lt
total 256
-rw-rw-r-- 1 ddvento consult     0 Feb 10 11:44 hpci.fileinfo.log
-rw-rw-r-- 1 ddvento consult   955 Feb 10 11:44 hpci.main.log
-rw-rw-r-- 1 ddvento consult     0 Feb 10 11:44 hpci.build-zlib-1.2.8-20170210T114427.log
-rw-rw-r-- 1 ddvento consult    43 Feb 10 11:44 hpci.modules.log
-rw-rw-r-- 1 ddvento consult  3297 Feb 10 11:44 hpci.env.log
-rwxrw-r-- 1 ddvento consult    50 Feb 10 11:44 build-zlib-1.2.8
```
Peek at those files to see what they are. The two empty ones are
`hpci.fileinfo.log` (with some information about the files it installed)
and the one with the long name (with the actual standard output/error from
running the `build-zlib-1.2.8` file). Both are empty because our script did
nothing.
 
 and also let's look at `/glade/scratch/ddvento/test_installs/zlib/1.2.8/` (value of `$HPCI_SW_DIR` seen above):
 ```
 ddvento@yslogin6 /glade/u/home/ddvento/github/HPCinstall/yellowstone $ ls -l /glade/scratch/ddvento/test_installs/zlib/1.2.8/
total 0
drwxrwxr-x 2 ddvento consult 512 Feb 10 11:44 BUILD_DIR
ddvento@yslogin6 /glade/u/home/ddvento/github/HPCinstall/yellowstone $ ls -l /glade/scratch/ddvento/test_installs/zlib/1.2.8/BUILD_DIR/
total 256
-rw-rw-r-- 1 ddvento consult     50 Feb 10 11:44 build-zlib-1.2.8
-rw-rw-r-- 1 ddvento consult      0 Feb 10 11:44 hpci.build-zlib-1.2.8-20170210T114427.log
-rw-rw-r-- 1 ddvento consult   3297 Feb 10 11:44 hpci.env.log
-rw-rw-r-- 1 ddvento consult      0 Feb 10 11:44 hpci.fileinfo.log
-rw-rw-r-- 1 ddvento consult    955 Feb 10 11:44 hpci.main.log
-rw-rw-r-- 1 ddvento consult     43 Feb 10 11:44 hpci.modules.log
-rw-rw-r-- 1 ddvento consult 571091 Feb 10 11:44 zlib-1.2.8.tar.gz
```
So `HPCinstall` has done the following:
 - created the five `hpci.*.log` files in current directory:
     - `hpci.env.log` contains the list of all the environment variables in the
     system, right before the script started executing
     - `hpci.modules.log` contains the list of all the loaded modules, right before
     the script is executed
     - `hpci.main.log` contains a log of what happened, including the checksum of the installed directory
     - :star: `hpci.fileinfo.log` with some information about the files it installed
     - `hpci.build-zlib-1.2.8-20161116T114509.txt` contains the stdout and stderr
     produced by running `build-zlib-1.2.8` (in this case nothing)
 - made the `build-zlib-1.2.8` script executable (we did not make so in 3. when we created it)
 - created the directory `/picnic/scratch/ddvento/test_installs/zlib/1.2.8/BUILD_DIR/` (and all the necessary parents)
 - copied in the directory of the previous bullet the five `hpci.*.log` plus the source
 archive and the `build-zlib-1.2.8` scripts for reproducibility
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

6. Note the `#HPCI -x` directive which will execute (source) whatever instruction you have
there, like `module load such-and-such` or `export THIS_AND_THAT`

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
