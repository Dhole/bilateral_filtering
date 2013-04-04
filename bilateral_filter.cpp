#include <string>
#include <graphlab.hpp>

/*
 * Graphlab implementation of bilateral filtering on images 
 */
using namespace graphlab;

int iter = 10;

// Structure defining the node data
struct pixel
{
	double val_0; // Original value before iteration
	double val_1; // New value after calculation during iteration
	double self_wei; // Connection weight to itself
	int counter;
	
	pixel():val_0(0.0), self_wei(0.0) { }
	explicit pixel(double value_0, double weight):val_0(value_0), val_1(0.0),
		       self_wei(weight), counter(0){ }

	void save(graphlab::oarchive& oarc) const {
		oarc << val_0 << val_1 << self_wei << counter;
	}
	void load(graphlab::iarchive& iarc) {
		iarc >> val_0 >> val_1 >> self_wei >> counter;
	}
};

// Structure defining the edge data
struct edge
{
	double wei; // Weight between nodes
	edge():wei(0.0) { }
	explicit edge(double weight):wei(weight){ }

	void save(graphlab::oarchive& oarc) const {
		oarc << wei;
	}
	void load(graphlab::iarchive& iarc) {
		iarc >> wei;
	}
};

typedef graphlab::distributed_graph<pixel, edge> graph_type;

bool line_parser(graph_type& graph, const std::string& filename,
		 const std::string& textline)
{
	// Skip line if it's a comment
	if (textline[0] == '#')
		return true;
	std::stringstream strm(textline);
	graphlab::vertex_id_type vid;
	double val;
	strm >> vid;
	strm >> val;
	while(1) {
		graphlab::vertex_id_type other_vid;
		double weight;
		strm >> other_vid;
		strm >> weight;
		if (strm.fail())
			break;
		if (other_vid == vid)
			graph.add_vertex(vid, pixel(val, weight));
		else
			graph.add_edge(vid, other_vid, edge(weight));
	}
	return true;
}

class filter_program :
			public graphlab::ivertex_program<graph_type, double>,
			public graphlab::IS_POD_TYPE
{
public:
	// we are going to gather on all the out-edges
	edge_dir_type gather_edges(icontext_type& context,
				   const vertex_type& vertex) const {
		return graphlab::OUT_EDGES;
	}

	// for each out-edge gather the weighted sum of the edge.
	double gather(icontext_type& context, const vertex_type& vertex,
		      edge_type& edge) const {
		return edge.data().wei * edge.target().data().val_0;
		//return edge.target().data().val_0;
		//return edge.source().data().pagerank / edge.source().num_out_edges();
	}

	// Do the sumation of weights * values and update the vertex values
	void apply(icontext_type& context, vertex_type& vertex,
		   const gather_type& total) {
		double new_val = total + vertex.data().self_wei * vertex.data().val_0;
		vertex.data().val_1 = new_val;
		vertex.data().val_0 = vertex.data().val_1;
		vertex.data().counter++;
		if (vertex.data().counter < iter)
			context.signal(vertex);
		//vertex.data().val_1 = (total + vertex.data().val_0) / (vertex.num_out_edges() + 1);
	}

	// No scatter needed. Return NO_EDGES
	edge_dir_type scatter_edges(icontext_type& context,
				    const vertex_type& vertex) const {
		return graphlab::NO_EDGES;
	}
};

class graph_writer {
public:
	std::string save_vertex(graph_type::vertex_type v) {
		std::stringstream strm;
		// remember the \n at the end! This will provide a line break
		// after each page.
		// Save the vertex id and the vertex updated value
		strm << v.id() << "\t" << v.data().val_1 << "\n";
		return strm.str();
	}
	std::string save_edge(graph_type::edge_type e) { return ""; }
};


int main(int argc, char** argv)
{
	graphlab::mpi_tools::init(argc, argv);
	graphlab::distributed_control dc;

	// Parse command line options
	graphlab::command_line_options clopts("Bilateral filter.");
	std::string graph_dir;
	clopts.attach_option("graph", graph_dir, "The graph file. Required ");
	clopts.add_positional("graph");
	clopts.attach_option("iterations", iter, "The number of iterations.");
	clopts.add_positional("iterations");
	if (!clopts.parse(argc, argv)) {
		dc.cout() << "Error in parsing command line arguments." << std::endl;
		return EXIT_FAILURE;
	}
	if (graph_dir == "") {
		dc.cout() << "Graph not specified. Cannot continue";
		return EXIT_FAILURE;
	}

	//... main body ...
	dc.cout() << "Bilateral Filter Program!\n";
	graph_type graph(dc);
	graph.load(graph_dir, line_parser);
	graph.finalize();
	
	graphlab::omni_engine<filter_program> engine(dc, graph, "sync");
	engine.signal_all();
	engine.start();

	const float runtime = engine.elapsed_seconds();
	dc.cout() << "Finished Running engine in " << runtime << " seconds." << std::endl;

	graph.save("output",
		   graph_writer(),
		   false, // set to true if each output file is to be gzipped
		   true, // whether vertices are saved
		   false); // whether edges are saved

	graphlab::mpi_tools::finalize();

	return 0;
}