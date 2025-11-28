"""
WVG Parser - Annex G
Based on 3GPP TS 23.040 version 16.0.0 Release 16 - Annex G

This is a starting point outline for parsing StandardWVG headers.
"""

from dataclasses import dataclass
from typing import Optional, List
from model import (
    WVGType, StandardWVGHeader, GeneralInfo, ColorConfiguration,
    DefaultColors, CodecParameters, ColorScheme, TextCodeMode,
    TimeStamp, ElementMask, AttributeMask, GenericParameters,
    CoordinateMode, CompactCoordinateParams, FlatCoordinateParams,
    AspectRatio, Orientation, AnimationMode,
    CharacterSizeWVGHeader, CharacterSizeWVG, PeakDescription,
    PEAK_VALUES, PEAK_POSITIONS, PEAK_WIDTHS, GRID_LINES_CHAR,
    WVGElement, ElementType, Point, PolylineElement, CircularPolylineElement,
    BezierPolylineElement, CurveSegment, BezierPoint, ReuseElement, Transform
)


class BitReader:
    """Helper class to read bits from a byte stream."""
    
    def __init__(self, data: bytes):
        self.data = data
        self.byte_pos = 0
        self.bit_pos = 0  # 0-7, MSB first
    
    def read_bits(self, num_bits: int) -> int:
        """Read n bits from the stream, MSB first."""
        result = 0
        for _ in range(num_bits):
            if self.byte_pos >= len(self.data):
                raise EOFError("End of data reached")
            
            # Read bit (MSB first)
            byte = self.data[self.byte_pos]
            bit = (byte >> (7 - self.bit_pos)) & 1
            result = (result << 1) | bit
            
            # Advance position
            self.bit_pos += 1
            if self.bit_pos == 8:
                self.bit_pos = 0
                self.byte_pos += 1
        
        return result
    
    def read_bit(self) -> int:
        """Read a single bit."""
        return self.read_bits(1)
    
    def read_byte(self) -> int:
        """Read a full byte (8 bits)."""
        return self.read_bits(8)
    
    def peek_bits(self, num_bits: int) -> int:
        """Peek at the next n bits without consuming them."""
        saved_byte_pos = self.byte_pos
        saved_bit_pos = self.bit_pos
        result = self.read_bits(num_bits)
        self.byte_pos = saved_byte_pos
        self.bit_pos = saved_bit_pos
        return result
    
    @property
    def position(self) -> tuple[int, int]:
        """Return current position as (byte_pos, bit_pos)."""
        return (self.byte_pos, self.bit_pos)
    
    @property
    def total_bits_read(self) -> int:
        """Return total number of bits read."""
        return self.byte_pos * 8 + self.bit_pos


class WVGParser:
    """Parser for WVG (Wireless Vector Graphics) format."""
    
    def __init__(self, data: bytes):
        self.reader = BitReader(data)
        self.data = data
    
    def parse(self):
        """Parse the WVG data and return a parsed structure."""
        # First bit determines WVG type
        wvg_type_bit = self.reader.read_bit()
        wvg_type = WVGType(wvg_type_bit)
        
        print(f"WVG Type: {'Standard WVG' if wvg_type == WVGType.STANDARD else 'Character Size WVG'}")
        
        if wvg_type == WVGType.STANDARD:
            return self.parse_standard_wvg()
        else:
            return self.parse_character_size_wvg()
    
    def parse_standard_wvg(self) -> StandardWVGHeader:
        """Parse Standard WVG header."""
        header = StandardWVGHeader()
        
        # Parse General Info
        header.general_info = self.parse_general_info()
        
        # Parse Color Configuration
        header.color_config = self.parse_color_configuration()
        
        # Parse Default Colors
        header.default_colors = self.parse_default_colors()
        
        # Parse Codec Parameters
        header.codec_params = self.parse_codec_parameters()
        
        return header
    
    def parse_general_info(self) -> GeneralInfo:
        """
        Parse General Info section of StandardWVG header.
        
        Structure (from spec):
        - Version: 4 bits (0-15)
        - Text code mode: 1 bit (0=GSM 7-bit, 1=UCS2 16-bit)
        - Has author: 1 bit
        - Has title: 1 bit  
        - Has timestamp: 1 bit
        - [Author string if present]
        - [Title string if present]
        - [Timestamp if present]
        """
        info = GeneralInfo()
        
        # Version (4 bits)
        info.version = self.reader.read_bits(4)
        print(f"  Version: {info.version}")
        
        # Text code mode (1 bit)
        text_mode = self.reader.read_bit()
        info.text_code_mode = TextCodeMode(text_mode)
        print(f"  Text Code Mode: {'UCS2 16-bit' if text_mode else 'GSM 7-bit'}")
        
        # Optional fields flags
        has_author = self.reader.read_bit()
        has_title = self.reader.read_bit()
        has_timestamp = self.reader.read_bit()
        
        print(f"  Has Author: {bool(has_author)}")
        print(f"  Has Title: {bool(has_title)}")
        print(f"  Has Timestamp: {bool(has_timestamp)}")
        
        # TODO: Parse author string if present
        if has_author:
            info.author = self._parse_string(info.text_code_mode)
            print(f"  Author: {info.author}")
        
        # TODO: Parse title string if present
        if has_title:
            info.title = self._parse_string(info.text_code_mode)
            print(f"  Title: {info.title}")
        
        # TODO: Parse timestamp if present
        if has_timestamp:
            info.timestamp = self._parse_timestamp()
            print(f"  Timestamp: {info.timestamp}")
        
        return info
    
    def _parse_string(self, text_mode: TextCodeMode) -> str:
        """Parse a string based on text mode. Placeholder implementation."""
        # TODO: Implement proper string parsing
        # GSM 7-bit or UCS2 16-bit encoding
        # Need to determine length first
        return "<string parsing not implemented>"
    
    def _parse_timestamp(self) -> TimeStamp:
        """Parse timestamp. Placeholder implementation."""
        # TODO: Implement timestamp parsing
        # Typically: year, month, day, hour, minute, second
        return TimeStamp()
    
    def parse_color_configuration(self) -> ColorConfiguration:
        """
        Parse Color Configuration section.
        
        Structure:
        - Color scheme code: variable bits (see ColorScheme enum)
        - [Palette data if applicable]
        """
        config = ColorConfiguration()
        
        # TODO: Parse color scheme (variable length prefix code)
        # First check 2 bits, may need more
        first_bits = self.reader.read_bits(2)
        
        if first_bits <= 1:
            # 2-bit codes: 00 = B/W, 01 = reserved
            config.scheme = ColorScheme.BLACK_WHITE if first_bits == 0 else ColorScheme.BLACK_WHITE
        else:
            # Need to read more bits for longer codes
            # This is a placeholder - actual parsing depends on prefix codes
            config.scheme = ColorScheme.BLACK_WHITE
        
        print(f"  Color Scheme: {config.scheme.name}")
        
        return config
    
    def parse_default_colors(self) -> DefaultColors:
        """
        Parse Default Colors section.
        
        Structure depends on color scheme and flags.
        """
        colors = DefaultColors()
        # TODO: Implement based on color scheme
        return colors
    
    def parse_codec_parameters(self) -> CodecParameters:
        """
        Parse Codec Parameters section.
        
        Structure:
        - Element mask (8+ bits)
        - Attribute mask (4 bits)
        - Generic parameters
        - Coordinate system parameters
        """
        params = CodecParameters()
        
        # Parse Element Mask
        params.element_mask = self.parse_element_mask()
        
        # Parse Attribute Mask
        params.attribute_mask = self.parse_attribute_mask()
        
        # Parse Generic Parameters
        params.generic_params = self.parse_generic_parameters()
        
        # Parse Coordinate System
        # TODO: Determine if compact or flat mode
        
        return params
    
    def parse_element_mask(self) -> ElementMask:
        """
        Parse Element Mask.
        
        8 bits for basic elements:
        - bit 0: local envelope
        - bit 1: polyline
        - bit 2: circular polyline
        - bit 3: bezier polyline
        - bit 4: simple shape
        - bit 5: reuse
        - bit 6: group
        - bit 7: animation
        
        If extension bit set, 5 more bits follow.
        """
        mask = ElementMask()
        
        mask.has_local_envelope = bool(self.reader.read_bit())
        mask.has_polyline = bool(self.reader.read_bit())
        mask.has_circular_polyline = bool(self.reader.read_bit())
        mask.has_bezier_polyline = bool(self.reader.read_bit())
        mask.has_simple_shape = bool(self.reader.read_bit())
        mask.has_reuse = bool(self.reader.read_bit())
        mask.has_group = bool(self.reader.read_bit())
        mask.has_animation = bool(self.reader.read_bit())
        
        print(f"  Element Mask: envelope={mask.has_local_envelope}, polyline={mask.has_polyline}, "
              f"circular={mask.has_circular_polyline}, bezier={mask.has_bezier_polyline}")
        
        # TODO: Check for extension bit and parse additional elements
        
        return mask
    
    def parse_attribute_mask(self) -> AttributeMask:
        """
        Parse Attribute Mask (4 bits).
        
        - bit 0: line type
        - bit 1: line width
        - bit 2: fill
        - bit 3: line color
        """
        mask = AttributeMask()
        
        mask.has_line_type = bool(self.reader.read_bit())
        mask.has_line_width = bool(self.reader.read_bit())
        mask.has_fill = bool(self.reader.read_bit())
        mask.has_line_color = bool(self.reader.read_bit())
        
        print(f"  Attribute Mask: line_type={mask.has_line_type}, line_width={mask.has_line_width}, "
              f"fill={mask.has_fill}, line_color={mask.has_line_color}")
        
        return mask
    
    def parse_generic_parameters(self) -> GenericParameters:
        """
        Parse Generic Parameters.
        
        - Angle resolution: 2 bits
        - Scale resolution: 2 bits
        - Index bits: 3 bits (value + 3)
        - Curve offset bits: 1 bit (4 or 5)
        """
        params = GenericParameters()
        
        # TODO: Implement generic parameter parsing
        
        return params
    
    def parse_character_size_wvg(self) -> CharacterSizeWVG:
        """
        Parse Character Size WVG.
        
        Structure (from spec):
        - Compact mode: 1 bit (0=not compact, 1=compact)
        - If compact:
            - Aspect ratio: 2 bits (may extend to 4 bits)
            - Has polyline: 1 bit
            - Has circular polyline: 1 bit
            - Has bezier polyline: 1 bit
            - Relative use: 1 bit
            - Max X bits: 2 bits (grid lines: 7, 15, 31, 63)
            - Max Y bits: 2 bits
            - [Peak X description if non-uniform]
            - [Peak Y description if non-uniform]
        - If not compact:
            - Similar but with different coordinate encoding
        - Elements follow after header
        """
        wvg = CharacterSizeWVG()
        header = CharacterSizeWVGHeader()
        
        # Compact mode (1 bit)
        header.is_compact = bool(self.reader.read_bit())
        print(f"  Compact Mode: {header.is_compact}")
        
        if header.is_compact:
            header = self._parse_compact_char_header(header)
        else:
            header = self._parse_non_compact_char_header(header)
        
        wvg.header = header
        
        # Store header for element parsing context
        self._char_header = header
        
        # Parse elements
        print("\n  Parsing Elements:")
        wvg.elements = self._parse_char_size_elements(header)
        
        return wvg
    
    def _parse_char_size_elements(self, header: CharacterSizeWVGHeader) -> List[WVGElement]:
        """
        Parse Character Size WVG elements.
        
        Element type is determined by prefix code based on which elements
        are present (from header flags):
        - If only polyline: no type code needed, all are polylines
        - If 2 types: 1 bit prefix (0 or 1)
        - If 3 types: variable prefix (0, 10, 11)
        
        Elements present can be: polyline, circular polyline, bezier polyline, reuse
        """
        elements = []
        
        # Determine which element types are available
        available_types = []
        if header.has_polyline:
            available_types.append('polyline')
        if header.has_circular_polyline:
            available_types.append('circular')
        if header.has_bezier_polyline:
            available_types.append('bezier')
        if header.relative_use:
            available_types.append('reuse')
        
        print(f"    Available element types: {available_types}")
        
        # Calculate bits needed for element type coding
        num_types = len(available_types)
        if num_types == 0:
            print("    No element types available!")
            return elements
        
        element_count = 0
        max_elements = 100  # Safety limit
        
        try:
            while element_count < max_elements:
                # Check if we have enough data left
                remaining_bits = (len(self.data) - self.reader.byte_pos) * 8 - self.reader.bit_pos
                if remaining_bits < 4:  # Minimum bits for any element
                    print(f"    End of data (remaining bits: {remaining_bits})")
                    break
                
                # Parse element type
                element_type = self._parse_char_element_type(available_types)
                if element_type is None:
                    break
                
                print(f"    Element {element_count}: type={element_type}")
                
                # Parse the element based on type
                element = self._parse_char_element(element_type, header)
                if element:
                    elements.append(element)
                    element_count += 1
                else:
                    break
                    
        except EOFError:
            print(f"    Reached end of data after {element_count} elements")
        
        print(f"    Total elements parsed: {len(elements)}")
        return elements
    
    def _parse_char_element_type(self, available_types: List[str]) -> Optional[str]:
        """
        Parse element type code for character size WVG.
        
        Encoding depends on number of available types:
        - 1 type: no code needed
        - 2 types: 1 bit (0=first, 1=second)
        - 3 types: prefix code (0=first, 10=second, 11=third)
        - 4 types: prefix code (0=first, 10=second, 110=third, 111=fourth)
        """
        num_types = len(available_types)
        
        if num_types == 1:
            return available_types[0]
        
        if num_types == 2:
            bit = self.reader.read_bit()
            return available_types[bit]
        
        if num_types == 3:
            first_bit = self.reader.read_bit()
            if first_bit == 0:
                return available_types[0]
            else:
                second_bit = self.reader.read_bit()
                return available_types[1] if second_bit == 0 else available_types[2]
        
        if num_types == 4:
            first_bit = self.reader.read_bit()
            if first_bit == 0:
                return available_types[0]
            else:
                second_bit = self.reader.read_bit()
                if second_bit == 0:
                    return available_types[1]
                else:
                    third_bit = self.reader.read_bit()
                    return available_types[2] if third_bit == 0 else available_types[3]
        
        return None
    
    def _parse_char_element(self, element_type: str, header: CharacterSizeWVGHeader) -> Optional[WVGElement]:
        """Parse a single character size WVG element."""
        element = WVGElement()
        
        if element_type == 'polyline':
            element.element_type = ElementType.POLYLINE
            element.polyline = self._parse_char_polyline(header)
        elif element_type == 'circular':
            element.element_type = ElementType.CIRCULAR_POLYLINE
            element.circular_polyline = self._parse_char_circular_polyline(header)
        elif element_type == 'bezier':
            element.element_type = ElementType.BEZIER_POLYLINE
            element.bezier_polyline = self._parse_char_bezier_polyline(header)
        elif element_type == 'reuse':
            element.element_type = ElementType.REUSE
            element.reuse = self._parse_char_reuse(header)
        else:
            return None
        
        return element
    
    def _parse_char_polyline(self, header: CharacterSizeWVGHeader) -> PolylineElement:
        """
        Parse a polyline element in character size WVG.
        
        Structure:
        - Number of points: variable (encoded)
        - First point: (max_x_bits, max_y_bits)
        - Subsequent points: relative offsets or absolute
        """
        polyline = PolylineElement()
        
        # Parse number of points
        num_points = self._parse_char_num_points()
        print(f"      Polyline with {num_points} points")
        
        # Parse first point (absolute coordinates)
        first_x = self.reader.read_bits(header.max_x_bits)
        first_y = self.reader.read_bits(header.max_y_bits)
        polyline.points.append(Point(x=first_x, y=first_y))
        print(f"        Point 0: ({first_x}, {first_y})")
        
        # Parse remaining points
        for i in range(1, num_points):
            point = self._parse_char_point(header, polyline.points[-1])
            polyline.points.append(point)
            if i < 5:  # Only print first few
                print(f"        Point {i}: ({point.x}, {point.y})")
        
        if num_points > 5:
            print(f"        ... ({num_points - 5} more points)")
        
        return polyline
    
    def _parse_char_circular_polyline(self, header: CharacterSizeWVGHeader) -> CircularPolylineElement:
        """
        Parse a circular polyline element in character size WVG.
        
        Structure:
        - Number of segments: variable
        - First point: absolute
        - Segments: point + curve offset
        """
        circular = CircularPolylineElement()
        
        # Parse number of segments
        num_segments = self._parse_char_num_points()
        print(f"      Circular polyline with {num_segments} segments")
        
        # Parse first point
        first_x = self.reader.read_bits(header.max_x_bits)
        first_y = self.reader.read_bits(header.max_y_bits)
        circular.first_point = Point(x=first_x, y=first_y)
        print(f"        First point: ({first_x}, {first_y})")
        
        # Parse segments
        last_point = circular.first_point
        for i in range(num_segments):
            segment = CurveSegment()
            segment.point = self._parse_char_point(header, last_point)
            # Curve offset: typically 4 or 5 bits, signed
            curve_bits = 4  # TODO: Get from codec params
            offset_raw = self.reader.read_bits(curve_bits)
            # Convert to signed offset (-0.5 to 0.5 range)
            max_val = (1 << curve_bits) - 1
            segment.curve_offset = (offset_raw - max_val / 2) / max_val
            circular.segments.append(segment)
            last_point = segment.point
            if i < 3:
                print(f"        Segment {i}: ({segment.point.x}, {segment.point.y}), curve={segment.curve_offset:.3f}")
        
        if num_segments > 3:
            print(f"        ... ({num_segments - 3} more segments)")
        
        return circular
    
    def _parse_char_bezier_polyline(self, header: CharacterSizeWVGHeader) -> BezierPolylineElement:
        """
        Parse a bezier polyline element in character size WVG.
        
        Structure:
        - Number of points: variable
        - First point: absolute (always on-curve)
        - Subsequent points: on-curve flag + coordinates
        """
        bezier = BezierPolylineElement()
        
        # Parse number of points
        num_points = self._parse_char_num_points()
        print(f"      Bezier polyline with {num_points} points")
        
        # Parse first point (always on-curve)
        first_x = self.reader.read_bits(header.max_x_bits)
        first_y = self.reader.read_bits(header.max_y_bits)
        bezier.first_point = Point(x=first_x, y=first_y)
        print(f"        First point: ({first_x}, {first_y}) [on-curve]")
        
        # Parse remaining points
        last_point = bezier.first_point
        for i in range(num_points - 1):
            bp = BezierPoint()
            # On-curve flag: 1 bit
            bp.on_curve = bool(self.reader.read_bit())
            bp.point = self._parse_char_point(header, last_point)
            bezier.points.append(bp)
            last_point = bp.point
            if i < 3:
                curve_str = "on-curve" if bp.on_curve else "control"
                print(f"        Point {i+1}: ({bp.point.x}, {bp.point.y}) [{curve_str}]")
        
        if num_points > 4:
            print(f"        ... ({num_points - 4} more points)")
        
        return bezier
    
    def _parse_char_reuse(self, header: CharacterSizeWVGHeader) -> ReuseElement:
        """
        Parse a reuse element in character size WVG.
        
        Structure:
        - Element index: variable bits
        - Transform: translation, optional rotation/scale
        """
        reuse = ReuseElement()
        
        # Element index: typically 3-6 bits depending on number of elements
        index_bits = 3  # TODO: Calculate from context
        reuse.element_index = self.reader.read_bits(index_bits)
        print(f"      Reuse element index: {reuse.element_index}")
        
        # Transform
        reuse.transform = Transform()
        reuse.transform.translate_x = self.reader.read_bits(header.max_x_bits)
        reuse.transform.translate_y = self.reader.read_bits(header.max_y_bits)
        print(f"        Translation: ({reuse.transform.translate_x}, {reuse.transform.translate_y})")
        
        # TODO: Parse optional rotation and scale
        
        return reuse
    
    def _parse_char_num_points(self) -> int:
        """
        Parse number of points using variable-length encoding.
        
        Encoding (typical):
        - 0-6: 3 bits direct
        - 7+: 3 bits = 111, then additional bits
        """
        # First 3 bits
        val = self.reader.read_bits(3)
        if val < 7:
            return val + 2  # Minimum 2 points
        
        # Extended encoding
        ext = self.reader.read_bits(3)
        if ext < 7:
            return 7 + ext + 2
        
        # Further extension
        ext2 = self.reader.read_bits(4)
        return 14 + ext2 + 2
    
    def _parse_char_point(self, header: CharacterSizeWVGHeader, last_point: Point) -> Point:
        """
        Parse a point coordinate in character size WVG.
        
        Uses relative encoding from last point.
        """
        # Read relative offset
        # Offset encoding depends on grid configuration
        # For simplicity, using same bits as absolute coordinates
        # TODO: Implement proper relative encoding
        
        x = self.reader.read_bits(header.max_x_bits)
        y = self.reader.read_bits(header.max_y_bits)
        
        return Point(x=x, y=y)
    
    def _parse_compact_char_header(self, header: CharacterSizeWVGHeader) -> CharacterSizeWVGHeader:
        """Parse compact character size WVG header."""
        
        # Aspect ratio (2 bits, may extend to 4)
        aspect_bits = self.reader.read_bits(2)
        if aspect_bits == 0b11:
            # Extended aspect ratio - read 2 more bits
            ext_bits = self.reader.read_bits(2)
            aspect_code = (0b11 << 2) | ext_bits
            header.aspect_ratio = self._decode_aspect_ratio(aspect_code)
        else:
            header.aspect_ratio = AspectRatio(aspect_bits)
        print(f"  Aspect Ratio: {header.aspect_ratio.name}")
        
        # Element presence flags
        header.has_polyline = bool(self.reader.read_bit())
        header.has_circular_polyline = bool(self.reader.read_bit())
        header.has_bezier_polyline = bool(self.reader.read_bit())
        print(f"  Elements: polyline={header.has_polyline}, circular={header.has_circular_polyline}, "
              f"bezier={header.has_bezier_polyline}")
        
        # Relative use flag
        header.relative_use = bool(self.reader.read_bit())
        print(f"  Relative Use: {header.relative_use}")
        
        # Max X and Y bits (2 bits each, gives grid lines: 7, 15, 31, 63)
        max_x_code = self.reader.read_bits(2)
        max_y_code = self.reader.read_bits(2)
        header.max_x_bits = max_x_code + 3  # 3-6 bits
        header.max_y_bits = max_y_code + 3
        print(f"  Grid: max_x_bits={header.max_x_bits} ({GRID_LINES_CHAR.get(max_x_code, '?')} lines), "
              f"max_y_bits={header.max_y_bits} ({GRID_LINES_CHAR.get(max_y_code, '?')} lines)")
        
        # Check for non-uniform grid (peak descriptions)
        # Peak X
        has_peak_x = bool(self.reader.read_bit())
        if has_peak_x:
            header.peak_x = self._parse_peak_description()
            print(f"  Peak X: value={header.peak_x.peak_value}, pos={header.peak_x.peak_position}, "
                  f"width={header.peak_x.peak_width}")
        
        # Peak Y
        has_peak_y = bool(self.reader.read_bit())
        if has_peak_y:
            header.peak_y = self._parse_peak_description()
            print(f"  Peak Y: value={header.peak_y.peak_value}, pos={header.peak_y.peak_position}, "
                  f"width={header.peak_y.peak_width}")
        
        return header
    
    def _parse_non_compact_char_header(self, header: CharacterSizeWVGHeader) -> CharacterSizeWVGHeader:
        """Parse non-compact character size WVG header. Placeholder."""
        # TODO: Implement non-compact mode parsing
        # Non-compact mode uses flat coordinate system
        print("  Non-compact character size WVG parsing not fully implemented")
        
        # Element presence flags (same as compact)
        header.has_polyline = bool(self.reader.read_bit())
        header.has_circular_polyline = bool(self.reader.read_bit())
        header.has_bezier_polyline = bool(self.reader.read_bit())
        print(f"  Elements: polyline={header.has_polyline}, circular={header.has_circular_polyline}, "
              f"bezier={header.has_bezier_polyline}")
        
        # Relative use flag
        header.relative_use = bool(self.reader.read_bit())
        print(f"  Relative Use: {header.relative_use}")
        
        # In non-compact mode, coordinate bits are specified differently
        # TODO: Parse flat coordinate parameters
        
        return header
    
    def _parse_peak_description(self) -> PeakDescription:
        """
        Parse a peak description for non-uniform grid.
        
        Structure:
        - Peak value: 2 bits (00=no peak/1.0, 01=1.5, 10=2.0, 11=2.5)
        - Peak position: 4 bits (0-12, as fraction of 12)
        - Peak width: 2 bits (00=0.3, 01=0.4, 10=0.5, 11=0.6)
        """
        peak = PeakDescription()
        
        # Peak value (2 bits)
        value_code = self.reader.read_bits(2)
        peak.peak_value = PEAK_VALUES.get(value_code, 1.0)
        
        # Peak position (4 bits, 0-12)
        pos_code = self.reader.read_bits(4)
        if pos_code <= 12:
            peak.peak_position = PEAK_POSITIONS[pos_code]
        else:
            peak.peak_position = 0.5  # Default to center if invalid
        
        # Peak width (2 bits)
        width_code = self.reader.read_bits(2)
        peak.peak_width = PEAK_WIDTHS.get(width_code, 0.4)
        
        return peak
    
    def _decode_aspect_ratio(self, code: int) -> AspectRatio:
        """Decode aspect ratio from code."""
        # Map extended codes to AspectRatio enum
        aspect_map = {
            0b00: AspectRatio.RATIO_1_1,
            0b01: AspectRatio.RATIO_4_3,
            0b10: AspectRatio.RATIO_16_9,
            0b1100: AspectRatio.RATIO_64_27,
            0b1101: AspectRatio.RATIO_256_81,
            0b1110: AspectRatio.RATIO_1024_243,
            0b1111: AspectRatio.RATIO_4096_729,
        }
        return aspect_map.get(code, AspectRatio.RATIO_1_1)


def load_wvg_from_hex(hex_string: str) -> bytes:
    """Convert a hex string to bytes."""
    # Remove any whitespace and newlines
    hex_string = hex_string.replace(' ', '').replace('\n', '').replace('\r', '')
    return bytes.fromhex(hex_string)


def main():
    """Main entry point."""
    import sys
    
    # Example: Load from file or use test data
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            data = f.read()
    else:
        # Test with sample hex data
        # This would typically come from parsing the wvg file
        test_hex = "6a186800800c8028004040081d6e666aa24029a44d3705bd037883f53071a732498a59925755"
        data = load_wvg_from_hex(test_hex)
    
    print(f"Data length: {len(data)} bytes")
    print(f"First bytes (hex): {data[:16].hex()}")
    print()
    
    parser = WVGParser(data)
    
    try:
        result = parser.parse()
        print()
        print("Parsing completed!")
        print(f"Bits read: {parser.reader.total_bits_read}")
    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
