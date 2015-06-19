
import sys
import CrazyflieController
import DetectionController

def main():

    print '************'
    print 'main: connect to crazyflie'
    cf = CrazyflieController.CrazyflieController()
    cf.connect()

    print '************'
    print 'main: connect to leap'
    dc = DetectionController.DetectionController(cf)

    # Keep this process running until Enter is pressed
    print "main:: press enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        print '************'
        print 'main: shut down'
        cf.cleanup()
        dc.cleanup()


if __name__ == "__main__":
    main()
