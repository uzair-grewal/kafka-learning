import customtkinter as ctk

def create_main_window(on_insert, on_update):
    app = ctk.CTk()
    app.title("School DBMS Control Panel")
    app.geometry("500x500")

    # --- INSERT SECTION ---
    ctk.CTkLabel(app, text="Add New Student", font=("Arial", 16, "bold")).pack(pady=(20, 5))
    
    first_name_entry = ctk.CTkEntry(app, placeholder_text="First Name", width=300)
    first_name_entry.pack(pady=5)
    
    last_name_entry = ctk.CTkEntry(app, placeholder_text="Last Name", width=300)
    last_name_entry.pack(pady=5)

    # We use a lambda to pass the entry widgets to the main logic
    ctk.CTkButton(app, text="Insert Student", 
                  command=lambda: on_insert(first_name_entry, last_name_entry)).pack(pady=10)

    # --- UPDATE SECTION ---
    ctk.CTkLabel(app, text="Update Student Email", font=("Arial", 16, "bold")).pack(pady=(20, 5))
    
    student_id_entry = ctk.CTkEntry(app, placeholder_text="Student ID", width=100)
    student_id_entry.pack(pady=5)
    
    email_entry = ctk.CTkEntry(app, placeholder_text="New Email", width=100)
    email_entry.pack(pady=5)

    ctk.CTkButton(app, text="Update Email", 
                  command=lambda: on_update(student_id_entry, email_entry)).pack(pady=10)

    return app
