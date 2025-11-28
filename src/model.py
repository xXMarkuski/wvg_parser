"""
WVG (Wireless Vector Graphics) Data Structures
Based on 3GPP TS 23.040 version 16.0.0 Release 16 - Annex G
"""

from dataclasses import dataclass, field
from enum import IntEnum, Enum, auto
from typing import Optional, List, Union


# ==============================================================================
# Enumerations
# ==============================================================================

class WVGType(IntEnum):
    """WVG type indicator (first bit)"""
    CHARACTER_SIZE = 0
    STANDARD = 1


class ColorScheme(IntEnum):
    """Color scheme codes"""
    BLACK_WHITE = 0b00          # 2 colors
    GRAYSCALE_2BIT = 0b010      # 4 grayscales
    PREDEFINED_4COLOR = 0b011   # 4 predefined colors
    RGB_6BIT = 0b100            # 6-bit RGB
    WEBSAFE = 0b101             # 8-bit websafe
    RGB_6BIT_PALETTE = 0b1100   # 6-bit RGB with palette
    WEBSAFE_PALETTE = 0b1101    # websafe with palette
    RGB_12BIT = 0b1110          # 12-bit RGB
    RGB_24BIT = 0b1111          # 24-bit RGB


class LineWidth(IntEnum):
    """Line width settings"""
    NO_LINE = 0b00
    FINE = 0b01
    MEDIUM = 0b10
    THICK = 0b11


class LineType(IntEnum):
    """Line type settings"""
    SOLID = 0b00
    DASH = 0b01
    DOT = 0b10
    RESERVED = 0b11


class AspectRatio(IntEnum):
    """Aspect ratio codes"""
    RATIO_1_1 = 0b00
    RATIO_4_3 = 0b01
    RATIO_16_9 = 0b10
    RATIO_64_27 = 0b1100
    RATIO_256_81 = 0b1101
    RATIO_1024_243 = 0b1110
    RATIO_4096_729 = 0b1111


class Orientation(IntEnum):
    """Display orientation"""
    LANDSCAPE = 0
    PORTRAIT = 1


class ElementType(Enum):
    """Element types in WVG"""
    LOCAL_ENVELOPE = auto()
    POLYLINE = auto()
    CIRCULAR_POLYLINE = auto()
    BEZIER_POLYLINE = auto()
    SIMPLE_SHAPE = auto()
    REUSE = auto()
    GROUP = auto()
    ANIMATION = auto()
    POLYGON = auto()
    SPECIAL_SHAPE = auto()
    FRAME = auto()
    TEXT = auto()
    EXTENDED = auto()


class SimpleShapeType(IntEnum):
    """Simple shape types"""
    RECTANGLE = 0
    ELLIPSE = 1


class SpecialShapeType(IntEnum):
    """Special shape types"""
    REGULAR_POLYGON = 0b00
    STAR = 0b01
    GRID = 0b10


class PolygonType(IntEnum):
    """Polygon base types"""
    POLYLINE = 0b00
    CIRCULAR_POLYLINE = 0b01
    BEZIER_POLYLINE = 0b10


class AnimationMode(IntEnum):
    """Animation mode"""
    SIMPLE = 0
    STANDARD = 1


class AnimationCycleType(IntEnum):
    """Animation cycle type"""
    SHORT = 0  # ~1 second, 4 segments
    LONG = 1   # ~2 seconds, 8 segments


class TextCodeMode(IntEnum):
    """Text encoding mode"""
    GSM_7BIT = 0
    UCS2_16BIT = 1


class CoordinateMode(IntEnum):
    """Coordinate system mode"""
    FLAT = 0
    COMPACT = 1


# ==============================================================================
# Color Data Structures
# ==============================================================================

@dataclass
class Color:
    """RGB Color representation"""
    r: int = 0
    g: int = 0
    b: int = 0


@dataclass
class ColorPalette6Bit:
    """6-bit color palette"""
    num_colors: int = 0  # 1-32 colors
    colors: List[Color] = field(default_factory=list)


@dataclass
class ColorPalette8Bit:
    """8-bit websafe color palette"""
    num_colors: int = 0  # 1-128 colors
    colors: List[int] = field(default_factory=list)  # websafe indices


@dataclass
class ColorConfiguration:
    """Color configuration from header"""
    scheme: ColorScheme = ColorScheme.BLACK_WHITE
    palette_6bit: Optional[ColorPalette6Bit] = None
    palette_8bit: Optional[ColorPalette8Bit] = None


@dataclass
class DefaultColors:
    """Default colors for drawing"""
    line_color: Optional[Color] = None       # BLACK if not specified
    fill_color: Optional[Color] = None       # No fill if not specified
    background_color: Optional[Color] = None  # WHITE if not specified


# ==============================================================================
# Coordinate System Structures
# ==============================================================================

@dataclass
class PeakDescription:
    """Peak description for compact coordinate grid"""
    peak_value: float = 1.0      # 1.0, 1.5, 2.0, or 2.5
    peak_position: float = 0.5   # 0/12 to 12/12
    peak_width: float = 0.4      # 0.3, 0.4, 0.5, or 0.6


@dataclass
class Point:
    """A coordinate point"""
    x: int = 0
    y: int = 0


@dataclass
class Offset:
    """Relative coordinate offset"""
    x: int = 0
    y: int = 0


@dataclass
class CompactCoordinateParams:
    """Compact coordinate system parameters"""
    aspect_ratio: AspectRatio = AspectRatio.RATIO_1_1
    orientation: Orientation = Orientation.LANDSCAPE
    trans_xy_bits: int = 5  # 5-8 bits for translation
    max_x_bits: int = 4     # determines grid lines: 15, 31, 63, 127
    max_y_bits: int = 4
    peak_x: Optional[PeakDescription] = None
    peak_y: Optional[PeakDescription] = None
    redefine_resolution_hint: bool = False


@dataclass
class FlatCoordinateParams:
    """Flat coordinate system parameters"""
    drawing_width: int = 0
    drawing_height: int = 0
    max_x_bits: int = 0
    max_y_bits: int = 0
    xy_all_positive: bool = True
    trans_xy_bits: int = 0
    num_points_bits: int = 0
    offset_x_bits_level1: int = 0
    offset_y_bits_level1: int = 0
    offset_x_bits_level2: int = 0
    offset_y_bits_level2: int = 0


# ==============================================================================
# Header Structures
# ==============================================================================

@dataclass
class TimeStamp:
    """Timestamp in WVG header"""
    year: int = 0
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0


@dataclass
class GeneralInfo:
    """General info from standard WVG header"""
    version: int = 0
    text_code_mode: TextCodeMode = TextCodeMode.GSM_7BIT
    author: Optional[str] = None
    title: Optional[str] = None
    timestamp: Optional[TimeStamp] = None


@dataclass
class ElementMask:
    """Element mask indicating which elements are present"""
    has_local_envelope: bool = False
    has_polyline: bool = False
    has_circular_polyline: bool = False
    has_bezier_polyline: bool = False
    has_simple_shape: bool = False
    has_reuse: bool = False
    has_group: bool = False
    has_animation: bool = False
    # Extension bits
    has_polygon: bool = False
    has_special_shape: bool = False
    has_frame: bool = False
    has_text: bool = False
    has_extended: bool = False


@dataclass
class AttributeMask:
    """Attribute mask indicating which attributes are used"""
    has_line_type: bool = False
    has_line_width: bool = False
    has_fill: bool = False
    has_line_color: bool = False


@dataclass
class GenericParameters:
    """Generic codec parameters"""
    angle_resolution: float = 22.5  # degrees per unit
    angle_bits: int = 3
    scale_resolution: float = 0.25  # 1/4
    scale_bits: int = 3
    index_bits: int = 3
    curve_offset_bits: int = 4  # 4 or 5 bits


@dataclass
class CodecParameters:
    """Codec parameters from header"""
    element_mask: ElementMask = field(default_factory=ElementMask)
    attribute_mask: AttributeMask = field(default_factory=AttributeMask)
    generic_params: GenericParameters = field(default_factory=GenericParameters)
    coordinate_mode: CoordinateMode = CoordinateMode.COMPACT
    compact_params: Optional[CompactCoordinateParams] = None
    flat_params: Optional[FlatCoordinateParams] = None


@dataclass
class CharacterSizeWVGHeader:
    """Header for character size WVG"""
    is_compact: bool = False
    aspect_ratio: AspectRatio = AspectRatio.RATIO_1_1
    has_polyline: bool = False
    has_circular_polyline: bool = False
    has_bezier_polyline: bool = False
    relative_use: bool = False
    max_x_bits: int = 3
    max_y_bits: int = 3
    peak_x: Optional[PeakDescription] = None
    peak_y: Optional[PeakDescription] = None


@dataclass
class StandardWVGHeader:
    """Header for standard WVG"""
    general_info: GeneralInfo = field(default_factory=GeneralInfo)
    color_config: ColorConfiguration = field(default_factory=ColorConfiguration)
    default_colors: DefaultColors = field(default_factory=DefaultColors)
    codec_params: CodecParameters = field(default_factory=CodecParameters)
    animation_mode: AnimationMode = AnimationMode.SIMPLE


# ==============================================================================
# Element Attributes
# ==============================================================================

@dataclass
class ElementAttributes:
    """Attributes for graphical elements"""
    line_type: LineType = LineType.SOLID
    line_width: LineWidth = LineWidth.FINE
    line_color: Optional[Color] = None
    has_fill: bool = False
    fill_color: Optional[Color] = None


@dataclass
class OverrideAttributeSet:
    """Override attributes for reuse elements"""
    line_type: Optional[LineType] = None
    line_width: Optional[LineWidth] = None
    line_color: Optional[Color] = None
    has_fill: Optional[bool] = None
    fill_color: Optional[Color] = None


# ==============================================================================
# Transform
# ==============================================================================

@dataclass
class Transform:
    """Transform element for scale, rotate, translate"""
    translate_x: int = 0
    translate_y: int = 0
    angle: Optional[int] = None
    scale_x: Optional[float] = None
    scale_y: Optional[float] = None
    center_x: Optional[int] = None
    center_y: Optional[int] = None


# ==============================================================================
# Line Elements
# ==============================================================================

@dataclass
class PolylineElement:
    """Polyline element - set of straight lines"""
    points: List[Point] = field(default_factory=list)
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class CurveSegment:
    """Curve segment for circular polyline"""
    point: Point = field(default_factory=Point)
    curve_offset: float = 0.0  # -0.5 to 0.5


@dataclass
class CircularPolylineElement:
    """Circular polyline with arc segments"""
    first_point: Point = field(default_factory=Point)
    segments: List[CurveSegment] = field(default_factory=list)
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class BezierPoint:
    """Point in a Bezier curve"""
    point: Point = field(default_factory=Point)
    on_curve: bool = True  # True for on-curve, False for control point


@dataclass
class BezierPolylineElement:
    """Bezier polyline with control points"""
    first_point: Point = field(default_factory=Point)
    points: List[BezierPoint] = field(default_factory=list)
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


# ==============================================================================
# Polygon Elements
# ==============================================================================

@dataclass
class PolygonElement:
    """Closed polygon element"""
    polygon_type: PolygonType = PolygonType.POLYLINE
    # Union of polyline, circular, or bezier data
    polyline: Optional[PolylineElement] = None
    circular_polyline: Optional[CircularPolylineElement] = None
    bezier_polyline: Optional[BezierPolylineElement] = None
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


# ==============================================================================
# Shape Elements
# ==============================================================================

@dataclass
class RectangleElement:
    """Rectangle shape"""
    center: Point = field(default_factory=Point)
    width: int = 0
    height: int = 0
    angle: int = 0
    rounded_corners: bool = False
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class EllipseElement:
    """Ellipse shape"""
    center: Point = field(default_factory=Point)
    width: int = 0  # major axis
    height: int = 0  # minor axis
    angle: int = 0
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class SimpleShapeElement:
    """Simple shape (rectangle or ellipse)"""
    shape_type: SimpleShapeType = SimpleShapeType.RECTANGLE
    rectangle: Optional[RectangleElement] = None
    ellipse: Optional[EllipseElement] = None


@dataclass
class RegularPolygonShape:
    """Regular polygon special shape"""
    center: Point = field(default_factory=Point)
    num_vertices: int = 3  # vertices = value + 3
    diameter: int = 0
    angle: int = 0
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class StarShape:
    """Star special shape"""
    center: Point = field(default_factory=Point)
    num_vertices: int = 3
    vertex_angle: int = 0  # 0, 36, 60, or 90 degrees
    diameter: int = 0
    angle: int = 0
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class GridShape:
    """Grid special shape"""
    center: Point = field(default_factory=Point)
    width: int = 0
    height: int = 0
    rows: int = 1  # 1-16
    columns: int = 1  # 1-16
    angle: int = 0
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


@dataclass
class SpecialShapeElement:
    """Special shape element"""
    shape_type: SpecialShapeType = SpecialShapeType.REGULAR_POLYGON
    regular_polygon: Optional[RegularPolygonShape] = None
    star: Optional[StarShape] = None
    grid: Optional[GridShape] = None


# ==============================================================================
# Text Element
# ==============================================================================

@dataclass
class TextElement:
    """Text element"""
    position: Point = field(default_factory=Point)
    font_size: int = 0
    angle: int = 0
    text_mode: TextCodeMode = TextCodeMode.GSM_7BIT
    text: str = ""
    attributes: ElementAttributes = field(default_factory=ElementAttributes)


# ==============================================================================
# Group Element
# ==============================================================================

@dataclass
class GroupElement:
    """Group element marker"""
    is_end: bool = False
    transform: Optional[Transform] = None
    display: bool = True


# ==============================================================================
# Reuse Element
# ==============================================================================

@dataclass
class ArrayParameter:
    """Array parameters for reuse element"""
    rows: int = 1
    columns: int = 1
    array_width: Optional[int] = None
    array_height: Optional[int] = None


@dataclass
class ReuseElement:
    """Reuse element for referencing other elements"""
    element_index: int = 0
    transform: Transform = field(default_factory=Transform)
    array_params: Optional[ArrayParameter] = None
    override_attrs: Optional[OverrideAttributeSet] = None


# ==============================================================================
# Animation Elements
# ==============================================================================

@dataclass
class SimpleAnimationElement:
    """Simple animation element"""
    cycle_type: AnimationCycleType = AnimationCycleType.SHORT
    visibility_pattern: Optional[int] = None  # 4 or 8 bit pattern
    begin_transform: Optional[Transform] = None
    end_transform: Optional[Transform] = None
    bouncing: bool = False
    rotation_direction: int = 0  # 0=counter-clockwise, 1=clockwise
    round_rotation: bool = False


@dataclass
class StandardAnimationElement:
    """Standard animation element"""
    element_index: int = 0
    begin_transform: Optional[Transform] = None
    end_transform: Optional[Transform] = None
    rotation_direction: int = 0
    round_rotation: bool = False
    begin_line_color: Optional[Color] = None
    begin_fill_color: Optional[Color] = None
    end_line_color: Optional[Color] = None
    end_fill_color: Optional[Color] = None
    begin_time: int = 0  # in 10ms units
    duration: int = 0    # in 10ms units
    exist_after: bool = False
    repeat: bool = False
    bouncing: bool = False


@dataclass
class AnimationElement:
    """Animation element (simple or standard)"""
    mode: AnimationMode = AnimationMode.SIMPLE
    simple: Optional[SimpleAnimationElement] = None
    standard: Optional[StandardAnimationElement] = None


# ==============================================================================
# Frame Element
# ==============================================================================

@dataclass
class FrameElement:
    """Frame element for multi-page graphics"""
    keep_last_frame: bool = False
    has_fill_color: bool = False
    fill_color: Optional[Color] = None


# ==============================================================================
# Local Envelope Element
# ==============================================================================

@dataclass
class LocalEnvelopeDescription:
    """Local envelope description"""
    coordinate_resolution: int = 0  # 0-7 for different scales
    max_xy_bits: int = 3  # 3-6 bits (7, 15, 31, 63 grid lines)


@dataclass
class LocalEnvelopeElement:
    """Local envelope element"""
    is_end: bool = False
    description: Optional[LocalEnvelopeDescription] = None
    position: Optional[Point] = None  # top-left corner in global coords


# ==============================================================================
# Extended Element
# ==============================================================================

@dataclass
class ExtendedElement:
    """Extended element for future expansion"""
    size_of_size: int = 0  # 5-bit value
    size: int = 0  # payload size in bytes
    element_type: int = 0  # 8-bit type
    payload: bytes = b""


# ==============================================================================
# Generic Element Wrapper
# ==============================================================================

@dataclass
class WVGElement:
    """Generic element wrapper"""
    element_type: ElementType = ElementType.POLYLINE
    polyline: Optional[PolylineElement] = None
    circular_polyline: Optional[CircularPolylineElement] = None
    bezier_polyline: Optional[BezierPolylineElement] = None
    polygon: Optional[PolygonElement] = None
    simple_shape: Optional[SimpleShapeElement] = None
    special_shape: Optional[SpecialShapeElement] = None
    text: Optional[TextElement] = None
    group: Optional[GroupElement] = None
    reuse: Optional[ReuseElement] = None
    animation: Optional[AnimationElement] = None
    frame: Optional[FrameElement] = None
    local_envelope: Optional[LocalEnvelopeElement] = None
    extended: Optional[ExtendedElement] = None


# ==============================================================================
# Top-Level WVG Structures
# ==============================================================================

@dataclass
class CharacterSizeWVG:
    """Character size WVG document"""
    header: CharacterSizeWVGHeader = field(default_factory=CharacterSizeWVGHeader)
    elements: List[WVGElement] = field(default_factory=list)


@dataclass
class StandardWVG:
    """Standard WVG document"""
    header: StandardWVGHeader = field(default_factory=StandardWVGHeader)
    num_elements: int = 0
    elements: List[WVGElement] = field(default_factory=list)


@dataclass
class WVGDocument:
    """Top-level WVG document"""
    wvg_type: WVGType = WVGType.STANDARD
    character_size_wvg: Optional[CharacterSizeWVG] = None
    standard_wvg: Optional[StandardWVG] = None


# ==============================================================================
# Web Safe Color Palette
# ==============================================================================

WEBSAFE_PALETTE = [
    (255, 255, 255), (255, 204, 255), (255, 153, 255), (255, 102, 255),
    (255, 51, 255), (255, 0, 255), (255, 255, 204), (255, 204, 204),
    (255, 153, 204), (255, 102, 204), (255, 51, 204), (255, 0, 204),
    (255, 255, 153), (255, 204, 153), (255, 153, 153), (255, 102, 153),
    (255, 51, 153), (255, 0, 153), (204, 255, 255), (204, 204, 255),
    (204, 153, 255), (204, 102, 255), (204, 51, 255), (204, 0, 255),
    (204, 255, 204), (204, 204, 204), (204, 153, 204), (204, 102, 204),
    (204, 51, 204), (204, 0, 204), (204, 255, 153), (204, 204, 153),
    (204, 153, 153), (204, 102, 153), (204, 51, 153), (204, 0, 153),
    (153, 255, 255), (153, 204, 255), (153, 153, 255), (153, 102, 255),
    (153, 51, 255), (153, 0, 255), (153, 255, 204), (153, 204, 204),
    (153, 153, 204), (153, 102, 204), (153, 51, 204), (153, 0, 204),
    (153, 255, 153), (153, 204, 153), (153, 153, 153), (153, 102, 153),
    (153, 51, 153), (153, 0, 153), (102, 255, 255), (102, 204, 255),
    (102, 153, 255), (102, 102, 255), (102, 51, 255), (102, 0, 255),
    (102, 255, 204), (102, 204, 204), (102, 153, 204), (102, 102, 204),
    (102, 51, 204), (102, 0, 204), (102, 255, 153), (102, 204, 153),
    (102, 153, 153), (102, 102, 153), (102, 51, 153), (102, 0, 153),
    (51, 255, 255), (51, 204, 255), (51, 153, 255), (51, 102, 255),
    (51, 51, 255), (51, 0, 255), (51, 255, 204), (51, 204, 204),
    (51, 153, 204), (51, 102, 204), (51, 51, 204), (51, 0, 204),
    (51, 255, 153), (51, 204, 153), (51, 153, 153), (51, 102, 153),
    (51, 51, 153), (51, 0, 153), (0, 255, 255), (0, 204, 255),
    (0, 153, 255), (0, 102, 255), (0, 51, 255), (0, 0, 255),
    (0, 255, 204), (0, 204, 204), (0, 153, 204), (0, 102, 204),
    (0, 51, 204), (0, 0, 204), (0, 255, 153), (0, 204, 153),
    (0, 153, 153), (0, 102, 153), (0, 51, 153), (0, 0, 153),
    (255, 255, 102), (255, 204, 102), (255, 153, 102), (255, 102, 102),
    (255, 51, 102), (255, 0, 102), (255, 255, 51), (255, 204, 51),
    (255, 153, 51), (255, 102, 51), (255, 51, 51), (255, 0, 51),
    (255, 255, 0), (255, 204, 0), (255, 153, 0), (255, 102, 0),
    (255, 51, 0), (255, 0, 0), (204, 255, 102), (204, 204, 102),
    (204, 153, 102), (204, 102, 102), (204, 51, 102), (204, 0, 102),
    (204, 255, 51), (204, 204, 51), (204, 153, 51), (204, 102, 51),
    (204, 51, 51), (204, 0, 51), (204, 255, 0), (204, 204, 0),
    (204, 153, 0), (204, 102, 0), (204, 51, 0), (204, 0, 0),
    (153, 255, 102), (153, 204, 102), (153, 153, 102), (153, 102, 102),
    (153, 51, 102), (153, 0, 102), (153, 255, 51), (153, 204, 51),
    (153, 153, 51), (153, 102, 51), (153, 51, 51), (153, 0, 51),
    (153, 255, 0), (153, 204, 0), (153, 153, 0), (153, 102, 0),
    (153, 51, 0), (153, 0, 0), (102, 255, 102), (102, 204, 102),
    (102, 153, 102), (102, 102, 102), (102, 51, 102), (102, 0, 102),
    (102, 255, 51), (102, 204, 51), (102, 153, 51), (102, 102, 51),
    (102, 51, 51), (102, 0, 51), (102, 255, 0), (102, 204, 0),
    (102, 153, 0), (102, 102, 0), (102, 51, 0), (102, 0, 0),
    (51, 255, 102), (51, 204, 102), (51, 153, 102), (51, 102, 102),
    (51, 51, 102), (51, 0, 102), (51, 255, 51), (51, 204, 51),
    (51, 153, 51), (51, 102, 51), (51, 51, 51), (51, 0, 51),
    (51, 255, 0), (51, 204, 0), (51, 153, 0), (51, 102, 0),
    (51, 51, 0), (51, 0, 0), (0, 255, 102), (0, 204, 102),
    (0, 153, 102), (0, 102, 102), (0, 51, 102), (0, 0, 102),
    (0, 255, 51), (0, 204, 51), (0, 153, 51), (0, 102, 51),
    (0, 51, 51), (0, 0, 51), (0, 255, 0), (0, 204, 0),
    (0, 153, 0), (0, 102, 0), (0, 51, 0), (17, 17, 17),
    (34, 34, 34), (68, 68, 68), (85, 85, 85), (119, 119, 119),
    (136, 136, 136), (170, 170, 170), (187, 187, 187), (221, 221, 221),
    (238, 238, 238), (192, 192, 192), (128, 0, 0), (128, 0, 128),
    (0, 128, 0), (0, 128, 128), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
]


# ==============================================================================
# Constants
# ==============================================================================

# Grid line options for different bit sizes
GRID_LINES_COMPACT = {0: 15, 1: 31, 2: 63, 3: 127}
GRID_LINES_CHAR = {0: 7, 1: 15, 2: 31, 3: 63}

# Peak values
PEAK_VALUES = {0b01: 1.5, 0b10: 2.0, 0b11: 2.5}

# Peak positions (0-12) / 12
PEAK_POSITIONS = [i / 12.0 for i in range(13)]

# Peak widths
PEAK_WIDTHS = {0b00: 0.3, 0b01: 0.4, 0b10: 0.5, 0b11: 0.6}

# Coordinate resolution scales (for redefine resolution)
COORDINATE_RESOLUTIONS = [1/27, 1/32, 1/38, 1/48, 1/64, 1/85, 1/128, 1/160]

# Local envelope grid resolutions
LOCAL_RESOLUTIONS = [1/27, 1/32, 1/48, 1/64, 1/85, 1/128, 1/160]

# Angle resolution values (degrees per unit)
ANGLE_RESOLUTIONS = {0b00: 1.40625, 0b01: 5.625, 0b10: 11.25, 0b11: 22.5}

# Scale resolution values
SCALE_RESOLUTIONS = {0b00: 0.25, 0b01: 1/16, 0b10: 1/64, 0b11: 1/256}

# Vertex angles for stars (degrees)
VERTEX_ANGLES = {0b00: 0, 0b01: 36, 0b10: 60, 0b11: 90}

# 2-bit color value to 8-bit mapping
COLOR_2BIT_TO_8BIT = {0: 0, 1: 85, 2: 170, 3: 255}

# Grayscale colors (2-bit)
GRAYSCALE_COLORS = [
    Color(0, 0, 0),
    Color(85, 85, 85),
    Color(170, 170, 170),
    Color(255, 255, 255),
]

# 4 predefined colors
PREDEFINED_4_COLORS = [
    Color(255, 255, 255),  # White
    Color(255, 0, 0),      # Red
    Color(0, 255, 0),      # Green
    Color(0, 0, 255),      # Blue
]
