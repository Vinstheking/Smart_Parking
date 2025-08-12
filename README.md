# Car Damage Detection App

## Overview
The **Car Damage Detection App** is an AI-powered application that identifies and classifies vehicle damages from images.  
Built using **ResNet50** for transfer learning, the system is trained on third-quarter front and rear views of cars.  
Users can simply drag and drop an image into the app to instantly get the predicted damage category.  

This project can be used for:
- **Insurance claim processing**
- **Repair assessments**
- **Automated vehicle inspections**

---

## Features

### Image Upload
- **Drag-and-Drop Support:** Upload car images for instant analysis.
- **Damage Prediction:** Displays the identified damage class and confidence score.

### Supported Damage Categories
1. Front Normal  
2. Front Crushed  
3. Front Breakage  
4. Rear Normal  
5. Rear Crushed  
6. Rear Breakage  

### Performance
- Dataset: ~1,700 images  
- Classes: 6  
- Accuracy: ~80% on validation set  

---

## Technology Stack
- **Model:** ResNet50 (Transfer Learning)
- **Language:** Python
- **Frameworks & Libraries:** Pytorch
- **Dataset:** Custom-labeled third-quarter front/rear car views
- **Frontend:** Streamlit UI

---

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps
1. **Clone the repository:**
   ```bash
   git clone <repository-link>
   cd car-damage-detection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## Usage
1. Launch the Streamlit app in your browser.
2. Drag and drop a car image (third-quarter front or rear view).
3. View the predicted damage category and confidence score.

---

## Future Enhancements
- Expand dataset for more vehicle models and angles.
- Improve accuracy with further fine-tuning.
- Add bounding box detection for localized damage identification.
- Integrate with insurance APIs for direct claim processing.

---


## Contact
**Email:** [vins.techn@gmail.com](mailto:vins.techn@gmail.com)  
**GitHub:** [Vinay's GitHub](https://github.com/Vinstheking)
