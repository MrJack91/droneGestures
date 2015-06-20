

class BaseStateHandler(object):

    def __init__(self, piloting_configuration, cfc, current_state):
        # default don't change state
        self.piloting_configuration = piloting_configuration
        self.cfc = cfc
        self.orig_state = current_state
        self.next_state = current_state

    def handle(self, hand):
        # init every handel with its orig state
        self.next_state = self.orig_state
        self.hand = hand

    def check_cf(self):
        """ check if the crazyflie properly connected
        :return: if true: access can get via self.cfc.cf
        """
        if self.cfc.cf is not None:
            return True
        else:
            return False
