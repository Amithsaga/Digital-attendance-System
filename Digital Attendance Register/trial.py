import tkinter as tk
from tkinter import messagebox
import os
import pandas as pd
import cv2
from PIL import ImageTk, Image
from take_attendance import log_attendance, train_face_recognizer, recognize_faces

# Function to capture student details and save photos
def capture_student_details():
    student_name = entry_name.get()
    student_id = entry_id.get()

    if student_name and student_id:
        student_folder = os.path.join('student_photos', str(student_id))

        # Create a folder for the student's photos if it doesn't exist
        if not os.path.exists(student_folder):
            os.makedirs(student_folder)

        # Capture exactly 10 photos of the student
        cap = cv2.VideoCapture(0)
        count = 0
        while count < 10:
            ret, frame = cap.read()
            cv2.imshow('Press Space to Capture Photo, Q to Quit', frame)
            if cv2.waitKey(1) & 0xFF == ord(' '):
                photo_path = os.path.join(student_folder, f'{student_id}_{count}.jpg')
                cv2.imwrite(photo_path, frame)
                count += 1
                print(f"Captured image {count}")
            elif cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if count == 10:
            # Check if the CSV file exists and is not empty
            if os.path.isfile('student_details.csv') and os.path.getsize('student_details.csv') > 0:
                df = pd.read_csv('student_details.csv')
            else:
                df = pd.DataFrame(columns=['Name', 'ID', 'Photo'])

            # Append student details to the DataFrame
            new_data = {'Name': student_name, 'ID': student_id, 'Photo': student_folder}
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv('student_details.csv', index=False)

            messagebox.showinfo("Success", f"Captured {count} images for student ID: {student_id}.")
        else:
            messagebox.showerror("Error", "Image capture incomplete. Please try again.")

    else:
        messagebox.showerror("Error", "Please provide all details.")

# Function to log attendance
def log_attendance_and_recognize():
    face_recognizer = train_face_recognizer()
    recognize_faces(face_recognizer)
    messagebox.showinfo("Info", "Attendance saved successfully.")

# Function to show attendance records
def show_attendance_records():
    if os.path.isfile('attendance.csv'):
        os.startfile('attendance.csv')
    else:
        messagebox.showinfo("Attendance Records", "No attendance records found.")

# Validation functions
def validate_id(P):
    return P.isdigit() or P == ""

def validate_name(P):
    return P.isalpha() or P == ""

# Creating the main application window
window = tk.Tk()
window.title("Face Recognizer")
window.geometry("1280x720")
window.configure(background="black")

# Logo and Title
logo = Image.open("UI_Image/logo.png")
logo = logo.resize((50, 47), Image.LANCZOS)
logo1 = ImageTk.PhotoImage(logo)
titl = tk.Label(window, bg="black", relief=tk.RIDGE, bd=20, font=("arial", 35))
titl.pack(fill=tk.X)
l1 = tk.Label(window, image=logo1, bg="black")
l1.place(x=560, y=10)
titl = tk.Label(window, text="JNNCE SHIVAMOGGA", bg="yellow", fg="green", font=("arial", 27))
titl.place(x=610, y=12)
a = tk.Label(window, text="Welcome to the Digital Attendance Register \n with Face Recognition", bg="black", fg="yellow", bd=10, font=("arial", 35))
a.pack()

# Student Details Frame
frame_upload = tk.Frame(window, padx=20, pady=20, bg="black")
frame_upload.place(x=100, y=270)

label_id = tk.Label(frame_upload, text="Student ID", bg="black", fg="yellow", font=("times new roman", 12), bd=5, relief=tk.RIDGE)
label_id.grid(row=0, column=0, sticky="w", padx=5, pady=5)
validate_id_cmd = window.register(validate_id)
entry_id = tk.Entry(frame_upload, bd=5, bg="white", fg="black", relief=tk.RIDGE, font=("times", 25, "bold"), validate="key", validatecommand=(validate_id_cmd, "%P"), insertbackground="black")
entry_id.grid(row=0, column=1, padx=5, pady=5)

label_name = tk.Label(frame_upload, text="Student Name", bg="black", fg="yellow", font=("times new roman", 12), bd=5, relief=tk.RIDGE)
label_name.grid(row=1, column=0, sticky="w", padx=5, pady=5)
validate_name_cmd = window.register(validate_name)
entry_name = tk.Entry(frame_upload, bd=5, bg="white", fg="black", relief=tk.RIDGE, font=("times", 25, "bold"), validate="key", validatecommand=(validate_name_cmd, "%P"), insertbackground="black")
entry_name.grid(row=1, column=1, padx=5, pady=5)

upload_button = tk.Button(frame_upload, text="Take Image", command=capture_student_details, bd=10, font=("times new roman", 18), bg="black", fg="yellow", height=2, width=17)
upload_button.grid(row=2, column=0, columnspan=2, pady=10)

# Attendance Logging Frame
frame_log = tk.Frame(window, padx=20, pady=20, bg="black")
frame_log.place(x=670, y=270)

log_button = tk.Button(frame_log, text="Log Attendance", command=log_attendance_and_recognize, bd=10, font=("times new roman", 18), bg="black", fg="yellow", height=2, width=17)
log_button.grid(row=0, column=0, columnspan=2, pady=10)

# Attendance Records Frame
frame_show = tk.Frame(window, padx=20, pady=20, bg="black")
frame_show.place(x=1000, y=270)

show_button = tk.Button(frame_show, text="Show Attendance Records", command=show_attendance_records, bd=10, font=("times new roman", 18), bg="black", fg="yellow", height=2, width=20)
show_button.pack(padx=10, pady=10, expand=True)

# Exit Button
exit_button = tk.Button(window, text="EXIT", bd=10, command=window.quit, font=("times new roman", 16), bg="black", fg="yellow", height=2, width=17)
exit_button.place(x=700, y=660)

window.mainloop()
