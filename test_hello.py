from hello import greet


def test_greet_default():
    assert greet("world") == "Hello, world!"


def test_greet_custom_name():
    assert greet("Iliasse") == "Hello, Iliasse!"


def test_greet_shout():
    assert greet("Iliasse", shout=True) == "HELLO, ILIASSE!"
