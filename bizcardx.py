# Importing necessary libraries
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import easyocr
import cv2
import pandas as pd
import numpy as np
import base64
import re
import mysql.connector
import time
import io
import os


# Connection with MYSQL Database
password = open("mysql_password.txt", "r").readline()

mydb = mysql.connector.connect(host ="localhost",
                               user = "root",
                               password = password,
                               database = "bizcardx_db")
my_cursor = mydb.cursor()


# Data Extraction from Business Card using easyocr
def data_extract(uploaded_file):
    img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
    reader = easyocr.Reader(["en"])
    result = reader.readtext(img, detail = 0, paragraph = True)
    result1 = reader.readtext(img ,detail = 0, paragraph = False)

    data = {"Company_Name": [], "Card_Holder_Name": [], "Designation": [], "Mobile_Number": [], "Email_Address": [], 
        "Website_URL": [], "Area": [], "City": [], "State": [], "Pincode": [], "Image": []}

    for i in result:
        # name, designation, company name
        if re.findall(r"^[A-Za-z]+", i):                                                
            if not re.findall(r"[@|www]", i):                                          
                if re.findall(f"{result1[0]}", i) :
                    data["Card_Holder_Name"].append(*re.findall(f"{result1[0]}", i))
                    data["Designation"].append(*re.findall(f"{result1[1]}", i))   
                else:
                    data["Company_Name"].append(i)

        # website url            
        if re.findall(r"w..|W..", i):
            data["Website_URL"].append(*re.findall(r"[w|W]+.+?com\b", i))

        # email
        if re.findall(r"@", i):
            data["Email_Address"].append(*re.findall(r"[a-z]+@.+?com", i))
        
        # mobile number
        if re.findall(r"[+|-]", i):
            if re.search(r"[\s]([+][0-9-]+.)", i) is not None:
                data["Mobile_Number"].append(*re.findall(r"[\s]([+][0-9-]+.)", i))
            else:
                data["Mobile_Number"].append(*re.findall(r"[0-9-]+", i))

        # area, city, state, pincode
        if re.findall(r"[0-9]{6}",i): 
            data["Area"].append(*re.findall(r"[0-9].*St",i))
            data["City"].append(*re.findall(r",.([A-za-z]+).", i))
            if re.findall(r"[,|;].([A-Za-z]+)[\W|\s][0-9]{6}", i):
                data["State"].append(*re.findall(r"[,|;].([A-Za-z]+)[\W|\s][0-9]{6}", i))
            else:
                data["State"].append(*re.findall(r"[,|;].([A-Za-z]+).[\W|\s][0-9]{6}", i))
            data["Pincode"].append(*re.findall(r"[0-9]{6}",i))

    # image
    file = open(os.path.join("Creative Modern Business Card",uploaded_file.name),'rb').read()
    file = base64.b64encode(file)
    data["Image"].append(file)

    df = pd.DataFrame(data, index = ["Info"])
    return data, df


# Table Creation in MYSQL
def create_tables():
    query = '''CREATE TABLE IF NOT EXISTS bizcardx_data(ID INT PRIMARY KEY AUTO_INCREMENT,                                                                 
                                                        COMPANY_NAME VARCHAR(50),
                                                        CARD_HOLDER_NAME VARCHAR(50),
                                                        DESIGNATION VARCHAR(50),
                                                        EMAIL_ADDRESS VARCHAR(50),
                                                        MOBILE_NUMBER TEXT,
                                                        WEBSITE_URL VARCHAR(50),
                                                        AREA VARCHAR(50),
                                                        CITY VARCHAR(30),
                                                        STATE VARCHAR(30),
                                                        PINCODE INT,
                                                        IMAGE LONGBLOB)'''
    my_cursor.execute(query)


# Inserting Data into MYSQL table(bizcardx_data)
def insert_data(data):
    create_tables()
    query = '''INSERT INTO bizcardx_data(COMPANY_NAME,
                                         CARD_HOLDER_NAME,
                                         DESIGNATION,
                                         MOBILE_NUMBER,
                                         EMAIL_ADDRESS,
                                         WEBSITE_URL,
                                         AREA,
                                         CITY,
                                         STATE,
                                         PINCODE,
                                         IMAGE)
                                         VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    for i in tuple(zip(*data.values())): 
        my_cursor.execute(query, tuple(i))
        mydb.commit()


# Getting ID column from Database
def ids():
    query = '''SELECT ID FROM bizcardx_data'''
    my_cursor.execute(query)
    data = [i for i in my_cursor.fetchall()]
    df = pd.DataFrame(data, columns = my_cursor.column_names)
    return df


# Retrieving Data for Modification
def retrieve_data_for_modify(name):
    query = f'''SELECT * FROM bizcardx_data
                WHERE ID = {name}
                LIMIT 1'''
    my_cursor.execute(query)
    data = [i for i in my_cursor.fetchall()]
    df = pd.DataFrame(data, columns = my_cursor.column_names)
    return df


# Updating Records in MYSQL After Modification
def update_records(c_name, ch_name, desig, mob_number, email, web_url, area, city, state, pincode):  
    query = f'''UPDATE bizcardx_data SET COMPANY_NAME = %s,
                                        CARD_HOLDER_NAME = %s,
                                        DESIGNATION = %s,
                                        MOBILE_NUMBER = %s,
                                        EMAIL_ADDRESS = %s,
                                        WEBSITE_URL = %s,
                                        AREA = %s,
                                        CITY = %s,
                                        STATE = %s,
                                        PINCODE = %s
                WHERE ID = "{st.session_state["ids_1"]}"
                LIMIT 1'''
    values = (c_name, ch_name, desig, mob_number, email, web_url, area, city, state, pincode)
    my_cursor.execute(query, values)
    mydb.commit()
    return "updated successfully"
    

# Function for Deleting Records
def delete_records(name):
    query = f'''DELETE FROM bizcardx_data
                WHERE ID = "{name}"
                LIMIT 1 '''
    my_cursor.execute(query)
    mydb.commit()
    return "deleted successfully"


# Retrieving All Data in MYSQL
def retrieve_all_data():   
    query = '''SELECT * FROM bizcardx_data'''
    my_cursor.execute(query)
    data = [i for i in my_cursor.fetchall()]
    df = pd.DataFrame(data, columns = my_cursor.column_names, index = range(1, len(data) + 1))
    return df


# Retrieving Image from Database
def retrieve_image():
    query = f'''SELECT IMAGE FROM bizcardx_data
                WHERE ID = {st.session_state["ids_2"]}'''
    my_cursor.execute(query)
    data = my_cursor.fetchone()[0]
   
    # Decode the string
    binary_data = base64.b64decode(data)

    # Convert the bytes into a PIL image
    image = Image.open(io.BytesIO(binary_data))
  
    return image



# Streamlit Setup
st.set_page_config("", layout = "wide")

selected = option_menu(None, 
                       options = ["Menu", "Extract and Upload", "Modify", "Delete"], 
                       orientation = "horizontal",
                       icons = ["house-door-fill", "cloud-upload", "gear", "trash"],
                       default_index = 0,
                       styles = {"nav-link": {"font-size": "18px", "text-align": "center", "margin": "1px"},
                                 "icon": {"color": "yellow", "font-size": "20px"},
                                 "nav-link-selected": {"background-color": "#9457eb"}})


if selected == "Menu":
    st.title(":red[BizCardX: Extracting Business Card Data with OCR]")
    st.markdown("")
    st.markdown(f'''The result of the project would be a Streamlit application that allows users to upload
                    an image of a business card and extract relevant information from it using easyOCR. The extracted information should
                    be displayed in a clean and organized manner, and users should be able to easily
                    add it to the database with the click of a button. And Allow the user to Read the data,
                    Update the data and delete the data through the streamlit UI.''')
    

if selected == "Extract and Upload":
    col11, col12 = st.columns(2)

    with col11:
        x = st.file_uploader(":blue[drop your files here...]", type = ["jpg", "jpeg", "png"])
        if x is not None:
            st.image(x, use_column_width = True) 

    with col12:
        if x is not None:
            with st.form(key='my_form'):
                data, df = data_extract(x)
                st.table(df.iloc[0, 0:10].T)
                submit_button = st.form_submit_button(label='Upload')
                if submit_button:
                    with st.spinner("uploading..."):
                            insert_data(data)
                            time.sleep(3)
                            st.success("uploaded successfully", icon="✅")
                            

if selected == "Modify":

    def modify():
        update_records(st.session_state["c_name"], st.session_state["ch_name"], st.session_state["desig"], st.session_state["mob_number"], 
                       st.session_state["email"], st.session_state["web_url"], st.session_state["area"], st.session_state["city"], 
                       st.session_state["state"], st.session_state["pincode"])
    
    st.markdown(":blue[ALL RECORDS FROM DATABASE]")
    st.dataframe(retrieve_all_data())
    
    modify_records = st.selectbox(":blue[select ID to modify records]", options = ids(), key = "ids_1")

    if modify_records is not None:
        r_df = retrieve_data_for_modify(st.session_state["ids_1"])

        with st.form(key = "my_form_modify"):

            if r_df.shape[0] > 0:
                c_name = st.text_input(":violet[COMPANY_NAME]", r_df.loc[0, "COMPANY_NAME"], key = "c_name" )

                ch_name = st.text_input(":violet[CARD_HOLDER_NAME]", r_df.loc[0, "CARD_HOLDER_NAME"], key = "ch_name")

                desig = st.text_input(":violet[DESIGNATION]", r_df.loc[0, "DESIGNATION"], key = "desig")

                mob_number = st.text_input(":violet[MOBILE_NUMBER]", r_df.loc[0, "MOBILE_NUMBER"], key ="mob_number")

                email = st.text_input(":violet[EMAIL_ADDRESS]", r_df.loc[0, "EMAIL_ADDRESS"], key = "email")

                web_url = st.text_input(":violet[WEBSITE_URL]", r_df.loc[0, "WEBSITE_URL"], key = "web_url")

                area = st.text_input(":violet[AREA]", r_df.loc[0, "AREA"], key = "area")

                city = st.text_input(":violet[CITY]", r_df.loc[0, "CITY"], key ="city")

                state = st.text_input(":violet[STATE]", r_df.loc[0, "STATE"], key ="state")

                pincode = st.text_input(":violet[PINCODE]", r_df.loc[0, "PINCODE"], key = "pincode")

            
                button = st.form_submit_button(label='Modify',
                                            on_click = modify)                              
                if button:
                    with st.success("Updated Successfully", icon="✅"):
                        time.sleep(3)
                        st.empty()
        

if selected == "Delete":

    def delete():
        delete_records(st.session_state["ids_2"])

    st.markdown(":blue[ALL RECORDS FROM DATABASE]")
    st.dataframe(retrieve_all_data())

    del_records = st.selectbox(":blue[select ID to delete records]", options = ids(), key = "ids_2")

    delete_button = st.button("Delete", key = "del", on_click = delete)
    if delete_button:
        with st.success("Deleted successfully", icon="✅"):
            time.sleep(3)
            st.empty()

    if del_records is not None:
        col21, col22 = st.columns(2)
        with col21:
            st.dataframe(retrieve_data_for_modify(st.session_state["ids_2"]).iloc[0, 0:10].T, use_container_width = True)
        with col22:
            st.image(retrieve_image(), use_column_width = True)
            
        
        
# ---------------------------x------------------------------x------------------------------x----------------------------x--------------------------x----------------------------