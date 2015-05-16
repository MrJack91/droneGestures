
import ControlCrazyflie, ControlDetection

def main():

    print 'connect to crazyflie'
    cf = ControlCrazyflie.ControlCrazyflie()
    cf.connect()


    print 'connect to leap'
    cd = ControlDetection.ControlDetection(cf)


if __name__ == "__main__":
    main()
