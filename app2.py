from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
from google.generativeai.models import list_models
import matplotlib.pyplot as plt  # Ensure this import is included

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

def input_pdf_setup(file_path):
    if file_path is not None:
        # Specify the path to the Poppler bin directory
        poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"

        # Convert the PDF to image
        images = pdf2image.convert_from_path(file_path, poppler_path=poppler_path)
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
        raise FileNotFoundError("File path is None")

def extract_match_percentage(response):
    try:
        # Find the first element that is a valid percentage
        for word in response.split():
            if '%' in word:
                return float(word.strip('%'))
    except ValueError:
        return None
    return None

def plot_percentage_match(match_percentage):
    # Create a pie chart
    labels = 'Match', 'Mismatch'
    sizes = [match_percentage, 100 - match_percentage]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0)  # explode the first slice

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

def plot_bar_graph(match_percentages):
    # Categorize the match percentages into quadrants
    categories = ['0-25%', '25-50%', '50-75%', '75-100%']
    counts = [0, 0, 0, 0]
    
    for percentage in match_percentages:
        if percentage <= 25:
            counts[0] += 1
        elif 25 < percentage <= 50:
            counts[1] += 1
        elif 50 < percentage <= 75:
            counts[2] += 1
        else:
            counts[3] += 1

    # Plot the bar graph
    fig, ax = plt.subplots()
    ax.bar(categories, counts, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    ax.set_xlabel('Match Percentage')
    ax.set_ylabel('Number of Resumes')
    ax.set_title('Resume Match Percentage Distribution')

    st.pyplot(fig)

def process_resumes_in_directory(directory_path, input_text, input_prompt):
    if not os.path.exists(directory_path):
        st.write("Directory does not exist.")
        return

    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    if not pdf_files:
        st.write("No PDF files found in the directory.")
        return

    match_percentages = []
    for pdf_file in pdf_files:
        file_path = os.path.join(directory_path, pdf_file)
        pdf_content = input_pdf_setup(file_path)
        
        st.subheader(f"Processing: {pdf_file}")

        response = get_gemini_response(input_text, pdf_content, input_prompt)
        match_percentage = extract_match_percentage(response)
        
        st.subheader("The Response is")
        st.write(response)
        if match_percentage is not None:
            match_percentages.append(match_percentage)
        else:
            st.write("Could not extract match percentage from the response.")
    
    if match_percentages:
        st.subheader("Resume Ranks")
        plot_bar_graph(match_percentages)
    else:
        st.write("No valid match percentages could be extracted from the responses.")

## Streamlit App

st.set_page_config(page_title="Raymondjames Resume Ranking system")
st.header("Raymondjames Resume profile selector")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])
directory_path = st.text_input("Enter the directory path containing the resumes (PDF):")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage match")
submit_ranks = st.button("Resume Ranks")

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

input_prompt_ranks = """
You are an expert in resume ranking with a deep understanding of the following technologies:
1. Data science
2. Full-stack web development
3. Big data engineering
4. Software engineering
5. Software testing
6. DevOps
7. Data analysis

Your task is to evaluate the resume against the provided job profile and job description. Provide the percentage of match if the resume matches the job description. The output should come as a percentage.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        
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

elif submit_ranks:
    if directory_path:
        process_resumes_in_directory(directory_path, input_text, input_prompt_ranks)
    else:
        st.write("Please enter the directory path.")
