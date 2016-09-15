import hpcinstall
import pytest

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
# note below the
#    hpcinstall.ask_confirmation_for = lambda x, y: str(x) + str(y)

def test_get_prefix_and_moduledir():
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
