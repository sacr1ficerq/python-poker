class Player:
    def __init__(self, name, stack, table):
        self.name = name
        self.stack = stack
        self.table = table

        self.cards = []

    def __repr__(self):
        return f'player: \'{self.name}\'\tchips: {self.stack}'
