# LDView

LDView is a modern Linked Data viewer and URI dereferencer, inspired by [LodView](https://github.com/LodLive/LodView). It provides an intuitive interface for exploring and visualizing RDF data.

## Features

- **Flexible Data Sources**: Connect to either RDF files or SPARQL endpoints
- **Interactive SPARQL Editor**: Built-in YASGUI editor for querying your data
- **Rich Relationship Display**: Shows both direct and inverse relations between resources
- **Dual Operation Modes**:
  - Semantic Web style (`303 see other` redirects from *identification URI* to *documentation URI*)
  - Direct resource display of provided URI
- **Content Negotiation**: Supports various RDF formats based on user agent preferences
- **Smart Visualization**: Automatic display of:
  - Images
  - Geographic maps

## Quick Start with Docker

LDView is designed to run as a Docker container, typically behind a reverse proxy like nginx.

```bash
# Build and start the container
docker compose up --build

# Or run in background
docker compose up -d
```

The application will be available at `http://localhost:8000`. 
The configuration `BASE_URI` is used to determine what URI to be looked up. When set `"https://example.com/"`, an incoming request for `http://localhost:8000/data` will lookup RDF for the URI `https://example.com/data`.

## Configuration

All configuration options are available in `config.py`. Key settings include:

- Data source selection (RDF files or SPARQL endpoint)
- URI redirect behavior
- Content negotiation preferences
- Visualization settings

For detailed configuration options, please refer to the comments in `config.py`.

## Getting Started

### Installation
1. Clone the repository.
2. Install dependencies (e.g., `pip install -r requirements.txt`).
3. Set up your environment as needed.

### Running Tests
- Run tests with `pytest` or your preferred test command.

### Development
- To run the application in development mode, execute the following command:
```bash
python app.py
```
The application is typically deployed behind a reverse proxy (e.g., nginx). A sample nginx configuration is provided in the `nginx/example.conf` file.

## Development Status

This is a prototype implementation, actively being developed and tested.

## Acknowledgments

LDView is inspired by [LodView](https://github.com/LodLive/LodView), a widely-used Linked Data visualization tool.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/renevoorburg/ldview)
- [Issue Tracker](https://github.com/renevoorburg/ldview/issues)
