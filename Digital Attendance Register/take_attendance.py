import cv2
import os
import pandas as pd
import numpy as np
import datetime
import time

def preprocess_face(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces_detected = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
    faces = []
    for (x, y, w, h) in faces_detected:
        face = image[y:y + h, x:x + w]
        face = cv2.resize(face, (200, 200))  # Resize to a fixed size
        faces.append(face)
    return faces

def train_face_recognizer():
    image_paths = []
    labels = []

    # Load student data from CSV
    df = pd.read_csv('student_details.csv')

    for index, row in df.iterrows():
        student_folder = row['Photo']
        student_id = row['ID']

        # Check if student_id can be converted to an integer
        try:
            student_id = int(student_id)  # Ensure the ID is an integer
        except ValueError:
            print(f"Invalid student ID: {student_id}. Skipping this student.")
            continue

        # Read all photos in the student's folder
        if os.path.exists(student_folder):
            for image_file in os.listdir(student_folder):
                image_path = os.path.join(student_folder, image_file)
                image_paths.append(image_path)
                labels.append(student_id)
        else:
            print(f"Folder not found for ID: {student_id}")

    # Check if the face module is available
    if hasattr(cv2, 'face'):
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    else:
        raise Exception("OpenCV face module not found. Ensure you have installed opencv-contrib-python.")

    faces = []
    ids = []
    for image_path, label in zip(image_paths, labels):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        processed_faces = preprocess_face(image)
        for face in processed_faces:
            faces.append(face)
            ids.append(label)

    if len(faces) > 0:
        face_recognizer.train(faces, np.array(ids))
    return face_recognizer

def log_attendance(student_id):
    today = datetime.date.today().strftime("%Y-%m-%d")
    attendance_file = 'attendance.csv'

    # Check if the attendance file exists
    if os.path.isfile(attendance_file):
        # Check if the file is empty
        if os.path.getsize(attendance_file) > 0:
            df = pd.read_csv(attendance_file)
        else:
            df = pd.DataFrame(columns=['Date', 'ID', 'Name'])
    else:
        df = pd.DataFrame(columns=['Date', 'ID', 'Name'])

    # Check if attendance for the student has already been logged today
    if not df[(df['Date'] == today) & (df['ID'] == student_id)].empty:
        print(f"Attendance already logged for {student_id} today.")
        return

    # Fetch student name from the student details CSV
    student_details_df = pd.read_csv('student_details.csv')
    student_name = student_details_df.query(f'ID == {student_id}')['Name'].values[0]

    # Append new attendance record
    new_data = {'Date': today, 'ID': student_id, 'Name': student_name}
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(attendance_file, index=False)
    print(f"Attendance logged for {student_id} on {today}")

def recognize_faces(face_recognizer):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognized_students = set()

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            face_roi = gray[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (200, 200))  # Resize to the same size as the training images

            label, confidence = face_recognizer.predict(face_roi)

            if confidence < 80:  # Adjust confidence threshold as needed
                # Fetch student details from CSV based on recognized label
                df = pd.read_csv('student_details.csv')
                student = df[df['ID'] == label]

                if len(student) > 0 and label not in recognized_students:
                    student_id = student.iloc[0]['ID']
                    student_name = student.iloc[0]['Name']
                    log_attendance(student_id)
                    recognized_students.add(label)

                    # Draw the name on the frame
                    cv2.putText(frame, student_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    print(f"Recognized {student_name} with confidence {confidence}")

                elif label in recognized_students:
                    print(f"Student {label} already logged today.")
                    cv2.putText(frame, student_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                else:
                    print(f"Student with ID {label} not found in database.")
            else:
                print(f"Unknown face detected with confidence {confidence}")

            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Recognizing Faces', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        elapsed_time = time.time() - start_time
        if elapsed_time > 20:
            print("20 seconds have passed. Stopping camera.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    face_recognizer = train_face_recognizer()
    recognize_faces(face_recognizer)
