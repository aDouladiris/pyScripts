
import os
import sys
from datetime import datetime, timedelta, date, timezone

# Clearing cli for raw input
if sys.platform.startswith('linux'):
    try:
        os.system('clear')
    except:
        pass
elif sys.platform.startswith('win32'):
    try:
        os.system('cls')
    except:
        pass


# Calculate if a month has 31, 30, 29 or 28 days by adding 30 days with timedelta, subtract the days and compare them with each other
def days_of_month(date):
    date_after_30_days = date + timedelta(days=30)
    difference = date.day - date_after_30_days.day
    if difference == 1:
        return 31
    if difference == 0:
        return 30
    if difference == -1:
        return 29
    if difference == -2:
        return 28


def calculate_time_difference(date_to_calculate, current_time):

    time_difference = current_time - date_to_calculate
    # This attr returns only the difference in days
    time_difference_days = time_difference.days
    #########################################################
    days_of_specific_month = days_of_month(date_to_calculate)
    specific_month = date_to_calculate.strftime("%B")
    
    print("The date to calculate is", date_to_calculate.strftime("%d-%m-%Y %H:%M:%S") )
    print("Current date is", current_time.strftime("%d-%m-%Y %H:%M:%S") )
    print('The difference is {} days'.format(time_difference_days))
    print('The month {} has {} days'.format(specific_month, days_of_specific_month))



# Get the current time and split in day, month, year, hours, minutes and seconds
current_time = datetime.now()
current_day = int(current_time.strftime("%d"))
current_month = int(current_time.strftime("%m"))
current_year = int(current_time.strftime("%Y"))
current_hour = int(current_time.strftime("%H"))
current_minute = int(current_time.strftime("%M"))
current_second = int(current_time.strftime("%S"))

while(1):
    print("------------------------------------------------------------------------------------")
    print("Enter a choice:\n1.Date Difference Calculation\n2.Exit")
    print("------------------------------------------------------------------------------------")
    choice = str(input())
    if choice == '1':
        print("Enter a date that is at least one day earlier that the current date:")
        print("day")
        day_input = int(input())
        print("month")
        month_input = int(input())
        print("year")
        year_input = int(input())

        # Use datetime exceptions to avoid date errors like insert a day with 3 digits
        try:
            date_to_validate = datetime(year=year_input, month=month_input, day=day_input, hour=current_hour, minute=current_minute, second=current_second)
        except ValueError as error:
            print(error)
            break

        if date_to_validate:
            # Calculate timedelta to avoid calculations for future dates
            difference_to_validate = current_time - date_to_validate
            # This attr returns only the difference in days
            difference_in_days = difference_to_validate.days
            
            if difference_in_days > 0:
                calculate_time_difference(date_to_validate, current_time)
            else:
                print("The difference {} in days is not greater than zero".format(difference_in_days))

    elif choice == '2':
        print("Exiting...")
        break