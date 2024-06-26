import streamlit as st
from PIL import Image
import sys

args = list(sys.argv[1:])[0]
st.markdown('<h2 style="color:white">Welcome '+args+'!!! </h1>',unsafe_allow_html=True)

# Load image

image = Image.open("akkay.jpg")

# Display image
st.image(image, caption='Its the truth', use_column_width=True)
