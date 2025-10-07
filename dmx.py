import time
import threading
from pyftdi.ftdi import Ftdi
import numpy as np

def map_to(val, min, max):
    assert max > min
    val = np.clip(val, 0, 1)
    return int(round(min + val * (max - min)))

def show_devices():
    """
    List available FTDI devices
    """

    Ftdi.show_devices()

class DMXUniverse:
    """
    Interface to an ENTTEC OpenDMX (FTDI) DMX interface
    """
    def __init__(self, url='ftdi://ftdi:232:AL6E8JFW/1'):
        self.url = url
        try:
            self.port = Ftdi.create_from_url(url)
            self.port.reset()
            self.port.set_baudrate(baudrate=250000)
            self.port.set_line_property(bits=8, stopbit=2, parity='N', break_=False)
        except ValueError:
            self.port = None
            assert "Port error"
        assert self.port.is_connected

        # The 0th byte must be 0 (start code)
        # 513 bytes are sent in total
        self.data = bytearray(513 * [0])

        self.devices = []

    def __del__(self):
        self.port.close()

    def __setitem__(self, idx, val):
        assert (idx >= 1)
        assert (idx <= 512)
        assert isinstance(val, int)
        assert (val >= 0 and val <= 255)
        self.data[idx] = val

    def set_float(self, start_chan, chan_no, val, min=0, max=255):
        assert (chan_no >= 1)

        # If val is an array of values
        if hasattr(val, '__len__'):
            for i in range(len(val)):
                int_val = map_to(val[i], min, max)
                self[start_chan + chan_no - 1 + i] = int_val
        else:
            int_val = map_to(val, min, max)
            self[start_chan + chan_no - 1] = int_val

    def add_device(self, device):
        # Check for partial channel overlaps between devices, which
        # are probably an error
        for other in self.devices:
            # Two devices with the same type and the same channel are probably ok
            if device.chan_no == other.chan_no and type(device) == type(other):
                continue

            if device.chan_overlap(other):
                raise Exception('partial channel overlap between devices "{}" and "{}"'.format(device.name, other.name))

        self.devices.append(device)
        return device

    def start_dmx_thread(self, interval):
        """
        Thread to write channel data to the output port
        """

        def dmx_thread_fn():
            base_time = time.time()
            next_time = 0
            priv_time = time.time()
            fps = []
            counter = 0
            while self.dmx_thread_run:
                for dev in self.devices:
                    dev.update(self)

                self.port.set_break(True)
                self.port.set_break(False)
                self.port.write_data(self.data)
                next_time = ((base_time - time.time()) % interval) or interval
                fps.append(1 / (time.time() - priv_time))
                priv_time = time.time()
                counter += 1
                if (len(fps) > 5): del fps[0]
                if (counter % 100 == 0): print("fps: " + str(np.average(fps)))
                # The maximum update rate for the Enttec OpenDMX is 40Hz
                time.sleep(next_time)

        dmx_thread = threading.Thread(target=dmx_thread_fn, args=(), daemon=True)
        self.dmx_thread_run = self.port is not None
        dmx_thread.start()

    def stop_dmx_thread(self):
        if not "dmx_thread" in self: return
        self.dmx_thread_run = False

class DMXDevice:
    def __init__(self, name, chan_no, num_chans):
        assert (chan_no >= 1)
        self.name = name
        self.chan_no = chan_no
        self.num_chans = num_chans

    def chan_overlap(this, that):
        """
        Check if two devices have overlapping channels
        """

        this_last = this.chan_no + (this.num_chans - 1)
        that_last = that.chan_no + (that.num_chans - 1)

        return (
            (this.chan_no >= that.chan_no and this.chan_no <= that_last) or
            (that.chan_no >= this.chan_no and that.chan_no <= this_last)
        )

    def update(self, dmx: DMXUniverse):
        raise NotImplementedError
