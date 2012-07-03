import math
from utils import normalize

def sin(i, amp, phase=0):
    i = normalize(i)
    phase = normalize(phase, 360) - 90
    return (0.5 * amp * math.sin((i * 2 * math.pi) + math.radians(phase))) + (0.5 * amp)

def saw_up(i, amp, phase=0):
    phase = normalize(phase, 360)
    i = normalize(i + phase/360.)
    return amp * i

def saw_down(i, amp, phase=0):
    phase = normalize(phase, 360)
    i = normalize(i + phase/360.)
    return amp * (1 - i)

def square(i, amp, phase=0):
    phase = normalize(phase, 360)
    i = normalize(i + phase/360.)
    if i < 0.5:
        return 0
    else:
        return amp

def triangle(i, amp, phase=0):
    phase = normalize(phase, 360)
    i = normalize(i + phase/360.)
    if i < 0.5:
        return amp * 2 * i
    else:
        return amp * 2 * (1 - i)

