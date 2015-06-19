
import sys, CrazyflieController, DetectionController

def main():

    print 'connect to crazyflie'
    cf = CrazyflieController.CrazyflieController()
    cf.connect()

    print 'connect to leap'
    dc = DetectionController.DetectionController(cf)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
