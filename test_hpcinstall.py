import hpcinstall
import pytest, os

@pytest.yield_fixture(autouse = True) # call this method around each test method
def run_before_after():
    # before part -- save the stuff that I'll be stubbing out
    old_os = hpcinstall.os
    old_ask = hpcinstall.ask_confirmation_for

    # run tests
    yield

    # after part - restore the original stuff
    hpcinstall.os = old_os
    hpcinstall.ask_confirmation_for = old_ask

from contextlib import contextmanager
@contextmanager
def my_env_variables(stub_os):
    overwritten = {}
    for var in stub_os.environ:
        if var in os.environ:
            print "Saving", var, "currently", os.environ[var] + ".",
            overwritten[var] = os.environ[var]
        else:
            print "No", var, "to save.",
        print "Setting", var, "to", stub_os.environ[var]
        os.environ[var] = stub_os.environ[var]
    try:
        yield stub_os
    finally:
        print "---"
        for var in stub_os.environ:
            print "evaluating", var, "...",
            if var in overwritten:
                print "restoring"
                os.environ[var] = overwritten[var]
            else:
                print "deleting"
                del os.environ[var]

@pytest.fixture
def dirs():                    # stub dirs
    dirs = {}
    dirs["sw_install_dir"]  = "/glade/apps/"
    dirs["sw_install_struct"] = "${COMP}/${COMP_VER}/${MPI}/${MPI_VER}"
    dirs["mod_install_dir"] = "/glade/mods/"
    dirs["mod_install_struct"] = "${MPI}/${MPI_VER}/${COMP}/${COMP_VER}"
    dirs["scratch_tree"]    = "/glade/scra/"
    return dirs

@pytest.fixture
def opt():                                                          # stub options
    opt = lambda: None
    opt.csgteam = False                                             # not csgteam
    opt.force = True                                                # ignore actual paths on the filesystems
    opt.preserve = False                                            # do not preserve (unless asked)
    opt.defaults = {}                                               # do not use any defaults
    install_script = lambda : None                                  # fake file object
    install_script.name = "build-mysoftware-1.2.3"                  # with this filename
    opt.install_script = install_script                             # stuffed as an option
    # make sure no script repo by default
    return opt

@pytest.fixture
def stub_os():              # stub os, replacing "import os"
    stub_os = lambda: None
    stub_env = {}
    stub_env["USER"] = "somebody"
    stub_os.environ = stub_env
    stub_os.path = os.path
    return stub_os

def test_howto_push_to_github(opt):
    # no script repo by default, should cause no git pushing
    assert hpcinstall.howto_push_to_github(opt, "somedir") == ""

    opt.defaults['script_repo'] = "~/.hpcinstall/ys-install-scripts"
    #opt.defaults['git_cmd'] = "/some/odd/path/git"
    opt.install_script.name = "netcdf-mpi-1.2.3"
    opt.prog = "netcdf-mpi"
    opt.vers = "1.2.3"
    dirs = "/software/1.2.3/mpt/4.1.5/intel/16.0.3/"
    expected = ("mkdir -p ~/.hpcinstall/ys-install-scripts/software/1.2.3/mpt/4.1.5/intel/16.0.3/ && "
                "cp netcdf-mpi-1.2.3 ~/.hpcinstall/ys-install-scripts/software/1.2.3/mpt/4.1.5/intel/16.0.3/ && "
                "cd ~/.hpcinstall/ys-install-scripts && "
                "git add software/1.2.3/mpt/4.1.5/intel/16.0.3/ && "
                'git -c "user.name=${SUDO_USER}" -c "user.email=${SUDO_USER}" commit -m "netcdf-mpi v1.2.3 install in `hostname` on `date`" && '
                "git push")
    assert hpcinstall.howto_push_to_github(opt, dirs) == expected

# not testing print_invocation_info() since it's harmless and hard to test

def test_config_data_dirs():
    # note some dirs have the slash some don't and the expected ones do not match
    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_dir: /glade/apps/opt/\n"
             "sw_install_struct: ${C}/${CV}/${M}/${MV}\n"
             "mod_install_dir: /glade/apps/opt/modulefiles\n"
             "mod_install_struct: ${M}/${MV}/${C}/${CV}\n"
             )
    expected = {"scratch_tree": "/glade/scratch/",
                "sw_install_dir": "/glade/apps/opt/",
                "sw_install_struct": "${C}/${CV}/${M}/${MV}",
                "mod_install_dir": "/glade/apps/opt/modulefiles/",
                "mod_install_struct": "${M}/${MV}/${C}/${CV}"
               }
    parsed = hpcinstall.parse_config_data(data)
    assert len(expected) == len(parsed)
    for key in parsed:
        print key
        assert expected[key] == parsed[key]

def test_config_data_environment():
    data = ( "scratch_tree: /glade/scratch\n"       # dirs and struct are mandatory so including them anyway
             "sw_install_dir: /glade/apps/opt\n"
             "sw_install_struct: ${C}/${CV}/${M}/${MV}\n"
             "python_cmd: /path/to/my/python\n"
             "mod_install_dir: /glade/apps/opt/modulefiles\n"
             "mod_install_struct: ${M}/${MV}/${C}/${CV}\n"
             "git_cmd: /path/to/my/git\n"
             "script_repo: ~csgteam/.hpcinstall/chey-install-scripts\n")
    expected = {"scratch_tree":    "/glade/scratch/",
                "sw_install_dir":  "/glade/apps/opt/",
                "sw_install_struct": "${C}/${CV}/${M}/${MV}",
                "mod_install_dir": "/glade/apps/opt/modulefiles/",
                "mod_install_struct": "${M}/${MV}/${C}/${CV}",
                "script_repo":     "~csgteam/.hpcinstall/chey-install-scripts",
                "git_cmd":         "/path/to/my/git",
                "python_cmd": "/path/to/my/python"}
    parsed = hpcinstall.parse_config_data(data)
    assert len(expected) == len(parsed)
    for key in expected:
        print key
        assert expected[key] == parsed[key]

def test_missing_config_data():
    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_struct: abc\n"
             "mod_install_struct: xyz\n"
             "sw_install_dir: /glade/apps/opt/\n")                      # missing directory
    with pytest.raises(KeyError):
        hpcinstall.parse_config_data(data)

    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_dir: bar\n"
             "mod_install_struct: xyz\n"
             "sw_install_dir: /glade/apps/opt/\n")                      # missing struct
    with pytest.raises(KeyError):
        hpcinstall.parse_config_data(data)

    with pytest.raises(KeyError):
        data = "mod_install_dir: /glade/apps/opt/modulefiles\n"         # missing lots
        hpcinstall.parse_config_data(data)

    data = ( "scratch_tree: foo\n"                # dirs and struct are mandatory so including them
             "sw_install_dir: bar\n"              # everything else should be optional
             "mod_install_dir: baz\n"
             "sw_install_struct: abc\n"
             "mod_install_struct: xyz\n"
           )
    parsed = hpcinstall.parse_config_data(data)
    assert parsed is not None
    # not asserting anything here, assertions are in test_config_data_environment()

def test_parse_installscript_filename():
    sw, ver = hpcinstall.parse_installscript_filename("build-mysoftware-3.2.6")
    assert (sw, ver) == ("mysoftware", "3.2.6")
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("incorrect_name")
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("incorrect_name-version")
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("build-mysoftware-v3.2.6")
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("build-netcdf-mpi-1.2.3")

# not testing parse_command_line_arguments() since it's harmless and hard to test

# not testing ask_confirmation_for() since it's trivial and hard to test

def test_get_prefix_and_moduledir_for_user(dirs, opt, stub_os):
    # not testing file_already_exist() and corresponding forcing
    hpcinstall.os = stub_os
    opt.prog = "foo"
    opt.vers = "1.2.3"
    opt.defaults = dirs
    d = hpcinstall.get_prefix_and_moduledir(opt, "gnu/4.4.1", "gnu/4.4.1")
    assert d.prefix        == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/foo/1.2.3/gnu/4.4.1") + "/"
    assert d.basemoduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles") + "/"
    assert d.idepmoduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles/idep") + "/"
    assert d.cdepmoduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles/gnu/4.4.1") + "/"
    assert d.relativeprefix == "/foo/1.2.3/gnu/4.4.1/"

    d = hpcinstall.get_prefix_and_moduledir(opt, "gnu/4.4.1/mpi/1.2.3", "mpi/1.2.3/gnu/4.4.1")
    assert d.prefix        == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/foo/1.2.3/gnu/4.4.1/mpi/1.2.3") + "/"
    assert d.basemoduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles") + "/"
    assert d.idepmoduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles/idep") + "/"
    assert d.cdepmoduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles/mpi/1.2.3/gnu/4.4.1") + "/"
    assert d.relativeprefix == "/foo/1.2.3/gnu/4.4.1/mpi/1.2.3/"

    stub_os.environ['INSTALL_TEST_BASEPATH'] = "/I_want_this_tree_instead"
    hpcinstall.os = stub_os
    d = hpcinstall.get_prefix_and_moduledir(opt, "", "")
    assert d.prefix        == os.path.abspath("/I_want_this_tree_instead/foo/1.2.3") + "/"
    assert d.basemoduledir == os.path.abspath("/I_want_this_tree_instead/modulefiles") + "/"
    assert d.idepmoduledir == os.path.abspath("/I_want_this_tree_instead/modulefiles/idep") + "/"
    assert d.cdepmoduledir == "not_compiler_dependent"
    assert d.relativeprefix == "/foo/1.2.3/"

def test_get_prefix_and_moduledir_for_csgteam(dirs, opt, stub_os):
    # not testing file_already_exist() and corresponding forcing
    stub_os.environ["USER"] = "csgteam"
    opt.prog = "foo"
    opt.vers = "1.2.3"
    opt.defaults = dirs
    opt.csgteam = True
    hpcinstall.os = stub_os
    d = hpcinstall.get_prefix_and_moduledir(opt, "", "")
    assert d.prefix        == os.path.abspath(dirs["sw_install_dir"] + "/foo/1.2.3/") + "/"
    assert d.basemoduledir == os.path.abspath(dirs["mod_install_dir"]) + "/"
    assert d.idepmoduledir == os.path.abspath(dirs["mod_install_dir"]) + "/idep/"
    assert d.cdepmoduledir == "not_compiler_dependent"

# not testing justify() since it's only pretty-printing (no need to test behavior)

# not testing prepare_variables_and_warn() since it's trivial

# not testing start_logging_current_session() and stop_logging_current_session() since it's trivial and hard to test

# not testing log_full_env() since it's trivial and hard to test

# not testing string_or_file() since it's trivial and hard to test

def test_identify_compiler_mpi(stub_os, opt, dirs):
    hpcinstall.os = stub_os                          # no environmental variables
    opt.defaults = dirs
    bin_comp_mpi, mod_comp_mpi = hpcinstall.identify_compiler_mpi(opt)
    assert bin_comp_mpi == ''
    assert mod_comp_mpi == ''

    stub_os.environ['COMP'] = 'intel'
    stub_os.environ['COMP_VER'] = '16.0.1'
    stub_os.environ['MPI'] = 'mpt'
    stub_os.environ['MPI_VER'] = '2.15b'
# the following not strictly needed, but don't want to rely on default's dir
    dirs["sw_install_struct"] = "${COMP}/${COMP_VER}/${MPI}/${MPI_VER}"
    dirs["mod_install_struct"] = "${MPI}/${MPI_VER}/${COMP}/${COMP_VER}"
    opt.defaults = dirs
    with my_env_variables(stub_os):
        bin_comp_mpi, mod_comp_mpi = hpcinstall.identify_compiler_mpi(opt)
    assert bin_comp_mpi == 'intel/16.0.1/mpt/2.15b'
    assert mod_comp_mpi == 'mpt/2.15b/intel/16.0.1'

def test_verify_compiler_mpi_none(stub_os, opt, dirs):
    hpcinstall.os = stub_os                          # no environmental variables
    opt.defaults = dirs
    hpcinstall.verify_compiler_mpi(opt)

def test_verify_compiler_no_version(stub_os, opt, dirs):
    hpcinstall.os = stub_os
    stub_os.environ['LMOD_FAMILY_COMPILER'] = "intel"
    opt.defaults = dirs
    with pytest.raises(SystemExit):
        hpcinstall.verify_compiler_mpi(opt)

def test_verify_compiler_and_mpi_no_version(stub_os, opt, dirs):
    hpcinstall.os = stub_os
    stub_os.environ['LMOD_FAMILY_COMPILER'] = "intel"
    stub_os.environ['LMOD_FAMILY_MPI'] = "mpt"
    opt.defaults = dirs
    with pytest.raises(SystemExit):
        hpcinstall.verify_compiler_mpi(opt)
    stub_os.environ['LMOD_COMPILER_VERSION'] = "1.2.3"
    with pytest.raises(SystemExit):
        hpcinstall.verify_compiler_mpi(opt)

def test_parse_installscript_for_modules_noprereq():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI -x module load gnu\n"
            "#HPCI -l ncarcompilers/1.0 ncarenv\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")

    mtl, prereq = hpcinstall.parse_installscript_for_modules(data)
    assert mtl == "module purge; module load gnu; ml ncarcompilers/1.0 ncarenv; "
    assert prereq == ""

def test_parse_installscript_for_modules_prereq_multiple_lines():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI -x module load gnu\n"
            "#HPCI -x export FOO=bar\n"
            "#HPCI -l ncarcompilers/1.0 ncarenv\n"
            "#HPCI -l netcdf\n"
            "#HPCI -p python numpy/12.0.3\n"
            "#HPCI -p matplotlib\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")

    mtl, prereq = hpcinstall.parse_installscript_for_modules(data)
    assert mtl == "module purge; module load gnu; export FOO=bar; ml ncarcompilers/1.0 ncarenv netcdf; ml python numpy/12.0.3 matplotlib; "
    assert prereq == '"python","numpy/12.0.3","matplotlib"'

def test_parse_installscript_for_modules_prereq():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI -x module load gnu\n"
            "#HPCI -l ncarcompilers/1.0 ncarenv\n"
            "#HPCI -p python numpy/12.0.3\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")

    mtl, prereq = hpcinstall.parse_installscript_for_modules(data)
    assert mtl == "module purge; module load gnu; ml ncarcompilers/1.0 ncarenv; ml python numpy/12.0.3; "
    assert prereq == '"python","numpy/12.0.3"'

def test_parse_installscript_for_modules_legacy():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI module load gnu\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = ["module load gnu"]
    actual = hpcinstall.parse_installscript_for_directives(data)
    assert actual == expected

def test_parse_installscript_for_modules_single():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI -x module load gnu\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = ["module load gnu"]
    actual = hpcinstall.parse_installscript_for_directives(data, "-x")
    assert actual == expected

def test_parse_installscript_for_modules_multiple():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI -x module use /my/cool/directory/\n"
            "#HPCI -x ml gnu\n"
            "#HPCI -x ml python py.test\n"
            "#HPCI -x export FOO=bar\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = ["module use /my/cool/directory/", "ml gnu", "ml python py.test", "export FOO=bar"]
    actual = hpcinstall.parse_installscript_for_directives(data, "-x")
    assert actual == expected

def test_parse_installscript_for_modules_comments():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI -x module use /my/cool/directory/ # I need this to load a special version of python\n"
            "#HPCI -x ml python py.test              # this is my special version of python \n"
            "#HPCI -x  export FOO=bar                # Other things\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = ["module use /my/cool/directory/", "ml python py.test", "export FOO=bar"]
    actual = hpcinstall.parse_installscript_for_directives(data, "-x")
    assert actual == expected

def test_how_to_call_yourself(opt):
    opt.modules_to_load = "ml python; ml gnu;"
    args = ['./hpcinstall', 'build-example-1.2.3']
    expected = (['ssh', '-t', 'localhost', '/bin/bash', '-l', '-c',
                "'ml purge; ml python; ml gnu; cd /the/pwd/; /some/strange/dir/hpcinstall build-example-1.2.3 --nossh'"], False)
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/", "/the/pwd/", opt)
    assert actual == expected

def test_how_to_call_yourself_with_preserve(opt):
    opt.modules_to_load = "ml python; ml gnu;"
    opt.preserve = True
    args = ['./hpcinstall', 'build-example-1.2.3', '-c']
    expected = ("ml python; ml gnu; cd /the/pwd/; /some/strange/dir/hpcinstall build-example-1.2.3 -c --nossh", True)
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/", "/the/pwd/", opt)
    assert actual == expected

def test_how_to_call_yourself_with_environment(opt):
    opt.modules_to_load = "ml intel;"
    opt.defaults['python_cmd'] = "/the/good/python"
    args = ['./hpcinstall', 'build-example-1.2.3']
    expected = (['ssh', '-t', 'localhost', '/bin/bash', '-l', '-c',
                "'ml purge; ml intel; cd /the/pwd/; /the/good/python /some/strange/dir/hpcinstall build-example-1.2.3 --nossh'"], False)
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/", "/the/pwd/", opt)
    assert actual == expected

def test_wrap_command():
    actual = hpcinstall.wrap_command_for_stopping_on_errors("ml gnu; ml broken; ml mpt")
    expected = "(set -e; ml gnu; ml broken; ml mpt)"
    assert actual == expected

# not testing archive_in() since it's simple and hard to test
# actually all the methods which append files_to_archive[] are the trival or simple ones
# which I did not test

# not testing execute_installscript() since it's very hard to test, and relatively simple
# only simple part that is testable in execute_installscript() is it has two logs to append to files_to_archive[]
