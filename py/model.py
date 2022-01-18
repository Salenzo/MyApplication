class target(object):
    def __init__(self,lifePoint) -> None:
        super().__init__()
        self.lifePoint = lifePoint

class agent(target):
    def __init__(self, lifePoint) -> None:
        super().__init__(lifePoint)

class enemy(target):
    def __init__(self, lifePoint) -> None:
        super().__init__(lifePoint)

class floor(object):
    def __init__(self) -> None:
        super().__init__()