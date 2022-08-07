from ctypes import *
import atexit
import time
import sys

codec = "latin-1"

vblib = cdll.LoadLibrary('./VoicemeeterRemote64.dll')

# define exit method

def exit_handler():
    print("Exiting...")
    print("Logout signal: %s" % logout())

atexit.register(exit_handler)

# connect to voicemeeter

vmType = 0

## declare types
vblib.VBVMR_Login.restype = c_long
vblib.VBVMR_Logout.restype = c_long

def login():
    global vblib, vmType

    print("Logging in...")
    loginResult = vblib.VBVMR_Login()
    if loginResult != 0:
        exit()

    print("Successfully logged in.")

    vmType = getVoicemeeterType()

    print()

def logout():
    return vblib.VBVMR_Logout()


# detect voicemeeter type

## declare types
vblib.VBVMR_GetVoicemeeterType.argtypes = (POINTER(c_long),)
vblib.VBVMR_GetVoicemeeterType.restype = c_long

def getVoicemeeterType():
    vmType = c_long()
    vblib.VBVMR_GetVoicemeeterType(byref(vmType))

    print("Detected type is: %s" % vmType.value)

    return vmType.value

def getDeviceCount(vmType):
    match(vmType):
        case 1:
            return 2
        case 2:
            return 3
        case 3:
            return 5


# available device info

## declare types
vblib.VBVMR_Input_GetDeviceDescA.argtypes = (c_long, POINTER(c_long), c_char_p, c_char_p)
vblib.VBVMR_Input_GetDeviceDescA.restype = c_long
vblib.VBVMR_Output_GetDeviceDescA.argtypes = (c_long, POINTER(c_long), c_char_p, c_char_p)
vblib.VBVMR_Output_GetDeviceDescA.restype = c_long

## get device info

def getDeviceType(devType):
    match(devType):
        case 1:
            return "MME"
        case 3:
            return "WDM"
        case 4:
            return "KS"
        case 5:
            return "ASIO"

def getAvailableOutputDevices():
    devices = []

    numberOfOutputDevices = vblib.VBVMR_Output_GetDeviceNumber()

    for n in range(numberOfOutputDevices):
        devType = c_long()
        devName = create_string_buffer(256)
        devId = create_string_buffer(256)

        ret = vblib.VBVMR_Output_GetDeviceDescA(c_long(n), byref(devType), devName, devId)
        if ret != 0:
            login()

        devices.append(devName.value.decode(codec))

    return devices

def getAvailableInputDevices():
    devices = []

    numberOfInputDevices = vblib.VBVMR_Input_GetDeviceNumber()

    for n in range(numberOfInputDevices):
        devType = c_long()
        devName = create_string_buffer(256)
        devId = create_string_buffer(256)

        ret = vblib.VBVMR_Input_GetDeviceDescA(c_long(n), byref(devType), devName, devId)
        if ret != 0:
            login()

        devices.append(devName.value.decode(codec))

    return devices


# selected device info

## declare type
vblib.VBVMR_GetParameterStringA.argtypes = (c_char_p, c_char_p)
vblib.VBVMR_GetParameterStringA.restype = c_long

def getSelectedDevice(index, devType):
    deviceToCheck = ("%s[%s].device.name" % (devType, index)).encode(codec)
    selectedDevice = create_string_buffer(512)

    ret = vblib.VBVMR_GetParameterStringA(deviceToCheck, selectedDevice)
    if ret != 0:
        login()

    return selectedDevice.value.decode(codec)

def getSelectedOutputDevices():
    global vmType

    selectedOutputDevices = []

    for n in range(getDeviceCount(vmType)):
        selectedOutputDevices.append(getSelectedDevice(n, "Bus"))

    return selectedOutputDevices

def getSelectedInputDevices():
    global vmType

    selectedInputDevices = []

    for n in range(getDeviceCount(vmType)):
        selectedInputDevices.append(getSelectedDevice(n, "Strip"))

    return selectedInputDevices


# compare selected and available devices to detect unavailable devices

def getUnavailableOutputDevices():
    availableOutputDevices = getAvailableOutputDevices()
    selectedOutputDevices = getSelectedOutputDevices()

    return [device for device in selectedOutputDevices
            if device != ""
                and device not in availableOutputDevices]

def getUnavailableInputDevices():
    availableInputDevices = getAvailableInputDevices()
    selectedInputDevices = getSelectedInputDevices()

    return [device for device in selectedInputDevices
            if device != ""
                and device not in availableInputDevices]


# restart audio engine

vblib.VBVMR_SetParameterFloat.argtypes = (c_char_p, c_float)
vblib.VBVMR_SetParameterFloat.restype = c_long

def restartAudioEngine():
    print("Restarting...")
    print()
    vblib.VBVMR_SetParameterFloat("Command.Restart".encode(codec), 1)

# check for restart condition

lastUnavailableOutputDevices = []
lastUnavailableInputDevices = []

def checkForRestart():
    global lastUnavailableOutputDevices, lastUnavailableInputDevices

    unavailableOutputDevices = getUnavailableOutputDevices()
    unavailableInputDevices = getUnavailableInputDevices()

    print("Unavailable Outputs: %s" % unavailableOutputDevices)
    print("Unavailable Inputs: %s" % unavailableInputDevices)
    print()

    shouldRestart = False

    if(len(unavailableOutputDevices) < len(lastUnavailableOutputDevices)
        or len(unavailableInputDevices) < len(lastUnavailableInputDevices)):
        shouldRestart = True

    lastUnavailableOutputDevices = unavailableOutputDevices
    lastUnavailableInputDevices = unavailableInputDevices

    return shouldRestart

# script execution

login()

while True:
    if checkForRestart():
        restartAudioEngine()
    time.sleep(5)
