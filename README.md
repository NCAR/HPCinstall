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

Install zlib
