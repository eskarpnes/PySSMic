import os

from simulator import Simulator


def test_simulator():
    config = {
        "neighbourhood": "test",
        "timefactor": 0.000001,
        "length": 86400,
        "algo": "fifty_fifty"
    }

    run_name = "test_simulator"
    s = Simulator(config, run_name)
    s.start()
    filename = run_name + ".pkl"
    file_exists = os.path.isfile(filename)
    if file_exists:
        os.remove(filename)

    assert file_exists
