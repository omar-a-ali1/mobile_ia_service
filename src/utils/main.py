import face_recognition
import cv2
# Open the default camera

picture_of_me = face_recognition.load_image_file("../../uploads/profile.jpeg")
my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

cam = cv2.VideoCapture(0)
while True:
    ret, frame = cam.read()
    # Display the captured frame
    cv2.imshow('Camera', frame)
    
    picture = face_recognition.face_encodings(frame)
    if picture:
        result = face_recognition.compare_faces([my_face_encoding], picture[0])
        if result[0]:
            print("Match found!")
            

    if cv2.waitKey(1) == ord('q'):
        break
# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()