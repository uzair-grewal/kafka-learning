from common.db import execute_query
from .app import create_main_window

def handle_insert_student(fn_entry, ln_entry):
    first_name = fn_entry.get()
    last_name = ln_entry.get()

    if not first_name or not last_name:
        print("Error: Both names are required!")
        return

    query = "INSERT INTO students (first_name, last_name) VALUES (%s, %s)"
    execute_query(query, (first_name, last_name))
    
    # Clear fields after success
    fn_entry.delete(0, 'end')
    ln_entry.delete(0, 'end')
    print(f"Inserted: {first_name} {last_name}")

def handle_update_mark(id_entry, email_entry):
    s_id = id_entry.get()
    email = email_entry.get()

    if not s_id or not email:
        print("Error: ID and Email are required!")
        return

    query = "UPDATE students SET email = %s WHERE student_id = %s"
    execute_query(query, (email, int(s_id))) 
    
    id_entry.delete(0, 'end')
    email_entry.delete(0, 'end')
    print(f"Updated Student {s_id} to Email {email}")

if __name__ == "__main__":
    app = create_main_window(handle_insert_student, handle_update_mark)
    app.mainloop()
