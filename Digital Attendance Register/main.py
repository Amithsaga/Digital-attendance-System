import pandas as pd
import os
import cv2

def capture_student_details():
    student_name = input("Enter student name: ")
    student_id = input("Enter student ID: ")

    # Create a folder for student photos if it doesn't exist
    student_folder = f'student_photos/{student_id}'
    if not os.path.exists(student_folder):
        os.makedirs(student_folder)

    # Capture the student's photos
    cap = cv2.VideoCapture(0)
    photo_count = 0
    while photo_count < 10:
        ret, frame = cap.read()
        cv2.imshow('Press Space to Capture Photo', frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            photo_path = f'{student_folder}/{student_id}_{photo_count}.jpg'
            cv2.imwrite(photo_path, frame)
            photo_count += 1
            print(f"Captured photo {photo_count}")

    cap.release()
    cv2.destroyAllWindows()

    # Check if the CSV file exists and is not empty
    if os.path.isfile('student_details.csv') and os.path.getsize('student_details.csv') > 0:
        df = pd.read_csv('student_details.csv')
    else:
        df = pd.DataFrame(columns=['Name', 'ID', 'Photo'])

    # Append student details to the DataFrame
    new_data = {'Name': student_name, 'ID': student_id, 'Photo': student_folder}
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    df.to_csv('student_details.csv', index=False)
    print("Student details saved successfully!")

def main():
    capture_student_details()

if __name__ == "__main__":
    main()
