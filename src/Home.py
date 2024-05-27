import streamlit as st
import resources
import base64


##st.image('src/resources/image.jpg')
@st.cache_data
def get_image_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_image_as_base64("src/resources/image.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"]{{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
}}

</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

