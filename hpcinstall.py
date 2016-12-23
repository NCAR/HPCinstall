#!/usr/bin/env python
import argparse, os, stat, shutil, sys, subprocess, yaml, datetime, re, glob
from collections import namedtuple, OrderedDict
import tee, hashdir
import blessed
term = blessed.Terminal()

HPCi_log = "hpci.main.log"
env_log = "hpci.env.log"
module_log = "hpci.modules.log"
list_of_dirs =['scratch_tree', 'sw_install_dir', 'mod_install_dir' ]

def print_invocation_info():
    if os.environ['USER'] == "csgteam":
        running_user = "csgteam (invoked by " + os.environ['SUDO_USER'] + ")"
    else:
        running_user = os.environ['USER']
    print term.bold_magenta("On " + str(datetime.datetime.now().isoformat()) + " " + running_user)
    print term.bold_magenta("called HPCinstall from " + os.path.realpath(__file__))
    print term.bold_magenta("invoked as"),
    arguments = list(sys.argv)
    try:
        ssh_position = arguments.index("--nossh")
        arguments.pop(ssh_position)
    except ValueError:
        print >> sys.stderr, term.bold_red("INTERNAL ERROR: Wrong ssh invocation, please report it to https://github.com/NCAR/HPCinstall/issues/")
        sys.exit(2)
    try:
        arguments.pop(ssh_position) # was ssh_position + 1
    except IndexError:
        pass                        # sudo user is optional

    simple = True
    for arg in arguments:
        if " " in arg or "'" in arg or '"' in arg or "\\" in arg:
            simple = False
    if simple:
        print " ".join(arguments)
    else:
        print arguments
    print # emtpy line

def parse_config_data(yaml_data):
    default_dirs = {}
    config = yaml.safe_load(yaml_data)
    if not config:
        raise KeyError(list_of_dirs)

    for dirname in list_of_dirs:
        default_dirs[dirname] = os.path.abspath(
                                   os.path.expandvars(
                                      os.path.expanduser(
                                         config[dirname]))) + "/"
    my_env = 'environment_prefix'
    if my_env in config:
        default_dirs[my_env] = config[my_env]
    return default_dirs

def parse_installscript_filename(filename):
    sw_structure = filename.split("-")
    if len(sw_structure) < 3:
        print >> sys.stderr, term.bold_red("The software name and version must be specified as <build-software-version>. Got '" + filename + "' instead.")
        print >> sys.stderr, term.bold_red("Or you may use any filename, by including #HPCI -n software' and '#HPCI -v version' directives")
        sys.exit(1)

    try:
        version = int(sw_structure[2].replace(".", ""))
        if version < 0:
            raise ValueError()
    except ValueError:
        print >> sys.stderr, term.bold_red("The software name and version must be specified as <build-software-version>. Got '" + filename + "' instead.")
        print >> sys.stderr, term.bold_red("Or you may use any filename, by including #HPCI -n software' and '#HPCI -v version' directives")
        sys.exit(1)

    return sw_structure[1], sw_structure[2]

def validate_url(u):
    # cut and paste from django with localhost removed, no test needed
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return regex.match(u)

def parse_command_line_arguments(list_of_files):
    parser = argparse.ArgumentParser()
    parser.add_argument("install_script", metavar="install-software-ver", type=argparse.FileType('r'),
                                                               help="script in the current directory which\n" +
                                                                    "                 does the build and install (do not use\n" +
                                                                    "                 './', relative nor fully qualified paths)")
    parser.add_argument("-c", "--csgteam", action="store_true", default=False, help='Install as csgteam (default: False)')
    parser.add_argument("-f", "--force", action="store_true", default=False, help='Force overwrite of existing install (default: False)')
    parser.add_argument("-d", "--debug", action="store_true", default=False, help='Debug mode i.e. more verbose output (default: False)')
    parser.add_argument("-p", "--preserve", action="store_true", default=False, help='Preserve current environment - not valid with --csgteam (default: False)')
    parser.add_argument("--nossh", nargs='?', help=argparse.SUPPRESS) # Never manually invoke this
    # do not add a command line argument named defaults, because it will be overridden (see below)
    # do not add a command line argument named modules-to-load or modules_to_load, because it will be overridden (see below)
    # do not add a command line argument named urls, because it will be overridden (see below)
    # do not add a command line argument named tarballs, because it will be overridden (see below)
    # do not add a command line argument named prog, because it will be overridden (see below)
    # do not add a command line argument named vers, because it will be overridden (see below)
    # do not add a command line argument named sudo-user or sudo_user, because it will be overridden (see below)

    should_exit = False
    try:
        args = parser.parse_args()
    except IOError, e:
        print >> sys.stderr, term.bold_red("Troubles accessing <install-software-ver> file")
        print >> sys.stderr, e
        print
        parser.print_help()
        sys.exit(1)          # can't try most of the following

    install_script_str = args.install_script.read()
    legacy_stuff = parse_installscript_for_directives(install_script_str)
    stuff        = parse_installscript_for_directives(install_script_str, "-")
    if len(stuff) == 0:
        modules_to_load = ""
        if len(legacy_stuff) > 0:
            print >> sys.stderr, term.bold_red("Deprecation ERROR: The anonymous      '#HPCI foo'    directive is deprecated.")
            print >> sys.stderr, term.bold_red("                   Must use the named '#HPCI -x foo' directive instead.")
            should_exit = True
    else:
        if len(legacy_stuff) != len(stuff):
            print >> sys.stderr, term.bold_red("ERROR: anoymous '#HPCI foo' directives are not supported anymore")
            print >> sys.stderr, term.bold_red("       use '#HPCI -x foo' directives instead.")
            should_exit = True
        mtl_list = parse_installscript_for_directives(install_script_str, "-x")
        modules_to_load = "; ".join(mtl_list)
        if len(mtl_list) > 0:
            modules_to_load += ";"

    # Make sure user doesn't preserve environment during system install
    if args.preserve and args.csgteam:
        print >> sys.stderr, term.bold_red("ERROR: preserve environment not allowed for system installation (-c).")
        should_exit = True

    arg_sudo_user = args.nossh
    args.nossh = "--nossh" in sys.argv

    # Run test during execution step (not during initial pass)
    if args.nossh:
        if subcall(modules_to_load,            # try loading modules
                   stop_on_errors=True,        # stop at the first failure
                   log="/dev/null",            # don't output anything (output already happened in the ssh call)
                   debug=args.debug,           # use specified debug level
                  ) != 0:
            print >> sys.stderr, term.bold_red("Modules from " + args.install_script.name + " are not loadable:")
            print >> sys.stderr, modules_to_load
            should_exit = True

        env_sudo_user = os.environ.get('SUDO_USER', '')
        if arg_sudo_user is not None:
            if env_sudo_user == '':
                os.environ['SUDO_USER'] = arg_sudo_user
            else:
                if env_sudo_user != arg_sudo_user:
                    print >> sys.stderr, term.bold_red("ERROR: Can't figure out the actual user invoking csgteam")
                    should_exit = True

    config_filename = ( os.path.dirname(os.path.realpath(__file__)) + # directory where this script is
                        "/config.hpcinstall.yaml" )
    try:
        defaults = parse_config_data(open(config_filename))
        args.defaults = defaults
    except KeyError:
        print >> sys.stderr, term.bold_red("Error: " + config_filename + " does not contain the expected fields"), list_of_dirs
        should_exit = True
    except IOError as e:
        print >> sys.stderr, e
        print >> sys.stderr, term.bold_red("Cannot set " + list_of_dirs +  " -- ABORTING")
        should_exit = True

    args.modules_to_load = modules_to_load

    urls     = parse_installscript_for_directives(install_script_str, "-u")
    args.urls = urls
    tarballs = parse_installscript_for_directives(install_script_str, "-a")
    parsed_tarballs = []
    for tarball in tarballs:
        for globbed_tarball in glob.iglob(tarball):
            t = os.path.abspath(os.path.expanduser(globbed_tarball))
            parsed_tarballs.append(t)
            if not os.access(t, os.R_OK):
                print >> sys.stderr, term.bold_red("Troubles accessing file: " + t)
                should_exit = True
            else:
                list_of_files.append(t)
    args.tarballs = parsed_tarballs

    if len(urls) == 0 and len(tarballs) == 0:
        print >> sys.stderr, term.bold_red("ERROR: Either or both the '#HPCI -u URL' and '#HPCI -a source.tgz' must be provided")
        should_exit = True

    for u in urls:
        if not validate_url(u):
            print >> sys.stderr, term.bold_red("URL specified in install script " + args.install_script.name  + " is not a valid URL: " + u)
            should_exit = True

    progname = parse_installscript_for_directives(install_script_str, "-n")
    progver  = parse_installscript_for_directives(install_script_str, "-v")
    if len(progname) > 1 or len(progver) > 1:
        print >> sys.stderr, term.bold_red("'#HPCI -n software' and '#HPCI -v version' can't be specified more than once")
        should_exit = True

    if should_exit:
        print >> sys.stderr, "" # just an empty line to make the output more clear in case of errors
        parser.print_help()
        sys.exit(1)

    if len(progname) == 1 and len(progver) == 1:
        args.prog = progname[0]
        args.vers  = progver[0]
    else:
        args.prog, args.vers = parse_installscript_filename(args.install_script.name)

    return args

def ask_confirmation_for(options, msg):
    if options.csgteam:
        print msg,
        answer = sys.stdin.readline()
        print
        if answer.lower().strip() != "yes":
            print >> sys.stderr, term.bold_red("You did not say an ethusiastic 'yes', aborting...")
            sys.exit(1)

def get_prefix_and_moduledir(options, my_dep):
    default_dirs = options.defaults
    my_prog = options.prog + "/" + options.vers
    if options.csgteam:
        if os.environ['USER'] != "csgteam":
            ask_confirmation_for(options, "Should sudo into 'csgteam' to install as such. Continue anyway? ")
        prefix    = os.path.abspath(default_dirs["sw_install_dir"] + "/" + my_prog + "/" + my_dep)
        moduledir = os.path.abspath(default_dirs["mod_install_dir"])
    else:
        if "INSTALL_TEST_BASEPATH" in os.environ:
            basepath = os.environ['INSTALL_TEST_BASEPATH']
        else:
            basepath = default_dirs["scratch_tree"] + os.environ['USER'] + "/test_installs/"
        prefix    = os.path.abspath(basepath + "/" + my_prog + "/" + my_dep)
        moduledir = os.path.abspath(basepath + "/modulefiles/")

    if os.path.exists(prefix):
        if not options.force:
            print >> sys.stderr, term.bold_red("ERROR: Path already exists: " + prefix)
            sys.exit(1)
        else:
            ask_confirmation_for(options, "WARNING: " + prefix +
                                 " already exists and you speficied --force to delete it. Continue? ")
            shutil.rmtree(prefix)
    directories = namedtuple('Directories', ['prefix','basemoduledir','idepmoduledir','cdepmoduledir'])
    suffix = my_dep
    if suffix == "":
        suffix = "cdep"
    d = directories(prefix        =                 prefix + "/",
                    basemoduledir =                 moduledir + "/",
                    idepmoduledir =                 moduledir + "/idep/",
                    cdepmoduledir = os.path.abspath(moduledir + "/" + suffix) + "/" )
    return d

def prepare_variables_and_warn(dirs, options):
    variables = OrderedDict([
                 ('HPCI_SW_DIR',       dirs.prefix),
                 ('HPCI_SW_NAME',      options.prog),
                 ('HPCI_SW_VERSION',   options.vers),
                 ('HPCI_MOD_DIR',      dirs.basemoduledir),
                 ('HPCI_MOD_DIR_IDEP', dirs.idepmoduledir),
                 ('HPCI_MOD_DIR_CDEP', dirs.cdepmoduledir),
                 ])

    print term.bold_green("Setting environmental variables:")
    for key in variables:
        os.environ[key] = variables[key]
        print "{:<17}".format(key), "=", variables[key]

    ask_confirmation_for(options, "This will attempt global install in " + dirs.prefix +
                         " by running ./" + options.install_script.name + " as " + os.environ['USER'] + ". Continue? ")
    return variables

real_stdout = None
def redirect_output(log):
    global real_stdout
    if real_stdout == None:
        real_stdout = sys.stdout
    sys.stdout = open(log, 'w')

def restore_output():
    if not real_stdout == None:
        sys.stdout = real_stdout

def start_logging_current_session(files_to_archive, log=HPCi_log, continuation=False):
    if continuation:
        tee.append_out_to(log)
    else:
        tee.overwrite_out_to(log)
        files_to_archive.append(log)
def stop_logging_current_session():
    tee.close_all_files()

def wrap_command_for_stopping_on_errors(command):
    prefix = "(set -e; "
    suffix = ")"
    return prefix + command + suffix

def subcall(command, log=None, use_popen = False, debug=False, stop_on_errors=False):
    if stop_on_errors:
        command = wrap_command_for_stopping_on_errors(command)
    if log:
        command += " &> " + log
    if debug:
        print >> sys.stderr, term.bold_blue("DEBUG: " + command)
    if use_popen:
        return subprocess.Popen(command, stderr=subprocess.STDOUT, stdout = subprocess.PIPE, shell=True)
    else:
        return subprocess.call(command, shell=True)

def log_full_env(files_to_archive, module_use):
    print term.bold_green("Saving environment status in " + env_log + "..."),
    subcall(module_use + "env", env_log)
    print "Done."
    files_to_archive.append(env_log)

    print term.bold_green("Saving module list in " + module_log + "..."),
    subcall(module_use + "module list", module_log)
    print "Done.\n"
    files_to_archive.append(module_log)

def identify_compiler_mpi():
    compiler = os.environ.get('LMOD_FAMILY_COMPILER','').strip()
    mpi = ""
    try:
        if compiler:
            compiler += "/" + os.environ['LMOD_COMPILER_VERSION'].strip()
            mpi = os.environ.get('LMOD_FAMILY_MPI','').strip()
            if mpi:
                mpi += "/" + os.environ['LMOD_MPI_VERSION'].strip() + "/"
    except KeyError, ke:
        for broken_key in ke.args:
            print >> sys.stderr, term.bold_red("Error: " + broken_key + " not set")
        sys.exit(1)
    return mpi + compiler

def parse_installscript_for_directives(install_script_str, argument = ""):
    directive = "#HPCI " + argument
    executing_lines = []
    for line in install_script_str.splitlines(True):
        if line.startswith(directive):
            exe_line = line.replace(directive, "", 1).split(" #")[0].strip()
            executing_lines.append(exe_line)
#    modules_to_run = "; ".join(executing_lines)
#    if len(modules_to_run) > 0:
#        modules_to_run += ";"
    return executing_lines

def execute_installscript(options, files_to_archive, module_use):
    current_perm = os.stat(options.install_script.name)
    os.chmod(options.install_script.name, current_perm.st_mode | stat.S_IEXEC)
    print term.bold_green("Running ./" + options.install_script.name + "...")
    stop_logging_current_session()                                  # log the output of the script in a different dir
    log = "hpci." + os.path.basename(options.install_script.name)  + "-" + str(
     datetime.datetime.now().isoformat().split(".")[0].replace("-", "").replace(":", "")) + ".log" #  20161116T114145
    start_logging_current_session(files_to_archive, log=log)
    p = subcall(module_use + "./" + options.install_script.name, use_popen=True, debug=options.debug)
    process_output = " "
    while process_output != "":               # continue while the process is running, it'll be "" when EOF is reached
        process_output = p.stdout.readline()  # needs to do this instead of using subprocess.call to allow 
        print process_output,                 # 'tee' to log the process output
    p.wait()
    stop_logging_current_session()
    files_to_archive.append(log)
    start_logging_current_session(files_to_archive, continuation=True)
    print term.bold_green("Done running ./" + options.install_script.name + " - exited with code " + str(p.returncode))
    if p.returncode != 0:
        fake_opt = lambda: None
        fake_opt.csgteam = True
        ask_confirmation_for(fake_opt, "Running " + options.install_script.name + " failed. Archive logs anyway? ")
    files_to_archive.append(options.install_script.name)

def archive_in(prefix, files_to_archive):
    build_dir = prefix + "/BUILD_DIR/"
    if not os.path.exists(build_dir):
    	os.makedirs(build_dir)
    for somefile in files_to_archive:
        if os.path.isfile(somefile):
            shutil.copyfile(somefile, build_dir + os.path.basename(somefile))
        else:
            shutil.copytree(somefile, build_dir + os.path.basename(somefile), symlinks=True)

def how_to_call_yourself(args, yourself, pwd, opt):
    # Assuming bash makes things MUCH easier, dropping support for other shells
    # (it is not less general, since bash can call tcsh, csh, ksh, python, etc.)
    # Should support for other shells be added, needs to be done at least in
    # wrap_command_for_stopping_on_errors() too.
    shell = ["/bin/bash"] #os.environ['SHELL']
    if "bash" in shell[0]:
        shell.append('-l')
    shell.append('-c')
    args_copy = list(args)
    args_copy[0] = os.path.abspath(yourself + "/hpcinstall")
    reset_env_hack = "--nossh " + os.environ.get('SUDO_USER', '')
    args_copy.append(reset_env_hack.strip())
    comb_cmd = opt.modules_to_load + " cd " + pwd + "; " + " ".join(args_copy)

    if opt.preserve:
        new_invocation = comb_cmd
        use_shell = True
    else:
        module_prefix = "ml purge; "
        if opt.defaults.get('environment_prefix'):
            module_prefix += opt.defaults['environment_prefix'] + "; "
        new_invocation = ["ssh","-t","localhost"] + shell + ["'" + module_prefix + comb_cmd + "'"]
        use_shell = False
    
    return new_invocation, use_shell

# execution starts here
if __name__ == "__main__":
    files_to_archive = []
    options = parse_command_line_arguments(files_to_archive)
    script_dir = os.path.dirname(os.path.realpath(__file__)) # directory where this script is

    # hack to reset the environment -- assume everything into the environment has been
    # reset, and continue executing "as is" the following `if` did not exist.
    if not options.nossh:
        exe_cmd, use_shell = how_to_call_yourself(sys.argv, script_dir, os.getcwd(), options)
        sys.exit(subprocess.call(exe_cmd, shell = use_shell))

    comp_mpi = identify_compiler_mpi()
    dirs = get_prefix_and_moduledir(options, comp_mpi)
    module_use = ""
#   TODO: figure out if this has any value
#    if not dirs.moduledir in os.environ['MODULEPATH']:
#        module_use = "module use " + dirs.moduledir + "; "
    log_full_env(files_to_archive, module_use)
    start_logging_current_session(files_to_archive)
    print_invocation_info()
    prepare_variables_and_warn(dirs, options)
    execute_installscript(options, files_to_archive, module_use)
    for tarball in options.tarballs:
        print term.blue("Archiving file: " + tarball)
    for u in options.urls:
        print term.blue("For more details about this code, see URL: " + u)
    print term.bold_green("Hashdir:"), hashdir.hashdir(dirs.prefix), os.path.abspath(os.path.expanduser(dirs.prefix))
    stop_logging_current_session()
    hashlog = "hpci.fileinfo.log"
    redirect_output(hashlog)
    hashdir.hashdir(dirs.prefix, verbose=True)
    restore_output()
    files_to_archive.append(hashlog)
    archive_in(dirs.prefix, files_to_archive)
