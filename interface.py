import streamlit as st 
from PIL import Image

img = Image.open("logo.jpg")

st.image(img, width=600)

st.title("Real-time-Price-Monitoring-Alert-System")

st.header("Daily Price Tracking")
st.header("Historical Storage")
st.header("Price Comparision")
st.header("Alert System for Price Change")
st.header("Automated Pipeline")


st.markdown("### Database connective")

st.success("Proceed successfully!")
st.info("This is an info message.")
st.warning("Kindly Check your Balance.")
st.error("Account has been locked!")