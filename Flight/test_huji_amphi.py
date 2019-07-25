import drone_utils as du
from time import sleep
from click._compat import raw_input

def main():
    dr = du.Drone()

    print("start mission...")
    # sleep(20)

    dr.take_off(10)
    sleep(2)
    print("Starting to sample")
    dr.take_sample()
    for k in range(2):
        for i in range(6):
            dr.goto(-2.8, 2.8)
            dr.take_sample()
        dr.goto(2.8, 2.8)
        dr.take_sample()
        for i in range(6):
            dr.goto(2.8, -2.8)
            dr.take_sample()
        dr.goto(2.8, 2.8)
        dr.take_sample()
    for j in range(3):
        dr.goto(-2.8, 2.8)
        dr.take_sample()
    dr.land()
    raw_input("Press any key to turn off the drone")
    dr.close_connection()



if __name__=='__main__':
    main()