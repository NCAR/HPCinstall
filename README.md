# HPCinstall

`HPCinstall` is a piece of software used to install other software. What it does is simply to run a given install script, but it will help by automatize the stupid, clerical, tedious tasks, letting the script do only the complicated parts.

## Features
 
Some of the features of `HPCinstall` are: 
* automatic log of everything (environment, log, script used for install, etc) 
* automatic archive of the logs in the install directory
* automatic generation of the install directory name (and module name) from the name and version of the software to be compiled and the loaded compiler module
* automatic similar things
 
It is easier to show how it achieves these goals with an example

## Use example - zlib v1.2.8

1. Download the software to be installed. I manually run `wget http://zlib.net/zlib-1.2.8.tar.gz`.
2. Untar the tarball and go into the directory. Create a file named `build-name-version`. So in this case I run `touch build-zlib-1.2.8`.
3. Load the `hpcinstall` module and run `hpcinstall build-zlib-1.2.8` 
4. The install script `build-zlib-1.2.8` we created in bullet 2 is empty, so it does nothing, but `HPCinstall` still does something with it. The output of running `hpcinstall build-zlib-1.2.8` should be something like:
 ```
Saving environment status in hpci.env.log ... Done.
Saving module list in hpci.modules.log ... Done.

On 2016-08-25T14:25:51.690300 ddvento
called HPCinstall as /glade/u/home/ddvento/github/HPCinstall/HPCinstall-v1.0/hpcinstall 

Setting environmental variables:
HPCI_SW_DIR     = /glade/scratch/ddvento/test_installs//zlib/1.2.8/intel/12.1.5
HPCI_SW_NAME    = zlib
HPCI_SW_VERSION = 1.2.8
HPCI_MOD_DIR    = /glade/scratch/ddvento/test_installs//modulefiles/

Running ./build-zlib-1.2.8 ...
Done running ./build-zlib-1.2.8 - exited with code 0
```
 Let's look at what `HPCinstall` has done in the current directory:
 ```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls -lt | head
total 1104
-rw-rw-r--  1 ddvento consult    451 Aug 25 14:25 hpci.main.log
-rw-rw-r--  1 ddvento consult    162 Aug 25 14:25 hpci.build-example-1.2.3-7629.log
-rw-rw-r--  1 ddvento consult    280 Aug 25 14:25 hpci.modules.log
-rw-rw-r--  1 ddvento consult   8152 Aug 25 14:25 hpci.env.log
-rwxrw-r--  1 ddvento consult      0 Aug 25 11:36 build-zlib-1.2.8
```
 and also let's look at `/glade/scratch/ddvento/test_installs//zlib/1.2.8/intel/12.1.5` (value of `$HPCI_SW_DIR` mentioned above):
 ```
ddvento@yslogin1 $ ls -l /glade/scratch/ddvento/test_installs//zlib/1.2.8/intel/12.1.5/
total 0
drwxrwxr-x 2 ddvento consult 512 Aug 25 11:36 BUILD_DIR

ddvento@yslogin1 $ ls -l /glade/scratch/ddvento/test_installs//zlib/1.2.8/intel/12.1.5/BUILD_DIR/
total 384
-rw-rw-r-- 1 ddvento consult  161 Aug 25 14:25 build-zlib-1.2.8
-rw-rw-r-- 1 ddvento consult  162 Aug 25 14:25 hpci.build-zlib-1.2.8-3249.txt
-rw-rw-r-- 1 ddvento consult 8152 Aug 25 14:25 hpci.env.log
-rw-rw-r-- 1 ddvento consult  451 Aug 25 14:25 hpci.main.log
-rw-rw-r-- 1 ddvento consult  280 Aug 25 14:25 hpci.modules.log
-rw-rw-r-- 1 ddvento consult 9140 Aug 25 14:25 hpcinstall
```
So `HPCinstall` has done the following:
 - created the four `hpci.*.log` files in current directory:
     - `hpci.env.log` contains the list of all the environment variables in the system, right before the script started executing
     - `hpci.modules.log` contains the list of all the loaded modules, right before the script is executed
     - `hpci.main.log` contains a log of what happened
     - `hpci.build-zlib-1.2.8-3249.txt` contains the stdout and stderr produced by running `build-zlib-1.2.8` (in this case nothing)
 - made the `build-zlib-1.2.8` script executable (we did not make so in 3. when we created it)
 - created the directory `/glade/scratch/ddvento/test_installs//zlib/1.2.8/intel/12.1.5/` (and all the necessary parents)
 - copied in the directory of the previous bullet the four `hpci.*.log` plus the `hpcinstall` and the `build-zlib-1.2.8` scripts for reproducibility
 - note that it has not done anything with `/glade/scratch/ddvento/test_installs//modulefiles/` (other than setting the env var)
5. A real install will need to do something, so let's put the following into `build-zlib-1.2.8` (any language will work, using `bash` for this example):
 ```
#!/bin/env bash
#
#HPCI ml reset
#HPCI ml sw intel gnu/4.8.2
#HPCI ml remove netcdf

./configure --prefix=$HPCI_SW_DIR
make && make install
```

6. Note the `#HPCI` directive which will execute (source) whatever instruction you have there, like `module load such-and-such` or `export THIS_AND_THAT`

6. run `hpcinstall build-zlib-1.2.8` and [go playing in the hallway](http://www.xkcd.com/303/)

7. If the last line of the log is different from `Done running ./build-zlib-1.2.8 - exited with code 0`, figure out what was wrong, and go back to previous bullet.

8. Run  `cat hpci.main.log` and look at the content of `$HPCI_SW_DIR` directory, which for me is `/glade/scratch/ddvento/test_installs//zlib/1.2.8/intel/12.1.5` (this is where everything should be installed, but **only** if the build script described at the bullet 5. uses `$HPCI_SW_DIR` as prefix)

9. Run some program using this version of zlib (ideally making that program a test case for [shark](https://github.com/NCAR/shark/)). If everything is fine, you may install globally by running `HPCinstall` as csgteam (or as yourself, if you have writing permissions) by using the `--csgteam` option:
 ```
hpcinstall -c build-zlib-1.2.8
```
 If you are running this as a test, beware! **THIS WILL INSTALL in /glade/apps/opt !!!!!** (or wherever the default, user-visible install directory is on that system -- this is chosen at install time with a line in `config.hpcinstall.yaml`)
 So do it for a piece of software for which is appropriate (if directory exists, `HPCinstall` will not clobber, but you might want to play safe and use a strange name instead)

# Notes
 1. The install directory is automatically generated and contains the name and version of the compiler module loaded, per our policies. If no compiler is loaded, only software name and version would be used, such in `/glade/apps/opt/zlib/1.2.8/`, which is the policy for non-compiled stuff, such as pure-python (non compiled) libraries. It is now possible to change the base path of test installs from `/glade/scratch/$USER/test_installs` to a custom path by setting the `INSTALL_TEST_BASEPATH` environment variable before running `HPCinstall`.

 2. The modules are specified as comments in file `build-zlib-1.2.8`. This is needed for `HPCinstall` to correctly generate the `hpci.modules.log` file and (especially) to correctly generate the install directory as `/glade/apps/opt/zlib/1.2.8/gnu/4.8.2` (note the automatic use of the loaded module). If you are ok with not having both of these features, you may load the modules in any other way you want (e.g. command line before invoking, or executable `module such-and-such` in the script), and everything else will work just fine -- **HOWEVER THIS IS NOT RECOMMENDED PRACTICE**, ask Sidd for details.

 3. The install directory should not exist, to prevent involuntary clobbering. Use the `--force` option to allow `HPCinstall` to clobber previous builds. Note that the path is not currently cleaned up before rerunning the install script, so manually cleaning may still be desired.

 4. The number (3249 in this case) at the end of the install script log `hpci.build-zlib-1.2.8-3249.txt` is the PID of the execution.
It is added to avoid deleting the log from previous attempts, so one can compare the current erros with the previous one(s) in
case of failures, to see if any progress has been made. To reduce clutter, the other logs (modules, env, etc) are clobbered
because tend to have more obvious content and not error messages.

 5. The csgteam install is interactive! It may ask a bunch of questions. We may need to discuss in the group meeting whether or not
this is desired, it can be easily changed if appropriate, as well as if we want the script to know about picnic and whatsnot

