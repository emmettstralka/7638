######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

# If you see different scores locally and on Gradescope, this may be because:
# - you forgot that the test cases for each are different (e.g., if your
#   solution is not robust enough, you may pass Test Case 4 locally but still
#   fail Test Case 4 on Gradescope, or vice-versa);
# - you are uploading a different file than the one you are executing locally
#   (i.e., if this local ID doesn't match the ID on Gradescope, this indicates
#   that you uploaded a different file), in which case you should use the
#   OUTPUT_UNIQUE_FILE_ID to determine if this is the case; and/or
# - you modified one of the other files in the project in a way that causes your
#   local results to differ (since those changes don't carry over to
#   Gradescope), in which case you should download a fresh copy of all the
#   project files.

# These import statements give you access to library functions which you may
# (or may not?) want to use.
import random
import re
import time
from math import *

from body import *
from solar_system import *
from satellite import *


def estimate_next_pos(gravimeter_measurement, get_theoretical_gravitational_force_at_point, distance, steering, other=None):
    """
    Estimate the next (x,y) position of the satelite.
    This is the function you will have to write for part A.
    :param gravimeter_measurement: float
        A floating point number representing
        the measured magnitude of the gravitation pull of all the planets
        felt at the target satellite at that point in time.
    :param get_theoretical_gravitational_force_at_point: Func
        A function that takes in (x,y) and outputs a float representing the magnitude of the gravitation pull from
        of all the planets at that (x,y) location at that point in time.
    :param distance: float
        The target satellite's motion distance
    :param steering: float
        The target satellite's motion steering
    :param other: any
        This is initially None, but if you return an OTHER from
        this function call, it will be passed back to you the next time it is
        called, so that you can use it to keep track of important information
        over time. (We suggest you use a dictionary so that you can store as many
        different named values as you want.)
    :return:
        estimate: Tuple[float, float]. The (x,y) estimate of the target satellite at the next timestep
        other: any. Any additional information you'd like to pass between invocations of this function
        optional_points_to_plot: List[Tuple[float, float, float]].
            A list of tuples like (x,y,h) to plot for the visualization
    """
    # time.sleep(1)  # uncomment to pause for the specified seconds each timestep

    # example of how to get the gravity magnitude at a point in the solar system:
    #gravity_magnitude = get_theoretical_gravitational_force_at_point(-1*AU, 1*AU)

    # TODO - remove this canned answer which makes this template code
    # pass one test case once you start to write your solution....
    #xy_estimate = (139048139368.39096, -2225218287.6720667)

    # Initalizaion
    if other is None:
        P = []
        for _ in range(10000):
            x = random.uniform(-4 * AU, 4 * AU)
            y = random.uniform(-4 * AU, 4 * AU)
            theta = (atan2(y, x) + pi / 2) % (2 * pi)
            P.append((x, y, theta))
    else:
        P = other["particles"]

    # Imporatance Weights
    W = []
    for x, y, theta in P:
        force_predicted = get_theoretical_gravitational_force_at_point(x, y)
        rel = (force_predicted-gravimeter_measurement)/ max(abs(gravimeter_measurement),.000000000001)
        sigma = .08
        weight = exp(-.5 * (rel / sigma) ** 2)
        # old weight = 1.0/(1.0 + abs(force_predicted - gravimeter_measurement) / abs(gravimeter_measurement))
        W.append(weight)

    # Resample - Resample Wheel 
    N = len(P)

    resampled = []

    index = int(random.random() * N % N)
    beta = 0.0
    max_weight = max(W)
    if max_weight == 0.0:
        max_weight = 1.0
        W = [1.0] * N

    for _ in P:
        beta += random.random() * 2.0 * max_weight

        while beta > W[index]:
            beta -= W[index]
            index = (index + 1) % N

        resampled.append(P[index])

    # Fuzzing - Change percentage of them change X, Y and orentation fuzzy 8% noise and 40% of total particles
    New_P = []
    postion_s = .01 * AU
    heading_s = .01 
    for x, y, theta in resampled:
        if random.random() < .4:
            x += random.gauss(0, postion_s)
            y += random.gauss(0, postion_s)
            theta = (theta + random.gauss(0, heading_s)) % (2 * pi)
        New_P.append((x, y, theta))



    # Motion - Counterclockwise orbit gaussing noise, bicycle motion model
    satellite_length = 10.2
    tolerance = .001
    turn = tan(steering) * distance / satellite_length

    New_P2 = []
    for X, Y, theta in New_P:
        if abs(turn) < tolerance:
            X = X + distance * cos(theta)
            Y = Y + distance * sin(theta)
            theta = (theta + turn) % (2 * pi)
        else:
            radius = distance / turn
            cx = X - sin(theta) * radius
            cy = Y + cos(theta) * radius
            theta = (theta + turn) % (2 * pi)
            X = cx + sin(theta) * radius
            Y = cy - cos(theta) * radius

        New_P2.append((X, Y, theta))


    # Estimate - Avg of all the particles 
    xy_estimate = (sum(X for X, Y, theta in New_P2) / len(New_P2), sum(Y for X, Y, theta in New_P2) / len(New_P2))
    other = {"particles": New_P2}
    optional_points_to_plot = New_P2[::500]

    # You may optionally also return a list of (x,y,h) points that you would like
    # the PLOT_PARTICLES=True visualizer to plot for visualization purposes.
    #PLOT_PARTICLES = True
    # If you include an optional third value, it will be plotted as the heading
    # of your particle.
    #optional_points_to_plot = [(1*AU, 1*AU), (2*AU, 2*AU), (3*AU, 3*AU)]  # Sample (x,y) to plot
    #optional_points_to_plot = [(1*AU, 1*AU, 0.5), (2*AU, 2*AU, 1.8), (3*AU, 3*AU, 3.2)]  # (x,y,heading)

    return xy_estimate, other, optional_points_to_plot


def next_angle(solar_system, percent_illuminated_measurements, percent_illuminated_sense_func,
               distance, steering, other=None):
    """
    Gets the next angle at which to send out an sos message to the home planet,
    the last planet in the solar system.
    This is the function you will have to write for part B.
    :param solar_system: SolarSystem
        A model of the solar system containing the sun and planets as Bodys (contains positions, velocities, and masses)
        Planets are listed in order from closest to furthest from the sun
    :param percent_illuminated_measurements: List[float]
        A list of floating point number from 0 to 100 representing
        the measured percent illumination of each planet in order from closest to furthest to sun
        as seen by the target satellite.
    :param percent_illuminated_sense_func: Func
        A function that takes in (x,y) and outputs the list of percent illuminated measurements of each planet
        as would be seen by satellite at that (x,y) location.
    :param distance: float
        The target satellite's motion distance
    :param steering: float
        The target satellite's motion steering
    :param other: any
        This is initially None, but if you return an OTHER from
        this function call, it will be passed back to you the next time it is
        called, so that you can use it to keep track of important information
        over time. (We suggest you use a dictionary so that you can store as many
        different named values as you want.)
    :return:
        bearing: float. The absolute angle from the satellite to send an sos message between -pi and pi
        xy_estimate: Tuple[float, float]. The (x,y) estimate of the target satellite at the next timestep
        other: any. Any additional information you'd like to pass between invocations of this function
        optional_points_to_plot: List[Tuple[float, float, float]].
            A list of tuples like (x,y,h) to plot for the visualization
    """

    # __________________________

    # Initalizaion
    if other is None:
        P = []
        for _ in range(10000):
            x = random.uniform(-4 * AU, 4 * AU)
            y = random.uniform(-4 * AU, 4 * AU)
            theta = (atan2(y, x) + pi / 2) % (2 * pi)
            P.append((x, y, theta))
    else:
        P = other["particles"]


    # Imporatance Weights - Access to measurments or ( also have planets locaiotn too) & funciton to produce measurments for particles 
    W = []
    for x, y, theta in P:
        percent_illuminated_predicted = percent_illuminated_sense_func(x, y) #predict
        total_error = 0.0

        for measured, predicted_value in zip(percent_illuminated_measurements, percent_illuminated_predicted):
            total_error += abs(predicted_value - measured)

        W.append(1.0 / (1.0 + total_error))

    # Resample - Resample Wheel 
    N = len(P)

    resampled = []

    index = int(random.random() * N % N)
    beta = 0.0
    max_weight = max(W)
    if max_weight == 0.0:
        max_weight = 1.0
        W = [1.0] * N

    for _ in P:
        beta += random.random() * 2.0 * max_weight

        while beta > W[index]:
            beta -= W[index]
            index=(index+ 1) % N

        resampled.append(P[index])

    # Fuzzing - Change percentage of them change X, Y and orentation fuzzy 8% noise and 40% of total particles
    New_P = []
    postion_s = .01 * AU
    heading_s = .01 
    for x, y, theta in resampled:
        if random.random() < .4:
            x += random.gauss(0, postion_s)
            y += random.gauss(0, postion_s)
            theta = (theta + random.gauss(0, heading_s)) % (2 * pi)
        New_P.append((x, y, theta))



    # Motion - Counterclockwise orbit gaussing noise, bicycle motion model
    satellite_length = 10.2
    tolerance = .001
    turn = tan(steering) * distance / satellite_length

    New_P2 = []
    for X, Y, theta in New_P:
        if abs(turn) < tolerance:
            X = X + distance * cos(theta)
            Y = Y + distance * sin(theta)
            theta = (theta + turn) % (2 * pi)
        else:
            radius = distance / turn
            cx = X - sin(theta) * radius
            cy = Y + cos(theta) * radius
            theta = (theta + turn) % (2 * pi)
            X = cx + sin(theta) * radius
            Y = cy - cos(theta) * radius

        New_P2.append((X, Y, theta))


    # Estimate - Avg of all the particles 
    xy_estimate = (sum(X for X, Y, theta in New_P2) / len(New_P2), sum(Y for X, Y, theta in New_P2) / len(New_P2))
    other = {"particles": New_P2}
    optional_points_to_plot = New_P2[::500]

    # Tansmit Message - last Planet and xy estimate
    bearing = atan2(solar_system.planets[-1].r[1] - xy_estimate[1], solar_system.planets[-1].r[0] - xy_estimate[0])





    # __________________________


    # At what angle to send an SOS message this timestep
    #bearing = 0.0
    

    return bearing, xy_estimate, other, optional_points_to_plot


def who_am_i():
    # Please specify your GT login ID in the whoami variable (ex: jsmith326).
    whoami = 'estralka3'
    return whoami


# Better Results usign uniform randomness vs gaussinan 
# Use the mean of particles reccomened 
# Particle Impoversement - when particle distribution collapese around teh wrong area
# Partile Degenericy - Very small sigma, only a few particles with alot of weight (solve with resampling)
# could try to implement Effective sampel size add more particles in when < M/4

# Use Bicycle model to mimic the movement of the particles 
# Sun assume it is (0,0)
# No need to nomalize the weights
# Look at last slide of bycicle motion 101 
# bicycle miotn is not straight line motion 
# trianlges show orentiona
# atan2  consider teh quandrants the particles need to be in quadrants
# do not add noise back in Fuzzy is only noise 

# B 
# Need to know the home planet and statallite loccation home palant is outermost 
# Multipe measurements - Loop end result in a list of measurements to consolidate prediciton Weight
# No Gravity Measurment 
# Angle is different 
# q6 PS3 stack errors (product?) for first 4 planets last one is home planet
# 