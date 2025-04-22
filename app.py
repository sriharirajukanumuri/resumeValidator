from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
from google.generativeai.models import list_models
import matplotlib.pyplot as plt  # Make sure this import is included

# Configure the API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List and print the available models
models = list_models()
for model in models:
    print(model.name)

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(contents=[input, pdf_content[0]])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Specify the path to the Poppler bin directory
        poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"

        # Convert the PDF to image
        images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
def plot_percentage_match(match_percentage):
    # Create a pie chart
    labels = 'Match', 'Mismatch'
    sizes = [match_percentage, 100 - match_percentage]
    colors = ['#ff9999','#66b3ff']
    explode = (0.1, 0)  # explode the first slice

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

def extract_match_percentage(response):
    try:
        # Find the first element that is a valid percentage
        for word in response.split():
            if '%' in word:
                return float(word.strip('%'))
    except ValueError:
        return None
    return None

## Streamlit App

st.set_page_config(page_title="Raymondjames Resume Ranking system")
st.header("Raymondjames Resume profile selector")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage match")

input_prompt1 = """
You are an experienced HR professional with a strong background in technology. Your expertise includes the following domains:
1. Data science
2. Full-stack web development
3. Big data engineering
4. Software engineering
5. Software testing
6. DevOps
7. Data analysis

Your task is to review the provided resume against the job description, focusing on the job title and relevant technologies. Please provide a comprehensive evaluation of whether the candidate's profile aligns with the role, structured as follows:
1. **Overall Fit:** A summary of the candidate’s suitability for the role.
2. **Strengths:** Key strengths of the candidate in relation to the job requirements.
3. **Weaknesses:** Areas where the candidate's profile does not align with the job requirements.
4. **Recommendation:** A professional recommendation on whether to move forward with the candidate.

Please ensure your evaluation is thorough and based on the specified job requirements.
"""

input_prompt3 = """
You are a skilled Applicant Tracking System (ATS) scanner with a deep understanding of the following technologies:
1. Data science
2. Full-stack web development
3. Big data engineering
4. Software engineering
5. Software testing
6. DevOps
7. Data analysis

Your task is to evaluate the resume against the provided job profile and job description. Provide the results in the following format:
1. **Percentage Match:** The percentage that indicates how well the resume matches the job description.
2. **Keywords Missing:** A list of important keywords or skills that are missing from the resume.
3. **Final Thoughts:** Additional comments or observations about the candidate's alignment with the job requirements.

Please ensure the output is clear and structured as specified.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        
        match_percentage = extract_match_percentage(response)
        
        st.subheader("The Response is")

        if match_percentage is not None:
            st.subheader("Percentage Match Graph")
            plot_percentage_match(match_percentage)
        else:
            st.write("Could not extract match percentage from the response.")

        st.write(response)

    else:
        st.write("Please upload the resume")
