import sqlite3

def process_sqlite(file_path, search_term, find_first_only=True):
    results = []
    search_lower = search_term.lower()
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            try:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                select_query = f"SELECT rowid, * FROM {table};"
                cursor.execute(select_query)
                for row in cursor.fetchall():
                    rowid = row[0]
                    found_in_row = False
                    for col, value in zip(['rowid'] + columns, row):
                        if value is not None and search_lower in str(value).lower():
                            results.append((
                                "SQLite",
                                f"{table}: {col} (rowid={rowid})",
                                str(value)
                            ))
                            found_in_row = True
                            if find_first_only:
                                break
                    if find_first_only and found_in_row:
                        break
                if find_first_only and results:
                    break
            except Exception as e:
                results.append(("SQLite Error", f"{table}", f"Error: {e}"))
        conn.close()
    except Exception as e:
        results.append(("SQLite Error", "Connection", f"Error: {e}"))
    return results

def register(registry):
    registry[".db"] = {
        "handler": process_sqlite,
        "name": "SQLite search",
        "description": "Searches all tables in SQLite (*.db) files"
    }