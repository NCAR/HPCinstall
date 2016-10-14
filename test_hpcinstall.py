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

def test_parse_config_data():
    # note some dirs have the slash some don't and the expected ones do not match
    data = ( "scratch_tree: /glade/scratch\n"
             "sw_install_dir: /glade/apps/opt/\n"
             "mod_install_dir: /glade/apps/opt/modulefiles\n")
    expected = {"scratch_tree": "/glade/scratch/", "sw_install_dir": "/glade/apps/opt", "mod_install_dir": "/glade/apps/opt/modulefiles"}
    parsed = hpcinstall.parse_config_data(data)
    for key in parsed:
        assert os.path.abspath(expected[key]) == os.path.abspath(parsed[key])

    with pytest.raises(KeyError):
        data = "useless_stuff: something"
        hpcinstall.parse_config_data(data)

    with pytest.raises(KeyError):
        data = ""
        hpcinstall.parse_config_data(data)

def test_parse_installscript_filename():
    sw = hpcinstall.parse_installscript_filename("build-mysoftware-3.2.6")
    assert sw == "mysoftware/3.2.6"
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("build-mysoftware-v3.2.6")
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("incorrect_name")
    with pytest.raises(SystemExit):
        hpcinstall.parse_installscript_filename("incorrect_name-version")

# not testing parse_command_line_arguments() since it's harmless and hard to test

# not testing ask_confirmation_for() since it's trivial and hard to test

def test_get_prefix_and_moduledir_for_user(dirs, opt, stub_os):
    # not testing file_already_exist() and corresponding forcing
    hpcinstall.os = stub_os
    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", dirs)
    assert prefix    == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/foo/1.2.3") + "/"
    assert moduledir == os.path.abspath(dirs["scratch_tree"] + stub_os.environ['USER'] + "/test_installs/modulefiles") + "/"

    stub_os.environ['INSTALL_TEST_BASEPATH'] = "/I_want_this_tree_instead"
    hpcinstall.os = stub_os
    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", dirs)
    assert prefix    == os.path.abspath("/I_want_this_tree_instead/foo/1.2.3") + "/"
    assert moduledir == os.path.abspath("/I_want_this_tree_instead/modulefiles") + "/"

def test_get_prefix_and_moduledir_for_csgteam(dirs, opt, stub_os):
    # not testing file_already_exist() and corresponding forcing
    stub_os.environ["USER"] = "csgteam"
    opt.csgteam = True
    hpcinstall.os = stub_os
    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", dirs)
    assert prefix    == os.path.abspath(dirs["sw_install_dir"] + "/foo/1.2.3/") + "/"
    assert moduledir == os.path.abspath(dirs["mod_install_dir"]) + "/"

# not testing justify() since it's only pretty-printing (no need to test behavior)

def test_prepare_variables_and_warn(opt):
    # this method is trivial, the only thing to test is that pass_env has all the variables needed
    hpcinstall.ask_confirmation_for = lambda x, y: str(x) + str(y)
    vars = hpcinstall.prepare_variables_and_warn("/glade/apps/opt", "/glade/apps/modulefiles", opt)
    for var in vars:
        assert "(" + var + ")s" in hpcinstall.pass_env, "to pass " + var + " to the environemnt, it needs to be included in hpcinstall.pass_env"

# not testing start_logging_current_session() and stop_logging_current_session() since it's trivial and hard to test

def test_subcall_helper(stub_os):
    stub_os.environ['SHELL'] = '/q/bash'
    stub_os.getcwd = lambda: "current_dir"
    hpcinstall.os = stub_os
    actual = hpcinstall._subcall_helper(modules_to_load = "module load foo/1.2.3; ml bar/4.5.6;",
                                        command = "./install-crap-7.8.9",
                                        variables = False,
                                        log = False)
    expected = '''ssh -t localhost "/q/bash -l -c 'ml purge; cd current_dir; module load foo/1.2.3; ml bar/4.5.6; ./install-crap-7.8.9'"'''
    assert actual == expected, "Failed environment setting for bash"

    stub_os.environ['SHELL'] = 'tcsh'
    actual = hpcinstall._subcall_helper(modules_to_load = "module load foo/1.2.3; ml bar/4.5.6;",
                                        command = "./install-crap-7.8.9",
                                        variables = False,
                                        log = False)
    expected = '''ssh -t localhost "tcsh -c 'ml purge; cd current_dir; module load foo/1.2.3; ml bar/4.5.6; ./install-crap-7.8.9'"'''
    assert actual == expected, "Failed environment setting for tcsh"

    actual = hpcinstall._subcall_helper(modules_to_load = "module load foo/1.2.3;",
                                        command = "./use-crap-7.8.9",
                                        variables = False,
                                        log = "random_file.log")
    expected = '''ssh -t localhost "tcsh -c 'ml purge; cd current_dir; module load foo/1.2.3; ./use-crap-7.8.9'" &> random_file.log'''
    assert actual == expected

    # not testing the variables because that is complicated and would simply test the correctness of hpcinstall.pass_env,
    # which is already tested in test_prepare_variables_and_warn()

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

def test_parse_installscript_for_modules_single():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI module load gnu\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = "module load gnu;"
    actual = hpcinstall.parse_installscript_for_modules(data)
    assert actual == expected

def test_parse_installscript_for_modules_multiple():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI module use /my/cool/directory/\n"
            "#HPCI ml gnu\n"
            "#HPCI ml python py.test\n"
            "#HPCI  export FOO=bar\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = "module use /my/cool/directory/; ml gnu; ml python py.test; export FOO=bar;"
    actual = hpcinstall.parse_installscript_for_modules(data)
    assert actual == expected

def test_parse_installscript_for_modules_comments():
    data = ("#!/bin/bash\n"
            "#\n"
            "#HPCI module use /my/cool/directory/ # I need this to load a special version of python\n"
            "#HPCI ml python py.test              # this is my special version of python \n"
            "#HPCI  export FOO=bar                # Other things\n"
            "echo Installing $HPCI_SW_NAME version $HPCI_SW_VERSION in ${HPCI_SW_DIR}.\n"
            "echo Just kidding, done nothing\n")
    print data
    expected = "module use /my/cool/directory/; ml python py.test; export FOO=bar;"
    actual = hpcinstall.parse_installscript_for_modules(data)
    assert actual == expected

def test_verify_modules_are_loadable():
    hpcinstall.verify_modules_are_loadable("ml reset;", "no file")
    with pytest.raises(SystemExit):
        hpcinstall.verify_modules_are_loadable("ml nonexistingmodule;", "no file")

def test_how_to_call_yourself(stub_os):
    hpcinstall.os = stub_os
    stub_os.environ['SHELL'] = "/bin/bash"
    args = ['./hpcinstall', 'build-example-1.2.3', '-u', 'http://example.com']
    expected = ['ssh', '-t', 'localhost', '/bin/bash', '-l', '-c',
                "'/some/strange/dir/hpcinstall build-example-1.2.3 -u http://example.com --nossh'"]
    actual = hpcinstall.how_to_call_yourself(args, "/some/strange/dir/")
    assert actual == expected

# not testing archive_in() since it's simple and hard to test
# actually all the methods which append files_to_archive[] are the trival or simple ones
# which I did not test

# not testing execute_installscript() since it's very hard to test, and relatively simple
# only simple part that is testable in execute_installscript() is it has two logs to append to files_to_archive[]
