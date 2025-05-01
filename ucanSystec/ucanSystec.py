# -*- coding:utf-8 -*-
"""
ucanSystec.py
Author: SMFSW
Copyright (c) 2016-2018 SMFSW

The MIT License (MIT)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import os
import time
from sys import version_info
from ctypes import *

if version_info > (3,):
    long = int  # workaround for python 3 as long and int are unified


USBCAN_PRODCODE_PID_GW001 = 0x1100          # order code GW-001 "USB-CANmodul" outdated
USBCAN_PRODCODE_PID_GW002 = 0x1102          # order code GW-002 "USB-CANmodul" outdated
USBCAN_PRODCODE_PID_MULTIPORT = 0x1103      # order code 3004006/3404000/3404001 "Multiport CAN-to-USB"
USBCAN_PRODCODE_PID_BASIC = 0x1104          # order code 3204000/3204001 "USB-CANmodul1"
USBCAN_PRODCODE_PID_ADVANCED = 0x1105       # order code 3204002/3204003 "USB-CANmodul2"
USBCAN_PRODCODE_PID_USBCAN8 = 0x1107        # order code 3404000 "USB-CANmodul8"
USBCAN_PRODCODE_PID_USBCAN16 = 0x1109       # order code 3404001 "USB-CANmodul16"
USBCAN_PRODCODE_PID_RESERVED3 = 0x1110
USBCAN_PRODCODE_PID_ADVANCED_G4 = 0x1121    # order code ------- "USB-CANmodul2" 4th generation
USBCAN_PRODCODE_PID_BASIC_G4 = 0x1122       # order code 3204000 "USB-CANmodul1" 4th generation
USBCAN_PRODCODE_PID_RESERVED1 = 0x1144
USBCAN_PRODCODE_PID_RESERVED2 = 0x1145
USBCAN_PRODCODE_PID_RESERVED4 = 0x1162


baudrateSystec = {
    # --- bit rate values for 1st and 2nd generation (G1/G2) of USB-CANmodul ---
    "G2": {
        10000:      0x672f,     # CAN baud rate 10kBit/s
        20000:      0x532f,     # CAN baud rate 20kBit/s
        25000:      0x1f34,     # CAN baud rate 25kBit/s
        50000:      0x472f,     # CAN baud rate 50kBit/s
        100000:     0x432f,     # CAN baud rate 100kBit/s
        125000:     0x031c,     # CAN baud rate 125kBit/s
        250000:     0x011c,     # CAN baud rate 250kBit/s
        500000:     0x001c,     # CAN baud rate 500kBit/s
        800000:     0x0016,     # CAN baud rate 800kBit/s
        1000000:    0x0014,     # CAN baud rate 1MBit/s
    },
    # --- bit rate values for 3rd generation (G3) of USB-CANmodul ---
    "G3": {
        10000:      0x80771772,     # 10kBit/s 85.00% (CLK = 1, see L-487 since version 15)
        20000:      0x00771772,     # 20kBit/s 85.00%
        25000:      0x805F0051,     # 25kBit/s
        50000:      0x003B1741,     # 50kBit/s 87.50%
        100000:     0x001D1741,     # 100kBit/s 87.50%
        125000:     0x00170741,     # 125kBit/s 87.50%
        250000:     0x000B0741,     # 250kBit/s 87.50%
        500000:     0x00050741,     # 500kBit/s 87.50%
        800000:     0x00030731,     # 800kBit/s 86.67%
        1000000:    0x00020741,     # 1000kBit/s 87.50%
    },
    # --- bit rate values for 4th generation (G3) of USB-CANmodul ---
    "G4": {
        10000:      0x412F0077,     # 10kBit/s 85.00%
        20000:      0x412F003B,     # 20kBit/s 85.00%
        25000:      0x4016005f,     # 25kBit/s
        50000:      0x412F0017,     # 50kBit/s 85.00%
        100000:     0x412F000B,     # 100kBit/s 85.00%
        125000:     0x401C000B,     # 125kBit/s 87.50%
        250000:     0x401C0005,     # 250kBit/s 87.50%
        500000:     0x401C0002,     # 500kBit/s 87.50%
        800000:     0x401B0001,     # 800kBit/s 86.67%
        1000000:    0x40180001,     # 1000kBit/s 83.33
    },
}

# uses predefined extended values of baudrate for Multiport 3004006,
# USB-CANmodul1 3204000 or USB-CANmodul2 3204002 (do not use for GW-001/002)
USBCAN_BAUD_USE_BTREX = 0x0000
# USBCAN_BAUD_AUTO = 0xFFFF               # automatic baudrate detection (not implemented in this version)

# uses predefined values of BTR0/BTR1 for GW-001/002
USBCAN_BAUDEX_USE_BTR01 = 0x00000000
# USBCAN_BAUDEX_AUTO = 0xFFFFFFFF         # automatic baudrate detection (not implemented in this version)

# The Callback function is called, if certain events did occur.
# These Defines specify the event.
eventSystec = {
    "USBCAN_EVENT_INITHW":      0,  # the USB-CANmodul has been initialized
    "USBCAN_EVENT_INITCAN":     1,  # the CAN interface has been initialized
    "USBCAN_EVENT_RECIEVE":     2,  # a new CAN message has been received (for compatibility reason)
    "USBCAN_EVENT_RECEIVE":     2,  # a new CAN message has been received
    "USBCAN_EVENT_STATUS":      3,  # the error state in the module has changed
    "USBCAN_EVENT_DEINITCAN":   4,  # the CAN interface has been deinitialized (UcanDeinitCan() was called)
    "USBCAN_EVENT_DEINITHW":    5,  # the USB-CANmodul has been deinitialized (UcanDeinitHardware() was called)
    "USBCAN_EVENT_CONNECT":     6,  # a new USB-CANmodul has been connected
    "USBCAN_EVENT_DISCONNECT":  7,  # a USB-CANmodul has been disconnected
    "USBCAN_EVENT_FATALDISCON": 8,  # a USB-CANmodul has been disconnected during operation
    "USBCAN_EVENT_RESERVED1":   0x80
}

statusSystec = {
    "USBCAN_CANERR_OK":                 0x0000,     # No error occurred.
    "USBCAN_CANERR_XMTFULL":            0x0001,     # Transmit buffer in CAN controller is overrun.
    "USBCAN_CANERR_OVERRUN":            0x0002,     # Receive buffer in CAN controller is overrun.
    "USBCAN_CANERR_BUSLIGHT":           0x0004,     # Error limit 1 in CAN controller exceeded.The CAN controller is in state "Warning limit".
    "USBCAN_CANERR_BUSHEAVY":           0x0008,     # Error limit 2 in CAN controller exceeded.The CAN controller is in state "Error Passive".
    "USBCAN_CANERR_BUSOFF":             0x0010,     # CAN controller is in BUSOFF state.
    "USBCAN_CANERR_QOVERRUN":           0x0040,     # Receive buffer in module’s firmware is overrun.
    "USBCAN_CANERR_QXMTFULL":           0x0080,     # Transmit buffer in module’s firmware is overrun.
    "USBCAN_CANERR_REGTEST":            0x0100,     # Obsolete
    "USBCAN_CANERR_MEMTEST":            0x0200,     # Obsolete
    "USBCAN_CANERR_TXMSGLOST":          0x0400,     # A transmit CAN message was deleted automatically by the firmware because transmission timeout
    "USBCAN_USBERR_STATUS_TIMEOUT":     0x2000,     # The USB - CANmodul has been reset because the status channel was not polled each second.
    "USBCAN_USBERR_WATCHDOG_TIMEOUT":   0x4000,     # The USB - CANmodul has been reset because the internal watchdog was not triggered by the firmware.
}

retSystec = {
    "USBCAN_SUCCESSFUL":            0x00,
    "USBCAN_ERR_RESOURCE":          0x01,
    "USBCAN_ERR_MAXMODULES":        0x02,
    "USBCAN_ERR_HWINUSE":           0x03,
    "USBCAN_ERR_ILLVERSION":        0x04,
    "USBCAN_ERR_ILLHW":             0x05,
    "USBCAN_ERR_ILLHANDLE":         0x06,
    "USBCAN_ERR_ILLPARAM":          0x07,
    "USBCAN_ERR_BUSY":              0x08,
    "USBCAN_ERR_TIMEOUT":           0x09,
    "USBCAN_ERR_IOFAILED":          0x0a,
    "USBCAN_ERR_DLL_TXFULL":        0x0b,
    "USBCAN_ERR_MAXINSTANCES":      0x0c,
    "USBCAN_ERR_CANNOTINIT":        0x0d,
    "USBCAN_ERR_DISCONNECT":        0x0e,
    "USBCAN_ERR_NOHWCLASS":         0x0f,
    "USBCAN_ERR_ILLCHANNEL":        0x10,
    "USBCAN_ERR_ILLHWTYPE":         0x12,
    "USBCAN_ERRCMD_NOTEQU":         0x40,
    "USBCAN_ERRCMD_REGTST":         0x41,
    "USBCAN_ERRCMD_ILLCMD":         0x42,
    "USBCAN_ERRCMD_EEPROM":         0x43,
    "USBCAN_ERRCMD_ILLBDR":         0x47,
    "USBCAN_ERRCMD_NOTINIT":        0x48,
    "USBCAN_ERRCMD_ALREADYINIT":    0x49,
    "USBCAN_ERRCMD_ILLSUBCMD":      0x4a,
    "USBCAN_ERRCMD_ILLIDX":         0x4b,
    "USBCAN_ERRCMD_RUNNING":        0x4c,
    "USBCAN_WARN_NODATA":           0x80,
    "USBCAN_WARN_SYS_RXOVERRUN":    0x81,
    "USBCAN_WARN_DLL_RXOVERRUN":    0x82,
    "USBCAN_WARN_FW_TXOVERRUN":     0x85,
    "USBCAN_WARN_FW_RXOVERRUN":     0x86,
    "USBCAN_WARN_NULL_PTR":         0x90,
    "USBCAN_WARN_TXLIMIT":          0x91,
}


# noinspection PyPep8Naming
class tCanMsgStruct(Structure):
    """ Systec CAN message structure
    DWORD   m_dwID      # CAN identifier
    BYTE    m_bFF       # CAN frame format
    BYTE    m_bDLC      # CAN data length code
    BYTE    m_bData[8]  # CAN data
    DWORD   m_dwTime    # Receipt time in ms
    """
    _pack_ = 1      # set alignment
    _fields_ = [("dw_id", c_long), ("b_ff", c_ubyte), ("b_dlc", c_ubyte),
                ("b_data0", c_ubyte), ("b_data1", c_ubyte), ("b_data2", c_ubyte), ("b_data3", c_ubyte),
                ("b_data4", c_ubyte), ("b_data5", c_ubyte), ("b_data6", c_ubyte), ("b_data7", c_ubyte),
                ("dw_time", c_ulong)]

    def __str__(self):
        return "ID {}  Nb {}  Data {} {} {} {} {} {} {} {} - Time {}".format(
            hex(self.dw_id), self.b_dlc,
            hex(self.b_data0), hex(self.b_data1), hex(self.b_data2), hex(self.b_data3),
            hex(self.b_data4), hex(self.b_data5), hex(self.b_data6), hex(self.b_data7),
            self.dw_time)


# noinspection PyPep8Naming
class tUcanHardwareInfoEx(Structure):
    """ Systec Hardware infos structure
    DWORD       m_dwSize        # number of Bytes of this structure
    tUcanHandle m_UcanHandle    # USB-CAN-Handle
    BYTE        m_bDeviceNr     # device number
    DWORD       m_dwSerialNr    # serial number
    DWORD       m_dwFwVersionEx # Firmware Version
    DWORD       m_dwReserved    # reserved
    DWORD       m_dwProductCode # Hardware Type (see Table 15)
    """
    _pack_ = 1
    _fields_ = [("m_dwSize", c_long), ("m_UcanHandle", c_ubyte), ("m_bDeviceNr", c_ubyte), ("m_dwSerialNr", c_ulong),
                ("m_dwFwVersionEx", c_ulong), ("m_dwProductCode", c_ulong)]

    def __str__(self):
        return "{}  {}  {}  {}  {}  {}".format(
            self.m_dwSize, self.m_UcanHandle, self.m_bDeviceNr, hex(self.m_dwSerialNr),
            hex(self.m_dwFwVersionEx), hex(self.m_dwProductCode))


# noinspection PyPep8Naming
class tUcanInitCanParam(Structure):
    """ Systec CAN module init parameters structure
    DWORD  m_dwSize         # Size of this structure in bytes
    BYTE   m_bMode          # CAN Transmission Mode (see table)
    BYTE   m_bBTR0          # Baud rate register 0 of the SJA1000
    BYTE   m_bBTR1          # Baud rate register 1 of the SJA1000
    BYTE   m_bOCR           # Output control register of the SJA1000 (should always be 0x1A)
    DWORD  m_dwAMR          # Acceptance filter mask of the SJA1000
    DWORD  m_dwACR          # Acceptance filter code of the SJA1000
    DWORD  m_dwBaudrate     # Baudrate register for Multiport, USB-CANmodul1 and USB-CANmodul2
    WORD   m_wNrOfRxBufferEntries   # number of entries in receive buffer in USBCAN-library
    WORD   m_wNrOfTxBufferEntries   # number of entries in transmit buffer in USBCAN-library
    """
    _pack_ = 1
    _fields_ = [("m_dwSize", c_long), ("m_bMode", c_ubyte), ("m_bBTR0", c_ubyte), ("m_bBTR1", c_ubyte),
                ("m_bOCR", c_ubyte), ("m_dwAMR", c_ulong), ("m_dwACR", c_ulong), ("m_dwBaudrate", c_ulong),
                ("m_wNrOfRxBufferEntries", c_ushort), ("m_wNrOfTxBufferEntries", c_ushort)]

    def __str__(self):
        return "{}  {}  {}  {}  {}  {}  {}  {}  {}  {}".format(
            self.m_dwSize, hex(self.m_bMode), hex(self.m_bBTR0), hex(self.m_bBTR1),
            hex(self.m_bOCR), hex(self.m_dwAMR), hex(self.m_dwACR), hex(self.m_dwBaudrate),
            self.m_wNrOfRxBufferEntries, hex(self.m_wNrOfTxBufferEntries))


# noinspection PyPep8Naming
class tUcanChannelInfo(Structure):
    """ Systec CAN module channel infos structure
    DWORD   m_dwSize       # size of this structure in bytes
    BYTE    m_bMode        # CAN-mode (see tUcanMode)
    BYTE    m_bBTR0        # Bus Timing Register 0
    BYTE    m_bBTR1        # Bus Timing Register 1
    BYTE    m_bOCR         # Output Control Register
    DWORD   m_dwAMR        # Acceptance Mask Register
    DWORD   m_dwACR        # Acceptance Code Register
    DWORD   m_dwBaudrate   # Baudrate Register for Multiport, USB-CANmodul1 und USB-CANmodul2
    BOOL    m_fCanIsInit   # is TRUE when CAN-channel was initialised
    WORD    m_wCanStatus   # last CAN state (see UcanGetStatus())
    """
    _pack_ = 1
    _fields_ = [("m_dwSize", c_long), ("m_bMode", c_ubyte), ("m_bBTR0", c_ubyte), ("m_bBTR1", c_ubyte),
                ("m_bOCR", c_ubyte), ("m_dwAMR", c_ulong), ("m_dwACR", c_ulong), ("m_dwBaudrate", c_ulong),
                ("m_fCanIsInit", c_bool), ("m_wCanStatus", c_ushort)]

    def __str__(self):
        return "{}  {}  {}  {}  {}  {}  {}  {}  {}  {}".format(
            self.m_dwSize, hex(self.m_bMode), hex(self.m_bBTR0), hex(self.m_bBTR1),
            hex(self.m_bOCR), hex(self.m_dwAMR), hex(self.m_dwACR), hex(self.m_dwBaudrate),
            self.m_fCanIsInit, hex(self.m_wCanStatus))


# noinspection PyPep8Naming
class tUcanMsgCountInfo(Structure):
    """ Systec CAN module messages count structure
    WORD m_wSentMsgCount    # Counter for transmitted CAN-messages
    WORD m_wRecvdMsgCount   # Counter for received CAN-messages
    """
    _pack_ = 1
    _fields_ = [("m_wSentMsgCount", c_ulong), ("m_wRecvdMsgCount", c_ulong)]

    def __str__(self):
        return "{}  {}".format(self.m_wSentMsgCount, self.m_wRecvdMsgCount)


# noinspection PyPep8Naming
class tStatusStruct(Structure):
    """ Systec CAN module status structure
    WORD m_wCanStatus   # present CAN status
    WORD m_wUsbStatus   # present USB status
    """
    _pack_ = 1
    _fields_ = [("m_wCanStatus", c_ulong), ("m_wUsbStatus", c_ulong)]

    def __str__(self):
        return "{}  {}".format(self.m_wCanStatus, self.m_wUsbStatus)


def can_err_code_wrapper():
    """ Wrapper decorator for can error codes
    :return: wrapped function (through decorator) """
    def wrapper(fct):
        """ Wrapper
        :param fct: function to decorate with wrapper
        :return: return value of call to dll """
        def catch(*args, **kwargs):
            """ Try Catch decorator block """
            ret = -1
            try:
                ret = fct(*args, **kwargs)
            except WindowsError as e:
                print("Raised exception: {}".format(repr(e)))
                print("DLL is most probably missing")
            return ret
        return catch
    return wrapper


# noinspection PyPep8Naming
class ucanSystec(object):
    """ Systec usb-can module class """
    def __init__(self, verbose=False):
        """ instance init """
        self.verb = verbose
        print("=================== Start Systec Init ===================")

        # Get platform
        platform = os.environ['PROCESSOR_ARCHITECTURE']
        try:
            platform = os.environ["PROCESSOR_ARCHITEW6432"]
        except KeyError:
            pass    # key not found, pass
        print("* Platform is : {}".format(platform))

        # trick for not so clean installs of the driver on 64b machines
        if os.path.isfile("C:\\Windows\\System32\\Usbcan64.dll"):
            self.dll = WinDLL("Usbcan64.dll")
        else:
            self.dll = WinDLL("Usbcan32.dll")
        print("** Running DLL : {}".format(self.dll._name))     # shouldn't call _name directly

        self._ucanhandle = c_byte()
        self._ucanret = retSystec['USBCAN_ERRCMD_NOTINIT']
        self._use_ex = True
        self._hw_gen = ""
        self.tx_err_cnt, self.rx_err_cnt = c_long(0), c_long(0)
        self.msg_pending = c_long(0)

        self.msgcount = tUcanMsgCountInfo(0, 0)
        self.status = tStatusStruct(0, 0)
        self.hw_infos = tUcanHardwareInfoEx(sizeof(tUcanHardwareInfoEx), 0, 0, 0, 0, 0)
        # AMR and ACR for mode "receive all CAN messages".
        self.params = tUcanInitCanParam(sizeof(tUcanInitCanParam), 0, 0, 0, 0x1A, c_ulong(0xFFFFFFFF), c_ulong(0), 0, 500, 500)
        self.chan0_infos = tUcanChannelInfo(sizeof(tUcanChannelInfo), 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.chan1_infos = tUcanChannelInfo(sizeof(tUcanChannelInfo), 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.rxcan = tCanMsgStruct(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.txcan = tCanMsgStruct(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self._can_init_hw()

    def _can_init_hw(self):
        """ hardware init """
        print("==================== H/W Systec Init ====================")
        # Callback for UcanInitHardware() not implemented yet.
        # This can be done. See ctypes chapter 16.15.1.17. Callback functions
        # TODO: http:#docs.python.org/release/2.5/lib/ctypes-callback-functions.html
        self.can_init_hw()
        self.can_get_hw_infos()     # get hw infos to determine baudrate value to apply
        if not self.is_initialised():
            # self.can_close()
            return self
        self.set_hw_gen()
        self.can_set_speed()
        self.can_get_hw_infos()     # refresh hw infos to update channels config
        print("============== Done initialing Systec unit. =============")
        return self

    def set_hw_gen(self, gen="auto"):
        """ Set hardware gen
        :param gen: Hardware gen to set to ("G1", "G2", "G3", "G4")
        :return: Systec hardware generation """
        if gen != "auto":
            self._hw_gen = gen
        else:
            pid = self.hw_infos.m_dwProductCode & 0xFFFF
            if pid in (USBCAN_PRODCODE_PID_ADVANCED_G4, USBCAN_PRODCODE_PID_BASIC_G4):
                self._hw_gen = "G4"
            else:
                self._hw_gen = "G3"

        if self._hw_gen in ("G1", "G2"):
            self._use_ex = False
        else:
            self._use_ex = True

        print("Systec hardware set to {} gen of converters.".format(self._hw_gen))
        return self._hw_gen

    def can_set_speed(self, kbps=100000, dwBd=0):
        """ Set CAN bus speed
        :param kbps: speed to init
        :param dwBd: Baud rate registers value (refer to section 2.3.4)
        :return: return error code """
        if dwBd:
            self.params.m_bBTR0 = c_ubyte(USBCAN_BAUD_USE_BTREX >> 8)
            self.params.m_bBTR1 = c_ubyte(USBCAN_BAUD_USE_BTREX & 0xFF)
            self.params.m_dwBaudrate = c_uint(baudrateSystec[self._hw_gen].get(kbps))
        else:
            try:
                if self._hw_gen in ("G1", "G2"):
                    self.params.m_bBTR0 = c_ubyte(baudrateSystec["G2"].get(kbps) >> 8)
                    self.params.m_bBTR1 = c_ubyte(baudrateSystec["G2"].get(kbps) & 0xFF)
                    self.params.m_dwBaudrate = c_uint(USBCAN_BAUDEX_USE_BTR01)
                elif self._hw_gen in ("G3", "G4"):
                    self.params.m_bBTR0 = c_ubyte(USBCAN_BAUD_USE_BTREX >> 8)
                    self.params.m_bBTR1 = c_ubyte(USBCAN_BAUD_USE_BTREX & 0xFF)
                    self.params.m_dwBaudrate = c_uint(baudrateSystec[self._hw_gen].get(kbps))
                else:
                    print("Unhandled module gen {}. Cannot set speed.".format(self._hw_gen))
                    return retSystec["USBCAN_ERRCMD_ILLBDR"]
            except TypeError:
                print("Unhandled default speed {}. Try passing dwBd a custom value for desired speed instead.".format(kbps))
                return retSystec["USBCAN_ERRCMD_ILLBDR"]

        return self.can_init_can()

    def can_close(self):
        """ release systec module communication """
        print("=== Closing communication with systec USB-CAN module. ===")
        if self.is_initialised():
            self.can_deinit_can()
            self.can_deinit_hw()
            return self._ucanret

    def is_initialised(self):
        """ Returns True if usb/can module is initialized, False otherwise """
        return True if self._ucanhandle.value > -1 else False

    @staticmethod
    def _get_errcode(srch):
        """ get error code srch from usb-can module """
        for name, err in retSystec.items():
            if err == srch:
                return name
        return "UNKNOWN USB-CAN module error"

    @staticmethod
    def _get_status(srch):
        """ get status code srch from usb-can module """
        for name, st in statusSystec.items():
            if st == srch:
                return name
        return "UNKNOWN USB-CAN module status"

    @can_err_code_wrapper()
    def can_connect_callback(self, event=eventSystec["USBCAN_EVENT_CONNECT"]):
        """ Get function callback state
        :param event: connect callback type
        :return: True if event occured / False otherwise """
        return self.dll.UcanConnectControlFktEx(event, None, None)

    @can_err_code_wrapper()
    def can_fct_callback(self, event=eventSystec["USBCAN_EVENT_RECEIVE"], chan=255):
        """ Get function callback state
        :param event: function callback type
        :param chan: module channel
        :return: True if event occured / False otherwise """
        return self.dll.UcanCallbackFktEx(self._ucanhandle, event, chan, None)

    @can_err_code_wrapper()
    def can_get_err_cnt(self, chan=0):
        """ Get error count
        :param chan: module channel
        :return: error count on rx and tx """
        self._ucanret = self.dll.UcanGetCanErrorCounterEx(self._ucanhandle, chan, byref(self.tx_err_cnt), byref(self.rx_err_cnt))
        if self._ucanret:
            print("!FAIL! UcanGetCanErrorCounterEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_get_msg_pending(self, chan=0):
        """ Get pending messages count
        :param chan: module channel
        :return: rx pending messages count from usb-can module """
        self._ucanret = self.dll.UcanGetMsgPending(self._ucanhandle, chan,
                                                   c_long(5), byref(self.msg_pending))
        if self._ucanret:
            self.msg_pending = c_ubyte(0)
            if self.verb is True:
                print("!FAIL! UcanGetMsgPending = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self.msg_pending

    @can_err_code_wrapper()
    def can_get_msg_count(self, chan=0):
        """ Get messages count
        :param chan: module channel
        :return: messages count from usb-can module """
        self._ucanret = self.dll.UcanGetMsgCountInfoEx(self._ucanhandle, chan, byref(self.msgcount))
        if self._ucanret:
            self.msgcount = tUcanMsgCountInfo(0, 0)
            if self.verb is True:
                print("!FAIL! UcanGetMsgCountInfoEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self.msgcount

    @can_err_code_wrapper()
    def can_get_msg(self, chan=0, nb_msg=0):
        """ get message from usb-can module (channel 0)
        :param chan: module channel (get messages from any channel if set to 255)
        :param nb_msg: max number of messages to read at once (1 message at a time if set to 0)
        :return: return error code """
        self._ucanret = self.dll.UcanReadCanMsgEx(self._ucanhandle, byref(c_long(chan)), byref(self.rxcan), nb_msg)
        if self._ucanret and self.verb is True:
            print("!FAIL! UcanReadCanMsgEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self._ucanret

    @can_err_code_wrapper()
    def can_send_msg(self, message, chan=0):
        """ send message to usb-can module (channel 0)
        :param message: message to send
        :param chan: module channel
        :return: return error code """
        self.txcan = message
        self.txcan.b_ff = c_ubyte(0x80)
        self.txcan.dw_time = c_ulong(long(time.time()))
        self._ucanret = self.dll.UcanWriteCanMsgEx(self._ucanhandle, chan, byref(self.txcan), None)
        if self._ucanret and self.verb is True:
            print("!FAIL! UcanWriteCanMsgEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self._ucanret

    @can_err_code_wrapper()
    def can_reset(self, chan=0, flags=0):
        """ reset of the usb-can module
        :param chan: module channel
        :param flags: custom module reset flags
        :return: return error code """
        self._ucanret = self.dll.UcanResetCanEx(self._ucanhandle, chan, c_long(flags))
        if self._ucanret:
            print("!FAIL! UcanResetCanEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self._ucanret

    @can_err_code_wrapper()
    def can_init_hw(self, nbr=255, callback=None):
        """ Initialize module through dll
        :param nbr: Number of the module to init (255 means any)
        :param callback: Callback function
        :return: ucanSystec object """
        self._ucanret = self.dll.UcanInitHardware(byref(self._ucanhandle), nbr, callback)
        if self._ucanret:
            print("!FAIL! UcanInitHardware = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_init_can(self, chan=0):
        """ Initialize can through dll
        :param chan: module channel
        :return: ucanSystec object """
        if self._use_ex is True:
            self._ucanret = self.dll.UcanInitCanEx2(self._ucanhandle, chan, byref(self.params))
        else:
            self._ucanret = self.dll.UcanInitCan(self._ucanhandle, self.params.btr_h, self.params.btr_l,
                                                 self.params.dw_amr, self.params.dw_acr)
        if self._ucanret:
            print("!FAIL! UcanInitCanEx2 = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_deinit_hw(self):
        """ Uninit module through dll
        :return: ucanSystec object """
        self._ucanret = self.dll.UcanDeinitHardware(self._ucanhandle)
        if self._ucanret:
            print("!FAIL! UcanDeinitHardware = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_deinit_can(self):
        """ Uninit can through dll
        :return: ucanSystec object """
        self._ucanret = self.dll.UcanDeinitCan(self._ucanhandle)
        if self._ucanret:
            print("!FAIL! UcanDeinitCan = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_set_device_nr(self, num):
        """ sets can module with a new device nr
        :param num: new num to affect to the module (254-255 reserved)
        :return: ucanSystec object """
        self._ucanret = self.dll.UcanSetDeviceNr(self._ucanhandle, num)
        if self._ucanret:
            print("!FAIL! UcanSetDeviceNr = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_set_bd(self, btrh, btrl, bdrate, chan=0):
        """ sets can module with a new baud rate
        :param btrh: Baud rate register BTR0 (refer to section 2.3.4)
        :param btrl: Baud rate register BTR1 (refer to section 2.3.4)
        :param bdrate: Baud rate register for all sysWORXX modules (refer to section 2.3.4)
        :param chan: module channel
        :return: ucanSystec object """
        self._ucanret = self.dll.UcanSetBaudrateEx(self._ucanhandle, chan, btrh, btrl, bdrate)
        if self._ucanret:
            print("!FAIL! UcanSetBaudrateEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self

    @can_err_code_wrapper()
    def can_set_tx_timeout(self, chan=0, timeout=0):
        """ Sets the USB CAN transmit message timeout
        :param chan: module channel
        :param timeout: timeout value in ms
        :return: error code returned by dll """
        self._ucanret = self.dll.UcanSetTxTimeout(self._ucanhandle, chan, timeout)
        if self._ucanret:
            print("!FAIL! UcanSetTxTimeout = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self._ucanret

    @can_err_code_wrapper()
    def can_get_status(self, chan=0):
        """ get status of usb-can module
        :param chan: module channel
        :return: ucanSystec object """
        self._ucanret = self.dll.UcanGetStatusEx(self._ucanhandle, chan, byref(self.status))
        if self._ucanret and self.verb is True:
            print("!FAIL! UcanGetStatusEx = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        if self.status:
            print("!WARNING! UcanGetStatusEx = {} ({})".format(self._get_status(self.status), hex(self.status)))
        return self

    @can_err_code_wrapper()
    def can_get_hw_infos(self):
        """ Get module informations
        :return: error code returned by dll """
        self._ucanret = self.dll.UcanGetHardwareInfoEx2(self._ucanhandle, byref(self.hw_infos),
                                                        byref(self.chan0_infos), byref(self.chan1_infos))
        if self._ucanret and self.verb is True:
            print("!FAIL! UcanGetHardwareInfoEx2 = {} ({})".format(self._get_errcode(self._ucanret), hex(self._ucanret)))
        return self._ucanret

    @staticmethod
    def str_version(raw_ver):
        """ converts raw version to a version string
        :param raw_ver: raw version from module/dll
        :return: string representing major, minor & release version """
        major = raw_ver & 0x000000FF
        minor = (raw_ver & 0x0000FF00) >> 8
        release = (raw_ver & 0xFFFF0000) >> 16
        return "v{}.{}r{}".format(major, minor, release)

    @can_err_code_wrapper()
    def can_get_version(self):
        """ :return: usb-can DLL version """
        return self.str_version(self.dll.UcanGetVersionEx(1))   # param 1 is for Usbcan.dll version

    @can_err_code_wrapper()
    def can_get_fw_version(self):
        """ :return: usb-can Firmware version """
        return self.str_version(self.dll.UcanGetFwVersion(self._ucanhandle))


# test des differentes fonctions de CANId
if __name__ == "__main__":
    msg = tCanMsgStruct(0, 0, 8, 1, 2, 3, 4, 5, 6, 7, 8, 0)

    can_bus = ucanSystec()

    if can_bus.is_initialised():
        NR_POLLS = 30
        print("NR_POLLS = {}".format(NR_POLLS))

        for i in range(NR_POLLS):
            can_bus.can_send_msg(msg)
            time.sleep(0.4)
            can_bus.can_get_msg()

        can_bus.can_close()


# -------------------------------------------------------------------
# All possible return codes for the functions of the USBCAN-library:
#
# USBCAN_SUCCESSFUL    0x00
# This message returns if the function is executed successfully.
#
# USBCAN_ERR_RESOURCE    0x01
# This error message returns if one resource could not be
# generated. In this case the term resource means memory and
# handles provided by Windows.
#
# USBCAN_ERR_MAXMODULES    0x02
# An application has tried to open more than 64 USB-CANmoduls.
# The standard version of the USBCAN-library only supports up to
# 64 USB-CANmoduls at the same time (under Windows CE only 9).
# This error also appears if several applications try to access
# more than 64 USB-CANmoduls. For example, application 1 has
# opened 60 modules, application 2 has opened 4 modules and
# application 3 wants to open a module. Application 3 receives
# this error message.
#
# USBCAN_ERR_HWINUSE    0x03
# An application tries to initialize a USB-CANmodul with the
# device number x. If this module has already been initialized by
# its own or by another application, this error message is =.
#
# USBCAN_ERR_ILLVERSION    0x04
# This error message returns if the firmware version  of the
# USB-CANmodul is not compatible to the software version of the
# USBCAN-library. In this case, install the USB-CAN driver
# again.
#
# USBCAN_ERR_ILLHW    0x05
# This error message returns if a USB-CANmodul with the device
# number x is not found. If the function UcanInitHardware()  or
# UcanInitHardwareEx() has been called with the device number
# USBCAN_ANY_MODULE, and the error code appears, it indicates
# that no module is connected to the PC or all connected
# modules are already in use.
#
# USBCAN_ERR_ILLHANDLE    0x06
# This error message returns if a function received an incorrect
# USB-CAN handle. The function first checks which
# USB-CANmodul is initialized to this handle. This error occurs if
# no module has been initialized to this handle.
#
# USBCAN_ERR_ILLPARAM    0x07
# This error message returns if a wrong parameter is transferred to
# this function. For example, the value NULL has been handed
# over to a pointer variable instead of a valid address.
#
# USBCAN_ERR_BUSY    0x08
# This error message can occur if several threads are accessing a
# USB-CANmodul within a single application. After the other
# threads have finished their tasks, the function may be called
# again.
#
# USBCAN_ERR_TIMEOUT    0x09
# This error message occurs if the function transmits a command to
# the USB-CANmodul but no answer is =. To solve this
# problem, close the application, disconnect the USB-CANmodul,
# and connect it again.
#
# USBCAN_ERR_IOFAILED    0x0a
# This error message occurs if the communication to the
# USB-CAN driver was interrupted. This happens, for example, if
# the USB-CANmodul is disconnected during the execution of a
# function.
#
# USBCAN_ERR_DLL_TXFULL    0x0b
# The function  UcanWriteCanMsg()  or UcanWriteCanMsgEx()
# first checks if the transmit buffer within the USBCAN-library
# has enough capacity to store new CAN messages. If the buffer is
# full, this error message returns. The CAN message transferred to
# the function UcanWriteCanMsg() or UcanWriteCanMsgEx() will
# not be written into the transmission buffer in order to protect
# other CAN messages from overwriting. Since software driver
# version 3.05 the size of the transmit buffer is configurable (see
# function UcanInitCanEx() and Structure tUcanInitCanParam)
#
# USBCAN_ERR_MAXINSTANCES    0x0c
# In this software version, a maximum amount of 64 applications
# are able to have access to the USBCAN-library (under
# Windows CE only 9). If more applications attempt access to the
# DLL, this error message will occur. In this case, it is not possible
# to initialize a USB-CANmodul.
#
# USBCAN_ERR_CANNOTINIT    0x0d
# If a USB-CANmodul is initialized with the function
# UcanInitHardware()  or  UcanInitHardwareEx(), the software
# changes into the state HW_INIT. Functions like
# UcanReadCanMsg() or  UcanWriteCanMsg() return this error
# message while in HW_INIT state. With the function
# UcanInitCan(), the software changes into CAN_INIT state. In
# this state, it is possible to read and transmit CAN messages. USB-CANmodul
#
# USBCAN_ERR_DISCONNECT    0x0e
# This error code occurs if a function from USBCAN-library was
# called for a USB-CANmodul that was plugged-off from the
# computer recently.
#
# USBCAN_ERR_NOHWCLASS    0x0f
# This error code is deprecated and is not used any more.
#
# USBCAN_ERR_ILLCHANNEL    0x10
# This error code is = if an extended function of the
# USBCAN-library was called with parameter
# bChannel_p = USBCAN_CHANNEL_CH1, but
# USB-CANmodul GW-001, GW-002 or USB-CANmodul1 was
# used.
#
# USBCAN_ERR_ILLHWTYPE    0x12
# This error code occurs if an extended function of the USBCAN-
# library was called for a Hardware which does not support the
# feature.  Software Support for Windows OS
#
# USBCAN_ERRCMD_NOTEQU    0x40
# This error code occurs during communication between the PC
# and a USB-CANmodul. The PC sends a command to the
# USB-CANmodul, then the module executes the command  and
# returns a response to the PC. This error message returns if the
# answer does not correspond to the command.
#
# USBCAN_ERRCMD_REGTST    0x41
# The software tests the CAN controller on the USB-CANmodul
# when the CAN interface is initialized. Several registers of the
# CAN controller are checked. This error message returns if an
# error appears during this register test.
#
# USBCAN_ERRCMD_ILLCMD    0x42
# This error message returns if the USB-CANmodul receives a
# non-defined command. This error shows a version conflict
# between the firmware in the USB-CANmodul and the USBCAN-
# library.
#
# USBCAN_ERRCMD_EEPROM    0x43
# The USB-CANmodul has a serial EEPROM. This EEPROM
# contains the device number and the serial number. If an error
# occurs while reading these values, this error message is =.
#
# USBCAN_ERRCMD_ILLBDR    0x47
# The Multiport CAN-to-USB 3004006, USB-CANmodul1
# 3204000/3204001 or USB-CANmodul2 3204002/3204003 has
# been initialized with an invalid baud rate (BTR0 und BTR1).
#
# USBCAN_ERRCMD_NOTINIT    0x48
# It was tried to access a CAN-channel of Multiport CAN-to-USB
# 3004006 or USB-CANmodul2 3204002/3204003 that was not
# initialized.
#
# USBCAN_ERRCMD_ALREADYINIT    0x49
# The accessed CAN-channel of Multiport CAN-to-USB 3004006
# or USB-CANmodul2 3204002/3204003 was already initialized.
#
# USBCAN_ERRCMD_ILLSUBCMD   0x4A
# An internal error occurred within the DLL. In this case an
# unknown subcommand was called instead of a main command
# (e.g. for the cyclic CAN message - feature).
#
# USBCAN_ERRCMD_ILLIDX      0x4B
# An internal error occurred within the DLL. In this case an
# invalid index for a list was delivered to the firmware
# (e.g.for the cyclic CAN message - feature).
#
# USBCAN_ERRCMD_RUNNING     0x4C
# The caller tries to define a new list of cyclic CAN messages
# but this feature was already started. For defining a new list,
# it is necessary to stop the feature beforehand
#
# USBCAN_WARN_NODATA    0x80
# If the function UcanReadCanMsg() returns with this warning, it
# is an indication that the receive buffer contains no CAN
# messages.
#
# USBCAN_WARN_SYS_RXOVERRUN    0x81
# If an overrun in the receive buffer on the USB-CAN  system
# driver occurred, the USBCAN-library is informed about this
# event. The function  UcanReadCanMsg()  returns this warning
# and a valid CAN message. The warning indicates that CAN
# messages are lost. However, it does not indicate the position of
# the lost CAN messages.
#
# USBCAN_WARN_DLL_RXOVERRUN    0x82
# The USBCAN-library automatically requests CAN messages
# from the USB-CANmodul and stores the messages into a buffer
# of the DLL. If more CAN messages are received than  the DLL
# buffer size allows, this error message returns and CAN messages
# are lost. However, it does not indicate the position of the lost
# CAN messages. Since software driver version 3.05 the size of
# the receive buffer is configurable (see function UcanInitCanEx()
# and structure tUcanInitCanParam)
#
# USBCAN_WARN_FW_TXOVERRUN    0x85
# This warning is = by function UcanWriteCanMsg() and/or
# UcanWriteCanMsgEx() if flag
# USBCAN_CANERR_QXMTFULL is set in the CAN driver
# status. However, the transmit CAN message could be  stored to
# the DLL transmit buffer. This warning indicates that at least one
# transmit CAN message got lost in the device firmware layer.
# This warning does not indicate the position of the  lost CAN
# message.
#
# USBCAN_WARN_FW_RXOVERRUN    0x86
# This warning is = by function UcanWriteCanMsg() and/or
# UcanWriteCanMsgEx() if flag
# USBCAN_CANERR_QOVERRUN or flag
# USBCAN_CANERR_OVERRUN are set in the CAN driver
# status. The function has = with a valid CAN  message.
# This warning indicates that at least one received CAN message
# got lost in the firmware layer. This warning does not indicate the
# position of the lost CAN message.
#
# USBCAN_WARN_NULL_PTR   0x90
# This warning message is = by functions:
# UcanInitHwConnectControl() and/or
# UcanInitHwConnectControlEx() if a NULL pointer was passed
# as callback function address.
#
# USBCAN_WARN_TXLIMIT 0x91
# This warning message is = by the function
# UcanWriteCanMsgEx() if it was called to transmit more than one
# CAN message, but a part of them could not be stored to the
# transmit buffer within USBCAN-library (because the  buffer is
# full). The parameter  pdwCount_p includes the number of CAN
# vmessages which could be stored successfully to the  transmit
# buffer.
# -------------------------------------------------------------------
