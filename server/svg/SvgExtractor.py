import xml.etree.ElementTree as ET

from svg.svg_models import SvgMetaData, SvgRgbMatch, SvgCircle, SvgText, SvgRectangle, SvgLineSegment


class SVGExtractor:
    def __init__(self, svg_string):
        self.svg_string = svg_string

        # tree = ET.parse(self.svg_file)
        tree = ET.ElementTree(ET.fromstring(self.svg_string))
        self.root = tree.getroot()
        w = self.root.attrib.get('width', '100%')
        h = self.root.attrib.get('height', '100%')
        vb = self.root.attrib.get('viewBox')
        self.metadata = SvgMetaData(w, h, vb)

    def get_metadata(self):
        return self.metadata
    def parse_style(self, style_str):
        """Parse the style attribute into a dictionary."""
        style_dict = {}
        for item in style_str.split(';'):
            if ':' in item:
                key, value = item.split(':', 1)
                style_dict[key.strip()] = value.strip()
        return style_dict

    def is_color(self, color, match_color:SvgRgbMatch):
        """Check if the color is blue with a tolerance."""
        color = color.lower().lstrip('#')
        def check_color_part(color_part, match_part):
            if match_part > 0:
                return color_part > match_part
            return color_part < -match_part
        if len(color) == 6:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            is_match = check_color_part(r, match_color.r) and check_color_part(b, match_color.b) and check_color_part(g, match_color.g)
            return is_match
        return False

    def extract_lines(self, stroke:SvgRgbMatch):
        """Extract all blue stroke paths."""

        lines = []

        for elem in self.root.iter():
            if elem.tag.endswith('path'):
                style_str = elem.attrib.get('style', '')
                style = self.parse_style(style_str)
                if 'stroke' in style and self.is_color(style['stroke'], stroke):
                    d = elem.attrib.get('d', '')
                    points = self.parse_path_points(d)
                    for i in range(len(points) - 1):
                        seg = SvgLineSegment(start=points[i], end=points[i + 1])
                        lines.append(seg)
        return lines

    def extract_circles(self, fill:SvgRgbMatch):
        """Extract all blue fill circles."""

        circles = []

        for elem in self.root.iter():
            if elem.tag.endswith('circle'):
                style_str = elem.attrib.get('style', '')
                style = self.parse_style(style_str)
                if 'fill' in style and self.is_color(style['fill'], fill):
                    cx = float(elem.attrib.get('cx', '0'))
                    cy = float(elem.attrib.get('cy', '0'))
                    circles.append(SvgCircle(cx=cx, cy=cy))
        return circles

    def extract_text_elements(self):
        """Extract all text elements along with their bounding boxes."""
        text_elements = []

        for elem in self.root.iter():
            if elem.tag.endswith('text'):
                # Initialize text content
                text_content = ""

                # Check direct text
                if elem.text and elem.text.strip():
                    text_content += elem.text.strip()

                # Check tspans inside text
                for tspan in elem.findall('.//{http://www.w3.org/2000/svg}tspan'):
                    if tspan.text and tspan.text.strip():
                        text_content += tspan.text.strip()

                # Extract the bounding box attributes (x, y, width, height)
                x = float(elem.attrib.get('x', 0))
                y = float(elem.attrib.get('y', 0))

                # Create a TextElement instance
                text_element = SvgText(text=text_content, x=x, y=y)
                text_elements.append(text_element)

        return text_elements

    def extract_rectangles(self, fill:SvgRgbMatch):
        """Extract all blue fill rectangles."""

        rectangles = []

        for elem in self.root.iter():
            if elem.tag.endswith('rect'):
                style_str = elem.attrib.get('style', '')
                style = self.parse_style(style_str)
                if 'fill' in style and self.is_color(style['fill'], fill):
                    x = float(elem.attrib.get('x', '0'))
                    y = float(elem.attrib.get('y', '0'))
                    width = float(elem.attrib.get('width', '0'))
                    height = float(elem.attrib.get('height', '0'))
                    rectangles.append(SvgRectangle(x=x, y=y, width=width, height=height))
        return rectangles

    def parse_path_points(self, d_attr):
        """Parse a simple path data string into a list of points (handles M, L, H, V, Z)."""
        points = []
        tokens = d_attr.replace(',', ' ').split()
        i = 0
        mode = None
        current_x = 0
        current_y = 0
        start_point = None

        while i < len(tokens):
            token = tokens[i]
            if token.upper() in ('M', 'L', 'H', 'V', 'Z'):
                mode = token
                i += 1
                if mode.upper() == 'Z' and start_point:
                    points.append(start_point)  # close path to start
                continue

            if mode:
                is_relative = mode.islower()
                cmd = mode.upper()

                if cmd == 'M' or cmd == 'L':
                    x = float(tokens[i])
                    y = float(tokens[i+1])
                    if is_relative:
                        current_x += x
                        current_y += y
                    else:
                        current_x = x
                        current_y = y
                    points.append((current_x, current_y))
                    if cmd == 'M' and not start_point:
                        start_point = (current_x, current_y)
                    i += 2

                elif cmd == 'H':
                    x = float(tokens[i])
                    if is_relative:
                        current_x += x
                    else:
                        current_x = x
                    points.append((current_x, current_y))
                    i += 1

                elif cmd == 'V':
                    y = float(tokens[i])
                    if is_relative:
                        current_y += y
                    else:
                        current_y = y
                    points.append((current_x, current_y))
                    i += 1
        return points
