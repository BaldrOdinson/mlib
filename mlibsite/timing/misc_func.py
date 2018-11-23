#! /usr/bin/env python
# -*- coding: utf-8 -*-
def time_left(steps, timing_duration):
    """
    Высчитываем доступное для добавления этапа время.
    Берем длительность занятия из MethodTiming.duration
    Складываем длительности каждого этапа
    и возвращаем разницу
    """
    busy_time = 0
    for step in steps:
        busy_time += step.step_duration
    return timing_duration - busy_time
