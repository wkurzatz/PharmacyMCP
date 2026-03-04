# Health Canada Drug Product Database MCP Server

An MCP (Model Context Protocol) server that exposes the Health Canada Drug Product Database (DPD) APIs as tools. Query information on ~47,000 drugs approved for use in Canada including human pharmaceuticals, biologics, veterinary drugs, radiopharmaceuticals, and disinfectants.

## Features

- **15 tools** exposing all DPD API endpoints
- **4 resources** providing reference documentation
- **4 prompts** for guided workflows
- Async HTTP requests with httpx
- Support for English and French responses
- JSON and XML response formats
- Comprehensive drug product queries

## Available Tools

| Tool | Description |
|------|-------------|
| `get_active_ingredients` | Get active ingredients for a drug by drug code |
| `search_active_ingredients` | Search ingredients by name across all products |
| `get_company` | Get company/manufacturer information |
| `get_drug_product` | Get drug product by drug code |
| `search_drug_by_din` | Search by Drug Identification Number (DIN) |
| `search_drug_by_brand_name` | Search by brand name (e.g., "Tylenol") |
| `get_dosage_form` | Get dosage forms (tablet, capsule, etc.) |
| `get_packaging` | Get package sizes and UPC codes |
| `get_pharmaceutical_standard` | Get manufacturing standard |
| `get_route_of_administration` | Get administration routes (oral, IV, etc.) |
| `get_schedule` | Get drug schedules (prescription, OTC, etc.) |
| `get_product_status` | Get product status (marketed, cancelled, etc.) |
| `get_therapeutic_class` | Get ATC therapeutic classification |
| `get_veterinary_species` | Get approved species for veterinary drugs |
| `get_all_drug_info` | Get comprehensive info in one call |

## Available Resources

Resources provide reference data that agents can read for context:

| Resource URI | Description |
|-------------|-------------|
| `dpd://documentation/overview` | API overview, key identifiers, and typical workflows |
| `dpd://reference/status-codes` | Drug status code meanings (Approved, Marketed, Cancelled, etc.) |
| `dpd://reference/schedules` | Drug schedule classifications (Prescription, OTC, Narcotic, etc.) |
| `dpd://reference/routes` | Routes of administration reference (Oral, IV, Topical, etc.) |

## Available Prompts

Prompts provide guided workflows for common tasks:

| Prompt | Arguments | Description |
|--------|-----------|-------------|
| `drug_lookup` | `drug_name` | Comprehensive lookup of a drug by name |
| `compare_drugs` | `drug1`, `drug2` | Side-by-side comparison of two drugs |
| `find_alternatives` | `drug_name` | Find generic alternatives with same active ingredient |
| `check_din` | `din` | Verify a DIN and get product status/details |

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PharmacyMCP.git
   cd PharmacyMCP
   ```

2. **Create a virtual environment**

   Using venv (built-in):
   ```bash
   python -m venv .venv
   ```

   Or using uv (faster):
   ```bash
   uv venv .venv
   ```

3. **Activate the virtual environment**

   Windows (PowerShell):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Windows (Command Prompt):
   ```cmd
   .venv\Scripts\activate.bat
   ```

   macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**

   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

   Or using uv:
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Verify installation**
   ```bash
   python src/dpd_server.py
   ```
   The server will start and listen at `http://localhost:8000/mcp`. Press `Ctrl+C` to stop.

## Usage

### Running the server

```bash
python src/dpd_server.py
```

The server starts on **`http://localhost:8000/mcp`** using the MCP Streamable HTTP transport.

### Running with FastMCP CLI

```bash
fastmcp run src/dpd_server.py
```

### Connecting from Claude Desktop

Start the server first (`python src/dpd_server.py`), then add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "pharmacy-dpd": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Installing in VS Code with GitHub Copilot

Start the server first, then add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "pharmacy-dpd": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Connecting from Postman

Create a new MCP request in Postman and set the URL to:

```
http://localhost:8000/mcp
```

## Example Queries

Once connected, you can ask questions like:

- "Search for drugs with the brand name Tylenol"
- "What are the active ingredients in drug code 48905?"
- "Find drugs containing acetaminophen"
- "What is the status of DIN 00326925?"
- "Get all information about drug code 2049"
- "Compare Tylenol and Advil"
- "Find generic alternatives to Lipitor"

## How Agents Use Resources and Prompts

### Resources
Agents automatically have access to reference data without making API calls. For example, when interpreting a status code like "4", the agent can read `dpd://reference/status-codes` to understand it means "Cancelled Post-Market".

### Prompts
Prompts guide multi-step workflows. When you ask to look up a drug, the `drug_lookup` prompt provides a structured approach:
1. Search by brand name
2. Get the drug_code from results
3. Fetch comprehensive details
4. Present information in a clear format

## API Reference

This server wraps the Health Canada DPD API:
- **Base URL**: `https://health-products.canada.ca/api/drug/`
- **Documentation**: [DPD API Guide](https://health-products.canada.ca/api/documentation/dpd-documentation-en.html)

### Drug Status Codes

| Code | Status |
|------|--------|
| 1 | Approved |
| 2 | Marketed |
| 3 | Cancelled Pre Market |
| 4 | Cancelled Post Market |
| 6 | Dormant |
| 9 | Cancelled (Unreturned Annual) |
| 10 | Cancelled (Safety Issue) |
| 11 | Authorized By Interim Order |
| 12 | Authorization By Interim Order Revoked |
| 13 | Restricted Access |
| 14 | Authorization By Interim Order Expired |
| 15 | Cancelled (Transitioned to Biocides) |

## License

MIT
