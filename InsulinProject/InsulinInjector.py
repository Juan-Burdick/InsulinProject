import time
import random

#######################################################
# Variable Declaration
#######################################################

# running battery life total
# global because multiple functions need read access
batteryPercent = 100
# running insulin fill level
# global because multiple functions need read access
insulinPercent = 100
# boolean for whether a timer for standard check is running
# global because it is set to true in runtime
# and reset when standard check is performed
stdCheckIsSleeping = 0
# maintains last insulin reading
# global because it needs to be maintained between function calls
oldDataPoint = 110
# running average trend for each interval between standard checks
# global because per_second sets it and standard check resets it
aveTrend = 0
# person's initial glucose level
# global because multiple functions need read/write access
sugarLevel = 110


#######################################################
# Main Function
#######################################################
def run_time():
    # adding accessors to global variables
    global batteryPercent
    global insulinPercent
    global stdCheckIsSleeping
    sleep_time = 0  # local variable to set up a timer for standard check

    while True:  # This loop body needs to run until the system dies
        # run while battery and/or insulin are not low
        while (batteryPercent > 10) and (insulinPercent > 20):
            print("Sugar Level: " + str(sugarLevel))  # visualize trends in readings
            # if we just ran standard check, start a new timer
            if stdCheckIsSleeping == 0:
                sleep_time = time.time()  # set a fixed point to determine time passage
                stdCheckIsSleeping = 1  # timer is set
            # if timer was set AND time just ran out, run standard check
            elif (stdCheckIsSleeping == 1) and ((int(time.time()) - int(sleep_time)) >= 3):
                std_check()
            time.sleep(1)  # only perform all checks once per second
            # check current insulin level
            # nested function call: checks if emergency injection needed and updates trend
            check_insulin_level()
        # if battery or insulin are low, we have left the main loop body
        # run the low_resources function to suggest the user replenish
        # normal operation is necessarily suspended until recharged/refilled
        if (batteryPercent <= 10) or (insulinPercent <= 20):
            low_resources()


#######################################################
# Standard check, performed every 10 minutes
#######################################################
def std_check():
    # adding accessors to global variables
    global batteryPercent
    global stdCheckIsSleeping
    global sugarLevel
    global aveTrend

    # standard check consumes a minimal amount of battery, show depletion
    batteryPercent -= 1
    print("Battery Level: " + str(batteryPercent) + "%")  # visualize battery level
    print("Insulin Level: " + str(insulinPercent) + "%")  # visualize insulin level
    stdCheckIsSleeping = 0  # reset timer variable

    # IF glucose level is high and variance over the past 10 minutes
    # is greater than 5 and trend is positive, perform regular injection
    if (sugarLevel > 120) and (abs(aveTrend) > 5) and (aveTrend > 5):
        aveTrend = 0  # reset trend for next interval's use
        # call injection function with
        # [urgency = regular] and [overage = x] where x is height above optimal level
        injection("regular", int(sugarLevel - 110))
    # IF glucose level is high and variance is greater than 5 and trend
    # is negative, do nothing (it's already dropping)
    elif (sugarLevel > 120) and (abs(aveTrend) > 5) and (aveTrend < -5):
        aveTrend = 0  # reset trend for next interval's use
    # IF glucose level is high and variance is less than 5, do regular injection
    elif (sugarLevel > 120) and (abs(aveTrend) < 5):
        aveTrend = 0  # reset trend for next interval's use
        # call injection function with
        # [urgency = regular] and [overage = x] where x is height above optimal level
        injection("regular", int(sugarLevel - 110))
    # IF glucose level is low, alert user HIGH PRIORITY
    elif sugarLevel < 100:
        aveTrend = 0  # reset trend for next interval's use
        print("!!!ALERT!!! Sugar level is critically low, raise immediately!")
    # IF glucose level is in optimal range, but variance is excessively high
    # AND trend is positive, perform a regular injection
    elif (100 <= sugarLevel <= 120) and (aveTrend > 10):
        aveTrend = 0  # reset trend for next interval's use
        # call injection function with
        # [urgency = regular] and [overage = x] where x is height above optimal level
        injection("regular", int(sugarLevel - 110))
    # IF glucose level is in optimal range, but variance is excessively high
    # AND trend is negative, alert user LOW PRIORITY
    elif (100 <= sugarLevel <= 120) and (aveTrend < -10):
        aveTrend = 0  # reset trend for next interval's use
        print("ALERT! Sugar level is plummeting, raise soon.")
    else:
        aveTrend = 0  # reset trend for next interval's use


#######################################################
# Injection, performed when glucose is high or rising
#######################################################
def injection(urgency, overage):  # urgency is critical or regular
    # adding accessors to global variables
    global batteryPercent
    global insulinPercent
    global sugarLevel
    global oldDataPoint
    # local variable to determine battery depletion over time (random to mimic reality)
    battery_depletion = 0

    # glucose level is above 150, inject NOW
    if urgency == "critical":
        print("Emergency injection administered. Please consult medical services.")
        # reduce glucose level by amount necessary to stabilize to optimal of 110
        sugarLevel -= overage
        # reset trend's old value, it's not the spiked value anymore
        oldDataPoint = sugarLevel
    # glucose level is above 120 and not dropping, or
    # glucose level is in optimal belt but rising quickly
    elif urgency == "regular":
        print("Adjustment dose administered.")
        # reduce glucose level by amount necessary to stabilize to optimal of 110
        sugarLevel -= overage
        # reset trend's old value, it's not the spiked value anymore
        oldDataPoint = sugarLevel
    else:
        print("There's been an error.")

    # randomly generate battery depletion to mimic reality
    for x in range(1):
        battery_depletion = int(random.randrange(1, 4))
    # deplete storage values for battery life percentage and insulin fill level
    batteryPercent -= battery_depletion
    insulinPercent -= int(overage/3)
    print("Insulin Level: " + str(insulinPercent) + "%")


#######################################################
# Per Second insulin checks, Read and Track functions
#######################################################
# Read insulin
def check_insulin_level():
    # add accessor to glucose level for editing
    global sugarLevel
    # no actual reading apparatus connected
    # use random number to slightly modify existing level for now
    for x in range(1):
        sugarLevel += random.randrange(-5, 11)
    # call Trend tracking function
    # @param sugarLevel: most recent reading
    per_second_data_record(sugarLevel)


############################
# Track insulin changes within interval
# @param current_insulin_data: Most recent insulin reading
def per_second_data_record(current_insulin_data):
    # adding accessors to global variables
    global oldDataPoint
    global aveTrend

    # if insulin is above 150, emergency injection needed
    if current_insulin_data >= 150:
        # call injection function with
        # [urgency = critical] and [overage = x] where x is height above optimal level
        injection("critical", (current_insulin_data - 110))
    # if insulin reading is below 100, they are crashing
    # alert user of immediate need for sugar
    elif current_insulin_data <= 100:
        print("!!!ALERT!!! Sugar level is critically low, raise immediately!")
    else:
        # temporary var for difference between current reading and most recent reading
        cur_trend = current_insulin_data - oldDataPoint
        aveTrend += cur_trend  # add temporary var to average trend for interval
    oldDataPoint = current_insulin_data  # move pointer to current reading


#######################################################
# Low Resources: function has been suspended until replenished, by necessity
#######################################################
def low_resources():
    # adding accessors to global variables
    global batteryPercent
    global insulinPercent

    # loop while either resource is still low
    while (batteryPercent <= 10) or (insulinPercent <= 20):
        # if battery is what's low, ask user to replace or recharge
        if batteryPercent <= 10:
            print("Battery is low, please replace/recharge.")
            time.sleep(1)
            print("Please enter [yes] when battery is replaced.")
            cond = 1  # variable to ensure correct input
            # force correct input by looping until input is valid
            while cond != 0:
                replaced = input("")
                replaced.lower()  # to standardize input
                if replaced == "yes":
                    # battery replaced, reset and run appropriately
                    batteryPercent = 100
                    cond = 0
                elif replaced != "yes":
                    print("Has the battery been replaced? Enter [yes] when it has.")
        # if insulin is what's low, ask user to replace or refill
        if insulinPercent <= 20:
            print("Insulin is low, please replace/refill.")
            time.sleep(1)
            print("Please enter [yes] when insulin is refilled.")
            cond = 1  # variable to ensure correct input
            # force correct input by looping until input is valid
            while cond != 0:
                replaced = input("")
                replaced.lower()  # to standardize input
                if replaced == "yes":
                    # insulin refilled, reset and run appropriately
                    insulinPercent = 100
                    cond = 0
                elif replaced != "yes":
                    print("Has the insulin been refilled? Enter [yes] when it has.")


#######################################################
# Call the Main Function to start continuous operation
#######################################################
run_time()
