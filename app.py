import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="IMAGE FILTER", layout="centered")
st.title("IMAGE FILTER CONVERTER")

uploaded_file = st.file_uploader("Upload the image", type=["jpg", "jpeg", "png"])

color_space = st.selectbox(
    "Choose a color space to convert to",
    ("Grayscale", "HSV", "LAB", "Sepia")
)


saturation_scale = 1.0
value_scale = 1.0
sepia_intensity = 1.0
l_shift = a_shift = b_shift = 0

def convert_color(img, mode):
    if mode == "Grayscale":
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    elif mode == "HSV":
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s.astype(np.float32), saturation_scale)
        v = cv2.multiply(v.astype(np.float32), value_scale)
        hsv = cv2.merge([
            h,
            np.clip(s, 0, 255).astype(np.uint8),
            np.clip(v, 0, 255).astype(np.uint8)
        ])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    elif mode == "LAB":
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.int16)
        l, a, b = cv2.split(lab)

        l = np.clip(l + l_shift, 0, 255)
        a = np.clip(a + a_shift, 0, 255)
        b = np.clip(b + b_shift, 0, 255)

        lab = cv2.merge([l, a, b]).astype(np.uint8)
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    elif mode == "Sepia":
        base_filter = np.array([[0.393, 0.769, 0.189],
                                [0.349, 0.686, 0.168],
                                [0.272, 0.534, 0.131]])
        sepia_filter = base_filter * sepia_intensity
        sepia = cv2.transform(img, sepia_filter)
        sepia = np.clip(sepia, 0, 255)
        return sepia.astype(np.uint8)

def convert_array_to_image(img_array):
    if len(img_array.shape) == 2:
        return Image.fromarray(img_array)
    else:
        return Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    st.subheader("Original Image")
    st.image(image, use_container_width=True)


    
    if color_space!="Grayscale":
       st.markdown("---")
       st.subheader(f"{color_space} Settings")

    if color_space == "HSV":
        saturation_scale = st.slider("Saturation", 0.0, 3.0, 1.0, 0.1)
        value_scale = st.slider("Brightness", 0.0, 3.0, 1.0, 0.1)

    elif color_space == "LAB":
        l_shift = st.slider("Lightness Shift (L)", -50, 50, 0)
        a_shift = st.slider("Green-Red Shift (A)", -50, 50, 0)
        b_shift = st.slider("Blue-Yellow Shift (B)", -50, 50, 0)

    elif color_space == "Sepia":
        sepia_intensity = st.slider("Sepia Intensity", 0.0, 3.0, 1.0, 0.01)

    st.markdown("---")
    converted = convert_color(image_np, color_space)

    st.subheader(f"Converted Image - {color_space}")
    if color_space == "Grayscale":
        st.image(converted, use_container_width=True, channels="GRAY")
    else:
        converted_img = convert_array_to_image(converted)
        st.image(converted_img, use_container_width=True)

    buffer = BytesIO()
    if color_space == "Grayscale":
        Image.fromarray(converted).save(buffer, format="PNG")
    else:
        converted_img.save(buffer, format="PNG")

    st.download_button(
        label="📥 Download Converted Image",
        data=buffer.getvalue(),
        file_name=f"converted_{color_space.lower()}.png",
        mime="image/png"
    )
