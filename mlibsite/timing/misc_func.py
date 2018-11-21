def time_left(steps, timing_duration):
    busy_time = 0
    for step in steps:
        busy_time += step.step_duration
    return timing_duration - busy_time
