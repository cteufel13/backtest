
class Action:

    def __init__(self,type,amount,stop_loss):
        self.type = type
        self.amount = amount
        self.stop_loss = stop_loss
        pass

    def __repr__(self):
        return f'Action({self.type},{self.amount},{self.stop_loss})'