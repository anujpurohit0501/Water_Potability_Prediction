# Water Potability Classification 💧

## Overview

This project focuses on classifying water samples as **potable (safe for drinking)** or **non-potable (unsafe for drinking)** using machine learning classification techniques. The objective is to analyze different physicochemical properties of water and identify patterns that determine water quality.

## Problem Statement

Water quality assessment is important for ensuring safe drinking water. This project uses various chemical and physical parameters of water samples to build classification models that classify water as potable or non-potable.

## Dataset

The dataset contains physicochemical properties of water samples along with a target variable indicating water potability.

### Features:

* **ph** – Measures the acidity or alkalinity of water
* **hardness** – Amount of dissolved calcium and magnesium salts
* **tds** – Total dissolved solids present in water
* **chlorine** – Chlorine concentration in water
* **sulfate** – Sulfate concentration in water
* **conductivity** – Ability of water to conduct electrical current
* **organic_carbon** – Organic carbon content in water
* **trihalomethanes** – Concentration of disinfection by-products
* **turbidity** – Measure of water clarity

### Target Variable:

* **potability**

  * `0` → Non-potable water
  * `1` → Potable water

## Project Workflow

### 1. Data Exploration

* Loaded and inspected the dataset
* Checked dataset shape, data types, and statistical summaries
* Analyzed feature distributions and relationships

### 2. Data Cleaning & Preprocessing

* Checked for missing values
* Handled missing values using median imputation
* Checked and removed duplicate records
* Prepared the dataset for machine learning models

### 3. Exploratory Data Analysis (EDA)

Performed analysis using visualizations such as:

* Feature distribution plots
* Correlation heatmaps
* Potability class distribution
* Feature-wise comparison between potable and non-potable water samples

### 4. Machine Learning Classification

The following classification algorithms were implemented:

* Logistic Regression
* Decision Tree Classifier
* Random Forest Classifier
* K-Nearest Neighbors (KNN)
* Support Vector Machine (SVM)

### Model Evaluation

Models were evaluated using:

* Accuracy Score
* Precision
* Recall
* F1 Score
* Confusion Matrix

## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn
* Jupyter Notebook

## Project Structure

```text
Water-Potability-Classification/
│
├── dataset/
│   └── water_potability.csv
│
├── notebook/
│   └── Water_Potability_Classification.ipynb
│
├── README.md
│
└── requirements.txt
```

## Key Insights

* Missing values were handled using statistical imputation techniques.
* Water quality parameters show different levels of influence on potability classification.
* Exploratory analysis helped understand relationships between physicochemical properties and water safety.
* Classification models were compared to identify the most effective approach.

## Future Improvements

* Perform hyperparameter tuning for better model performance
* Apply feature selection techniques
* Deploy the model using Flask or Streamlit
* Integrate with real-time water quality monitoring systems

## Author

**Your Name**

## License

This project is created for educational and learning purposes.

