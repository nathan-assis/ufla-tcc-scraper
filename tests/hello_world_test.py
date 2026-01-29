from src.hello_world.hello_world import hello


def test_hello():
    assert hello() == "Hello, World!"
