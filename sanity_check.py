#!/usr/bin/env python3
# facilities for sanity checking and auto correcting user input

def pretty_print(reason, old_value_str, new_value_str):
    print("%s: \"%s\" -> \"%s\"" % (reason, old_value_str, new_value_str))

def sanity_check(sensor_name, value_str):
    """ Perform sanity checks after auto corrections if possible """

    try:
        value_float = float(value_str)
    except Exception as err:
        # possibility: user entered 2 dylos readings and didn't press submit
        if (sensor_name == "3m sd200 slm"):
            n_decimal_points = value_str.count(".")
            if (n_decimal_points > 1):
                # extract the last reading - the timestamp of the other
                # readings is uncertain. assume that each reading has a single
                # decimal point
                split = value_str.split(".")
                new_value_str = split[-2][1:] + "." + split[-1]
                pretty_print(
                    "multiple readings; extracted last",
                    value_str,
                    new_value_str
                )
                return sanity_check(sensor_name, new_value_str)
            else:
                raise err
        else:
            raise err

    if (sensor_name == "3m sd200 slm"):

        # stated range of 3m sd-200 slm is 40 to 130 dB
        if (value_float < 40):
            return False
        elif (value_float > 130):
            first_zero_loc = value_str.find("0")

            if (not "." in value_str):
                # possibility: user entered "0" instead of a decimal point
                if (first_zero_loc != -1):
                    new_value_str = value_str[:first_zero_loc] + "." + value_str[(first_zero_loc + 1):]
                    pretty_print(
                        "converted \"0\" -> \".\"",
                        value_str,
                        new_value_str
                    )
                    return sanity_check(sensor_name, new_value_str)

                # possibility: user did not enter decimal point. the 3m sd-200
                # slm has one decimal point so we add the decimal point between
                # the last and second to last characters
                else:
                    new_value_str = value_str[:-1] + "." + value_str[-1]
                    pretty_print(
                        "inserted decimal point",
                        value_str,
                        new_value_str
                    )
                    return sanity_check(sensor_name, new_value_str)

            else:
                return False

    elif ("dylos" in sensor_name):

        # dylos readings do not have decimal points; user may have meant to
        # enter "0" instead
        if ("." in value_str):
            new_value_str = value_str.replace(".", "0")
            pretty_print(
                "converted \".\" -> \"0\"",
                value_str,
                new_value_str
            )
            return sanity_check(sensor_name, new_value_str)

    return value_float

if (__name__ == "__main__"):
    print("running tests")
    # format: (sensor, observed_result, expected_result)
    tests = [
        ("3m sd200 slm", "5505", 55.5),
        ("3m sd200 slm", "555", 55.5),
        ("3m sd200 slm", "55.566.6", 66.6),
        ("3m sd200 slm", "5555", False),
        ("3m sd200 slm", "5", False),
        ("dylos generic", "62.3", 6203)
    ]
    for test in tests:
        print("\n== test input from sensor \033[4m%s\033[0m" % (test[0]))
        print("== input: %s" % test[1])
        print("== expected: %s" % test[2])
        result = sanity_check(test[0], test[1])
        print("== result: %s" % result)
        if (result == test[2]):
            print("== \033[92mPASSED\033[0m")
        else:
            print("== \033[91mFAILED\033[0m")
