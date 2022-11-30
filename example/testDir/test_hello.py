import pytest
import sys
sys.path.append('../')
from modulesToTest.hello3 import foo
from modulesToTest.hello4 import bar

def test_foo():
    assert foo(5) == -8

def test_bar():
    assert bar(10) == 20