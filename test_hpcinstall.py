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

@pytest.fixture
def dirs():                    # stub dirs
    dirs = {}
    dirs["sw_install_dir"]  = "/glade/apps/"
    dirs["mod_install_dir"] = "/glade/mods/"
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
    return opt

@pytest.fixture
def stub_os():              # stub os, replacing "import os"
    stub_os = lambda: None
    stub_env = {}
    stub_env["USER"] = "somebody"
    stub_os.environ = stub_env
    stub_os.path = os.path
    return stub_os

# not testing print_invocation_info() since it's harmless and hard to test

def test_essential_config_data():
    # note some dirs have the slash some don't and the expected ones do not match
    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_dir: /glade/apps/opt/\n"
             "mod_install_dir: /glade/apps/opt/modulefiles\n")
    expected = {"scratch_tree": "/glade/scratch/", "sw_install_dir": "/glade/apps/opt", "mod_install_dir": "/glade/apps/opt/modulefiles"}
    parsed = hpcinstall.parse_config_data(data)
    for key in parsed:
        assert os.path.abspath(expected[key]) == os.path.abspath(parsed[key])

def test_optional_config_data():
    # note some dirs have the slash some don't and the expected ones do not match
    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_dir: /glade/apps/opt/\n"
             "environment_prefix: ml python\n"
             "mod_install_dir: /glade/apps/opt/modulefiles\n")
    expected = {"scratch_tree": "/glade/scratch/", "sw_install_dir": "/glade/apps/opt", "mod_install_dir": "/glade/apps/opt/modulefiles", "environment_prefix": "ml python"}
    parsed = hpcinstall.parse_config_data(data)
    for key in expected:
        assert os.path.abspath(expected[key]) == os.path.abspath(parsed[key])

def test_missing_config_data():
    # note some dirs have the slash some don't and the expected ones do not match
    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_dir: /glade/apps/opt/\n")                      # missing directory
    with pytest.raises(KeyError):
        hpcinstall.parse_config_data(data)

    with pytest.raises(KeyError):
        data = "mod_install_dir: /glade/apps/opt/modulefiles\n"         # missing directories
        hpcinstall.parse_config_data(data)

def test_parse_installscript_filename():
    sw = hpcinstall.parse_installscript_filename("build-mysoftware-3.2.6")
    assert sw == "mysoftware/3.2.6"
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
    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", "gnu/4.4.1", dirs)
    assert prefix    == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/foo/1.2.3/gnu/4.4.1") + "/"
    assert moduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles") + "/"

    stub_os.environ['INSTALL_TEST_BASEPATH'] = "/I_want_this_tree_instead"
    hpcinstall.os = stub_os
    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", "", dirs)
    assert prefix    == os.path.abspath("/I_want_this_tree_instead/foo/1.2.3") + "/"
    assert moduledir == os.path.abspath("/I_want_this_tree_instead/modulefiles") + "/"

def test_get_prefix_and_moduledir_for_csgteam(dirs, opt, stub_os):
    # not testing file_already_exist() and corresponding forcing
    stub_os.environ["USER"] = "csgteam"
    opt.csgteam = True
    hpcinstall.os = stub_os
    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", "", dirs)
    assert prefix    == os.path.abspath(dirs["sw_install_dir"] + "/foo/1.2.3/") + "/"
    assert moduledir == os.path.abspath(dirs["mod_install_dir"]) + "/"

# not testing justify() since it's only pretty-printing (no need to test behavior)

# not testing prepare_variables_and_warn() since it's trivial

# not testing start_logging_current_session() and stop_logging_current_session() since it's trivial and hard to test

# not testing log_full_env() since it's trivial and hard to test

# not testing string_or_file() since it's trivial and hard to test

def test_identify_compiler_mpi_none(stub_os):
    hpcinstall.os = stub_os                          # no environmental variables
    comp_mpi = hpcinstall.identify_compiler_mpi()
    assert comp_mpi == ''

def test_identify_compiler_only(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['LMOD_FAMILY_COMPILER'] = "intel"
    stub_os.environ['LMOD_COMPILER_VERSION'] = "1.2.3"
    comp_mpi = hpcinstall.identify_compiler_mpi()
    assert comp_mpi == 'intel/1.2.3'

def test_identify_compiler_no_version(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['LMOD_FAMILY_COMPILER'] = "intel"
    with pytest.raises(SystemExit):
        comp_mpi = hpcinstall.identify_compiler_mpi()

def test_identify_compiler_and_mpi(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['LMOD_FAMILY_COMPILER'] = "intel"
    stub_os.environ['LMOD_COMPILER_VERSION'] = "1.2.3"
    stub_os.environ['LMOD_FAMILY_MPI'] = "mpt"
    stub_os.environ['LMOD_MPI_VERSION'] = "4.5.6"
    comp_mpi = hpcinstall.identify_compiler_mpi()
    assert comp_mpi == 'intel/1.2.3/mpt/4.5.6'

def test_identify_compiler_and_mpi_no_version(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['LMOD_FAMILY_COMPILER'] = "intel"
    stub_os.environ['LMOD_FAMILY_MPI'] = "mpt"
    with pytest.raises(SystemExit):
        comp_mpi = hpcinstall.identify_compiler_mpi()
    stub_os.environ['LMOD_COMPILER_VERSION'] = "1.2.3"
    with pytest.raises(SystemExit):
        comp_mpi = hpcinstall.identify_compiler_mpi()

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

def test_how_to_call_yourself(stub_os, opt):
    hpcinstall.os = stub_os
    opt.modules_to_load = "ml python; ml gnu;"
    stub_os.environ['SHELL'] = "/bin/bash"
    args = ['./hpcinstall', 'build-example-1.2.3']
    expected = (['ssh', '-t', 'localhost', '/bin/bash', '-l', '-c',
                "'ml purge; ml python; ml gnu; cd /the/pwd/; /some/strange/dir/hpcinstall build-example-1.2.3 --nossh'"], False)
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/", "/the/pwd/", opt)
    assert actual == expected

def test_how_to_call_yourself_with_preserve(stub_os, opt):
    hpcinstall.os = stub_os
    opt.modules_to_load = "ml python; ml gnu;"
    opt.preserve = True
    stub_os.environ['SHELL'] = "/bin/bash"
    args = ['./hpcinstall', 'build-example-1.2.3', '-c']
    expected = ("ml python; ml gnu; cd /the/pwd/; /some/strange/dir/hpcinstall build-example-1.2.3 -c --nossh", True)
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/", "/the/pwd/", opt)
    assert actual == expected

def test_how_to_call_yourself_with_environment(stub_os, opt):
    hpcinstall.os = stub_os
    opt.modules_to_load = "ml intel;"
    opt.defaults['environment_prefix'] = "ml python"
    stub_os.environ['SHELL'] = "/bin/bash"
    args = ['./hpcinstall', 'build-example-1.2.3']
    expected = (['ssh', '-t', 'localhost', '/bin/bash', '-l', '-c',
                "'ml purge; ml python; ml intel; cd /the/pwd/; /some/strange/dir/hpcinstall build-example-1.2.3 --nossh'"], False)
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/", "/the/pwd/", opt)
    assert actual == expected

def test_wrap_command_for_ksh(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['SHELL'] = "/bin/ksh"
    actual = hpcinstall.wrap_command_for_stopping_on_errors("ml gnu; ml broken; ml mpt")
    expected = "(set -e; ml gnu; ml broken; ml mpt)"
    assert actual == expected

def test_wrap_command_for_bash(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['SHELL'] = "/bin/bash"
    actual = hpcinstall.wrap_command_for_stopping_on_errors("ml gnu; ml broken; ml mpt")
    expected = "(set -e; ml gnu; ml broken; ml mpt)"
    assert actual == expected

def test_wrap_command_for_tcsh(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['SHELL'] = "/bin/tcsh"
    actual = hpcinstall.wrap_command_for_stopping_on_errors("ml gnu; ml broken; ml mpt")
    expected = "/bin/tcsh -e -c 'ml gnu; ml broken; ml mpt'"
    assert actual == expected

def test_wrap_command_for_csh(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['SHELL'] = "/bin/csh"
    actual = hpcinstall.wrap_command_for_stopping_on_errors("ml gnu; ml broken; ml mpt")
    expected = "/bin/csh -e -c 'ml gnu; ml broken; ml mpt'"
    assert actual == expected

# not testing archive_in() since it's simple and hard to test
# actually all the methods which append files_to_archive[] are the trival or simple ones
# which I did not test

# not testing execute_installscript() since it's very hard to test, and relatively simple
# only simple part that is testable in execute_installscript() is it has two logs to append to files_to_archive[]
