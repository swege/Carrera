"""This module contains the devices to communicate with the track."""

import ue9

class UE9(object):

    def __init__(self):
        self.device = ue9.UE9()
        self.device.feedback(EIOMask=255, EIOState=0, EIODir=0b11110000)

    @property
    def player(self, num):
        pass

    def enable_power(self, *tracks):
        """Enables the power for the given tracks.

        All other tracks will not be affected.

        Track | Port
        0     | EIO4
        1     | EIO5
        2     | EIO6
        3     | EIO7

        """
        mask = 0
        for track in tracks:
            mask |= 1 << (track + 4)
        self.device.feedback(EIOMask=mask, EIOState=240, EIODir=0b11110000)

    def disable_power(self, *tracks):
        """Disables the power for the given tracks.

        All other tracks will not be affected.

        Track | Port
        0     | EIO4
        1     | EIO5
        2     | EIO6
        3     | EIO7

        """
        mask = 0
        for track in tracks:
            mask |= 1 << (track + 4)
        self.device.feedback(EIOMask=mask, EIOState=0, EIODir=0b11110000)

    #def traffic_light(self):
    #    pass

    def track_state(self, num):
        state = self.device.feedback()['EIOState']
        return [not state & 0b1, not state & 0b10,
                not state & 0b100, not state & 0b1000]
