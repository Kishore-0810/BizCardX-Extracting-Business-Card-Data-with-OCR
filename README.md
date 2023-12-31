# BizCardX-Extracting-Business-Card-Data-with-OCR

The result of the project would be a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR. The extracted information should be displayed in a clean and organized manner, and users should be able to easily add it to the database with the click of a button. And Allow the user to Read the data, Update the data and delete the data through the streamlit UI.

## Implement Image Processing using OCR:
Use easyOCR to extract the relevant information from the uploaded business card image.The extracted information would include the company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pincode.

## Display the Extracted Information: 
Once the information has been extracted, display it in a clean and organized manner like dataframe or tables in the Streamlit GUI.

## Implement Database Integration: 
Use a database management system like MySQL to store the extracted information along with the uploaded business card image. You can use SQL queries to create tables and insert data in those tables.

## Modify and Delete Records:
Use SQL queries to retrieve data from the database, and Allow the user to View, Update and Delete the data through the streamlit UI.

## Getting Started
To get started with this project, do the following steps:

 1. Have some business card images in image format. 
 2. Install and Import the required Python packages like streamlit, streamlit-option-menu, mysql-connector-python, pandas, numpy, PIL, easyocr, cv2, base64, re, io, os, time.
 3. Set up a SQL database(mysql).
 4. open the terminal, type streamlit run 'bizcardx.py' script to start the Streamlit application in your web browser.

## Technologies
OCR,streamlit GUI, SQL,Data Extraction

