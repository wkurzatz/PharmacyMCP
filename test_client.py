"""
Test client for the Health Canada DPD MCP Server.

This script tests the MCP server tools by making direct HTTP requests
to the Health Canada DPD API (same endpoints the MCP server uses).
"""

import asyncio
import httpx
import warnings

# Suppress SSL warnings for corporate proxy environments
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

BASE_URL = "https://health-products.canada.ca/api/drug"

# Longer timeout for slow API responses
TIMEOUT = httpx.Timeout(120.0, connect=30.0)


async def make_request(endpoint: str, params: dict) -> dict | list | None:
    """Make a request with error handling."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
            response = await client.get(f"{BASE_URL}/{endpoint}/", params=params)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        print(f"  ERROR: Request timed out")
        return None
    except httpx.HTTPStatusError as e:
        print(f"  ERROR: HTTP {e.response.status_code}")
        return None
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        return None


async def test_search_by_brand_name(brand_name: str):
    """Test searching for drugs by brand name."""
    print(f"\n{'='*60}")
    print(f"Searching for brand name: {brand_name}")
    print('='*60)
    
    data = await make_request("drugproduct", {
        "brandname": brand_name, 
        "lang": "en", 
        "type": "json"
    })
    
    if data is None:
        return None
    
    if isinstance(data, list):
        print(f"Found {len(data)} results:")
        for item in data[:5]:
            print(f"  - {item.get('brand_name')} (DIN: {item.get('drug_identification_number')}, Code: {item.get('drug_code')})")
        if len(data) > 5:
            print(f"  ... and {len(data) - 5} more")
    else:
        print(f"Result: {data}")
    
    return data


async def test_search_by_din(din: str):
    """Test searching for a drug by DIN."""
    print(f"\n{'='*60}")
    print(f"Searching for DIN: {din}")
    print('='*60)
    
    data = await make_request("drugproduct", {
        "din": din, 
        "lang": "en", 
        "type": "json"
    })
    
    if data:
        print(f"Result: {data}")
    return data


async def test_get_drug_product(drug_code: int):
    """Test getting a drug product by code."""
    print(f"\n{'='*60}")
    print(f"Getting drug product for code: {drug_code}")
    print('='*60)
    
    data = await make_request("drugproduct", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data:
        if isinstance(data, dict):
            print(f"  Brand: {data.get('brand_name')}")
            print(f"  DIN: {data.get('drug_identification_number')}")
            print(f"  Class: {data.get('class_name')}")
            print(f"  Company: {data.get('company_name')}")
    return data


async def test_get_active_ingredients(drug_code: int):
    """Test getting active ingredients for a drug."""
    print(f"\n{'='*60}")
    print(f"Getting active ingredients for drug code: {drug_code}")
    print('='*60)
    
    data = await make_request("activeingredient", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data and isinstance(data, list):
        print(f"Found {len(data)} ingredients:")
        for item in data:
            print(f"  - {item.get('ingredient_name')}: {item.get('strength')} {item.get('strength_unit')}")
    
    return data


async def test_get_dosage_form(drug_code: int):
    """Test getting dosage form for a drug."""
    print(f"\n{'='*60}")
    print(f"Getting dosage form for drug code: {drug_code}")
    print('='*60)
    
    data = await make_request("form", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data and isinstance(data, list):
        for item in data:
            print(f"  - {item.get('pharmaceutical_form_name')}")
    
    return data


async def test_get_route(drug_code: int):
    """Test getting route of administration for a drug."""
    print(f"\n{'='*60}")
    print(f"Getting route of administration for drug code: {drug_code}")
    print('='*60)
    
    data = await make_request("route", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data and isinstance(data, list):
        for item in data:
            print(f"  - {item.get('route_of_administration_name')}")
    
    return data


async def test_get_schedule(drug_code: int):
    """Test getting schedule for a drug."""
    print(f"\n{'='*60}")
    print(f"Getting schedule for drug code: {drug_code}")
    print('='*60)
    
    data = await make_request("schedule", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data and isinstance(data, list):
        for item in data:
            print(f"  - {item.get('schedule_name')}")
    
    return data


async def test_get_status(drug_code: int):
    """Test getting status for a drug."""
    print(f"\n{'='*60}")
    print(f"Getting status for drug code: {drug_code}")
    print('='*60)
    
    data = await make_request("status", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data and isinstance(data, list):
        for item in data:
            print(f"  - Status: {item.get('status')}, Date: {item.get('history_date')}")
    
    return data


async def test_get_therapeutic_class(drug_code: int):
    """Test getting therapeutic class for a drug."""
    print(f"\n{'='*60}")
    print(f"Getting therapeutic class for drug code: {drug_code}")
    print('='*60)
    
    data = await make_request("therapeuticclass", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if data:
        if isinstance(data, dict):
            print(f"  - ATC: {data.get('tc_atc_number')} - {data.get('tc_atc')}")
        elif isinstance(data, list):
            for item in data:
                print(f"  - ATC: {item.get('tc_atc_number')} - {item.get('tc_atc')}")
    
    return data


async def test_search_ingredients(ingredient_name: str):
    """Test searching for active ingredients by name."""
    print(f"\n{'='*60}")
    print(f"Searching for ingredient: {ingredient_name}")
    print('='*60)
    
    data = await make_request("activeingredient", {
        "ingredientname": ingredient_name, 
        "lang": "en", 
        "type": "json"
    })
    
    if data and isinstance(data, list):
        print(f"Found {len(data)} results:")
        drug_codes = set(item.get('drug_code') for item in data)
        print(f"Across {len(drug_codes)} different drug products")
        for item in data[:5]:
            print(f"  - Drug {item.get('drug_code')}: {item.get('ingredient_name')} {item.get('strength')} {item.get('strength_unit')}")
        if len(data) > 5:
            print(f"  ... and {len(data) - 5} more")
    
    return data


async def test_din_with_ingredients(din: str):
    """Test searching for a drug by DIN and displaying its ingredients."""
    print(f"\n{'='*60}")
    print(f"Searching for DIN: {din} and displaying ingredients")
    print('='*60)
    
    # First, get the drug product by DIN
    data = await make_request("drugproduct", {
        "din": din, 
        "lang": "en", 
        "type": "json"
    })
    
    if not data:
        print(f"  No drug product found for DIN: {din}")
        return None
    
    # Handle both single result (dict) and multiple results (list)
    drug_info = data[0] if isinstance(data, list) else data
    drug_code = drug_info.get('drug_code')
    brand_name = drug_info.get('brand_name')
    
    print(f"  Found: {brand_name} (Drug Code: {drug_code})")
    
    # Now get the active ingredients
    ingredients = await make_request("activeingredient", {
        "id": drug_code, 
        "lang": "en", 
        "type": "json"
    })
    
    if ingredients and isinstance(ingredients, list):
        print(f"\n  Active Ingredients ({len(ingredients)}):")
        for item in ingredients:
            name = item.get('ingredient_name')
            strength = item.get('strength')
            strength_unit = item.get('strength_unit')
            dosage_value = item.get('dosage_value')
            dosage_unit = item.get('dosage_unit')
            print(f"    - {name}: {strength} {strength_unit} (per {dosage_value} {dosage_unit})")
    else:
        print("  No ingredients found")
    
    return {"drug_info": drug_info, "ingredients": ingredients}


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  HEALTH CANADA DPD API TEST CLIENT")
    print("="*60)
    
    # Test 1: Search by brand name
    results = await test_search_by_brand_name("tylenol")
    
    # If brand search worked, get a drug code for more tests
    drug_code = None
    if isinstance(results, list) and len(results) > 0:
        drug_code = results[0].get('drug_code')
        din = results[0].get('drug_identification_number')
        
        # Test 2: Search by DIN
        await test_search_by_din(din)
        
        # Test 3-8: Get various details for the drug
        await test_get_drug_product(drug_code)
        await test_get_active_ingredients(drug_code)
        await test_get_dosage_form(drug_code)
        await test_get_route(drug_code)
        await test_get_schedule(drug_code)
        await test_get_status(drug_code)
        await test_get_therapeutic_class(drug_code)
    else:
        # Use a known drug code for testing if brand search failed
        print("\nBrand search failed, using known drug code 2049 (SINEQUAN)")
        drug_code = 2049
        await test_get_drug_product(drug_code)
        await test_get_active_ingredients(drug_code)
        await test_get_dosage_form(drug_code)
        await test_get_route(drug_code)
        await test_get_schedule(drug_code)
        await test_get_status(drug_code)
        await test_get_therapeutic_class(drug_code)
    
    # Test 9: Search by ingredient name
    await test_search_ingredients("acetaminophen")
    
    # Test 10: Search by specific DIN and display ingredients
    await test_din_with_ingredients("00396516")
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
