class Stack:
    list = []

    def push(self, val):
        self.list.append(val)

    def pop(self):
        return self.list.pop()

    def peek(self):
        return self.list[-1]

    def is_empty(self):
        return len(self.list) == 0

    def __str__(self):
        return ', '.join([str(i) for i in reversed(self.list)])
