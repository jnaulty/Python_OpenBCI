"""

Core OpenBCI object for handling connections and samples from the board.
CogTechBCI DevTeam
EXAMPLE USE:
def handle_sample(sample):
  print(sample.channels)

board = OpenBCIBoard()
board.print_register_settings()
board.start(handle_sample)



"""


import serial
import struct
import logging
import numpy as np

#import traits.api as t
from pyface.timer.api import do_after

READ_INTERVAL_MS = 250
START_BYTE = bytes(0xA0)  # start of data packet
END_BYTE = bytes(0xC0)  # end of data packet

TIMESERIES_LENGTH = 4500
MIN_HISTORY_LENGTH = 4500
MAX_HISTORY_LENGTH = 65000

# Hardware/Calibration parameters. ###########
gain_fac = 24.0
full_scale_V = 4.5 / gain_fac
correction_factor = 2.0  # Need to revisit why we need this factor, but based on
                        # physical measurements, it is necessary
creare_volts_per_count = full_scale_V / (2.0 ** 24) * correction_factor
creare_volts_per_FS = creare_volts_per_count * 2 ** (24 - 1)  # per full scale: +/- 1.0
#############################

SAMPLE_RATE = 250.0  # Hz
CHANNELS = 8

i_sample = 0


class OpenBCIBoard(object):
  """

  Handle a connection to an OpenBCI board.

  Args:
    port: The port to connect to.
    baud: The baud of the serial connection.

  """

  def __init__(self, port='COM9', baud=115200):
    self.ser = serial.Serial(port, baud)
    self.dump_registry_data()
    self.streaming = False
    self.filtering_data = False
    self.channels = 8
    self.timeseries = np.zeros([1, self.channels+1])
    history = []

  def connect(self, callback):
    """

    Start handling streaming data from the board. Call a provided callback
    for every single sample that is processed.

    Args:
      callback: A callback function that will receive a single argument of the
          OpenBCISample object captured.
    
    """
    if not self.streaming:
      # Send an 'x' to the board to tell it to start streaming us text.
      self.ser.write('s\n')
      self.ser.write('b\n')
      # Dump the first line that says "Arduino: Starting..."
      self.ser.readline()
      self.streaming = True
    if self.filtering_data:
      print 'Enabling filter'
      self.ser.write('f')
      self.ser.readline()
      self.ser.readline()
    while self.streaming:
      binary_data = self._read_serial_binary()
      sample = OpenBCISample(binary_data)
      callback(sample)
      

  """

  Turn streaming off without disconnecting from the board

  """
  def stop(self):
    self.streaming = False

  def disconnect(self):
    self.ser.close()
    self.streaming = False

  """ 


      SETTINGS AND HELPERS 


  """

  def dump_registry_data(self):
    """
    
    When starting the connection, dump all the debug data until 
    we get to a line with something about streaming data.
    
    """
    line = ''
    while 'begin streaming data' not in line:
      line = self.ser.readline()  

  def print_register_settings(self):
    self.ser.write('?')
    for number in xrange(0, 24):
      print(self.ser.readline())

  """

  Adds a filter at 60hz to cancel out ambient electrical noise.
  
  """
  def enable_filters(self):
    self.ser.write('f')
    self.filtering_data = True

  def disable_filters(self):
    self.ser.write('g')
    self.filtering_data = False;

  """
  Args:
    channel - An integer from 1-8 incidcating which channel to set. 
    toogle_position - An boolean indicating what position the channel should be set to.
  
  ***NEEDS TO BE TESTED***
  ***TODO: Change cascading ifs to mapping functions

  """
  def set_channel(self, channel, toggle_position):
    #Commands to set toggle to on position
    if toggle_position == 1: 
      if channel is 1:
        self.ser.write('q')
      if channel is 1:
        self.ser.write('w')
      if channel is 1:
        self.ser.write('e')
      if channel is 1:
        self.ser.write('r')
      if channel is 1:
        self.ser.write('t')
      if channel is 1:
        self.ser.write('y')
      if channel is 1:
        self.ser.write('u')
      if channel is 1:
        self.ser.write('i')
    #Commands to set toggle to off position
    elif toggle_position == 0: 
      if channel is 1:
        self.ser.write('1')
      if channel is 1:
        self.ser.write('2')
      if channel is 1:
        self.ser.write('3')
      if channel is 1:
        self.ser.write('4')
      if channel is 1:
        self.ser.write('5')
      if channel is 1:
        self.ser.write('6')
      if channel is 1:
        self.ser.write('7')
      if channel is 1:
        self.ser.write('8')
  def _read_serial_binary(self, max_bytes_to_skip=3000):
        """
        Returns (and waits if necessary) for the next binary packet. The
        packet is returned as an array [sample_index, data1, data2, ... datan].
        
        RAISES
        ------
        RuntimeError : if it has to skip to many bytes.
        
        serial.SerialTimeoutException : if there isn't enough data to read.
        """
        global i_sample
        def read(n):
            val = self.ser.read(n)
            # print bytes(val),
            return val

        n_int_32 = self.channels + 1

        # Look for end of packet.
        for i in xrange(max_bytes_to_skip):
            val = read(1)
            if not val:
                if not self.ser.inWaiting():
                    logging.warn('Device appears to be stalled. Restarting...')
                    self.ser.write('b\n')  # restart if it's stopped...
                    time.sleep(.100)
                    continue
            # self.serial_port.write('b\n') , s , x
            # self.serial_port.inWaiting()
            if bytes(struct.unpack('B', val)[0]) == END_BYTE:
                # Look for the beginning of the packet, which should be next
                val = read(1)
                if bytes(struct.unpack('B', val)[0]) == START_BYTE:
                    if i > 0:
                        logging.warn("Had to skip %d bytes before finding stop/start bytes." % i)
                    # Read the number of bytes
                    val = read(1)
                    n_bytes = struct.unpack('B', val)[0]
                    if n_bytes == n_int_32 * 4:
                        # Read the rest of the packet.
                        val = read(4)
                        sample_index = struct.unpack('i', val)[0]
#                         if sample_index != 0:
#                             logging.warn("WARNING: sample_index should be zero, but sample_index == %d" % sample_index)
                        # NOTE: using i_sample, a surrogate sample count.
                        t_value = i_sample / float(SAMPLE_RATE)  # sample_index / float(SAMPLE_RATE)
                        i_sample += 1
                        val = read(4 * (n_int_32 - 1))
                        data = struct.unpack('i' * (n_int_32 - 1), val)
                        data = np.array(data) / (2. ** (24 - 1));  # make so full scale is +/- 1.0
                        # should set missing data to np.NAN here, maybe by testing for zeros..
                        # data[np.logical_not(self.channel_array)] = np.NAN  # set deactivated channels to NAN.
                        data[data == 0] = np.NAN
                        # print data
                        return np.concatenate([[t_value], data])  # A list [sample_index, data1, data2, ... datan]
                    elif n_bytes > 0:
                        print "Warning: Message length is the wrong size! %d should be %d" % (n_bytes, n_int_32 * 4)
                        # Clear the buffer of those bytes.
                        _ = read(n_bytes)
                    else:
                        raise ValueError("Warning: Message length is the wrong size! %d should be %d" % (n_bytes, n_int_32 * 4))
        raise RuntimeError("Maximum number of bytes skipped looking for binary packet (%d)" % max_bytes_to_skip)
  def read_input_buffer(self):
        """
        Reads all binary data in input buffer to arrays. If there is new data
        available, it updates the timeseries array and fires a data_changed event.
        
        Returns
        -------
        True :
            if the device is functioning properly and data readout should continue, 
        False :
            if data readout should stop.
        """

        if not self.connected:
            return False

        data_changed = False

        # Read all the data...
        while self.ser.inWaiting() > (self.channels + 1 * 4 + 3):

            # New data is raw, as returned from the microprocessor, but scaled -1 -> +1.
            # Here, we scale it -> uV.
            new_data = self._read_serial_binary()

            ########## Uncomment this next line for debugging purposes. #######
            # new_data[1:] = self._read_mock_data()  # overwrites real data with mock data.

            # Now, we scale from -1 -> +1, to uV:
            new_data[1:] = new_data[1:] * creare_volts_per_FS * 1.0e6  # now uV.
            self.history.append(new_data)
            data_changed = True

        if data_changed:
            # If the history gets too long, cull it:
            if len(self.history) > MAX_HISTORY_LENGTH:
                self.history = self.history[-MIN_HISTORY_LENGTH:]

            # Update the numpy timeseries array.
            self.timeseries = np.array(self.history[-TIMESERIES_LENGTH:])

            # Infer which channels are on/off... we don't keep track of this
            #  internally b/c it's safer to infer it from the Arduino output.
            [self.channel_1_enabled,
             self.channel_2_enabled,
             self.channel_3_enabled,
             self.channel_4_enabled,
             self.channel_5_enabled,
             self.channel_6_enabled,
             self.channel_7_enabled,
             self.channel_8_enabled] = np.logical_not(np.isnan(self.history[-1][1:])).tolist()
            self.data_changed = True  # fire data_changed event.

        return True

  
class OpenBCISample(object):
  """Object encapulsating a single sample from the OpenBCI board."""

  def __init__(self, data):
    #parts = data.rstrip().split(', ')
    self.id = parts[0]
    self.channels = [1:]
    #for c in xrange(1, len(parts) - 1):
    #  self.channels.append(int(parts[c]))
    # This is fucking bullshit but I have to strip the comma from the last
    # sample because the board is returning a comma... wat?
    #self.channels.append(int(parts[len(parts) - 1][:-1])) 


