import mysql.connector
import os
from decimal import Decimal

def get_db_connection():
    """
    Creates a connection to Google Cloud SQL MySQL instance using standard MySQL connector.
    Make sure your instance is configured to accept external connections or you're running
    this from a Google Cloud resource with proper permissions.
    """
    try:
        connection = mysql.connector.connect(
            host="34.131.39.31", 
            database='pandeyji_eatery',
            user='root',
            passwd='F<Dr*X|};=|`a(3^',
        )
        
        if connection.is_connected():
            print("Successfully connected to the database!")
            return connection
            
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        raise
try:
    cnx = get_db_connection()
except Exception as e:
    print(f"Connection test failed: {e}")

def insert_order_item(food_item, quantity, order_id):
    """
    Inserts an order item into the database using a stored procedure.
    
    Args:
        food_item (str): The name or ID of the food item
        quantity (int): The quantity ordered
        order_id (int): The ID of the order
    
    Returns:
        int: 1 for success, -1 for failure
    """
    try:
        cursor = cnx.cursor()

        # Safely execute queries using parameterized queries
        cursor.execute("SELECT item_id FROM food_items WHERE name = %s", (food_item,))
        item_id = cursor.fetchone()
        
        # Check if the food item exists
        if item_id is None:
            print("Food item not found.")
            return -1

        item_id = item_id[0]  # Extract the item_id from the result tuple

        # Get the price for the food item
        cursor.execute("SELECT price FROM food_items WHERE name = %s", (food_item,))
        price = cursor.fetchone()

        # Check if price exists
        if price is None:
            print("Price for the food item not found.")
            return -1

        price = price[0]  # Extract the price from the result tuple

        # Calculate total price
        
        # Convert quantity to Decimal
        quantity = Decimal(quantity)

        # Now perform the multiplication
        total_price = price * quantity


        # Insert the order item into the orders table
        cursor.execute("""
            INSERT INTO orders (order_id, item_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item_id, quantity, total_price))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")
        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()
        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()
        return -1

# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()

def get_total_order_price(order_id):
    cursor = cnx.cursor()

    try:
        # Query to fetch all item_ids for a given order_id
        query = "SELECT item_id FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()

        if not items:
            print(f"No items found for order_id {order_id}")
            return 0

        # Create a list of item_ids from the fetched items
        item_ids = [item[0] for item in items]

        # Query to sum the price for all item_ids from the food_items table
        format_strings = ','.join(['%s'] * len(item_ids))  # Create a format string for the query
        query = f"SELECT SUM(price) FROM food_items WHERE item_id IN ({format_strings})"
        cursor.execute(query, tuple(item_ids))

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        return result if result is not None else 0  # Return 0 if no total found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        cursor.close()
        return -1


# Function to get the next available orer_id
def get_next_order_id():
    cursor = cnx.cursor()

    # Executing the SQL query to get the next available order_id
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result + 1

# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    if result:
        return result[0]
    else:
        return None


if __name__ == "__main__":
    # print(get_total_order_price(56))
    # insert_order_item('Samosa', 3, 99)
    # insert_order_item('Pav Bhaji', 1, 99)
    # insert_order_tracking(99, "in progress")
    print(get_next_order_id())
