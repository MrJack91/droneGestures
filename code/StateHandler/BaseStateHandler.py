
class BaseStateHandler(object):

    def __init__(self, current_state):
        # default don't change state
        self.next_state = current_state

    def handleState(self, hand):
        self.hand = hand


