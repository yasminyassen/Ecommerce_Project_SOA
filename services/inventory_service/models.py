from database import create_connection

def get_all_items():
    conn = create_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory")
    result = cursor.fetchall()
    conn.close()
    return result


def add_item(name, quantity_available , unit_price):
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (product_name, quantity_available, unit_price) VALUES (%s, %s, %s)",
        (name, quantity_available, unit_price)
    )
    conn.commit()
    conn.close()
    return True


def check_stock(product_id):
    conn = create_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT product_id, product_name, quantity_available, unit_price FROM inventory WHERE product_id = %s",
        (product_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result


def update_inventory(product_id, quantity_sold):
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    cursor.execute("SELECT quantity_available FROM inventory WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    available = row[0]
    if available < quantity_sold:
        conn.close()
        return "insufficient"

    cursor.execute(
        "UPDATE inventory SET quantity_available = quantity_available - %s WHERE product_id = %s",
        (quantity_sold, product_id)
    )
    conn.commit()
    conn.close()
    return True
