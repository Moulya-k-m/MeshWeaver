
import pytest

from meshweaver.node import execute_task


def test_addition():
    payload = {"operation": "add", "args": [10, 20]}
    assert execute_task(payload) == 30


def test_multiplication():
    payload = {"operation": "multiply", "args": [5, 4]}
    assert execute_task(payload) == 20


def test_division():
    payload = {"operation": "divide", "args": [10, 2]}
    assert execute_task(payload) == 5.0


def test_division_multiple_numbers():
    payload = {"operation": "divide", "args": [100, 2, 5]}
    assert execute_task(payload) == 10.0


def test_division_by_zero():
    payload = {"operation": "divide", "args": [10, 0]}

    with pytest.raises(ZeroDivisionError):
        execute_task(payload)


def test_division_insufficient_arguments():
    payload = {"operation": "divide", "args": [10]}

    with pytest.raises(ValueError):
        execute_task(payload)


def test_unsupported_operation():
    payload = {"operation": "subtract", "args": [10, 5]}

    with pytest.raises(ValueError):
        execute_task(payload)

