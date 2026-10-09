import streamlit as st
import mysql.connector


def get_connection():

    try:

        conn = mysql.connector.connect(

            host="localhost",

            user="root",

            password="root",   

            database="project_mysql"

        )

        return conn

    except mysql.connector.Error as e:

        st.error(f"MySQL Connection Error: {e}")

        return None