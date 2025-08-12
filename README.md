Car Damage Detection App
Overview
The Car Damage Detection App is an AI-powered application designed to identify and classify vehicle damages from images. Built using ResNet50 for transfer learning, the system is trained to recognize damage types from third-quarter front and rear views of cars. Users can simply drag and drop an image into the app, and it will instantly predict the type of damage.

This project aims to assist in insurance claims, repair assessments, and automated vehicle inspections by providing quick and accurate results.

Features
Image Upload:
Drag-and-Drop Support: Upload car images for instant analysis.

View Prediction: See the identified damage class and confidence score.

Damage Categories:
Front Normal

Front Crushed

Front Breakage

Rear Normal

Rear Crushed

Rear Breakage

Performance:
Trained on ~1,700 images across 6 classes.

Achieved ~80% accuracy on the validation set.

Technology Stack
Model: ResNet50 (Transfer Learning)

Language: Python

Frameworks & Libraries: TensorFlow / Keras, Streamlit, OpenCV, NumPy

Dataset: Custom-labeled images of third-quarter front/rear car views

Frontend: Streamlit UI for easy interaction

Installation and Setup
Prerequisites
Python 3.8 or higher

pip package manager

Steps
Clone the repository:

bash
Copy
Edit
git clone <repository-link>
cd car-damage-detection
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the app:

bash
Copy
Edit
streamlit run app.py
Usage
Launch the Streamlit app in your browser.

Drag and drop a car image (third-quarter front or rear view).

View the predicted damage category and confidence score.

Future Enhancements
Expand dataset for more vehicle models and angles.

Improve model accuracy with fine-tuning.

Add bounding box detection for localized damage identification.

Integrate with insurance APIs for direct claim processing.


Contact
For any queries or collaboration opportunities, reach out to:

Email: vins.techn@gmail.com

GitHub: Vinay's GitHub
