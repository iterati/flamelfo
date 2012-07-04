import math
import xml.etree.cElementTree as ET

NFRAMES = 30

def normalize(val, max_val=1):
    x = val/float(max_val)
    return (x - math.floor(x)) * max_val

def print_loop(flame, nframes=NFRAMES):
    element = ET.Element('flames')
    for i in xrange(nframes):
        for xform in flame.xforms:
            if xform.animate:
                xform.rot(360/float(nframes))
        element.append(flame.get_at(i/float(nframes)))
    return ET.tostring(element)

def polar(coord):
    x, y = coord
    l = math.sqrt(x**2 + y**2)
    t = math.atan2(y, x) * (180./math.pi)
    return l, t

def rect(coord):
    l, t = coord
    x = l * math.cos(t*math.pi/180.)
    y = l * math.sin(t*math.pi/180.)
    return x, y
