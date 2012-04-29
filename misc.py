#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta

class Player(object):

    def __init__(self, track, device, name):
        self.track = track
        self.device = device
        self.name = name
        self.times = []
        self.finished = False
        self.total_time = timedelta(seconds=0)
        self.rank = 0

    @property
    def rounds(self):
        return len(self.times)

    @property
    def total_seconds(self):
        return self.total_time.total_seconds()

    @property
    def finished(self):
        return self._finished

    @finished.setter
    def finished(self, value):
        self._finished = value
        if value:
            self.device.power_off(self.track)
