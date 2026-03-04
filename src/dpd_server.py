"""
Health Canada Drug Product Database (DPD) MCP Server

This MCP server exposes the Health Canada DPD APIs as tools for querying
drug product information approved for use in Canada.

Base API: https://health-products.canada.ca/api/drug/
"""

import httpx
import logging
import os
from fastmcp import FastMCP
from typing import Optional, Literal

# Configure logging level from environment variable (default: INFO)
_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, _log_level, logging.INFO))

# Initialize the MCP server
mcp = FastMCP("Health Canada Drug Product Database")

# Base URL for the DPD API
BASE_URL = "https://health-products.canada.ca/api/drug"

# Common types
Language = Literal["en", "fr"]
ResponseType = Literal["json", "xml"]
DrugStatus = Literal[1, 2, 3, 4, 6, 9, 10, 11, 12, 13, 14, 15]


# =============================================================================
# RESOURCES - Reference data that agents can read for context
# =============================================================================

@mcp.resource("dpd://documentation/overview")
def get_api_overview() -> str:
    """
    Health Canada Drug Product Database (DPD) API Overview.
    
    Provides general information about the DPD and how to use this MCP server.
    """
    return """
# Health Canada Drug Product Database (DPD) - API Overview

The DPD contains product-specific information on drugs approved for use in Canada. 
It is managed by Health Canada and includes:
- Human pharmaceutical and biological drugs
- Veterinary drugs
- Radiopharmaceutical drugs
- Disinfectant products

The database contains approximately 47,000+ products that are currently approved,
marketed, dormant, or cancelled.

## Key Identifiers

- **Drug Code**: Internal numeric identifier for each drug product
- **DIN (Drug Identification Number)**: 8-digit number assigned by Health Canada 
  to a drug product prior to being marketed in Canada (e.g., "00326925")

## Available Tools

1. **Search Tools**: Find drugs by brand name, DIN, or ingredient
2. **Detail Tools**: Get specific information using drug_code
3. **Comprehensive Tool**: get_all_drug_info() fetches everything at once

## Typical Workflow

1. Search by brand name or DIN to get the drug_code
2. Use the drug_code to query detailed information
3. Or use get_all_drug_info() for complete data in one call

## Language Support

All endpoints support English (en) and French (fr) responses.

## API Documentation

Official documentation: https://health-products.canada.ca/api/documentation/dpd-documentation-en.html
"""


@mcp.resource("dpd://reference/status-codes")
def get_status_codes_reference() -> str:
    """
    Reference for drug product status codes in the DPD.
    
    Explains what each status means and when products have that status.
    """
    return """
# Drug Product Status Codes Reference

| Code | Status | Description |
|------|--------|-------------|
| 1 | Approved | Active DIN reviewed and authorized for sale but not yet marketed in Canada |
| 2 | Marketed | Active DIN currently being sold in Canada |
| 3 | Cancelled Pre-Market | DIN cancelled before it was ever marketed in Canada |
| 4 | Cancelled Post-Market | DIN cancelled after being marketed (manufacturer discontinued sale) |
| 6 | Dormant | Active DIN previously marketed but sale suspended for 12+ months |
| 9 | Cancelled (Unreturned Annual) | DIN cancelled due to failure to provide Annual Notification |
| 10 | Cancelled (Safety Issue) | DIN cancelled following safety concerns or failure to provide safety evidence |
| 11 | Authorized By Interim Order | Authorized under an interim order (e.g., COVID-19 vaccines) |
| 12 | Authorization By Interim Order Revoked | Interim order authorization has been revoked |
| 13 | Restricted Access | Limited distribution/access program |
| 14 | Authorization By Interim Order Expired | Interim order authorization has expired |
| 15 | Cancelled (Transitioned to Biocides) | Product transitioned to biocides regulations |

## Common Use Cases

- **Finding available drugs**: Filter by status=2 (Marketed)
- **Historical research**: Include status 4, 6 (Cancelled Post-Market, Dormant)
- **Regulatory analysis**: Check for status 10 (Safety Issues)
"""


@mcp.resource("dpd://reference/schedules")
def get_schedules_reference() -> str:
    """
    Reference for drug schedules in Canada.
    
    Explains the different schedule classifications for drugs.
    """
    return """
# Canadian Drug Schedules Reference

Drug schedules indicate regulatory classification according to the Food and Drug 
Regulations and Controlled Drugs and Substances Act (CDSA).

## Schedule Types

| Schedule | Description |
|----------|-------------|
| **Prescription** | Drugs on the Prescription Drug List - require prescription |
| **Prescription Recommended** | Recommended to be added to Prescription Drug List |
| **OTC** | Over-the-counter drugs, no prescription needed |
| **Ethical** | Non-prescription but typically used under medical supervision |
| **Schedule C** | Radiopharmaceutical drugs (Food and Drugs Act Schedule C) |
| **Schedule D** | Biological products (Food and Drugs Act Schedule D) |
| **Schedule G** | Controlled drugs under various CDSA schedules |
| **Schedule G (CDSA III)** | Controlled substances - Schedule III of CDSA |
| **Schedule G (CDSA IV)** | Controlled substances - Schedule IV of CDSA |
| **Narcotic** | Narcotic drugs (formerly Narcotic Control Act) |
| **Narcotic (CDSA I)** | Narcotic substances - Schedule I of CDSA |
| **Narcotic (CDSA II)** | Narcotic substances - Schedule II of CDSA |
| **Targeted (CDSA IV)** | Targeted substances under CDSA Schedule IV |

## Important Notes

- A drug can have MULTIPLE schedules (e.g., "Prescription" AND "Schedule D")
- Schedule D includes vaccines, blood products, and other biologics
- Ethical products include MRI contrast agents and emergency medications
"""


@mcp.resource("dpd://reference/routes")
def get_routes_reference() -> str:
    """
    Common routes of administration for drug products.
    """
    return """
# Routes of Administration Reference

Routes indicate how the product is introduced to the body.

## Common Routes

| Route | Description |
|-------|-------------|
| Oral | Taken by mouth (tablets, capsules, liquids) |
| Topical | Applied to the skin surface |
| Intravenous (IV) | Injected directly into a vein |
| Intramuscular (IM) | Injected into a muscle |
| Subcutaneous (SC) | Injected under the skin |
| Inhalation | Breathed into the lungs |
| Rectal | Administered via the rectum |
| Ophthalmic | Applied to the eye |
| Otic | Applied to the ear |
| Nasal | Applied to nasal passages |
| Transdermal | Absorbed through the skin (patches) |
| Sublingual | Dissolved under the tongue |
| Intrathecal | Injected into spinal canal |
| Intra-articular | Injected into a joint |

## Notes

- A single product can have multiple routes of administration
- Route affects dosing, onset time, and bioavailability
"""


# =============================================================================
# PROMPTS - Guided workflows for common tasks
# =============================================================================

@mcp.prompt()
def drug_lookup(drug_name: str) -> str:
    """
    Guided workflow to look up comprehensive information about a drug.
    
    Args:
        drug_name: The brand name or common name of the drug to look up
    """
    return f"""Please help me find comprehensive information about the drug "{drug_name}".

Follow these steps:
1. First, search for the drug by brand name using search_drug_by_brand_name("{drug_name}")
2. If no results, try searching active ingredients with search_active_ingredients("{drug_name}")
3. Once you find the drug_code, use get_all_drug_info(drug_code) to retrieve all details
4. Present the information in a clear format including:
   - Brand name and DIN
   - Active ingredients and strengths
   - Dosage form and route of administration
   - Drug schedule (prescription/OTC/controlled)
   - Current market status
   - Therapeutic class
   - Manufacturer information

Focus on marketed (status=2) products unless I ask for historical/discontinued drugs."""


@mcp.prompt()
def compare_drugs(drug1: str, drug2: str) -> str:
    """
    Guided workflow to compare two drug products.
    
    Args:
        drug1: First drug brand name to compare
        drug2: Second drug brand name to compare
    """
    return f"""Please compare these two drugs: "{drug1}" and "{drug2}"

Steps:
1. Look up both drugs using search_drug_by_brand_name()
2. Get full details for each using get_all_drug_info()
3. Create a comparison covering:
   - Active ingredients (same or different?)
   - Strengths available
   - Dosage forms
   - Routes of administration
   - Schedules (prescription requirements)
   - Manufacturers
   - Market status

Highlight key differences and similarities. If these are generic equivalents, note that."""


@mcp.prompt()
def find_alternatives(drug_name: str) -> str:
    """
    Find alternative products with the same active ingredient.
    
    Args:
        drug_name: The drug brand name to find alternatives for
    """
    return f"""Help me find alternative drug products to "{drug_name}".

Steps:
1. First, look up "{drug_name}" to identify its active ingredient(s)
2. Search for other products containing the same active ingredient(s) using search_active_ingredients()
3. Filter to only marketed (status=2) products
4. For each alternative, provide:
   - Brand name and DIN
   - Manufacturer
   - Available strengths
   - Dosage forms
   
This helps identify generic alternatives or different formulations of the same medication."""


@mcp.prompt()
def check_din(din: str) -> str:
    """
    Verify a Drug Identification Number (DIN) and get product details.
    
    Args:
        din: The 8-digit DIN to verify (e.g., "00326925")
    """
    return f"""Please verify the Drug Identification Number (DIN): {din}

Steps:
1. Search for the DIN using search_drug_by_din("{din}")
2. If found, get complete details with get_all_drug_info()
3. Report:
   - Whether the DIN is valid
   - Current status (Marketed, Cancelled, Dormant, etc.)
   - Product details if found
   - If cancelled, note the reason and date
   
DIns are 8-digit numbers assigned by Health Canada. A valid format is required."""


async def make_request(endpoint: str, params: dict) -> dict | list | str:
    """Make an async HTTP request to the DPD API."""
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    
    # verify=False handles corporate proxy SSL issues
    # Longer timeout for slow API responses
    timeout = httpx.Timeout(120.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
        response = await client.get(f"{BASE_URL}/{endpoint}/", params=params)
        response.raise_for_status()
        
        if params.get("type") == "xml":
            return response.text
        return response.json()


@mcp.tool()
async def get_active_ingredients(
    drug_code: int,
    ingredient_name: Optional[str] = None,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get active ingredient(s) for a drug product.
    
    Active ingredients are components that have medicinal properties and supply
    pharmacological activity. Returns ingredient name, strength, and dosage information.
    
    Args:
        drug_code: The drug product code (required)
        ingredient_name: Filter by ingredient name (e.g., "zinc", "vitamin")
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of active ingredients with dosage_unit, dosage_value, drug_code,
        ingredient_name, strength, and strength_unit
    """
    params = {
        "id": drug_code,
        "ingredientname": ingredient_name,
        "lang": lang,
        "type": type
    }
    return await make_request("activeingredient", params)


@mcp.tool()
async def search_active_ingredients(
    ingredient_name: str,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Search for active ingredients by name across all drug products.
    
    Args:
        ingredient_name: The ingredient name to search for (e.g., "acetaminophen", "ibuprofen")
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of matching active ingredients with their drug codes
    """
    params = {
        "ingredientname": ingredient_name,
        "lang": lang,
        "type": type
    }
    return await make_request("activeingredient", params)


@mcp.tool()
async def get_company(
    company_code: int,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get company information by company code.
    
    Companies include DIN owners and manufacturers of drug products.
    
    Args:
        company_code: The company code (required)
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        Company details including company_name, company_type, street_name,
        city_name, province_name, country_name, postal_code
    """
    params = {
        "id": company_code,
        "lang": lang,
        "type": type
    }
    return await make_request("company", params)


@mcp.tool()
async def get_drug_product(
    drug_code: int,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get drug product information by drug code.
    
    Args:
        drug_code: The drug product code (required)
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        Drug product details including brand_name, drug_identification_number (DIN),
        class_name, company_name, number_of_ais, last_update_date
    """
    params = {
        "id": drug_code,
        "lang": lang,
        "type": type
    }
    return await make_request("drugproduct", params)


@mcp.tool()
async def search_drug_by_din(
    din: str,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Search for a drug product by Drug Identification Number (DIN).
    
    The DIN is an 8-digit number assigned by Health Canada to a drug product
    prior to being marketed in Canada.
    
    Args:
        din: The Drug Identification Number (e.g., "00326925")
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        Drug product details matching the DIN
    """
    params = {
        "din": din,
        "lang": lang,
        "type": type
    }
    return await make_request("drugproduct", params)


@mcp.tool()
async def search_drug_by_brand_name(
    brand_name: str,
    status: Optional[int] = None,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Search for drug products by brand name.
    
    Args:
        brand_name: The brand name to search for (e.g., "Tylenol", "Advil")
        status: Filter by product status:
            1=Approved, 2=Marketed, 3=Cancelled Pre Market, 4=Cancelled Post Market,
            6=Dormant, 9=Cancelled (Unreturned Annual), 10=Cancelled (Safety Issue),
            11=Authorized By Interim Order, 12=Authorization By Interim Order Revoked,
            13=Restricted Access, 14=Authorization By Interim Order Expired,
            15=Cancelled (Transitioned to Biocides)
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of drug products matching the brand name
    """
    params = {
        "brandname": brand_name,
        "status": status,
        "lang": lang,
        "type": type
    }
    return await make_request("drugproduct", params)


@mcp.tool()
async def get_dosage_form(
    drug_code: int,
    active_only: bool = False,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get dosage form(s) for a drug product.
    
    Dosage form is the form of presentation (e.g., tablet, capsule, liquid, powder).
    A product can have multiple dosage forms when it's a kit.
    
    Args:
        drug_code: The drug product code (required)
        active_only: If True, returns only active dosage forms
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of dosage forms with pharmaceutical_form_code and pharmaceutical_form_name
    """
    params = {
        "id": drug_code,
        "active": "yes" if active_only else None,
        "lang": lang,
        "type": type
    }
    return await make_request("form", params)


@mcp.tool()
async def get_packaging(
    drug_code: int,
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get packaging information for a drug product.
    
    Args:
        drug_code: The drug product code (required)
        type: Response format - "json" or "xml"
    
    Returns:
        Packaging details including package_size, package_size_unit,
        package_type, product_information, and upc (Universal Product Code)
    """
    params = {
        "id": drug_code,
        "type": type
    }
    return await make_request("packaging", params)


@mcp.tool()
async def get_pharmaceutical_standard(
    drug_code: int,
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get pharmaceutical standard for a drug product.
    
    The pharmaceutical standard is the standard to which a drug product
    is manufactured and represented.
    
    Args:
        drug_code: The drug product code (required)
        type: Response format - "json" or "xml"
    
    Returns:
        Pharmaceutical standard information (e.g., "MFR" for manufacturer standard)
    """
    params = {
        "id": drug_code,
        "type": type
    }
    return await make_request("pharmaceuticalstd", params)


@mcp.tool()
async def get_route_of_administration(
    drug_code: int,
    active_only: bool = False,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get route(s) of administration for a drug product.
    
    Indicates how the product is introduced to the body (e.g., oral, topical,
    intramuscular, intravenous, rectal). A product can have multiple routes.
    
    Args:
        drug_code: The drug product code (required)
        active_only: If True, returns only active routes
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of routes with route_of_administration_code and route_of_administration_name
    """
    params = {
        "id": drug_code,
        "active": "yes" if active_only else None,
        "lang": lang,
        "type": type
    }
    return await make_request("route", params)


@mcp.tool()
async def get_schedule(
    drug_code: int,
    active_only: bool = False,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get drug schedule(s) for a drug product.
    
    Schedules indicate the regulatory classification according to the Food and Drug
    Regulations and Controlled Drugs and Substances Act. Examples include:
    - Prescription
    - OTC (over the counter)
    - Schedule G (controlled drugs)
    - Narcotic
    - Schedule D (biological products)
    
    Args:
        drug_code: The drug product code (required)
        active_only: If True, returns only active schedules
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of schedules with schedule_name
    """
    params = {
        "id": drug_code,
        "active": "yes" if active_only else None,
        "lang": lang,
        "type": type
    }
    return await make_request("schedule", params)


@mcp.tool()
async def get_product_status(
    drug_code: int,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get the status of a drug product.
    
    Status types include:
    - Approved: Active DIN authorized for sale but not yet marketed
    - Marketed: Active DIN currently being sold in Canada
    - Dormant: Active DIN previously marketed but sale suspended 12+ months
    - Cancelled Post-Market: DIN cancelled after being marketed
    - Cancelled Pre-Market: DIN cancelled before being marketed
    - Cancelled (Safety Issue): DIN cancelled due to safety concerns
    
    Args:
        drug_code: The drug product code (required)
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        Status information including status, history_date, original_market_date,
        expiration_date, and lot_number
    """
    params = {
        "id": drug_code,
        "lang": lang,
        "type": type
    }
    return await make_request("status", params)


@mcp.tool()
async def get_therapeutic_class(
    drug_code: int,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get the therapeutic class(es) for a drug product.
    
    Therapeutic classification is assigned according to the drug's main therapeutic use,
    using the Anatomical Therapeutic Chemical (ATC) classification system.
    
    Args:
        drug_code: The drug product code (required)
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        Therapeutic class information including tc_atc_number (ATC code) and tc_atc (description)
    """
    params = {
        "id": drug_code,
        "lang": lang,
        "type": type
    }
    return await make_request("therapeuticclass", params)


@mcp.tool()
async def get_veterinary_species(
    drug_code: int,
    lang: Language = "en",
    type: ResponseType = "json"
) -> dict | list | str:
    """
    Get the veterinary species for a veterinary drug product.
    
    Only applicable to veterinary drugs. Returns the animal species the drug
    is approved for (e.g., dogs, cats, horses, cattle, poultry).
    
    Args:
        drug_code: The drug product code (required)
        lang: Response language - "en" for English, "fr" for French
        type: Response format - "json" or "xml"
    
    Returns:
        List of veterinary species with vet_species_name
    """
    params = {
        "id": drug_code,
        "lang": lang,
        "type": type
    }
    return await make_request("veterinaryspecies", params)


@mcp.tool()
async def get_all_drug_info(
    drug_code: int,
    lang: Language = "en"
) -> dict:
    """
    Get comprehensive information about a drug product in a single call.
    
    Fetches all available data for a drug product including: basic product info,
    active ingredients, company, dosage form, packaging, pharmaceutical standard,
    route of administration, schedule, status, and therapeutic class.
    
    Args:
        drug_code: The drug product code (required)
        lang: Response language - "en" for English, "fr" for French
    
    Returns:
        Dictionary containing all available information about the drug product
    """
    import asyncio
    
    # Fetch all data concurrently
    results = await asyncio.gather(
        make_request("drugproduct", {"id": drug_code, "lang": lang, "type": "json"}),
        make_request("activeingredient", {"id": drug_code, "lang": lang, "type": "json"}),
        make_request("form", {"id": drug_code, "lang": lang, "type": "json"}),
        make_request("packaging", {"id": drug_code, "type": "json"}),
        make_request("pharmaceuticalstd", {"id": drug_code, "type": "json"}),
        make_request("route", {"id": drug_code, "lang": lang, "type": "json"}),
        make_request("schedule", {"id": drug_code, "lang": lang, "type": "json"}),
        make_request("status", {"id": drug_code, "lang": lang, "type": "json"}),
        make_request("therapeuticclass", {"id": drug_code, "lang": lang, "type": "json"}),
        return_exceptions=True
    )
    
    keys = [
        "drug_product", "active_ingredients", "dosage_forms", "packaging",
        "pharmaceutical_standard", "routes_of_administration", "schedules",
        "status", "therapeutic_class"
    ]
    
    return {
        key: result if not isinstance(result, Exception) else {"error": str(result)}
        for key, result in zip(keys, results)
    }


if __name__ == "__main__":
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
