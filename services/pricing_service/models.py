from database import create_connection

def get_pricing_rules_for_product(product_id):
    conn = create_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pricing_rules WHERE product_id = %s", (product_id,))
    rules = cursor.fetchall()
    conn.close()
    return rules or []

def get_tax_rate(region):
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tax_rate FROM tax_rates WHERE region = %s", (region,))
    r = cursor.fetchone()
    conn.close()
    if r and r.get("tax_rate") is not None:
        return float(r["tax_rate"])
    # fallback: try 'Default' region
    return None
