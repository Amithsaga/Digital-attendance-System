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
        df = pd.read_csv('attendance.csv')
        messagebox.showinfo("Attendance Records", str(df))
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
window.configure(background="#2f2f2f")

# Logo and Title
logo = Image.open("UI_Image/logo.png")
logo = logo.resize((50, 47), Image.LANCZOS)
logo1 = ImageTk.PhotoImage(logo)
titl = tk.Label(window, bg="#2f2f2f", relief=tk.RIDGE, bd=20, font=("arial", 35))
titl.pack(fill=tk.X)
l1 = tk.Label(window, image=logo1, bg="#2f2f2f")
l1.place(x=560, y=10)
titl = tk.Label(window, text="JNNCE SHIVAMOGGA", bg="#2f2f2f", fg="#33cc33", font=("arial", 27))
titl.place(x=610, y=12)
a = tk.Label(window, text="Welcome to the Digital Attendance Register \n with Face Recognition", bg="#2f2f2f", fg="#33cc33", bd=10, font=("arial", 35))
a.pack()

# Student Details Frame
frame_upload = tk.Frame(window, padx=20, pady=20, bg="#2f2f2f")
frame_upload.place(x=100, y=270)

label_id = tk.Label(frame_upload, text="Student ID", bg="#2f2f2f", fg="#33cc33", font=("times new roman", 12), bd=5, relief=tk.RIDGE)
label_id.grid(row=0, column=0, sticky="w", padx=5, pady=5)
validate_id_cmd = window.register(validate_id)
entry_id = tk.Entry(frame_upload, bd=5, bg="#33cc33", fg="black", relief=tk.RIDGE