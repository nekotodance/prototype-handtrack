[README in Japanese](readme-jp.md)

## About prototype-handtrack
This is a prototype software that performs handtracking from webcam video using open-cv.  
Hold thumb and index finger to draw a line, tap thumb and pinky finger to clear the line.  

! [prototype-handtrack](docs/prototype-handtrack.gif)

## Required libraries
    pip install opencv-python mediapipe

## How to use
#### Preparation
Modify the following parts of the source code to match the webcam you are using.  

- WEBCUM_DEVICE_ID
Specify the device ID of the webcam.  
Try starting from 0, as it is assigned to virtual cameras, etc.  
- WEBCUM_WIDTH, WEBCUM_HEIGHT
Specify the video size of the webcam.  
Specify 1920,1080 for FullHD, 1280,720 for HD, etc. according to the webcam to be used.  
- WEBCUM_FPS
Specify the fps of the webcam.  
Specify 0fps, 30fps, 24fps, etc. according to the webcam used.  

#### Execution
    py prototype-handtrack.py

#### Key Operation
Q, ESC : Exit  
R : Mirror display on/off  
H : Show hand recognition part (Simple->Detailed->None->Return to the beginning)  
F : Show face recognition part (Simple->Detailed->None->Only eyes->Back to the beginning)  
C : Show/Hide WEB camera image  

That's all