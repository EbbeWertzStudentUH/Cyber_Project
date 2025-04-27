from svg.SvgExporter import ModelExporter
from svg.SvgToModelBuilder import SvgToModelBuilder

if __name__ == '__main__':
    svg_file = "../warehouse_model.svg"  # Input SVG file
    output_file = "./output.svg"  # Output SVG file

    builder = SvgToModelBuilder(svg_file)
    model = builder.build()
    print(model)
    exporter = ModelExporter(model, output_file, builder.extractor.get_metadata())
    exporter.create_new_svg()

