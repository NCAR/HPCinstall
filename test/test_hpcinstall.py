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
