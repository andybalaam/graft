import pytest
from graftlib.env import Env


def test_Getting_a_name_after_setting_returns_its_value():
    env = Env()
    env.set("mythree", 3)
    assert env.get("mythree") == 3


def test_Empty_Env_does_not_contain_names():
    env = Env()
    assert not env.contains("x")


def test_After_setting_a_name_Env_contains_it():
    env = Env()
    env.set("myname", "foo")
    assert env.contains("myname")
    assert not env.contains("othername")


def test_Values_from_parent_are_found_via_get():
    world = Env()
    world.set("w", 2)
    town = Env(world)
    town.set("t", 3)
    house = Env(town)
    house.set("h", 4)

    assert house.get("h") == 4
    assert house.get("t") == 3
    assert house.get("w") == 2
    assert not town.contains("h")
    assert not world.contains("t")


def test_Cloned_Env_has_same_values():
    parent = Env()
    parent.set("p", 10)
    child = Env(parent)
    child.set("c", 8)

    new_child = child.clone()
    assert child.get("c") == 8
    assert child.get("p") == 10


def test_Cloned_env_and_parents_are_independent():
    parent = Env()
    parent.set("p", 10)
    child = Env(parent)
    child.set("c", 8)

    new_child = child.clone()

    # Change the old things
    parent.set("p", 1010)
    child.set("c", 1008)
    assert child.get("p") == 1010
    assert child.get("c") == 1008

    # New child did not pick up changed values
    assert new_child.get("p") == 10
    assert new_child.get("c") == 8

    # Change new child and its parent
    new_child.set("c", 0)
    new_child.parent.set("p", 1)
    assert new_child.get("p") == 1
    assert new_child.get("c") == 0

    # Old stuff was unaffected
    assert child.get("p") == 1010
    assert child.get("c") == 1008
