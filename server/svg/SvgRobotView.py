import xml.etree.ElementTree as ET

class SvgRobotView:
    def __init__(self, id: str, has_package: bool, is_idle: bool, angle_deg: float, x: float, y: float):
        self.id = id
        self.has_package = has_package
        self.is_idle = is_idle
        self.angle_deg = angle_deg
        self.x = x
        self.y = y

    def to_element(self) -> ET.Element:
        group = ET.Element('g', attrib={
            'transform': f'translate({self.x},{self.y})'
        })

        # Base magenta rotated square (body)
        base_square = ET.SubElement(group, 'rect', attrib={
            'x': '-0.4',
            'y': '-0.4',
            'width': '0.8',
            'height': '0.8',
            'fill': 'magenta',
        })

        # Orange package overlay (non-rotated) if carrying a package
        if self.has_package:
            package_square = ET.SubElement(group, 'rect', attrib={
                'x': '-0.4',
                'y': '-0.4',
                'width': '0.8',
                'height': '0.8',
                'fill': 'orange',
                'transform': 'rotate(45)'
            })

        # Text (robot id)
        text = ET.SubElement(group, 'text', attrib={
            'x': '0',
            'y': '0',
            'fill': 'white',
            'font-size': '0.5',
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
        })
        text.text = self.id

        # Semi-circle movement arc if moving (not idle)
        if not self.is_idle:
            arc_path = self._create_semi_circle_path()
            arc = ET.SubElement(group, 'path', attrib={
                'd': arc_path,
                'fill': 'none',
                'stroke': 'black',
                'stroke-width': '0.1',
                'transform': f'rotate({self.angle_deg + 90})'
            })
        return group

    def _create_semi_circle_path(self) -> str:
        # Semi-circle radius
        r = 0.4
        # SVG arc path: move to left edge, arc to right edge
        d = f"M {-r},0 A {r},{r} 0 0,1 {r},0"
        return d
