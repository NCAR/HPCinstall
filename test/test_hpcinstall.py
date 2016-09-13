import hpcinstall

def test_parse_config_data():
    data = """scratch_tree: /glade/scratch
sw_install_dir: /glade/apps/opt
mod_install_dir: /glade/apps/opt/modulefiles"""
    expected = {"scratch_tree": "/glade/scratch/", "sw_install_dir": "/glade/apps/opt/", "mod_install_dir": "/glade/apps/opt/modulefiles/"}
    parsed = hpcinstall.parse_config_data(data)
    assert expected == parsed
