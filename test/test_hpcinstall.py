import hpcinstall
import pytest

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

# not testing "print_invocation_info" since it's harmless and hard to test

def test_parse_config_data():
    data = """scratch_tree: /glade/scratch
sw_install_dir: /glade/apps/opt
mod_install_dir: /glade/apps/opt/modulefiles"""
    expected = {"scratch_tree": "/glade/scratch/", "sw_install_dir": "/glade/apps/opt/", "mod_install_dir": "/glade/apps/opt/modulefiles/"}
    parsed = hpcinstall.parse_config_data(data)
    assert expected == parsed

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

# not testing "parse_command_line_arguments" since it's harmless and hard to test

# not testing "ask_confirmation_for" since it's trivial and hard to test

def test_get_prefix_and_moduledir():

    # stub options
    opt = lambda: None
    opt.csgteam = False     # not csgteam
    opt.force = True        # ignore actual paths on the filesystems

    # stub dirs
    dirs = {}
    dirs["sw_install_dir"]  = "/glade/apps"
    dirs["mod_install_dir"] = "/glade/mods"
    dirs["scratch_tree"]    = "/glade/scra"

    # stub os
    stub_os = lambda: None
    stub_env = {}
    stub_env["USER"] = "somebody"

    prefix, moduledir = hpcinstall.get_prefix_and_moduledir(opt, "foo/1.2.3", dirs)

    assert prefix    == "/glade/apps/foo/1.2.3"
    assert moduledir == "/glade/mods/foo"
    raise Exception("Too complicated method to test. Simplify?")

def test_prepare_variables_and_warn():
    # this method is trivial, the only thing to test is that pass_env has all the variables needed
    hpcinstall.ask_confirmation_for = lambda x, y: str(x) + str(y)
    vars = hpcinstall.prepare_variables_and_warn("/glade/apps/opt", "/glade/apps/modulefiles", None, "build-mysoftware-1.2.3")
    for var in vars:
        assert "(" + var + ")s" in hpcinstall.pass_env, "to pass " + var + " to the environemnt, it needs to be included in hpcinstall.pass_env"

# not testing "start_logging_current_session" and "stop_logging_current_session" since it's trivial and hard to test

def test_subcall():
    raise Exception("Too complicated method to test. Simplify?")

def test_parse_compiler_and_log_full_env():
    raise Exception("Too complicated method to test. Simplify?")
