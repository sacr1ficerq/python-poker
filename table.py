class Table:
    def __init__(self, sb, bb):
        self.bb = bb
        self.sb = sb

        self.players = []
        self.dealer = 0

    def __repr__(self):
        return f'sb: {self.sb}\t bb: {self.bb}\nplayers: {self.players}'
