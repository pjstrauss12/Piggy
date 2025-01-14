from teacher import PiggyParent
import sys
import time


class Piggy(PiggyParent):

    '''
    *************
    SYSTEM SETUP
    *************
    '''

    def __init__(self, addr=8, detect=True):
        PiggyParent.__init__(self) # run the parent constructor

        ''' 
        MAGIC NUMBERS <-- where we hard-code our settings
        '''
        self.LEFT_DEFAULT = 100 # motor speed
        self.RIGHT_DEFAULT = 95 # motor speed
        self.SAFE_DIST = 500 # how far I have to be from an object to drive
        self.corner_count = 0 # sets how many times the robot turns before get_me_out is activated
        self.MIDPOINT = 1600  # what servo command (1000-2000) is straight forward for your bot?
        self.load_defaults()
        

    def load_defaults(self):
        """Implements the magic numbers defined in constructor"""
        self.set_motor_limits(self.MOTOR_LEFT, self.LEFT_DEFAULT)
        self.set_motor_limits(self.MOTOR_RIGHT, self.RIGHT_DEFAULT)
        self.set_servo(self.SERVO_1, self.MIDPOINT)
        

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values. Python is cool.
        # Please feel free to change the menu and add options.
        print("\n *** MENU ***") 
        menu = {"n": ("Navigate", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "v": ("Veer", self.slither),
                "h": ("Hold Position", self.hold_position),
                "c": ("Calibrate", self.calibrate),
                "q": ("Quit", self.quit)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = str.lower(input("Your selection: "))
        # activate the item selected
        menu.get(ans, [None, self.quit])[1]()

    '''
    ****************
    STUDENT PROJECTS
    ****************
    '''

    def dance(self):
        """full dance"""
        # check to see it's safe
        if not self.safe_to_dance():
            print("Not enough space to dance!")
            return # return closes down method
        else:
            print("It's safe to dance!")
        for x in range(3):
            self.break_dance()
            self.spin()
            self.rotation()
            self.head_turn()
            self.other_move()
        self.servo(2000)
        print("I'm done dancing!")
    
    def safe_to_dance(self):
        """does a 360 distance check and returns true if safe"""
        for x in range(4):
            for ang in range(self.MIDPOINT-400, self.MIDPOINT+400, 100):
                self.servo(ang)
                time.sleep(.1)
                if self.read_distance() < 250:
                    return False
            self.turn_by_deg(90)
        return True

    def break_dance(self):
        """does some turning"""
        self.stop()
        self.right()
        time.sleep(1)
        self.right()
        time.sleep(1)
        self.right()
        time.sleep(1)
        self.right()
        time.sleep(.5)
        self.stop()

    def head_turn(self):
        """turns servo"""
        for x in range(4):
            self.servo(2000) # look right
            time.sleep(1)
            self.servo(1000) # look left
            time.sleep(1)

    def rotation(self):
        """turns cleanly in a circle"""
        for x in range(4):
            self.right()
            time.sleep(1)
        self.stop()
    
    def spin(self):
        """spins in place"""
        for x in range(4):
            self.turn_by_deg(90)
        self.stop()
    
    def other_move(self):
        """moves back and right"""
        for x in range(3):
            self.back()
            time.sleep(1)
            self.right()
            time.sleep(1)
        self.stop()

    def scan(self):
        """Sweep the servo and populate the scan_data dictionary"""
        for angle in range(self.MIDPOINT-500, self.MIDPOINT+500, 400):
            self.servo(angle)
            self.scan_data[angle] = self.read_distance()

    def obstacle_count(self):
        """Does a 360 scan and returns the number of obstacles it sees"""
        found_something = False # trigger
        trigger_distance = 250
        count = 0
        starting_position = self.get_heading() # write down starting position
        self.right(primary=60, counter=-60)
        while self.get_heading() != starting_position:
            if self.read_distance < trigger_distance and not found_something:
                found_something = True
                count += 1
                print("\n FOUND SOMETHING \n")
            elif self.read_distance() > trigger_distance and found_something:
                found_something = False
                print("I have a clear view.  Resetting my counter")
        self.stop()
        print("I have found this many things: %d" % count)
        return count

    def quick_check(self):
        """three quick checks"""
        for ang in range(self.MIDPOINT-100, self.MIDPOINT+101, 100):
            self.servo(ang)
            if self.read_distance() < self.SAFE_DIST:
                return False
        # if I get to the end, this means I didn't find anything dangerous
        return True        

    def nav(self):
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        """If it does not see anything in 350 mm, it drives forward"""
        self.servo(self.MIDPOINT)
        self.corner_count
        started_at = self.get_heading()
        while True:    
            while self.quick_check():
                self.corner_count # pulls up current corner_count
                self.fwd() # goes forward and costantly checks for objects
                time.sleep(.01)
            self.stop()
            self.nope()
            self.scan()
            self.corner_count += 1 # if there is an object, one will be added to corner_count, see get_me_out method
            self.look_for_stuff()
            self.get_me_out()
            self.corner_count # resets corner_count to 0 so it does not repeatedly go in circles when it wants to turn
            
    def get_me_out(self):
        """If stuck, turns robot around to get it out of a trap"""
        self.corner_count
        if self.corner_count > 5: # if robot turns more than 5 times, this method activates where it will turn out of it
            self.turn_by_deg(135)
            self.corner_count = 0 # resets corner_count so robot will not continuously spin 135 degrees
        
    
    def look_for_stuff(self):
        """Looks left and right, counts obstacles and determines to go left or right"""
        # traversal
        left_total = 0
        left_count = 0
        right_total = 0
        right_count = 0
        for ang, dist in self.scan_data.items():
                if ang < self.MIDPOINT:
                    right_total +=dist
                    right_count += 1
                else:
                    left_total += dist
                    left_count += 1
        left_avg = left_total / left_count
        right_avg = right_total / right_count
        if left_avg > right_avg: # if the left has a longer distance, it will turn left
            self.turn_by_deg(-45) 
        else:
            self.turn_by_deg(45) # if right distance is greater, it will turn right
        self.servo(self.MIDPOINT)
        self.corner_count # resets corner_count to 0 so robot does not spin too much when unnecessary
    
    def hold_position(self):
        starting_position = self.get_heading()
        while True:
            time.sleep(.1)
            new_ang = self.get_heading()
            if abs(starting_position-new_ang) > 20:
                self.turn_to_deg(starting_position)
                self.stop()
                print("I made it back!")

    def nope(self):
        if self.corner_count < 4:
            return False
        else:
            print("I don't like this")
            if self.read_distance() < self.SAFE_DIST:
                self.turn_by_deg(180)
                time.sleep(2)
                self.turn_by_deg(180)

    def slither(self):
        """practice a smooth veer"""
        #write down where we started
        starting_direction = self.get_heading()
        #start driving forward
        self.set_motor_power(self.MOTOR_LEFT, self.LEFT_DEFAULT)
        self.set_motor_power(self.MOTOR_RIGHT, self.RIGHT_DEFAULT)
        self.fwd()
        #throttle down left motor
        for power in range(self.LEFT_DEFAULT, 50, -10):
            self.set_motor_power(self.MOTOR_LEFT, power)
            time.sleep(.5)
        #throttle up left 
        for power in range(50, self.LEFT_DEFAULT + 1, 10):
            self.set_motor_power(self.MOTOR_LEFT, power)
            time.sleep(.1)
        # while lowering right
        for power in range(self.RIGHT_DEFAULT, 50, -10):
            self.set_motor_power(self.MOTOR_RIGHT, power)
            time.sleep(.5)
        #throttle up right 
        for power in range(50, self.RIGHT_DEFAULT + 1, 10):
            self.set_motor_power(self.MOTOR_RIGHT, power)
            time.sleep(.1)


        #straighten out
        while self.get_heading() != starting_direction:
            #if i need to veer right
            if self.get_heading() < starting_direction:
                print("I'm too far left!") # print
                self.set_motor_power(self.MOTOR_LEFT, 90)
                self.set_motor_power(self.MOTOR_RIGHT, 60)
            #if i need to veer left
            elif self.get_heading() > starting_direction:
                print("I'm too far right!") # print
            self.set_motor_power(self.MOTOR_LEFT, 60)
            self.set_motor_power(self.MOTOR_RIGHT, 90)
            time.sleep(.1)
        print("I think I'm done")
        self.stop()




###########
## MAIN APP
if __name__ == "__main__":  # only run this loop if this is the main file

    p = Piggy()

    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x\n")
        p.quit()

    try:
        while True:  # app loop
            p.menu()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        p.quit()  
