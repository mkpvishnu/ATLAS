import json
from datetime import datetime
import mysql.connector
from mysql.connector import Error

class DatabaseInserter:
    def __init__(self, host, database, user, password):
        self.connection_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': 3308
        }
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            print("Successfully connected to the database")
            return True
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def get_max_id(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MAX(id) FROM tickets")
            result = cursor.fetchone()
            return result[0] if result[0] else 90000000  # Default start if no records
        except Error as e:
            print(f"Error getting max ID: {e}")
            return 90000000
        
    def get_max_display_id(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MAX(display_id) FROM tickets")
            result = cursor.fetchone()
            return result[0] if result[0] else 100000000000  # Default start if no records
        except Error as e:
            print(f"Error getting max display ID: {e}")
            return 100000000000

    def insert_test_data(self, num_records):
        if not self.connection or not self.connection.is_connected():
            print("Not connected to database")
            return False

        # Get starting IDs
        start_id = self.get_max_id() + 1
        start_display_id = self.get_max_display_id() + 1

        # Base template for custom fields
        custom_fields = [
            {"name": "cf_single_line_text", "type": "text", "label": "Single Line Text", "value": None, "choice_id": None},
            {"name": "cf_multi_line_text", "type": "paragraph", "label": "Multi Line Text", "value": None, "choice_id": None},
            {"name": "cf_dropdown", "type": "dropdown", "label": "Dropdown", "value": None, "choice_id": None},
            {"name": "cf_checkbox", "type": "checkbox", "label": "Checkbox", "value": False, "choice_id": None},
            {"name": "cf_date", "type": "date", "label": "Date", "value": None, "choice_id": None},
            {"name": "cf_nested_field_level_1", "type": "dropdown", "label": "Nested Field - Level 1", "value": None, "choice_id": None},
            {"name": "cf_nested_field_level_2", "type": "dropdown", "label": "Nested Field - Level 2", "value": None, "choice_id": None},
            {"name": "cf_nested_field_level_3", "type": "dropdown", "label": "Nested Field - Level 3", "value": None, "choice_id": None},
            {"name": "cf_scriptalertdocumentcookiescript", "type": "date", "label": "alert(document.cookie)", "value": None, "choice_id": None}
        ]

        try:
            cursor = self.connection.cursor()
            
            insert_query = """
            INSERT INTO tickets (
                id, account_id, subject, description, description_text, deleted,
                priority, source, status, ticket_type, processing_status, tags,
                custom_fields, created_at, updated_at, display_id, requester_id,
                ticket_group, product_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            for i in range(num_records):
                current_id = start_id + i
                current_display_id = start_display_id + i
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                values = (
                    current_id,
                    99999996,
                    f'Sample Ticket - {i + 1} - {datetime.now().strftime("%Y%m%d%H%M%S")}',
                    '<div>Added by vishnu</div>',
                    'testing GDPR changes',
                    0,
                    '1',
                    '2',
                    'Open',
                    None,
                    'persisted',
                    '[]',
                    json.dumps(custom_fields),
                    current_time,
                    current_time,
                    current_display_id,
                    '48011247638',
                    None,
                    None
                )
                
                cursor.execute(insert_query, values)
                print(f"Inserted record {i+1}/{num_records} with ID: {current_id}")
            
            self.connection.commit()
            print(f"Successfully inserted {num_records} records")
            return True

        except Error as e:
            print(f"Error inserting data: {e}")
            self.connection.rollback()
            return False
        
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'middleware2',
        'user': 'admin',
        'password': 'jqMrduhk8uF8ApC'
    }
    
    NUMBER_OF_RECORDS = 20
    inserter = DatabaseInserter(**DB_CONFIG)
    
    if inserter.connect():
        inserter.insert_test_data(NUMBER_OF_RECORDS)
        inserter.close()