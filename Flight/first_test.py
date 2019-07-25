import drone_utils as du
from time import sleep


def main():
    dr = du.Drone()
    dr.take_off(10)
    print("take sample...")
    sleep(3)
    dr.land()
    sleep(3)
    dr.close_connection()
    print("test1")



if __name__=='__main__':
    main()

