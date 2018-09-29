from src.load_profile import LoadProfile


def test_to_message():
    load_profile = LoadProfile([0.0, 3600.0], [0.0, 1.0])
    expected = dict(timestamps=[0.0, 3600.0], loads=[0.0, 1.0])
    actual = load_profile.to_message()

    assert(expected == actual)
