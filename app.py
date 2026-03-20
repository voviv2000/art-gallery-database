import pandas as pd
import numpy as np
import streamlit as st

import os
import csv
import uuid
import random
import psycopg2

from faker import Faker
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv


# load env variables
load_dotenv()

# style sheet
st.set_page_config(page_title="Art Gallery Database", layout="wide")

st.markdown("""
    <style>
    /* Import a Google Font (Optional - e.g., 'Cormorant Garamond' for an elegant look) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            
    /* background and text color */
    .stApp {
        background-color: black;
        color: white;
    }
            
    .stSubheader, h2, [data-testid="stHeader"] {
        color: rgba(255, 255, 255, 1) !important; # pure white
        opacity: 1 !important;                     
        font-weight: 900 !important;               # thicker text
        -webkit-text-fill-color: white !important; 
    }
            
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: black !important;
        color: white !important;
        font-family: 'Arial', sans-serif !important;
        font-weight: 900 !important;
    }
            
    # header font
    h1, h2, h3, p, span, label, .stSubheader, .stMarkdown {
        color: white !important;
    }
            
    # tables and dataframes
    table {
        border: 2px solid white !important;
        color: white !important;
    }
    th, td {
        border: 1px solid white !important;
        color: white !important;
        background-color: black !important;
    }
            
    [data-testid="stDataFrame"] {
        border: 2px solid white !important;
    }
            
    /* navbar center top */
    .nav-container {
        display: flex;
        justify-content: center;
        border-bottom: 5px solid white; 
        padding: 10px;
        margin-bottom: 20px;
        background-color: black;
    }
            
    .nav-button {
        margin: 0 15px;
        text-decoration: none;
        color: white;
        font-weight: bold;
        border: 1px solid white;
        padding: 5px 15px;
    }
    /* hide other streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* minimal button look */
    .stButton>button {
        border-radius: 0px;
        border: 5px solid white !important;
        background-color: black !important;
        color: white !important;
        font-weight: 900 !important;
    }
    .stButton>button:hover {
        background-color: white;
        color: black;
    }
            

    
    </style>
    """, unsafe_allow_html=True)

# connnect to database
def get_connection():
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# navbar
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    view_gallery = st.button("GALLERY")
with col2:
    view_stats = st.button("ANALYTICS")
with col3:
    view_exhibitions = st.button("EXHIBITIONS")
with col4:
    view_customers = st.button("CUSTOMERS")
with col5:
    update_data = st.button("MANAGE")
st.markdown('</div>', unsafe_allow_html=True)



# views
if view_gallery or 'page' not in st.session_state:
    st.session_state.page = "Gallery"
if view_stats: st.session_state.page = "Stats"
if view_exhibitions: st.session_state.page = "Exhibitions"
if view_customers: st.session_state.page = "Customers"
if update_data: st.session_state.page = "Manage"



# gallery images
if st.session_state.page == "Gallery":
    st.subheader("BROWSE OUR GALLERY!")
    
    # get input
    search = st.text_input("SEARCH BY TITLE", placeholder="e.g. monet")

    # connect
    conn = get_connection()
    
    # left join
    query = """
        SELECT 
            a.artworkid, 
            a.title, 
            a.medium, 
            a.price, 
            i.iiifurl,
            i.openaccess
        FROM Artwork a
        LEFT JOIN published_images i ON a.artworkid = i.depictstmsobjectid
        WHERE (i.viewtype = 'primary' OR i.iiifurl IS NOT NULL OR i.viewtype IS NULL)
    """
    
    # apply filter
    if search:
        query += f" AND a.title ILIKE '%%{search}%%'"
    
    query += " LIMIT 24"
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # mormalize pandas column names 
    df.columns = ['artworkID', 'title', 'medium', 'price', 'iiifURL', 'openAccess']

    if not df.empty:
        # Create a grid of 3 columns
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                obj_id = row['artworkID']
                
                # use the iiifURL for images
                if row['iiifURL'] and str(row['iiifURL']) != 'None':
                    img_url = f"{row['iiifURL']}/full/!400,400/0/default.jpg"
                else:
                    # use object id api if else
                    img_url = f"https://api.nga.gov/iiif/3/full/!400,400/0/default.jpg?id={obj_id}"

                try:
                    # if image exists then render
                    st.image(img_url, use_column_width=True)
                except:
                    # add place holder image
                    st.image("https://via.placeholder.com/400x400.png?text=Image+Not+Found", use_column_width=True)

                # add pricing and title
                st.markdown(f"**{row['title']}**")
                st.write(f"Price: ${row['price']:,.2f}")
                st.markdown("---")
    else:
        st.write("NO RESULTS FOUND.")


# analysis
elif st.session_state.page == "Stats":
    st.subheader("ANALYTICS")

    conn = get_connection()
    if conn:
        query = """
        SELECT c.categoryname AS "Category", 
               COUNT(a.artworkid) AS "Piece Count", 
               SUM(a.price) AS "Total Market Value"
        FROM Category c
        JOIN Belongs b ON c.categoryid = b.categoryid
        JOIN Artwork a ON b.artworkid = a.artworkid
        GROUP BY c.categoryname
        ORDER BY "Total Market Value" DESC;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Display as a table and a bar chart
        st.write("### Category Stats")
        st.dataframe(df, use_container_width=True)
        
        st.write("### Inventory")
        # Ensure the column names here match the Aliases in your SQL (e.g., "Category")
        st.bar_chart(data=df, x="Category", y="Piece Count")


# exhibition page
elif st.session_state.page == "Exhibitions":
    st.subheader("EXHIBITIONS")
    
    # get input
    ex_search = st.text_input("SEARCH OUR EXHIBITIONS!", placeholder="e.g. Theme or Title")
    
    conn = get_connection()
    if conn:
        # construct query
        query = """
        SELECT 
            e.exhibitionname AS "Exhibition", 
            e.theme AS "Theme", 
            COUNT(DISTINCT d.artworkid) as "Total Artworks", 
            COUNT(DISTINCT att.customerid) as "Total Attendees",
            SUM(a.price) as "Total Value"
        FROM Exhibition e
        LEFT JOIN Displays d ON e.exhibitionid = d.exhibitionid
        LEFT JOIN Artwork a ON d.artworkid = a.artworkid
        LEFT JOIN Attends att ON e.exhibitionid = att.exhibitionid
        WHERE 1=1
        """
        
        # apply filters
        if ex_search:
            # ILIKE for case sensitivity
            query += f""" 
                AND (e.exhibitionname ILIKE '%%{ex_search}%%' 
                OR e.theme ILIKE '%%{ex_search}%%')
            """
            
        query += " GROUP BY e.exhibitionname, e.theme, e.exhibitionid"
        
        # diplay table
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            st.table(df)
        else:
            st.warning(f"No exhibitions or themes found matching '{ex_search}'.")


# client page
elif st.session_state.page == "Customers":
    st.subheader("CUSTOMERS")
    conn = get_connection()
    if conn:
        # format ttext
        query = """
        SELECT 
            c.customername AS "Customer Name", 
            SUM(a.price) AS "Total Spent"
        FROM Customer c
        JOIN Artwork a ON c.customerid = a.customerid
        GROUP BY c.customername
        HAVING SUM(a.price) > (
            SELECT AVG(total_spent) 
            FROM (
                SELECT SUM(price) AS total_spent 
                FROM Artwork 
                GROUP BY customerid
            ) sub
        )
        ORDER BY "Total Spent" DESC;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        st.info("Top Customers!")
        
        # display dataframe
        st.dataframe(df, use_container_width=True)


# update prices of artwork
elif st.session_state.page == "Manage":
    st.subheader("UPDATE ARTWORK PRICES")
    with st.form("update_price"):
        art_id = st.number_input("ARTWORK ID", step=1)
        new_price = st.number_input("NEW PRICE", min_value=0.0)
        submitted = st.form_submit_button("COMMIT CHANGE")
        
        if submitted:
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                
                # get input
                cur.execute('SELECT title FROM Artwork WHERE artworkid = %s', (art_id,))
                result = cur.fetchone()
                
                if result:
                    art_name = result[0]
                    
                    # update table
                    cur.execute('UPDATE Artwork SET price = %s WHERE artworkid = %s', (new_price, art_id))
                    conn.commit()
                    
                    # print notif
                    st.success(f"ARTWORK {art_id}: '{art_name}' UPDATED TO ${new_price:,.2f}")
                else:
                    st.error(f"Artwork ID {art_id} not found in database.")
                
                cur.close()
                conn.close()