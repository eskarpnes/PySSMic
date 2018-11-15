import os
from definitions import ROOT_DIR
from simulator import Simulator


def test_simulator():
    config = {
        "neighbourhood": "test",
        "timefactor": 0.000001,
        "length": 86400,
        "algo": "fifty_fifty"
    }
    os.mkdir(os.path.join(ROOT_DIR, "tmp"))
    run_name = os.path.join(ROOT_DIR, "tmp", "run0")
    s = Simulator(config, 0)
    s.start()
    filename = run_name + ".pkl"
    file_exists = os.path.isfile(filename)
    if file_exists:
        os.remove(filename)
        os.rmdir(os.path.join(ROOT_DIR, "tmp"))

    assert file_exists
