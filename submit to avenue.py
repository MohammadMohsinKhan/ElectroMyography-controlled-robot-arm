## ----------------------------------------------------------------------------------------------------------
## TEMPLATE
## Please DO NOT change the naming convention within this template. Some changes may
## lead to your program not functioning as intended.
import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)


## STUDENT CODE BEGINS
## ----------------------------------------------------------------------------------------------------------
import random
#these three thresholds are used in all of the functions
threshold_1 = 0.3
threshold_2 = 0.6
threshold_3 = 0.9
#gripper_open variable is used in the gripper function to check if the gripper is open or not
gripper_open = True
#open_state variable is used in the open_autoclave function to check if the drawer is open or not
open_state = False
#cycle_complete variable is used in the main function to check if 1 cycle has been completed so that it can move on to the next one
cycle_complete = False
#container_id is a list of all the containers and used in the main function
container_id = [1,2,3,4,5,6]

def location(id): #this function returns the location of where the container is supposed to be dropped of according to its id
    locations = [[-0.6174,0.2495,0.3908],[-0.0,-0.66,0.4],[0.0,0.65,0.3908],[-0.4,0.15,0.3],[0.0,-0.42,0.3],[0.0,0.42,0.3]]
    return locations[id-1]

def move_arm(id): #this function is used to control the arm using the right arm from the muscle emulator
    if arm.emg_right() > threshold_3:
        arm.move_arm(location(id)[0],location(id)[1],location(id)[2]) #moves arm to the autoclave for the container using the location function
    elif arm.emg_right() > threshold_2:
        arm.move_arm(0.4064,0.0,0.4826) # moves arm to the home location
    elif arm.emg_right() > threshold_1:
        #moves arm to the pickup location
        arm.move_arm(0.5321,0.0,0.035)

def gripper(): #this functions controls the gripper using the left arm from the muscle emulator
    global gripper_open
    #opens gripper after checking if it is closed first using the gripper_open variable
    if arm.emg_left() < threshold_2 and gripper_open == False:
        arm.control_gripper(-45)
        gripper_open = True
    #closes gripper after checking if it is open first using the gripper_open variable
    if arm.emg_left() > threshold_2 and gripper_open == True:
        arm.control_gripper(45)
        gripper_open = False

def open_autoclave(id): #this function opens and closes the autoclave bin using the left arm from the muscle emulator
    global open_state
    #opens the autoclave bin after checking if the bin is closed using the open_state variable and if the container is big
    if arm.emg_left() > threshold_1 and open_state == False and id > 3:
        arm.open_red_autoclave(id == 4)
        arm.open_green_autoclave(id == 5)
        arm.open_blue_autoclave(id == 6)
        open_state = True
    #closes the autoclave bin after checking if the bin is open using the open_state variable
    elif arm.emg_left() < threshold_1 and open_state == True and id > 3:
        arm.open_red_autoclave(False)
        arm.open_green_autoclave(False)
        arm.open_blue_autoclave(False)
        open_state = False

def main(): #this is the main function which calls all of the functions and takes care of spawning the containers
    global cycle_complete
    global container_id
    #spawns a container according to its id by random and then removes it form the list of container ids
    container = random.choice(container_id)
    container_id.remove(container)
    arm.spawn_cage(container)
    #this loop runs until all of the containers have been dropped off
    while True:
        location(container)
        move_arm(container)
        open_autoclave(container)
        gripper()
        if arm.emg_right() > threshold_3 and arm.emg_left() < threshold_2: #checks if the arm is at the drop off location and if the container has been dropped off which signifies that a cycle is complete
            cycle_complete = True
        if threshold_2 <= arm.emg_right() <= threshold_3 and cycle_complete == True and arm.emg_left() == 0: #this if condition checks if the arm is in the home position and then waits for the left muscle to be equal to zero so that the next container is spawned in
            #checks if all the containers have been spawned, if true then after the last one is dropped the loop ends and no more containers are spawned
            if len(container_id) != 0:
                container = random.choice(container_id)
                container_id.remove(container)
                arm.spawn_cage(container)
                cycle_complete = False
            else:
                arm.home()
                break

main()





