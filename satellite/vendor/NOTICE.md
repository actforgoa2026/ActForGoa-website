The Sentinel-2 request structure and true-colour gain in `eve_cdse.py` are adapted
from EVE ESA mcp-tool-registry `servers/cdse/helper.py`, revision
`a49119dedcb7e929b69b7d78912dd52665c871fc` (Apache-2.0).
Source: https://github.com/eve-esa/mcp-tool-registry/tree/a49119dedcb7e929b69b7d78912dd52665c871fc/servers/cdse

Modified for this hosted service: Sentinel-2 L2A only, exact acquisition windows,
catalog discovery, FLOAT32 spectral data, tile provenance, cached OAuth tokens,
bounded network responses, and no user-selected save path or evalscript.
The upstream eight-tool server is not exposed. REST and MCP share this adapter.

Goa boundary: geoBoundaries IND ADM1, release commit 9469f09, boundary ID
IND-ADM1-1811400; DataMeet India community / Election Commission of India;
CC BY 2.5 India. Historical 2011, simplified geometry, not a cadastral/legal boundary.
Source: https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/
License: https://creativecommons.org/licenses/by/2.5/in/
