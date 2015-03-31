import time
import smbus

__all__ = ['ADS1115']

from I2C import Adafruit_I2C

# ===========================================================================
# ADS1115 Class
# ===========================================================================
class ADS1115:
    i2c = None

    # IC Identifiers
    __IC_ADS1115 = 0x01

    # Config Register
    __ADS1115_REG_CONFIG_DR_8SPS      = 0x0000  # 8 samples per second
    __ADS1115_REG_CONFIG_DR_16SPS     = 0x0020  # 16 samples per second
    __ADS1115_REG_CONFIG_DR_32SPS     = 0x0040  # 32 samples per second
    __ADS1115_REG_CONFIG_DR_64SPS     = 0x0060  # 64 samples per second
    __ADS1115_REG_CONFIG_DR_128SPS    = 0x0080  # 128 samples per second
    __ADS1115_REG_CONFIG_DR_250SPS    = 0x00A0  # 250 samples per second (default)
    __ADS1115_REG_CONFIG_DR_475SPS    = 0x00C0  # 475 samples per second
    __ADS1115_REG_CONFIG_DR_860SPS    = 0x00E0  # 860 samples per second

    __ADS1015_REG_CONFIG_CQUE_MASK    = 0x0003
    __ADS1015_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
    __ADS1015_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
    __ADS1015_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
    __ADS1015_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

    __ADS1015_REG_CONFIG_CMODE_MASK   = 0x0010
    __ADS1015_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
    __ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

    __ADS1015_REG_CONFIG_CPOL_MASK    = 0x0008
    __ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
    __ADS1015_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

    __ADS1015_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
    __ADS1015_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
    __ADS1015_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

    __ADS1015_REG_CONFIG_MODE_MASK    = 0x0100
    __ADS1015_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
    __ADS1015_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

    __ADS1015_REG_CONFIG_PGA_MASK     = 0x0E00
    __ADS1015_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
    __ADS1015_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
    __ADS1015_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
    __ADS1015_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
    __ADS1015_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
    __ADS1015_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

    __ADS1015_REG_CONFIG_MUX_MASK     = 0x7000
    __ADS1015_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
    __ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

     # Config Register
    __ADS1015_REG_CONFIG_OS_MASK      = 0x8000
    __ADS1015_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
    __ADS1015_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
    __ADS1015_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion

    # Pointer Register
    __ADS1015_REG_POINTER_MASK        = 0x03
    __ADS1015_REG_POINTER_CONVERT     = 0x00
    __ADS1015_REG_POINTER_CONFIG      = 0x01
    __ADS1015_REG_POINTER_LOWTHRESH   = 0x02
    __ADS1015_REG_POINTER_HITHRESH    = 0x03
    
    # Dictionaries with the sampling speed values
    # These simplify and clean the code (avoid the abuse of if/elif/else clauses)
    spsADS1115 = {
        8:__ADS1115_REG_CONFIG_DR_8SPS,
        16:__ADS1115_REG_CONFIG_DR_16SPS,
        32:__ADS1115_REG_CONFIG_DR_32SPS,
        64:__ADS1115_REG_CONFIG_DR_64SPS,
        128:__ADS1115_REG_CONFIG_DR_128SPS,
        250:__ADS1115_REG_CONFIG_DR_250SPS,
        475:__ADS1115_REG_CONFIG_DR_475SPS,
        860:__ADS1115_REG_CONFIG_DR_860SPS
        }   

    # Dictionariy with the programable gains
    pgaADS1x15 = {
        6144:__ADS1015_REG_CONFIG_PGA_6_144V,
        4096:__ADS1015_REG_CONFIG_PGA_4_096V,
        2048:__ADS1015_REG_CONFIG_PGA_2_048V,
        1024:__ADS1015_REG_CONFIG_PGA_1_024V,
        512:__ADS1015_REG_CONFIG_PGA_0_512V,
        256:__ADS1015_REG_CONFIG_PGA_0_256V
        }  

    # Constructor
    def __init__(self, address=0x48, ic=__IC_ADS1115, debug=False):
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.debug = debug

        # Make sure the IC specified is valid
        if (ic > self.__IC_ADS1115):
            return -1
        else:
            self.ic = ic
            
        # Set pga value, so that getLastConversionResult() can use it,
        # any function that accepts a pga value must update this.
        self.pga = 6144

    def readADCSingleEnded(self, channel=0, pga=6144, sps=250):
        ''' 
            Gets a single-ended ADC reading from the specified channel in mV. 
            The sample rate for this mode (single-shot) can be used to lower the noise 
            (low sps) or to lower the power consumption (high sps) by duty cycling, 
            see datasheet page 14 for more info. 
            The pga must be given in mV, see page 13 for the supported values. 
        '''
    
        # With invalid channel return -1
        if (channel > 3):
            return -1
    
        # Disable comparator, Non-latching, Alert/Rdy active low
        # traditional comparator, single-shot mode
        config = self.__ADS1015_REG_CONFIG_CQUE_NONE    | \
                 self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                 self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                 self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                 self.__ADS1015_REG_CONFIG_MODE_SINGLE    

        # Set sample per seconds, defaults to 250sps
        config |= self.spsADS1115.setdefault(sps, self.__ADS1115_REG_CONFIG_DR_250SPS)

        # Set PGA/voltage range, defaults to +-6.144V  
        config |= self.pgaADS1x15.setdefault(pga, self.__ADS1015_REG_CONFIG_PGA_6_144V)
        self.pga = pga

        # Set the channel to be converted
        if channel == 3:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
        elif channel == 2:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
        elif channel == 1:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
        else:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

        # Set 'start single-conversion' bit
        config |= self.__ADS1015_REG_CONFIG_OS_SINGLE

        # Write config register to the ADC
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        self.i2c.writeList(self.__ADS1015_REG_POINTER_CONFIG, bytes)

        # Wait for the ADC conversion to complete
        # The minimum delay depends on the sps: delay >= 1/sps
        # We add 0.1ms to be sure
        delay = 1.0/sps+0.0001
        time.sleep(delay)

        # Read the conversion results
        result = self.i2c.readList(self.__ADS1015_REG_POINTER_CONVERT, 2)
        # Return a mV value for the ADS1115
        # (Take signed values into account as well)
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            return (val - 0xFFFF)*pga/32768.0
        else:
            return ( (result[0] << 8) | (result[1]) )*pga/32768.0


# ===========================================================================
# Adafruit_I2C Class
# ===========================================================================

class Adafruit_I2C(object):

    @staticmethod
    def getPiRevision():
        "Gets the version number of the Raspberry Pi board"
        # Revision list available at: http://elinux.org/RPi_HardwareHistory#Board_Revision_History
        try:
            with open('/proc/cpuinfo', 'r') as infile:
                for line in infile:
                    # Match a line of the form "Revision : 0002" while ignoring extra
                    # info in front of the revsion (like 1000 when the Pi was over-volted).
                    match = re.match('Revision\s+:\s+.*(\w{4})$', line)
                    if match and match.group(1) in ['0000', '0002', '0003']:
                        # Return revision 1 if revision ends with 0000, 0002 or 0003.
                        return 1
                    elif match:
                        # Assume revision 2 if revision ends with any other 4 chars.
                        return 2
                    # Couldn't find the revision, assume revision 0 like older code for compatibility.
            return 0
        except:
            return 0

    @staticmethod
    def getPiI2CBusNumber():
        # Gets the I2C bus number /dev/i2c#
        return 1 if Adafruit_I2C.getPiRevision() > 1 else 0

    def __init__(self, address, busnum=-1, debug=False):
        self.address = address
        # By default, the correct I2C bus is auto-detected using /proc/cpuinfo
        # Alternatively, you can hard-code the bus version below:
        # self.bus = smbus.SMBus(0); # Force I2C0 (early 256MB Pi's)
        # self.bus = smbus.SMBus(1); # Force I2C1 (512MB Pi's)
        self.bus = smbus.SMBus(busnum if busnum >= 0 else Adafruit_I2C.getPiI2CBusNumber())
        self.debug = debug

    def reverseByteOrder(self, data):
        ''' Reverses the byte order of an int (16-bit) or long (32-bit) value '''
        byteCount = len(hex(data)[2:].replace('L','')[::2])
        val       = 0
        for i in range(byteCount):
            val    = (val << 8) | (data & 0xff)
            data >>= 8
        return val

    def errMsg(self):
        print ("Error accessing 0x%02X: Check your I2C address" % self.address)
        return -1

    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        try:
            self.bus.write_byte_data(self.address, reg, value)
            if self.debug:
                print ("I2C: Wrote 0x%02X to register 0x%02X" % (value, reg))
        except IOError:
            return self.errMsg()

    def write16(self, reg, value):
        "Writes a 16-bit value to the specified register/address pair"
        try:
            self.bus.write_word_data(self.address, reg, value)
            if self.debug:
                print ("I2C: Wrote 0x%02X to register pair 0x%02X,0x%02X" % (value, reg, reg+1))
        except IOError:
            return self.errMsg()

    def writeRaw8(self, value):
        "Writes an 8-bit value on the bus"
        try:
            self.bus.write_byte(self.address, value)
            if self.debug:
                print ("I2C: Wrote 0x%02X" % value)
        except IOError:
            return self.errMsg()

    def writeList(self, reg, list):
        "Writes an array of bytes using I2C format"
        try:
            if self.debug:
                print ("I2C: Writing list to register 0x%02X:" % reg)
                print (list)
            self.bus.write_i2c_block_data(self.address, reg, list)
        except IOError:
            return self.errMsg()

    def readList(self, reg, length):
        "Read a list of bytes from the I2C device"
        try:
            results = self.bus.read_i2c_block_data(self.address, reg, length)
            if self.debug:
                print ("I2C: Device 0x%02X returned the following from reg 0x%02X" % (self.address, reg))
                print (results)
            return results
        except IOError:
            return self.errMsg()

    def readU8(self, reg):
        "Read an unsigned byte from the I2C device"
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if self.debug:
                print ("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
            return (result)
        except IOError:
            return self.errMsg()

    def readS8(self, reg):
        "Reads a signed byte from the I2C device"
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if result > 127: result -= 256
            if self.debug:
                print ("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
            return result
        except IOError:
            return self.errMsg()

    def readU16(self, reg, little_endian=True):
        "Reads an unsigned 16-bit value from the I2C device"
        try:
            result = self.bus.read_word_data(self.address,reg)
            # Swap bytes if using big endian because read_word_data assumes little 
            # endian on ARM (little endian) systems.
            if not little_endian:
                result = ((result << 8) & 0xFF00) + (result >> 8)
            if (self.debug):
                print ("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, result & 0xFFFF, reg))
            return result
        except IOError:
            return self.errMsg()

    def readS16(self, reg, little_endian=True):
        "Reads a signed 16-bit value from the I2C device"
        try:
            result = self.readU16(reg,little_endian)
            if result > 32767: result -= 65536
            return result
        except IOError:
            return self.errMsg()