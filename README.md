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

## Sample use

###Install zlib
According to [this document](https://docs.google.com/spreadsheets/d/1BxkASYb_Tdt7G-idwD7rScTLT1wj4rovwbZQ-L6Aguk/edit#gid=0) I should evaluate build/install tools by trying them on zlib, so here it is.

1. Download the software to be installed. After some googling `wget http://zlib.net/zlib-1.2.8.tar.gz` is the solution. I don't think it's worth saving this in the install script (URL often changes), so I don't. Nothing prevents you to think and do differently.
2. Anywhere in the filesystem (`HPCinstall` does not care) create a directory and run `tar xf zlib-1.2.8.tar.gz` into it. I don't think this is worth saving this in the install script, so I don't. Nothing prevents you to think and do differently.
3. Go into the untarred directory and create a file named `name-version` or `name-version-compiler-version`. So in this case I run `touch zlib-1.2.8-gnu-6.1.0`. 
4. At this point you can start using `HPCinstall` by invoking it using the file we just created as argument. So if `hpcinstall` is in your `PATH` you can run `hpcinstall zlib-1.2.8-gnu-6.1.0` otherwise run `/absolute/or/relative/path/hpcinstall zlib-1.2.8-gnu-6.1.0` (either one will work, `HPCinstall` does not require anything...) 
5. Now, the install script `zlib-1.2.8-gnu-6.1.0` we created at 3 is empty, so it does nothing, but `HPCinstall` still does something with it. The output on the script of running `hpcinstall zlib-1.2.8-gnu-6.1.0` should be something like:

Setting environmental variables:
```
INSTALL_DIR     = /glade/scratch/ddvento/zlib/1.2.8/gnu/6.1.0
MODULE_FILENAME = /glade/scratch/modulefiles/zlib/1.2.8.lua

Saving environment status in log.env.txt ... Done.
Saving module list in log.modules.txt ... Done.

Running ./zlib-1.2.8-gnu-6.1.0 ...
Done running ./zlib-1.2.8-gnu-6.1.0 - exited with code 0
```
Let's look at what `HPCinstall` has done in the current directory:

```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls -lt | head
total 1088
-rw-rw-r--  1 ddvento consult   348 Jul 29 20:45 log.hpcinstall.txt
-rw-rw-r--  1 ddvento consult     0 Jul 29 20:45 log.zlib-1.2.8-gnu-6.1.023975.txt
-rw-rw-r--  1 ddvento consult   151 Jul 29 20:45 log.modules.txt
-rw-rw-r--  1 ddvento consult  7846 Jul 29 20:45 log.env.txt
-rwxrw-r--  1 ddvento consult     0 Jul 29 15:55 zlib-1.2.8-gnu-6.1.0
-rw-r--r--  1 ddvento consult 76402 Apr 28  2013 ChangeLog
-rw-r--r--  1 ddvento consult  4236 Apr 28  2013 zlib.3
-rw-r--r--  1 ddvento consult  8734 Apr 28  2013 zlib.3.pdf
-rw-r--r--  1 ddvento consult 87883 Apr 28  2013 zlib.h
```
and also let's look at `/glade/scratch/ddvento/zlib/1.2.8/gnu/6.1.0`

```
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls /glade/scratch/ddvento/zlib/1.2.8/gnu/6.1.0
BUILD_DIR
ddvento@yslogin6 /glade/scratch/ddvento/build/zlib-1.2.8 $ ls /glade/scratch/ddvento/zlib/1.2.8/gnu/6.1.0/BUILD_DIR/ -l
total 256
-rw-rw-r-- 1 ddvento consult 6948 Jul 29 20:45 hpcinstall
-rw-rw-r-- 1 ddvento consult 7846 Jul 29 20:45 log.env.txt
-rw-rw-r-- 1 ddvento consult  348 Jul 29 20:45 log.hpcinstall.txt
-rw-rw-r-- 1 ddvento consult  151 Jul 29 20:45 log.modules.txt
-rw-rw-r-- 1 ddvento consult    0 Jul 29 20:45 log.zlib-1.2.8-gnu-6.1.023975.txt
```
So `HPCinstall` has done the following:
 - created the four `log.*.txt` files in current directory
 - made the `zlib-1.2.8-gnu-6.1.0` script executable (we did not make so in 3. when we created it)
 - created the directory `/glade/scratch/ddvento/zlib/1.2.8/gnu/6.1.0/BUILD_DIR/` (and all the necessary parents)
 - copied in the directory of the previous bullet the four `log.*.txt` plus the `hpcinstall` script itself.

Everything should be self-documenting, but let's look at the content of the four files

6. Let's start with the environment `log.env.txt`
