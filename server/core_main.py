from svg.SvgExporter import ModelExporter
from svg.SvgToModelBuilder import SvgToModelBuilder

if __name__ == '__main__':
    svg_file = "../warehouse_model.svg"  # Input SVG file
    output_file = "./output.svg"  # Output SVG file

    svg_content = ''
    with open(svg_file, "r") as f:
        svg_content += f.read()

    builder = SvgToModelBuilder(svg_content)
    model = builder.build()
    print(model)
    exporter = ModelExporter(model, builder.extractor.get_metadata())
    out_svg = exporter.to_svg()

    with open(output_file, "w") as f:
        f.write(out_svg)

