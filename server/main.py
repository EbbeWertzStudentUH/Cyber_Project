from svg.SvgExporter import ModelExporter
from svg.SvgToGraphModelBuilder import SvgToGraphModelBuilder

if __name__ == '__main__':
    svg_file = "../warehouse_model.svg"  # Input SVG file
    output_file = "./output.svg"  # Output SVG file

    builder = SvgToGraphModelBuilder(svg_file)
    graph = builder.build_graph()
    print(graph)
    exporter = ModelExporter(graph, output_file, builder.extractor.get_metadata())
    exporter.create_new_svg()

