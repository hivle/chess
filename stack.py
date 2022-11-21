class _Node:
    def __init__(self, data):
       self.data = data
       self.next = None
 
class Stack:
    def __init__(self):
        self.head = None
    
    def __str__(self) -> str:
        current = self.head
        result = ""
        while current is not None:
            result = str(current.data) + ' -> ' + result
            current = current.next
        if result == "":
            return "None"
        return result

    def push(self, data):
        if self.head is None:
            self.head = _Node(data)
        else:
            new_node = _Node(data)
            new_node.next = self.head
            self.head = new_node
 
    def pop(self):
        if self.head is None:
            return None
        popped = self.head.data
        self.head = self.head.next
        return popped

    def count(self, data) -> int:
        current = self.head
        count = 0
        while current is not None:
            if current.data == data:
                count += 1
            current = current.next
        return count
