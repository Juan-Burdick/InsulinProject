import time
import sched
import random

#######################################################
# Variable Declaration
#######################################################

batteryPercent = 100  # running battery life total
insulinPercent = 100  # running insulin fill level
batteryDepletion = 0
insulinDepletion = 0
stdCheckIsSleeping = 0
sleepTime = 0
oldDataPoint = 0
aveTrend = 0
sugarLevel = 110

backgroundTimer = sched.scheduler(time.time, time.sleep)

# TODO: Rapid time checks to determine trends
# TODO: At every rapid check, determine if emergency injection is needed
# TODO: Slow checks utilizing trend values to determine injection need


def run_time():
    global batteryPercent
    global insulinPercent
    global batteryDepletion
    global insulinDepletion
    global stdCheckIsSleeping
    global sleepTime

    while (batteryPercent > 10) and (insulinPercent > 10):
        print("Battery Level: " + str(batteryPercent) + "%")
        print("Insulin Level: " + str(insulinPercent) + "%")
        print("Sugar Level: " + str(sugarLevel))
        if stdCheckIsSleeping == 0:
            sleepTime = time.time()
            stdCheckIsSleeping = 1
        elif (stdCheckIsSleeping == 1) and ((int(time.time()) - int(sleepTime)) >= 10):
            std_check()
        time.sleep(1)
        check_insulin_level()
    if (batteryPercent <= 10) or (insulinPercent <= 10):
        low_resources()


def std_check():
    global batteryPercent
    global insulinPercent
    global stdCheckIsSleeping
    global sugarLevel
    global aveTrend

    # IF glucose level is high and variance over the past 10 minutes
    # is greater than 5 and trend is positive, perform regular injection
    # IF glucose level is high and variance is greater than 5 and trend
    # is negative, do nothing (it's already dropping)
    # IF glucose level is high and variance is less than 5, perform
    # a regular injection
    if (sugarLevel > 120) and (abs(aveTrend) > 5) and (aveTrend > 5):
        aveTrend = 0
        injection("regular", int(sugarLevel - 110))
        # Inject with [urgency = regular], and sugar above 110 as [overage]
    elif (sugarLevel > 120) and (abs(aveTrend) > 5) and (aveTrend < (-5)):
        stdCheckIsSleeping = 0
        aveTrend = 0
        run_time()
    elif (sugarLevel > 120) and (abs(aveTrend) < 5):
        aveTrend = 0
        injection("regular", int(sugarLevel - 110))
        # Inject with [urgency = regular], and sugar above 110 as [overage]
    # IF glucose level is low, alert user HIGH PRIORITY
    elif sugarLevel < 100:
        aveTrend = 0
        print("!!!ALERT!!! Sugar level is critically low, raise immediately!")
    # IF glucose level is in optimal range, but variance is excessively high
    # AND trend is positive, perform a regular injection
    # AND trend is negative, alert user LOW PRIORITY
    elif (100 <= sugarLevel <= 120) and (aveTrend > 10):
        aveTrend = 0
        injection("regular", int(sugarLevel - 110))
        # Inject with [urgency = regular], and sugar above 110 as [overage]
    elif (100 <= sugarLevel <= 120) and (aveTrend < (-10)):
        aveTrend = 0
        print("ALERT! Sugar level is plummeting, raise soon.")
    else:
        stdCheckIsSleeping = 0
        aveTrend = 0
        run_time()


def injection(urgency, overage):
    global batteryPercent
    global insulinPercent
    global batteryDepletion
    global sugarLevel
    if urgency == "critical":
        print("Emergency injection administered. Please consult medical services.")
        sugarLevel -= overage
    elif urgency == "regular":
        print("Adjustment dose administered.")
        sugarLevel -= overage
    else:
        print("There's been an error.")
    for x in range(1):
        batteryDepletion = int(random.randrange(1, 4))
    batteryPercent -= batteryDepletion
    insulinPercent -= int(overage/5)
    run_time()


def check_insulin_level():
    global sugarLevel
    for x in range(1):
        sugarLevel += random.randrange(-5, 6)
    per_second_data_record(sugarLevel)


def per_second_data_record(current_insulin_data):
    global oldDataPoint
    global aveTrend
    if current_insulin_data >= 150:
        injection("critical", (current_insulin_data - 110))
    elif (oldDataPoint == 0) and (current_insulin_data == 0):
        print("!!!ALERT!!! Sugar level is critically low, raise immediately!")
    elif (current_insulin_data <= 100) and (current_insulin_data != 0):
        print("!!!ALERT!!! Sugar level is critically low, raise immediately!")
    elif (oldDataPoint == 0) or (current_insulin_data == 0):
        run_time()
    else:
        curTrend = oldDataPoint - current_insulin_data
        aveTrend += curTrend
    oldDataPoint = current_insulin_data
    run_time()


def low_resources():
    global batteryPercent
    global insulinPercent
    while (batteryPercent <= 10) or (insulinPercent <= 10):
        if batteryPercent <= 10:
            print("Battery is low, please replace/recharge.")
            time.sleep(1)
            print("Please enter [yes] when battery is replaced.")
            cond = 1  # variable to ensure correct input
            # force correct input
            while cond != 0:
                replaced = input("")
                replaced.lower()  # to standardize input
                if replaced == "yes":
                    # battery replaced, reset and run appropriately
                    batteryPercent = 100
                    cond = 0
                else:
                    print("Has the battery been replaced? Enter [yes] when it has.")
        if insulinPercent <= 10:
            print("Insulin is low, please replace/refill.")
            time.sleep(1)
            print("Please enter [yes] when insulin is refilled.")
            cond = 1  # variable to ensure correct input
            # force correct input
            while cond != 0:
                replaced = input("")
                replaced.lower()  # to standardize input
                if replaced == "yes":
                    # insulin refilled, reset and run appropriately
                    insulinPercent = 100
                    cond = 0
                else:
                    print("Has the insulin been refilled? Enter [yes] when it has.")
        elif (batteryPercent > 10) and (insulinPercent > 10):
            run_time()

########################
########################
########################

run_time()