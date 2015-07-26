import sys

from Controller import CrazyflieController, DetectionController

def main():

    debug = False
    #debug = True

    print '************'
    print 'main: connect to crazyflie'
    cfc = CrazyflieController.CrazyflieController()

    if debug:
        print 'DEBUG MODE IS ON!'
        cfc.is_connected = True
    else:
        cfc.connect()

    print '************'
    print 'main: connect to leap'
    dc = DetectionController.DetectionController(cfc, debug)

    # Keep this process running until Enter is pressed
    print "main: press enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        print '************'
        print 'main: shut down'
        cfc.cleanup()
        dc.cleanup()


if __name__ == "__main__":
    main()
