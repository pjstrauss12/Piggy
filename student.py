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
        self.LEFT_DEFAULT = 80
        self.RIGHT_DEFAULT = 80
        self.MIDPOINT = 1200  # what servo command (1000-2000) is straight forward for your bot?
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
        #check to see it's safe
        if not self.safe_to_dance():
            print("Not enough space to dance!")
            return #return closes down method
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
            self.servo(2000) #look right
            time.sleep(1)
            self.servo(1000) #look left
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
        for angle in range(self.MIDPOINT-350, self.MIDPOINT+350, 30):
            self.servo(angle)
            self.scan_data[angle] = self.read_distance()

    def obstacle_count(self):
        """Does a 360 scan and returns the number of obstacles it sees"""
        found_something = False #trigger
        trigger_distance = 250
        count = 0
        starting_position = self.get_heading() #write down starting position
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

    def nav(self):
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        while True:    
            while self.read_distance() > 250:
                self.fwd()
                time.sleep(.01)
            self.stop()
            self.scan()
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
            if left_avg > right_avg:
                self.turn_by_deg(-90)
            else:
                self.turn_by_deg(90)
            self.servo(self.MIDPOINT)





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
