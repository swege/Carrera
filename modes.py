#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains different game modes."""
from datetime import datetime, timedelta

from utils import trim_time

class BaseMode(object):
    """Baseclass for all modes."""

    def __init__(self, device, ui, players, *args, **kwargs):
        if len(players) not in [1, 2, 3, 4]:
            raise ValueError('You need to pass 2, 3 or 4 players in a list')
        self.device = device
        self.ui = ui
        self.finished = False
        self.canceled = False
        self.players = players
        self.configure(*args, **kwargs)

    def configure(self, *args, **kwargs):
        """Make further configurations.

        Overwrite this method if you want to use more arguments.
        Additional arguments to __init__ will be passed to this method after
        the other arguments (device, ui, players) have been processed.

        """

    def cancel(self):
        """Cancel a match."""
        self.finished = True
        self.canceled = True

    def run(self):
        """Give control to the gamemode until the race is finished."""
        self.finished = False
        self.device.power_off(-1)
        self.start_time = datetime.now()
        countdown = True
        while not self.finished:
            now = self.now = datetime.now()
            delta = datetime.now() - self.start_time
            if countdown:
                self.device.traffic_lights = delta.seconds
                if delta > timedelta(seconds=4):
                    countdown = False
                    self.start_time = datetime.now()
                    self.device.traffic_lights = 4
                    for player in self.players:
                        player.last_time = player.last_pass = now
                    self.device.power_on(*[x.track for x in self.players if not x.disabled])
                self.ui.update()
                continue
            sensor_state = self.device.sensor_state()
            for sensor, player in zip(sensor_state, self.players):
                if sensor:
                    self._on_player_passed_line(player)
                if not player.disabled:
                    player.total_time = now - self.start_time
            self.check_conditions()
            self.ui.update()

    def save(self):
        """Write the acquired data to the database. (not implemented)"""

    def _on_player_passed_line(self, player):
        if not player.passed_start:
            player.passed_start = True
            player.last_pass = self.now
            return
        if not player.disabled and self.now - player.last_pass > timedelta(seconds=1):
            player.times.append(self.now - player.last_time)
            player.last_time = self.now
        player.last_pass = self.now
        self.on_player_passed_line(player)

    def on_player_passed_line(self, player):
        """Called when a car passes the sensor at the line and is not yet finished.

        Round time will be saved before calling and is accessable via the
        player object.

        """

    def check_conditions(self):
        """Check for winning conditions.

        Overwrite this method in your gamemode to check for certain conditions,
        e.g. timelimits. Called after every sensor polling.

        """

    @property
    def finished(self):
        return self._finished

    @finished.setter
    def finished(self, value):
        self._finished = value
        if value == True:
            self.device.power_off(-1)
            for player in self.players:
                player.finished = True

class Match(BaseMode):

    def configure(self, rounds):
        """Set the number of rounds needed to pass the race."""
        self.rounds = rounds

    def on_player_passed_line(self, player):
        """Set player.finished and his rank if the player made all rounds."""
        if len(player.times) >= self.rounds:
            player.finished = True
            player.rank = len([x for x in self.players if x.finished])
        if player.rank == len(self.players):
            self.finished = True

    def check_conditions(self):
        """Check if all players passed or are disabled."""
        if len([x for x in self.players if x.disabled]) == len(self.players):
            self.finished = True

class TimeAttack(BaseMode):

    def configure(self, seconds):
        """Set the timelimit (in seconds)"""
        self.seconds = seconds

    def check_conditions(self):
        """Check if the time is over

        Used to power off the tracks.

        """
        if self.now - self.start_time >= timedelta(seconds=self.seconds):
            self.finished = True
        if len([x for x in self.players if x.disabled]) == len(self.players):
            self.finished = True

    def on_player_passed_line(self, player):
        """Update the player rank on line pass."""
        prev_rank = player.rank
        prev_rounds = player.rounds - 1
        rank = len(self.players)
        for p in self.players:
            if p.rounds < player.rounds:
                rank -= 1
        player.rank = rank
        for p in self.players:
            if p.rank == 0:
                continue
            if p.rounds == prev_rounds and p.rank < prev_rank:
                p.rank += 1

class KnockOut(BaseMode):

    def on_player_passed_line(self, player):
        """Check if the player is next to last.

        If so, set the last player to finish and give him his rank.

        """
        n = 0
        for p in self.players:
            if p.rounds >= player.rounds:
                n += 1
        if player.rounds + n == len(self.players):
            rank = len(self.players)
            if n == 1:
                player.rank = 1
                player.finished = True
            for p in sorted(self.players, key=lambda x: x.rounds):
                if p.rounds < player.rounds:
                    p.rank = rank
                    p.finished = True
                rank -= 1

        if len([x for x in self.players if not x.disabled]) == 0:
            self.finished = True

    def check_conditions(self):
        """Check if all players are finished"""
        if len([x for x in self.players if x.disabled]) == len(self.players):
            self.finished = True

class Training(BaseMode):

    def configure(self, rounds):
        """Set the number of rounds a player may practise."""
        self.rounds = rounds

    def on_player_passed_line(self, player):
        """Check if the player made all his rounds."""
        now = datetime.now()
        if player.rounds >= self.rounds:
            player.finished = True

    def reset_player(self, player):
        """Reset the times of a player for the next training."""
        player.times = []
        player.finished = False
