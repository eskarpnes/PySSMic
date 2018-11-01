import util.optimizer_utils as u
import pandas as pd


def test_differentiate():
    series1 = pd.Series(index=[0, 3600], data=[0.0, 1.0])
    expected1 = pd.Series(index=[0, 3600], data=[0.000278, 0.000278]).round(4)
    actual1 = u.differentiate(series1).round(4)

    series2 = pd.Series(index=[0, 1, 2, 3, 4, 5], data=[0.0, 0.5, 1.0, 2.0, 2.0, 3.0])
    expected2 = pd.Series(index=[0, 1, 2, 3, 4, 5], data=[0.5, 0.5, 1.0, 0.0, 1.0, 1.0]).round(4)
    actual2 = u.differentiate(series2).round(4)

    assert all(list(expected1 == actual1))
    assert all(list(expected2 == actual2))


def test_interpolate():
    series = pd.Series(index=[2, 4, 6], data=[4.0, 8.0, 12.0])
    actual = u.interpolate(series, [i for i in range(9)]).round(4)
    expected = pd.Series(index=[i for i in range(9)], data=[4.0, 4.0, 4.0, 6.0, 8.0, 10.0, 12.0, 12.0, 12.0])
    assert all(list(actual.data == expected))
