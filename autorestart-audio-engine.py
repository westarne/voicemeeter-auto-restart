from ctypes import *
import time

vblib = cdll.LoadLibrary('./VoicemeeterRemote64.dll')

# connect to voicemeeter

## declare types
vblib.VBVMR_Login.restype = c_long
vblib.VBVMR_Logout.restype = c_long

def login():
    global vblib

    print("Logging in...")
    loginResult = vblib.VBVMR_Login()
    if loginResult != 0:
        exit()

    print("Successfully logged in.")
    print()


# available device info

## declare types
vblib.VBVMR_Input_GetDeviceDescA.argtypes = (c_long, POINTER(c_long), c_char_p, c_char_p)
vblib.VBVMR_Input_GetDeviceDescA.restype = c_long
vblib.VBVMR_Output_GetDeviceDescA.argtypes = (c_long, POINTER(c_long), c_char_p, c_char_p)
vblib.VBVMR_Output_GetDeviceDescA.restype = c_long

## get device info

def getDeviceType(type):
    match(type):
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

        devices.append(devName.value.decode('ascii'))

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

        devices.append(devName.value.decode('ascii'))

    return devices


# selected device info

## declare type
vblib.VBVMR_GetParameterStringA.argtypes = (c_char_p, c_char_p)
vblib.VBVMR_GetParameterStringA.restype = c_long

def getSelectedDevice(index, devType):
    deviceToCheck = ("%s[%s].device.name" % (devType, index)).encode('ascii')
    selectedDevice = create_string_buffer(512)

    ret = vblib.VBVMR_GetParameterStringA(deviceToCheck, selectedDevice)
    if ret != 0:
        login()

    return selectedDevice.value.decode('ascii')

def getSelectedOutputDevices():
    selectedOutputDevices = []

    for n in range(5):
        selectedOutputDevices.append(getSelectedDevice(n, "Bus"))

    return selectedOutputDevices

def getSelectedInputDevices():
    selectedInputDevices = []

    for n in range(5):
        selectedInputDevices.append(getSelectedDevice(n, "Strip"))

    return selectedInputDevices


# compare selected and available devices to detect unavailable devices

def getUnavailableOutputDevices():
    availableOutputDevices = getAvailableOutputDevices()
    return [device for device in getSelectedOutputDevices()
            if device != ""
                and device not in availableOutputDevices]

def getUnavailableInputDevices():
    availableInputDevices = getAvailableInputDevices()
    return [device for device in getSelectedInputDevices()
            if device != ""
                and device not in availableInputDevices]


# restart audio engine

vblib.VBVMR_SetParameterFloat.argtypes = (c_char_p, c_float)
vblib.VBVMR_SetParameterFloat.restype = c_long

def restartAudioEngine():
    print("Restarting...")
    print()
    vblib.VBVMR_SetParameterFloat("Command.Restart".encode('ascii'), 1)

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

login()

while True:
    if checkForRestart():
        restartAudioEngine()
    time.sleep(5)


# Logout
loginResult = vblib.VBVMR_Logout()
print("Logout result is %s" % loginResult)
