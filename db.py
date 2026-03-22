import psycopg2
from config import settings

def get_connection():
    """Establish a connection to the PostgreSQL database."""
    settings.require_db()
    
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )


def execute_query(sql: str) -> dict:
    """
    Execute a PostgreSQL query and return results or error information.
    
    Args:
        sql: PostgreSQL query string
        
    Returns:
        Dictionary with either:
        - {"success": True, "columns": [...], "rows": [...]} for SELECT queries
        - {"success": True, "message": "..."} for other queries
        - {"success": False, "error": "...", "error_type": "..."} on failure
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(sql)
        
        # Check if it's a SELECT query
        if cursor.description:
            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "columns": columns,
                "rows": [[str(cell) for cell in row] for row in rows],
                "row_count": len(rows)
            }
        else:
            # Non-SELECT query (INSERT, UPDATE, DELETE, etc.)
            row_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "message": f"Query executed successfully. {row_count} row(s) affected.",
                "row_count": row_count
            }
            
    except psycopg2.errors.SyntaxError as e:
        if conn:
            conn.close()
        return {
            "success": False,
            "error": f"SQL Syntax Error: {str(e)}",
            "error_type": "SyntaxError"
        }
    except psycopg2.errors.UndefinedTable as e:
        if conn:
            conn.close()
        return {
            "success": False,
            "error": f"Undefined Table: {str(e)}",
            "error_type": "UndefinedTable"
        }
    except psycopg2.errors.UndefinedColumn as e:
        if conn:
            conn.close()
        return {
            "success": False,
            "error": f"Undefined Column: {str(e)}",
            "error_type": "UndefinedColumn"
        }
    except psycopg2.errors.InvalidTextRepresentation as e:
        if conn:
            conn.close()
        return {
            "success": False,
            "error": f"Invalid Data Type: {str(e)}",
            "error_type": "InvalidTextRepresentation"
        }
    except psycopg2.DatabaseError as e:
        if conn:
            conn.close()
        return {
            "success": False,
            "error": f"Database Error: {str(e)}",
            "error_type": "DatabaseError"
        }
    except Exception as e:
        if conn:
            conn.close()
        return {
            "success": False,
            "error": f"Query Error: {str(e)}",
            "error_type": "UnexpectedError"
        }
    
if __name__ == "__main__":
    # Test the database connection
    try:
        conn = get_connection()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")