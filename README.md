# LDView

LDView is a modern Linked Data viewer and URI dereferencer, inspired by [LodView](https://github.com/LodLive/LodView). It provides an intuitive interface for exploring and visualizing RDF data.

## Features

- **Flexible Data Sources**: Connect to either RDF files or SPARQL endpoints
- **Interactive SPARQL Editor**: Built-in YASGUI editor for querying your data
- **Rich Relationship Display**: Shows both direct and inverse relations between resources
- **Dual Operation Modes**:
  - Semantic Web style redirects
  - Direct resource display
- **Content Negotiation**: Supports various RDF formats based on client preferences
- **Smart Visualization**: Automatic display of:
  - Images
  - Geographic maps
  - Other media types based on the data

## Quick Start with Docker

LDView is designed to run as a Docker container, typically behind a reverse proxy like nginx.

```bash
# Build and start the container
docker compose up --build

# Or run in background
docker compose up -d
```

The application will be available at `http://localhost:8000`.

## Configuration

All configuration options are available in `config.py`. Key settings include:

- Data source selection (RDF files or SPARQL endpoint)
- URI redirect behavior
- Content negotiation preferences
- Visualization settings

For detailed configuration options, please refer to the comments in `config.py`.

## Development Status

This is a prototype implementation, actively being developed and tested.

## Acknowledgments

LDView is inspired by [LodView](https://github.com/LodLive/LodView), a widely-used Linked Data visualization tool.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/renevoorburg/ldview)
- [Issue Tracker](https://github.com/renevoorburg/ldview/issues)
