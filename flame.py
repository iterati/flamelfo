from variations import variation_list, variable_list
import lfos
from utils import polar, rect
import colorsys, itertools, operator
import xml.etree.cElementTree as ET


class Flames(object):
    def __init__(self, element=None, filename=None):
        self.flames = []
        if operator.xor(element, filename):
            raise ValueError('Need element or filename, not both or neither')
        if element:
            self.from_element(element)
        elif filename:
            self.from_file(filename)

    def from_element(self, element):
        if element.tag == 'flames':
            self.flames = [Flame(flame) for flame in element.findall('flame')]
        elif element.tag == 'flame':
            self.flames = [Flame(element)]
        else:
            #TODO: ParseError?
            raise ValueError('Needs to be in <flames> or <flame>')

    def from_string(self, string):
        self.from_element(ET.fromstring(string))

    def from_file(self, filename):
        with open(filename, 'r') as f:
            self.from_string(f.read())

    def iter_flames(self):
        for flame in self.flames:
            yield flame

    def to_element(self):
        element = ET.Element('flames')
        element.extend([flame.to_element() for flame in self.iter_flames()])
        return element

    def to_string(self):
        return ET.tostring(self.to_element())

    def to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_string())
        return True


class Flame(object):
    _never_write = (
            'final',
            'palette',
            'xforms',
            'name',
            'scale',
            'x_offset',
            'y_offset',
            'width',
            'height',
            '_numx',
            )
    _defaults = {
            'name': 'none',
            'size': (720, 360),
            'center': (0.0, 0.0),
            'scale': 20,
            'time': 0,
            'rotate': 0.0,
            'brightness': 4,
            'gamma': 4,
            'gamma_threshold': 0.04,
            'background': (0., 0., 0.),
            'vibrancy': 1,
            'highlight_power': -1,
            'interpolation_type': 'log',
            'interpolation': 'linear',
            'palette_mode': 'linear',
            'oversample': 1,
            'filter': 0.2,
            'quality': 100,
            }

    def __init__(self, element=None):
        self.xforms = []
        self.final = None
        if element:
            self.from_element(element)
        else:
            for k, v in self._defaults.items():
                setattr(self, k, v)
            self.palette = Palette()

    def from_element(self, element):
        for k, v in element.items():
            try:
                if " " in v:
                    #coefs, for instance, are stored as '# # # # # #' and need
                    #need to be stored internally as floats.
                    setattr(self, k, map(float, v.split()))
                else:
                    #All numerical values should be stored as floats
                    setattr(self, k, float(v))
            except ValueError:
                #If conversion to float won't work, keep value as string
                setattr(self, k, v)
        self.name = str(self.name)
        self.scale = self.scale * 100 / self.size[0]
        xml_xforms = element.findall('xform')
        self._numx = len(xml_xforms)
        for xform in xml_xforms:
            self.xforms.append(Xform(self, xform))
        for finalx in element.findall('finalxform'):
            if self.final is not None:
                #TODO: Create ParsingError?
                raise ValueError('More than one Final Xform')
            self.final = Xform(self, finalx)
            self.final.animate = False
        self.palette = Palette(self, element.findall('color'))

    def to_element(self):
        element = ET.Element('flame')
        #attributes
        for k, v in self._iter_attributes():
            if isinstance(v, basestring):
                pass
            elif hasattr(v, "__iter__"):
                #For tuple and list elements, make a space-delimited string
                v = " ".join(str(i if i % 1 else int(i)) for i in v)
            else:
                #TODO: Might want to round here to truncate float precision errors
                v = v if v % 1 else int(v)
            element.set(k, v)
        #xforms
        element.extend(xform.to_string() for xform in self.xforms)
        #finalxform
        if self.final:
            element.apend(self.final.to_string())
        #colors
        element.append(self.palette.to_string())
        return element

    def to_string(self):
        return ET.tostring(self.to_element())

    def get_at(self, i):
        #TODO: Refactor as this is basically to_element
        element = ET.Element('flame')
        for k, v in self._iter_attributes():
            if isinstance(v, basestring):
                pass
            elif hasattr(v, "__iter__"):
                v = " ".join(str(i if i % 1 else int(i)) for i in v)
            else:
                v = v if v % 1 else int(v)
            element.set(k, v)
        element.extend(xform.get_at(i) for xform in self.xforms)
        if self.final != None:
            element.apend(self.final.to_string())
        element.append(self.palette.to_string())
        return element

    def copy(self):
        return Flame(ET.fromstring(self.to_string()))

    def iter_xforms(self):
        for xform in self.xforms:
            yield xform

    def _iter_attributes(self):
        #This returns all writable attributes and the derived attribs
        return itertools.chain(
            (
                ('name', self.name),
                ('size', self.size),
                ('center', self.center),
                ('scale', self.scale * self.width * 0.01),
            ),
            ((k, v) for (k, v) in self.__dict__.iteritems()\
                    if k not in self._never_write)
        )

    @property
    def size(self):
        return self.width, self.height

    @property
    def center(self):
        return self.x_offset, self.y_offset


class Xform(object):
    _never_write = (
            '_parent',
            'post',
            'lfos',
            'chaos',
            'xx',
            'xy',
            'yx',
            'yy',
            'ox',
            'oy',
            )
    _defaults = {
            'coefs': (1., 0., 0., 1., 0., 0.),
            'linear': 1,
            'color': 0.,
            'color_speed': 0.5,
            'opacity': 1.,
            'weight': 1.,
            }

    def __init__(self, parent, element=None):
        self._parent = parent
        self.lfos = []
        self.chaos = None
        self.post = None

        if element != None:
            self.from_element(element)
        else:
            for k, v in self._defaults.items():
                setattr(self, k, v)

    def from_element(self, element):
        for k, v in element.items():
            try:
                if " " in v:
                    setattr(self, k, float(v))
                else:
                    setattr(self, k, float(v))
            except ValueError:
                setattr(self, k, v)
        if element.get('chaos'):
            self.chaos = Chaos(self, element.get('chaos'))
        else:
            self.chaos = None
        if element.get('post'):
            self.post = PostXform(self, element.get('post'))
        else:
            self.post = None
        for lfo in element.findall('lfo'):
            self.lfos.append(LFO(self, lfo))

    def to_element(self, print_lfos=True):
        #need the right tag
        if self.isfinal():
            element = ET.Element('finalxform')
        else:
            element = ET.Element('xform')
        #coefs attr
        element.set('coefs', "{0} {1} {2} {3} {4} {5}".format(*self.coefs))
        #post attr
        if self.post:
            element.set('post', self.post.to_string())
        #chaos attr
        if self.chaos:
            element.set('chaos', self.chaos.to_string())
        #other attrs
        for k, v in self._iter_attributes():
            if isinstance(v, basestring):
                pass
            elif hasattr(v, "__iter__"):
                v = " ".join(str(i if i % 1 else int(i)) for i in v)
            else:
                v = v if v % 1 else int(v)
            element.set(k, v)
        #lfos if necessary
        if self.lfos and print_lfos:
            for lfo in self.lfos:
                if lfo.is_active():
                    element.append(lfo.to_string())
        return element

    def to_string(self, print_lfos=True):
        return ET.tostring(self.to_element(print_lfos))

    def copy(self):
        return Xform(ET.fromstring(self.to_string()))

    def get_at(self, i):
        xform = self.copy()
        if self.lfos:
            for lfo in self.lfos:
                if lfo.target in ['rotate', 'rotate_x', 'rotate_y', 'orbit']:
                    method = getattr(xform, lfo.target)
                    method(lfo.get_at(i))
                elif lfo.target in ['protate', 'protate_x', 'protate_y', 'porbit']:
                    method = getattr(xform, lfo.target[1:])
                    method(lfo.get_at(i))
                else:
                    setattr(xform, lfo.target, (getattr(xform, lfo.target) + lfo.get_at(i)))
        return xform.to_element(print_lfos=False)

    def list_vars(self):
        return [i for i in variation_list if i in self.__dict__]

    def iter_lfos(self):
        for lfo in self.lfos:
            yield lfo

    def _iter_attributes(self):
        return ((k, v) for (k, v) in self.__dict__.iteritems() if k not in self._never_write)

    def isfinal(self):
        return self is self._parent.final

    def ispost(self):
        return type(self._parent) == Xform

    def add_post(self, p=(1, 0, 0, 1, 0, 0)):
        if not self.post:
            self.post = PostXform(self, post=p)
        else:
            self.post.coefs = p

    def add_lfo(self):
        self.lfos.append(LFO(self))

    def scale(self, v):
        self.xp = (self.xp[0]*v, self.xp[1])
        self.yp = (self.yp[0]*v, self.yp[1])

    def scale_x(self, v):
        self.xp = (self.xp[0]*v, self.xp[1])

    def scale_y(self, v):
        self.yp = (self.yp[0]*v, self.yp[1])

    def rotate(self, deg):
        self.xp = (self.xp[0], self.xp[1]+deg)
        self.yp = (self.yp[0], self.yp[1]+deg)

    def rotate_x(self, deg):
        self.xp = (self.xp[0], self.xp[1]+deg)

    def rotate_y(self, deg):
        self.yp = (self.yp[0], self.yp[1]+deg)

    def orbit(self, deg, pivot=(0, 0)):
        if pivot == (0, 0):
            self.op = (self.op[0], self.op[1]+deg)
        else:
            self.o = (self.o[0]-self.p[0], self.o[1]-self.p[1])
            self.op = (self.op[0], self.op[1]+deg)
            self.o = (self.o[0]+self.p[0], self.o[1]+self.p[1])

    @property
    def index(self):
        if self.isfinal():
            return None
        try:
            return self._parent.xforms.index(self)
        except (AttributeError, ValueError):
            return None

    @property
    def coefs(self):
        return (self.xx, self.xy, self.yx, self.yy, self.ox, self.oy)
    @coefs.setter
    def coefs(self, value):
        self.xx, self.xy, self.yx, self.yy, self.ox, self.oy = value

    @property
    def x(self):
        return self.xx, self.xy
    @x.setter
    def x(self, value):
        self.xx, self.xy = value

    @property
    def y(self):
        return self.yx, self.yy
    @y.setter
    def y(self, value):
        self.yx, self.yy = value

    @property
    def o(self):
        return self.ox, self.oy
    @o.setter
    def o(self, value):
        self.ox, self.oy = value

    @property
    def polars(self):
        return self.xp, self.yp, self.op
    @polars.setter
    def polars(self, value):
        self.xp, self.yp, self.op = value

    @property
    def xp(self):
        return polar((self.xx, self.xy))
    @xp.setter
    def xp(self, value):
        self.xx, self.xy = rect(value)

    @property
    def yp(self):
        return polar((self.yx, self.yy))
    @yp.setter
    def yp(self, value):
        self.yx, self.yy = rect(value)

    @property
    def op(self):
        return polar((self.ox, self.oy))
    @op.setter
    def op(self, value):
        self.ox, self.oy = rect(value)


class PostXform(Xform):
    _default = (1., 0., 0., 1., 0., 0.)

    def __init__(self, parent, element=None, post=None):
        self._parent = parent
        if element:
            self.from_element(element)
        elif post:
            self.coefs = post
        else:
            self.coefs = self._default

    def from_element(self, element):
        self.coefs = map(float, element.split())

    def to_string(self):
        return "{0} {1} {2} {3} {4} {5}".format(*self.coefs)

    def isactive(self):
        return self.coefs != (1, 0, 0, 1, 0, 1)


class Chaos(object):
    def __init__(self, parent, element=None):
        self._parent = parent
        if element:
            self.from_element(element)
        else:
            self.value = []
            for i in xrange(self._parent._numx):
                self.value.append(1)

    def from_element(self, element):
        self.value = map(float, element.split())

    def to_string(self):
        rtn = []
        if self.isactive():
            for v in self.value:
                rtn.extend([str(v), ' '])
            rtn.pop()
        return ''.join(rtn)
    
    def isactive(self):
        for v in self.value:
            if v != 1:
                return True
        return False


class LFO(object):
    _defaults = {
            'target': None,
            'freq': 1,
            'shape': 'sin',
            'amp': 0,
            'phase': 0,
            }
    #TODO: generate from inspecting lfos?
    _shapes = [
            'sin',
            'saw_up',
            'saw_down',
            'square',
            'triangle'
            ]
    _valid_targets = set.union(
            set(variation_list),
            set(variable_list),
            set([
                'color',
                'color_speed',
                'weight',
                'opacity',
                'rotate',
                'rotate_x',
                'rotate_y',
                'protate',
                'protate_x',
                'protate_y',
                'orbit',
                'porbit',
                ]))

    def __init__(self, parent, element=None):
        self._parent = parent
        if element:
            self.from_element(element)
        else:
            for (k, v) in self._defaults.items():
                setattr(self, k, v)

    def from_element(self, element):
        self.target = element.get('target', self._defaults['target'])
        self.freq = float(element.get('freq', self._defaults['freq']))
        self.shape = element.get('shape', self._defaults['shape'])
        self.amp = float(element.get('amp', self._defaults['amp']))
        self.phase = float(element.get('phase', self._defaults['phase']))

    def to_element(self):
        if self.isactive():
            element = ET.Element('lfo')
            for (k, v) in self._dict__.iteritems():
                element.set(k, v)
            return element
        return None

    def to_string(self):
        return ET.tostring(self.to_element())

    def get_at(self, i):
        if self.isactive():
            method = getattr(lfos, self._shape)
            return method(i*self.freq, self.amp, self.phase)
        else:
            return 0.

    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, value):
        if value in self._valid_targets:
            self._target = value
            try:
                self._targetp = self._parent.__dict__[self.target]
            except KeyError:
                setattr(self._parent, value, 0.)
        else:
            raise ValueError('{0} is an invalid target'.format(value))

    @property
    def shape(self):
        return self._shape
    @shape.setter
    def shape(self, value):
        if value in self.shapes:
            self._shape = value
        else:
            raise ValueError('Invalid shape')


class Palette(object):
    def __init__(self, parent, element=None):
        self._parent = parent
        self.colors = []
        for i in xrange(256):
            self.colors.append(Color(i, self._parent))
        if element:
            self.from_element(element)

    def from_element(self, element):
        for color in element:
            self.colors[color._index] = Color(self._parent, element=element)

    def to_elements(self):
        return [color.to_element() for color in self.colors]


class Color(object):
    def __init__(self, parent, index=None, element=None):
        self._parent = parent
        self._index = index
        if element:
            self.from_element(element)
        else:
            self._color = (0, 0, 0)

    def from_element(self, element):
        self._index = int(element.get('index'))
        self.rgb = map(float, element.get('rgb', '0 0 0').split())

    def to_element(self, element):
        element = ET.Element('color')
        element.set('index', self._index)
        element.set('rgb', '{0} {1} {2}'.format(*self.rgb))
        return element

    @property
    def index(self):
        try:
            return self._parent.index(self)
        except (AttributeError, ValueError):
            return None

    @property
    def rgb(self):
        return self._color
    @rgb.setter
    def rgb(self, value):
        self._color = value

    @property
    def r(self):
        return self._color[0]
    @r.setter
    def r(self, value):
        self._color = value, self.g, self.b

    @property
    def g(self):
        return self._color[1]
    @g.setter
    def g(self, value):
        self._color = self.r, value, self.b

    @property
    def b(self):
        return self._color[2]
    @b.setter
    def b(self, value):
        self._color = self.r, self.g, value

    @property
    def hsv(self):
        return colorsys.rgb_to_hsv(*(x/255. for x in self.rgb))
    @hsv.setter
    def hsv(self, value):
        self._color = colorsys.hsv_to_rgb(*value)

    @property
    def h(self):
        return self.hsv[0]
    @h.setter
    def h(self, value):
        self._color = colorsys.hsv_to_rgb(value, self.s, self.v)

    @property
    def s(self):
        return self.hsv[1]
    @s.setter
    def s(self, value):
        self._color = colorsys.hsv_to_rgb(self.h, value, self.v)

    @property
    def v(self):
        return self.hsv[2]
    @v.setter
    def v(self, value):
        self._color = colorsys.hsv_to_rgb(self.h, self.s, value)

