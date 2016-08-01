# HPCinstall

## Goal and Vision

`HPCinstall` is a piece of software used to install other software. Its goals are:

1. Not being in your way (as much as possible) allowing you to do whatever you want
2. Nudge you (but not force you) towards some best practices which we agreed upon
3. Help you by automatically making the stupid, clerical, tedious tasks that you know you need to do, but don't have time and will to

Some of the best practices we agree that we should be doing and that `HPCinstall` tries to nudge you towards are:

* Make the install process easily reproducible, i.e. use a script file instead of typing commands at the prompt. A different approach is possible, namely using the `script` typescript (or something like it) e.g. as described [here](stackoverflow.com/questions/5985060/5985255#5985255). But that is not what `HPCinstall` does.
* Use a couple of environmental variables (which `HPCinstall` sets) to make the install script mentioned in above bullet independed from the particular version of the software you are installing
* Test the installed software as yourself before installing as csgteam 
 
## Features
 
Some of the features of `HPCinstall` are: 
* automatic log of everything (environment, log, script used for install, etc) 
* automatic archive of the logs in the install directory
* automatic generation of the install directory name (and module name) from the name and version of the software to be compiled and the loaded compiler module
* automatic similar things
 
It is easier to show how it achieves these goals with an example

## Very detailed example of use (covering every small thing, skip below if you want just a quicker summary)

###Install zlib
According to [this document](https://docs.google.com/spreadsheets/d/1BxkASYb_Tdt7G-idwD7rScTLT1wj4rovwbZQ-L6Aguk/edit#gid=0) I should evaluate build/install tools by trying them on zlib, so here it is. See the same document for what software *you* should install.

1. Download the software to be installed. After some googling `wget http://zlib.net/zlib-1.2.8.tar.gz` is the solution. I don't think it's worth saving this in the install script (URL may change), so I don't. Nothing prevents you to think and do differently.
2. Anywhere in the filesystem (`HPCinstall` does not care) create a directory and run `tar xf zlib-1.2.8.tar.gz` into it. I don't think this is worth saving this in the install script, so I don't. Nothing prevents you to think and do differently.
3. Go into the untarred directory and create a file named `name-version`. So in this case I run `touch zlib-1.2.8`. This is a requirement, but I might change `HPCinstall` to parse the directory name instead and leave you with a free filename, if the group so prefers.
4. This is a useless bullet point, it is here to show you in detail what `HPCinstall` does. Let's run `ls -l /glade/scratch/$USER/zlib/1.2.8/intel/12.1.5` and see the `No such file or directory` response (if the directory exists, either delete it or rename the `zlib-1.2.8` to something else).
5. At this point you can start using `HPCinstall` by invoking it on the file we've just created. So if `hpcinstall` is in your `PATH` you can run `hpcinstall zlib-1.2.8` otherwise run `/absolute/or/relative/path/hpcinstall zlib-1.2.8` (either one will work, `HPCinstall` does not require to be officially installed)
6. Now, the install script `zlib-1.2.8` we created in bullet 3 is empty, so it does nothing, but `HPCinstall` still does something with it. The output of running `hpcinstall zlib-1.2.8` should be something like:
 ```
Saving environment status in log.env.txt ... Done.
Saving module list in log.modules.txt ... Done.

Setting environmental variables:
INSTALL_DIR     = /glade/scratch/ddvento/zlib/1.2.8/intel/12.1.5
MODULE_FILENAME = /glade/scratch/modulefiles/zlib/1.2.8.lua

Running ./zlib-1.2.8 ...
Done running ./zlib-1.2.8 - exited with code 0
```
 Let's look at what `HPCinstall` has done in the current directory:
 ```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls -lt | head
total 1104
-rw-rw-r--  1 ddvento consult   135 Aug  1 10:46 log.modules.txt
-rw-rw-r--  1 ddvento consult  7450 Aug  1 10:46 log.env.txt
-rw-rw-r--  1 ddvento consult   231 Aug  1 10:43 log.hpcinstall.txt
-rw-rw-r--  1 ddvento consult     0 Aug  1 10:43 log.zlib-1.2.8-3120.txt
-rwxrw-r--  1 ddvento consult     0 Jul 29 15:55 zlib-1.2.8
-rw-r--r--  1 ddvento consult 76402 Apr 28  2013 ChangeLog
-rw-r--r--  1 ddvento consult  4236 Apr 28  2013 zlib.3
-rw-r--r--  1 ddvento consult  8734 Apr 28  2013 zlib.3.pdf
-rw-r--r--  1 ddvento consult 87883 Apr 28  2013 zlib.h
```
 and also let's look at `/glade/scratch/ddvento/zlib/1.2.8/intel/12.1.5` content (not empty anymore like in bullet 4. above):
 ```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls -l /glade/scratch/ddvento/zlib/1.2.8/intel/12.1.5
total 0
drwxrwxr-x 2 ddvento consult 512 Aug  1 10:43 BUILD_DIR

ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls -l /glade/scratch/ddvento/zlib/1.2.8/intel/12.1.5/BUILD_DIR/
total 256
-rw-rw-r-- 1 ddvento consult 7397 Aug  1 10:43 hpcinstall
-rw-rw-r-- 1 ddvento consult 7450 Aug  1 10:43 log.env.txt
-rw-rw-r-- 1 ddvento consult  231 Aug  1 10:43 log.hpcinstall.txt
-rw-rw-r-- 1 ddvento consult  135 Aug  1 10:43 log.modules.txt
-rw-rw-r-- 1 ddvento consult    0 Aug  1 10:43 log.zlib-1.2.8-3120.txt
-rw-rw-r-- 1 ddvento consult  126 Aug  1 10:43 zlib-1.2.8
```
So `HPCinstall` has done the following:
 - created the four `log.*.txt` files in current directory
 - made the `zlib-1.2.8` script executable (we did not make so in 3. when we created it)
 - created the directory `/glade/scratch/ddvento/zlib/1.2.8/intel/12.1.5/BUILD_DIR/` (and all the necessary parents)
 - copied in the directory of the previous bullet the four `log.*.txt` plus the `hpcinstall` and the `zlib-1.2.8` scripts for reproducibility
 - note that it has not done anything with `/glade/scratch/modulefiles/zlib/1.2.8.lua` (other than setting the env var)

 Everything should be self-documenting, but let's look at the content of the four files
7. Let's start with the environment `log.env.txt`
Run a `less log.env.txt` -- you will see the list of all the environment variables in the system, right before the script is executed

8. Move on with `cat log.modules.txt`. You will see:
 ```
Currently Loaded Modules:
  1) ncarenv/1.0        3) intel/12.1.5         5) netcdf/4.3.0
  2) ncarbinlibs/1.1    4) ncarcompilers/1.0
```
Which is the list of module I had loaded when I ran the script (it does not have to be the *reset* environment).
See in the **summary** below about a suggested way of loading modules with `HPCinstall`

9. Next file to cat is `log.hpcinstall.txt`. You will see:
 ```
Setting environmental variables:
INSTALL_DIR     = /glade/scratch/ddvento/zlib/1.2.8/intel/12.1.5
MODULE_FILENAME = /glade/scratch/modulefiles/zlib/1.2.8.lua

Running ./zlib-1.2.8 ...
Done running ./zlib-1.2.8 - exited with code 0
```
Which is the output that we have seen on the screen in step 6. Note that if our own script `zlib-1.2.8` produced any output, it would have
been printed onscreen, but it would **not** be included in this log, but in the subsequent.

10. Finally, the last log is `log.zlib-1.2.8-3120.txt` which in this case is empty, but it contains the output of the script `zlib-1.2.8`, see below for details.

## Summary (very succint example of use)

1. In the directory containing the source to be compiled (e.g. `zlib v1.2.8`) create a file like the following named `zlib-1.2.8` (any language will work, using `bash` for this example):
 ```
#!/bin/env bash
# ml reset
# ml sw intel gnu/4.8.2
# ml remove netcdf

./configure --prefix=$INSTALL_DIR
make && make install
```

2. run `hpcinstall zlib-1.2.8` and [go playing in the hallway](http://www.xkcd.com/303/)

3. If the last command is different from `Done running ./zlib-1.2.8 - exited with code 0`, figure out what was wrong, and go back to previous bullet, otherwise run:
 ```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ cat log.hpcinstall.txt
Setting environmental variables:
INSTALL_DIR     = /glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2
MODULE_FILENAME = /glade/scratch/modulefiles/zlib/1.2.8.lua

Running ./zlib-1.2.8 ...
Done running ./zlib-1.2.8 - exited with code 0
```

4. As see in the previous bullet, the code should have been installed into `/glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2`, verify that it worked by cd into it and poking around
 ```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ cd /glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2
ddvento@yslogin6 /glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2 $ ls -l
total 0
drwxrwxr-x 2 ddvento consult 512 Aug  1 11:30 BUILD_DIR
drwxrwxr-x 2 ddvento consult 512 Aug  1 11:30 include
drwxrwxr-x 3 ddvento consult 512 Aug  1 11:30 lib
drwxrwxr-x 3 ddvento consult 512 Aug  1 11:30 share
ddvento@yslogin6 /glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2 $ ls BUILD_DIR/ -l
total 384
-rw-rw-r-- 1 ddvento consult 7397 Aug  1 11:30 hpcinstall
-rw-rw-r-- 1 ddvento consult 7197 Aug  1 11:30 log.env.txt
-rw-rw-r-- 1 ddvento consult  228 Aug  1 11:30 log.hpcinstall.txt
-rw-rw-r-- 1 ddvento consult  341 Aug  1 11:30 log.modules.txt
-rw-rw-r-- 1 ddvento consult 5295 Aug  1 11:30 log.zlib-1.2.8-25493.txt
-rw-rw-r-- 1 ddvento consult  126 Aug  1 11:30 zlib-1.2.8
ddvento@yslogin6 /glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2 $ cat BUILD_DIR/log.modules.txt
Restoring modules to system default

Due to MODULEPATH changes the following have been reloaded:
  1) ncarcompilers/1.0     2) netcdf/4.3.0


Lmod Warning: Did not find: remove

Try: "module spider remove"
Currently Loaded Modules:
  1) ncarenv/1.0        3) gnu/4.8.2            5) netcdf/4.3.0
  2) ncarbinlibs/1.1    4) ncarcompilers/1.0
```

5. You may run as csgteam (or as yourself) with the `--csgteam` option:
 ```
hpcinstall -c zlib-1.2.8
```
 **THIS WILL INSTALL in /glade/apps/opt !!!!!**

6. Notes
 1. The install directory is automatically generated and contains the name and version of the compiler module loaded, per our policies. If no compiler is loaded, only software would be used, such in `/glade/scratch/ddvento/zlib/1.2.8/`, which is the policy for non-compiled stuff, such as pure-python (non compiled) libraries.

 2. The modules are specified as comments in file `zlib-1.2.8`. This is needed for `HPCinstall` to correctly generate the `log.modules.txt` file and (especially) to correctly generate the install directory as `/glade/scratch/ddvento/zlib/1.2.8/gnu/4.8.2` (note the automatic use of the loaded module). If you are ok with not having both of these features, you may load the modules in any other way you want (e.g. command line before invoking, or executable `module such-and-such` in the script), and everything else will work just fine

 3. The install directory must not exist. This is only to prevent involuntary clobbering. It is easy to add a `--force-clobber` option to allow `HPCinstall` if desired (the current workaround is to run a `mkdir` as first line of the install script, if necessary)

 4. The number (25493 in this case) at the end of the install script log `log.zlib-1.2.8-25493.txt` is the PID of the execution.
It is added to avoid deleting the log from previous attempts. I have often found myself re-running an install script, creating an error
which I wanted to compare with the previous one, only to discover I did not have the previous ones, so I decided to not delete them!
The other logs tend to be more obvious, so to reduce clutter, I do not do the same for them.

 5. The csgteam install is interactive! It may ask a bunch of questions. We may need to discuss in the group meeting whether or not
this is desired, it can be easily changed if appropriate, as well as if we want the script to know about picnic and whatsnot
