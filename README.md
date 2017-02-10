[![Build Status](https://travis-ci.com/NCAR/HPCinstall.svg?token=ZoVz2xMBgzXK6oqcK3qN&branch=master)](https://travis-ci.com/NCAR/HPCinstall)

# HPCinstall

`HPCinstall` is a piece of software used to install other software.
What it does is simply to run a given install script, but it will
help by automatize the stupid, clerical, tedious tasks, letting the script do only the complicated parts.

See https://wiki.ucar.edu/display/csg/Module+and+installation+management+process for the workflow we agreed on

## Features
 
Some of the features of `HPCinstall` are: 
* automatic log of everything (environment, log, script used for install, etc) 
* automatic archive of the logs in the install directory
* automatic generation of the install directory name (and module name) from
the name and version of the software to be compiled and the loaded compiler module
* automatic similar things
* :+1: checksum verification of the installation (at install time and post-mortem with `hashdir`)
 
It is easier to show how it achieves these goals with an example

## Use example - zlib v1.2.8

1. Download the software to be installed. I manually run `wget http://zlib.net/zlib-1.2.8.tar.gz`.
2. Untar the tarball and cd into the directory. Create a file named `build-name-version`. 
So in this case I run `touch build-zlib-1.2.8`.
3. Load the `hpcinstall` module and run `hpcinstall build-zlib-1.2.8` :collision: You will get the
`ERROR: Either or both the '#HPCI -u URL' and '#HPCI -a source.tgz' must be provided`
(see https://github.com/NCAR/HPCinstall/issues/15 for details)
4. You now you **must** specify one of the `-a`, or `-u` directive to document which
source code you are using (`-u` is recommended
*only* for software that you did not manually download a source archive, such as ones
that you install with `pip install` or `git clone`)
5. So run `echo "#HPCI -a ../zlib-1.2.8.tar.gz" > build-zlib-1.2.8` (to create that directive
into the file) and run again `hpcinstall build-zlib-1.2.8`
4. The install script `build-zlib-1.2.8` we created is almost empty, so it does nothing,
but `HPCinstall` still does something with it. The output of running
`hpcinstall build-zlib-1.2.8` should be something like:
 ```
Saving environment status in hpci.env.log ... Done.
Saving module list in hpci.modules.log ... Done.

On 2016-10-21T16:08:24.802860 ddvento
called HPCinstall from /picnic/u/home/ddvento/github/HPCinstall/trunk/hpcinstall
invoked as /picnic/u/home/ddvento/github/HPCinstall/trunk/hpcinstall build-zlib-1.2.8

Setting environmental variables:
HPCI_SW_DIR       = /picnic/scratch/ddvento/test_installs/zlib/1.2.8/
HPCI_SW_NAME      = zlib
HPCI_SW_VERSION   = 1.2.8
HPCI_MOD_DIR      = /picnic/scratch/ddvento/test_installs/modulefiles/
HPCI_MOD_DIR_IDEP = /picnic/scratch/ddvento/test_installs/modulefiles/idep/
HPCI_MOD_DIR_CDEP = /picnic/scratch/ddvento/test_installs/modulefiles/cdep/

Running ./build-zlib-1.2.8 ...
Done running ./build-zlib-1.2.8 - exited with code 0
Storing source archive: ../zlib-1.2.8.tar.gz
d41d8cd98f00b204e9800998ecf8427e /picnic/scratch/ddvento/test_installs/zlib/1.2.8
Connection to localhost closed.
```
 Let's look at what `HPCinstall` has done in the current directory:
 ```
ddvento@laramie1 zlib $ ls -lt
total 560
-rw-rw-r-- 1 ddvento consult      0 Oct  7 10:48 hpci.fileinfo.log
-rw-rw-r-- 1 ddvento consult    609 Oct  7 10:48 hpci.main.log
-rw-rw-r-- 1 ddvento consult    209 Oct  7 10:48 hpci.build-zlib-1.2.8-20161116T114509.log
-rw-rw-r-- 1 ddvento consult    250 Oct  7 10:48 hpci.modules.log
-rw-rw-r-- 1 ddvento consult   3853 Oct  7 10:48 hpci.env.log
-rwxrw-r-- 1 ddvento consult      0 Oct  7 10:45 build-zlib-1.2.8
-rw-rw-r-- 1 ddvento consult 571091 Apr 28  2013 zlib-1.2.8.tar.gz
```
:new: Now it also create a `hpci.fileinfo.log` with some information about
the files it installed (in this case it's empty because it did not
install any file, since our test scritp `build-zlib-1.2.8` does nothing).
 
 and also let's look at `/picnic/scratch/ddvento/test_installs/zlib/1.2.8/` (value of `$HPCI_SW_DIR` mentioned above):
 ```
ddvento@laramie1 zlib $ ls -l /picnic/scratch/ddvento/test_installs/zlib/1.2.8/
total 0
drwxrwxr-x 2 ddvento consult 4096 Oct  7 10:48 BUILD_DIR

ddvento@laramie1 zlib $ ls -l /picnic/scratch/ddvento/test_installs/zlib/1.2.8/BUILD_DIR/
total 768
-rw-rw-r-- 1 ddvento consult      0 Oct  7 10:48 build-zlib-1.2.8
-rw-rw-r-- 1 ddvento consult    209 Oct  7 10:48 hpci.build-zlib-1.2.8-20161116T114509.log
-rw-rw-r-- 1 ddvento consult   3853 Oct  7 10:48 hpci.env.log
-rw-rw-r-- 1 ddvento consult      0 Oct  7 10:48 hpci.fileinfo.log
-rw-rw-r-- 1 ddvento consult    609 Oct  7 10:48 hpci.main.log
-rw-rw-r-- 1 ddvento consult    250 Oct  7 10:48 hpci.modules.log
-rw-rw-r-- 1 ddvento consult 571091 Oct  7 10:48 zlib-1.2.8.tar.gz
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
