import tkinter as tk
from tkinter import filedialog, Label
import cv2
from PIL import Image, ImageTk
import customtkinter as ctk
import tempfile
import requests
from datetime import datetime
from deepface import DeepFace
# import verify

uploaded_image = None
captured_image = None
uploaded_image_path = None
captured_image_path = None
fox = None
dob = None
data = []
bio = ""
verified = None

def detect_and_extract_face(image_path):
    # Load the image
    img = cv2.imread(image_path)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Load the pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        print("No faces detected.")
        return None
    
    # Assuming only one face per passport image
    x, y, w, h = faces[0]
    
    # Extract the face from the image
    face_img = img[y:y+h, x:x+w]
    
    extracted_face_path = temp(face_img)
    # Save the extracted face
    # extracted_face_path = "extracted_face.jpg"
    # cv2.imwrite(extracted_face_path, face_img)
    
    return extracted_face_path

def verify():
    # print(captured_image_path, uploaded_image_path)
    a = detect_and_extract_face(captured_image_path)
    b = detect_and_extract_face(uploaded_image_path)
    
    verified = DeepFace.verify(img1_path=a, img2_path=b, model_name='Facenet')
    print(verified)
    if verified['verified']==True:
        label_10.config(text='Match', bg='green')
    else:
        label_10.config(text='Non-Match', bg='red')
        
    return verified['verified']

def temp(image):
    if image is not None:
            # Create a temporary file to store the image
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file_path = temp_file.name
                
                # Write the image array to the temporary file
                cv2.imwrite(temp_file_path, image)

            # Pass the temporary file path to your function
            return temp_file_path

            # After using the temporary file, you can delete it
            # os.remove(temp_file_path)
    else:
        print("Image array is empty or None.")

# API for data retrieval
def info(img_path):
    url = "https://worker.formextractorai.com/v2/extract"

    payload = open(img_path, 'rb')
    headers = {
        'X-WORKER-TOKEN': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNvdXJjZV9vd25lcl9pZCI6IjdhNzYwODY0LTk3NDYtNDc2Mi05N2U0LTJlNjVjYzQ5MTk2MyIsIndvcmtlcl90b2tlbl9pZCI6IjBmYWVlODgxLTdhODItNGZlNC1iNDAxLWI0Mjk0NzEwZmQ0NCIsInVzZXJfaWQiOiI3YTc2MDg2NC05NzQ2LTQ3NjItOTdlNC0yZTY1Y2M0OTE5NjMifQ.sCzg2t1LzoywVTqttsnYiLyIe6W9h4DHvTNgZmGiYIA',
        'X-WORKER-EXTRACTOR-ID': '3725194d-851d-4ca7-87a5-d9b356c9da46',
        'Content-Type': 'image/jpeg',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    fox = response.json()
    data.clear()  # Clear previous data
    data.append(("Name:", fox['documents'][0]['data']['given_name']))
    data.append(("Date of Birth:", fox['documents'][0]['data']['date_of_birth']))
    data.append(("Nationality:", fox['documents'][0]['data']['nationality']))
    data.append(("Sex:", fox['documents'][0]['data']['sex']))
    date_of_expiry = fox['documents'][0]['data']['date_of_expiry']
    data.append(("Date of Expiry:", date_of_expiry))
    data.append(("Passport Number:", fox['documents'][0]['data']['passport_number']))
    
    # Compare the date_of_expiry with the current date
    expiry_date = datetime.strptime(date_of_expiry, "%Y-%m-%d")
    current_date = datetime.now()
    if current_date > expiry_date:
        label_00.config(text="Expired", bg="red")
    else:
        label_00.config(text="Normal", bg="green")
    
    window.update_idletasks()

def open_file_dialog():
    global uploaded_image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", ".png;.jpg;.jpeg;.bmp;*.gif")])
    if file_path:
        # Load the selected image
        img1 = cv2.imread(file_path)
        img = Image.open(file_path)
        img = img.resize((300, 300), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk, width=300, height=300)
        img_label.image = img_tk
        uploaded_image = img1
        
        print(type(img),type(img_tk),type(img_label))
        if uploaded_image is not None:
            # Create a temporary file to store the image
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file_path = temp_file.name
                
                # Write the image array to the temporary file
                cv2.imwrite(temp_file_path, uploaded_image)
                info(temp_file_path)
                for widget in container_frame.winfo_children():
                    widget.destroy()
                for i, text in enumerate(data):
                    label = tk.Label(container_frame, text=text, bg="#f0f0f0", fg="black", font=("Arial", 12))
                    label.grid(row=i % 4, column=i // 4, padx=10, pady=5, sticky="w")
                
            window.geometry('')
            window.update_idletasks()  # Update the window size
            uploaded_image_path = temp_file_path
            # label_10.config(text="match")
        else:
            print("Image array is empty or None.")
                # After using the temporary file, you can delete it
                # os.remove(temp_file_path)
    else:
        print("No file selected.")

# Define a video capture object
vid = cv2.VideoCapture(0)

#Center the window to the screen
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

window = tk.Tk()
window.title("face aging")
window.configure(bg="white")

# Calculate the width and height of the boxes
box_width = 300
box_height = 300

frame = tk.Frame(window, bg="white")
frame.pack(pady=20)

# Create a label to display the uploaded image
img_label = tk.Label(frame, bg="white", width=42, height=20)
img_label.grid(row=0, column=2, padx=10, pady=10)

labels_frame = tk.Frame(frame, bg="white")
labels_frame.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

large_font = ("Arial", 16)

# ID Scan
header_00 = tk.Label(labels_frame, text="ID Scan", bg="white", fg="black", font=large_font)
header_00.grid(row=0, column=0, pady=(5, 0), padx=5, sticky="w")
label_00 = tk.Label(labels_frame, text=bio, bg="white", fg="black")
label_00.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="w")
label_00.config(font=("Arial", 20))  # Increase label size

# Biometric
header_10 = tk.Label(labels_frame, text="Biometric", bg="white", fg="black", font=large_font)
header_10.grid(row=2, column=0, pady=(10, 0), padx=5, sticky="w")
label_10 = tk.Label(labels_frame, text=bio, bg="white", fg="black")
label_10.grid(row=3, column=0, pady=(0, 5), padx=5, sticky="w")
label_10.config(font=("Arial", 20))  # Increase label size

# Screening Type
header_20 = tk.Label(labels_frame, text="Sreening", bg="white", fg="black", font=large_font)
header_20.grid(row=4, column=0, pady=(10, 0), padx=5, sticky="w")
label_20 = tk.Label(labels_frame, text="Cleared", bg="green", fg="black")
label_20.grid(row=5, column=0, pady=(0, 5), padx=5, sticky="w")
label_20.config(font=("Arial", 20))

# Create the left box for displaying camera feed
left_box = tk.Label(
    frame,
    width=box_width,
    height=box_height,
    bg="white",
)
left_box.grid(row=0, column=3, padx=20, pady=20)

# Function to update the camera feed in the left box
def update_frame():
    # Capture the video frame by frame
    ret, frame = vid.read()
    
    if not ret:
        return

    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)

    # Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Displaying photoimage in the label
    left_box.photo_image = photo_image

    # Configure image in the label
    left_box.configure(image=photo_image)

    # Repeat the same process after every 10 milliseconds
    left_box.after(10, update_frame)

# Function to capture and save image
def capture_image():
    global captured_image_path
    ret, frame = vid.read()
    print(ret)
    if ret:
        img_name = "captured_image.png"
        captured_image = frame
        # cv2.imwrite(img_name, frame)
        # label_10.config(text="Image Captured")
        # print(type(frame))
        captured_image_path = temp(frame)
        print(captured_image_path)
    return captured_image_path

button_frame = tk.Frame(window, bg="white")
button_frame.pack(pady=20)

upload_button = ctk.CTkButton(button_frame, text="Upload Image", command=open_file_dialog,
                              corner_radius=15,
                              fg_color="green", text_color="white",
                              font=("Arial", 12, "bold"),
                              width=120, height=40)
upload_button.pack(side=tk.LEFT, padx=20)
capture_button = ctk.CTkButton(button_frame, text="Capture Image", command=capture_image,
                               corner_radius=15,
                               fg_color="lightblue", text_color="white",
                               font=("Arial", 12, "bold"),
                               width=120, height=40)
capture_button.pack(side=tk.LEFT, padx=20)
verify_button = ctk.CTkButton(button_frame, text="verify", command=verify,
                               corner_radius=15,
                               fg_color="lightblue", text_color="white",
                               font=("Arial", 12, "bold"),
                               width=120, height=40)
verify_button.pack(side=tk.LEFT, padx=20)


# Create the container frame with fixed size
container_frame = tk.Frame(window, bg="#f0f0f0", bd=2, relief="groove", width=600, height=200)
container_frame.pack_propagate(False)  # Prevent the frame from resizing based on its content
container_frame.pack(padx=20, pady=20)



# Add data to the container using grid layout
for i, text in enumerate(data):
    label = tk.Label(container_frame, text=text, bg="#f0f0f0", fg="black", font=("Arial", 12))
    label.grid(row=i % 4, column=i // 4, padx=10, pady=5, sticky="w")

# Start the camera feed immediately
update_frame()

center_window(window)

# Start the main event loop to display the window
window.mainloop()

# Release the video capture object
vid.release()
