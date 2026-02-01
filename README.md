# churnanalysis

Customer churn prediction system built with Python, scikit-learn, and Streamlit.

## Customer Churn Prediction 📊
End-to-end machine learning project to analyze customer churn and build a predictive classification model.  
Kini dilengkapi dengan **interactive dashboard** yang menampilkan analisis **risk level based**, memungkinkan tim bisnis untuk memonitor churn secara real-time.

This repository demonstrates the complete workflow of a churn prediction system:
- Exploratory data analysis (EDA)
- Preprocessing & feature engineering
- Model training & evaluation
- Business insights & actionable dashboard

💡 Dataset is anonymized and used for educational and portfolio purposes only.

---

## ❓ What is Customer Churn?
Customer churn refers to the loss of clients or customers.  
Predicting churn enables businesses to identify **high-risk customers** early and implement **retention strategies**, which is often more cost-efficient than acquiring new customers.

---

## 🚀 Project Features

### Machine Learning Features
✔ Exploratory Data Analysis (EDA)  
✔ Data preprocessing (scaling & encoding)  
✔ Train/test split & model training  
✔ Logistic Regression classifier  
✔ Evaluation using metrics: classification report, confusion matrix, ROC-AUC, average precision  
✔ Clear notebook documenting each step  

### Dashboard Features
✔ **Interactive dashboard** with Streamlit  
✔ Filter by date range  
✔ **Risk Level Based Analysis**: High / Medium / Low  
✔ KPI section: Total Customers, Churn Rate, Retention Rate, ARPU  
✔ Visualizations: line chart churn rate, bar chart risk level distribution  
✔ Table: Top High Risk Customers  
✔ Automatic updates when dataset in cloud storage changes  

📌 [Dashboard Link with GCP Integration](https://churnanalysis-rxjzjmc43uqjaxvzhrughn.streamlit.app/)

---

## 🧠 Tech Stack
- Python  
- Pandas & NumPy  
- Scikit-learn (preprocessing & modeling)  
- Matplotlib & Seaborn (visualization)  
- Streamlit (dashboard & interactivity)  

---

## Dataset
Dataset must include the following columns:
- `customer_id` : unique customer ID  
- `last_trx_date` : last transaction date  
- `churn` : 1 = churn, 0 = active  
- `monetary` : total revenue  
- `risk_level` : High / Medium / Low  

> Dataset can be CSV stored locally or online (Google Cloud Storage)
