from stack import Stack
#TODO add more tests

def test_empty():
    testStack = Stack()
    output = testStack.pop()
    assert output is None
    assert testStack.count("any") == 0

def test_push_one_item():
    testStack = Stack()
    testStack.push("hello")
    assert testStack.head.data == "hello"
    assert testStack.count("hello") == 1
    assert testStack.count("other") == 0
    assert testStack.count(0) == 0

def test_pop():
    testStack = Stack()
    testStack.push("a")
    testStack.push(5)
    assert testStack.count("a") == 1
    temp = testStack.pop()
    assert testStack.count("a") == 1
    assert temp == 5
    temp = testStack.pop()
    assert temp == "a"
    assert testStack.count("a") == 0

