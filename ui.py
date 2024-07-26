import streamlit as st
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import os


DESCRIPTION_API_GATEWAY_URL="https://svp6nct490.execute-api.us-east-1.amazonaws.com/prod/generate-description"
HASHTAG_API_GATEWAY_URL="https://svp6nct490.execute-api.us-east-1.amazonaws.com/prod/suggest-hashtags"
ARTICLE_API_GATEWAY_URL= "https://svp6nct490.execute-api.us-east-1.amazonaws.com/prod/generate-article"
GENERATE_IMAGE_API_GATEWAY_URL= "https://svp6nct490.execute-api.us-east-1.amazonaws.com/prod/generate-image"
QUERY_IMAGES_API_GATEWAY_URL="https://svp6nct490.execute-api.us-east-1.amazonaws.com/prod/list-images"
BUCKET_NAME="cloudaistack-imagebucket97210811-uaztmy3s8fy6"




def preview_description(image_bytes, title, description):
    image = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.text((10, 10), title, font=font, fill="white")
    draw.text((10, 30), description, font=font, fill="white")

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()

def generate_description():
    st.header("Instagram Story and Post Generator")

    user_id = st.text_input("User ID", help="Enter a unique ID to track your feedback and preferences.")
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        st.image(image_bytes, caption='Uploaded Image.', use_column_width=True)

        prompt_type = st.selectbox("Select Prompt Type", ["Instagram Story", "Instagram Post"])

        custom_template = st.text_area("Custom Template (optional)")

        temperature = st.slider(
            "Temperature:",
            0.0, 1.0, 0.7,
            help="Controls the creativity of the generated text. Lower values make the text more deterministic, while higher values make it more creative and random."
        )

        if st.button("Generate Description", key="generate_description_button"):
            response = requests.post(DESCRIPTION_API_GATEWAY_URL , json={
                "user_id": user_id,
                "prompt_type": prompt_type,
                "custom_template": custom_template,
                "image_bytes": base64.b64encode(image_bytes).decode('utf-8'),
                "temperature": temperature
            })

            description_result = response.json()
     
            title = description_result['title']
       
            description = description_result['description']
        
            st.write("Generated Title:")
            st.write(title)
            st.write("Generated Description:")
            st.write(description)

            preview_image_bytes = preview_description(image_bytes, title, description)
            st.image(preview_image_bytes, caption='Preview of Description on Image', use_column_width=True)

            user_feedback = st.text_area("Not satisfied? Provide a brief description about this moment:")
            if st.button("Regenerate Description", key="regenerate_description_button"):
                response = requests.post(DESCRIPTION_API_GATEWAY_URL , json={
                    "user_id": user_id,
                    "prompt_type": prompt_type,
                    "custom_template": custom_template,
                    "user_description": user_feedback,
                    "image_bytes": base64.b64encode(image_bytes).decode('utf-8'),
                    "temperature": temperature
                })

                new_description_result = response.json()
                new_title = new_description_result['title']
                new_description = new_description_result['description']
                st.write("Regenerated Title:")
                st.write(new_title)
                st.write("Regenerated Description:")
                st.write(new_description)

                new_preview_image_bytes = preview_description(image_bytes, new_title, new_description)
                st.image(new_preview_image_bytes, caption='Preview of Regenerated Description on Image', use_column_width=True)

def generate_article_titles_and_subtitles():
    st.header("Article Title and Subtitle Generator")

    content = st.text_area("Provide the content of your article, specifying each paragraph with a number (e.g.,1., 2., etc.)")

    if st.button("Generate Titles and Subtitles", key="generate_titles_and_subtitles_button"):
        response = requests.post(ARTICLE_API_GATEWAY_URL , json={
            "content": content
        })

        article_result = response.json()
        st.write("Generated Title and Subtitles:")
        st.write(article_result)

def generate_image():
    st.header("Image Generator")

    prompt = st.text_area("Enter your text prompt:")
    

    init_image_mode ="STEP_SCHEDULE" 
    
    image_strength = st.slider(
        "Image Strength:",
        0.0, 1.0, 0.5,
        help="Adjust the influence of the initial image on the generated content. A higher value means more influence from the initial image."
    )
    
    cfg_scale = st.slider(
        "CFG Scale:",
        1.0, 20.0, 10.0,
        help="CFG (Classifier-Free Guidance) scale controls how strongly the generation follows the prompt. Higher values result in images more closely aligned with the prompt."
    )

    
    style_preset = st.selectbox(
        "Style Preset:",
        ["NONE", "3d-model", "analog-film", "anime", "cinematic", "comic-book", 
         "digital-art", "enhance", "fantasy-art", "isometric", "line-art", 
         "low-poly", "modeling-compound", "neon-punk", "origami", 
         "photographic", "pixel-art", "tile-texture"],
        help="Choose a style preset to influence the artistic style of the generated image. Options include 'photographic' for realistic images and 'cinematic' for more dramatic visuals."
    )

    if st.button("Generate Image", key="generate_image_button"):

        body = {
            "text_prompts": [{"text": prompt, "weight": 1.0}],
            "init_image_mode": init_image_mode if init_image_mode != "NONE" else None,
            "image_strength": image_strength,
            "cfg_scale": cfg_scale,
            "style_preset": style_preset,
            "extras": {}
        }

        response = requests.post(GENERATE_IMAGE_API_GATEWAY_URL , json=body)
        result = response.json()
        image_base64 = result.get('image_base64')
        if image_base64:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption='Generated Image', use_column_width=True)
        else:
            st.write("Failed to generate image")

def list_images():
    st.header("List Images")

    response = requests.post(QUERY_IMAGES_API_GATEWAY_URL, json={})
    data = response.json()

    if response.status_code == 200:
        images = data.get('images', [])
        next_token = data.get('next_token')

        for i in range(0, len(images), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(images):
                    with cols[j]:
                        st.image(images[i + j])

        if next_token:
            if st.button("Load More", key="load_more_button"):
                more_response = requests.post(QUERY_IMAGES_API_GATEWAY_URL, json={
                    "next_token": next_token
                })
                more_data = more_response.json()
                more_images = more_data.get('images', [])
                next_token = more_data.get('next_token')

                for i in range(0, len(more_images), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(more_images):
                            with cols[j]:
                                st.image(more_images[i + j])

                if not next_token:
                    st.write("No more images to load.")
        else:
            st.write("No more images to load.")
    else:
        st.error("Error retrieving images. Please try again later.")
def main():
    st.sidebar.title("Navigation")
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Instagram Content'

    if st.sidebar.button("Instagram Content", key="instagram_content_button"):
        st.session_state['page'] = 'Instagram Content'
    if st.sidebar.button("Article Titles & Subtitles", key="article_titles_button"):
        st.session_state['page'] = 'Article Titles & Subtitles'
    if st.sidebar.button("Generate Image", key="generate_image_button_nav"):
        st.session_state['page'] = 'Generate Image'
    if st.sidebar.button("List Images", key="list_images_button_nav"):
        st.session_state['page'] = 'List Images'

    if st.session_state['page'] == 'Instagram Content':
        generate_description()
    elif st.session_state['page'] == 'Article Titles & Subtitles':
        generate_article_titles_and_subtitles()
    elif st.session_state['page'] == 'Generate Image':
        generate_image()
    elif st.session_state['page'] == 'List Images':
        list_images()

if __name__ == "__main__":
    main()
