import sys

from Controller import CrazyflieController, DetectionController

def main():

    print '************'
    print 'main: connect to crazyflie'
    cfc = CrazyflieController.CrazyflieController()
    cfc.connect()

    print '************'
    print 'main: connect to leap'
    dc = DetectionController.DetectionController(cfc)

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
