import os
from flask import Flask, request, render_template, jsonify, send_file, Response
from dotenv import load_dotenv
from google import genai
import subprocess
import tempfile
import shutil
import time

load_dotenv()


app = Flask(__name__)

def get_gemini_client():
    """
    Helper to read the key from the request and return a client.
    This is where the key is 'read' for the backend.
    """
    # Prefer the key sent from frontend, fallback to server environment variable
    user_key = request.headers.get("X-Gemini-Key") or \
               request.form.get("api_key")
    if not user_key:
        return None
    
    return genai.Client(api_key=user_key)

def build_prompt(latex_content, job_description):
    """
    Integrates the expert ATS analyzer instructions as the default system-level prompt.
    """
    return f"""
I need you to act as an expert ATS (Applicant Tracking System) analyzer and resume consultant. 
Please review my resume thoroughly in comparison with my target job description and provide:

**PRELIMINARY RESEARCH STEP:**
Before analyzing the resume, search and analyze the target job role on hiring websites (LinkedIn Jobs, Indeed, Glassdoor, etc.) to understand:
- Common job titles used in the industry for this role
- Standard responsibilities and requirements
- Typical career progression paths
- Technology stacks and tools commonly mentioned
- Skill requirements at different experience levels
- How similar roles are described across different companies

Use these insights as additional context alongside the provided job description to ensure recommendations are industry-aligned and realistic.

1. ATS Score Analysis:
- Give me an overall ATS compatibility score out of 100
- Explain the scoring methodology used
- Identify any formatting or structural issues that might cause ATS rejection
- Check for proper use of keywords, standard section headings, and machine-readable format

2. Job Description Match Analysis:
- Calculate a match percentage between my resume and the job description
- List the key requirements from the job description and indicate which ones my resume addresses
- Identify critical keywords from the job description that are missing in my resume
- Highlight skills and qualifications mentioned in the job description that I should emphasize more
- Point out any gaps between what the job requires and what my resume shows

3. Detailed Section-by-Section Breakdown:
For each section of my resume (Summary/Objective, Work Experience, Skills, Certifications, Projects, etc.), provide:
- Good Points: What's working well in this section
- Points to Improve: What needs enhancement (metrics, vague statements, etc.)
- Points to Add: What's missing that should be included
- Update job titles, roles, and responsibilities to match the target role. 
- Emphasize transferable skills, tools, and responsibilities.

Strict Constraints (Do NOT modify):
- Education details
- Company names
- Employment dates (from/to)

**JOB TITLE MODIFICATION RULES:**
- ONLY use real-world, industry-standard job titles that actually exist in the market
- DO NOT create hybrid or made-up titles by combining multiple role names
- DO NOT add supplementary titles alongside existing titles
- Adjust job titles to commonly recognized alternatives that accurately reflect the responsibilities
- Verify job title legitimacy through your preliminary research on hiring websites
- Example ACCEPTABLE changes: "Software Developer" → "Software Engineer", "Programmer" → "Backend Developer"
- Example UNACCEPTABLE changes: "Software Developer" → "AI Software Developer Engineer", "Developer" → "Developer & ML Engineer"
- If current title is already industry-standard, keep it unchanged
- Job title should match what would appear on LinkedIn or Indeed for similar responsibilities

**CRITICAL CHRONOLOGICAL CONSISTENCY RULE:**
- **ONLY mention technologies, tools, frameworks, practices, or methodologies that were actually available and in use during the specific timeframe of each role**
- For roles from 2015-2017: Do NOT add modern AI tools (ChatGPT, LLMs, Stable Diffusion, etc.), modern cloud services, or frameworks that didn't exist then
- Respect the realistic career progression arc for the target role (e.g., an AI Engineer in 2026 likely started with traditional ML/data science in 2015-2017, then evolved through deep learning, cloud ML, and finally to LLMs/GenAI)
- For each experience period, verify that mentioned tools/technologies were available during those years
- Show natural skill evolution: foundational skills in early roles → intermediate technologies in mid-career → cutting-edge tools in recent roles
- Example: 2015-2017 role should mention Python, scikit-learn, traditional ML, basic neural networks; NOT transformer models, LangChain, or GPT APIs
- Cross-reference with your preliminary hiring website research to understand what technologies were standard for this role during each time period

Allowed Modifications:
- Job titles (adjust to industry-standard titles only, following rules above)
- Bullet points, Responsibilities, Achievements, Tools/tech stack wording (must be period-appropriate)
- Summary

4. Keyword Optimization:
- List the top 10-15 keywords from the job description AND from your hiring website research
- Show how many times each keyword appears in my resume
- Suggest where and how to naturally incorporate missing keywords **while respecting chronological constraints**
- For older roles, show how foundational versions of modern skills can be emphasized
- Prioritize keywords that appear frequently across multiple job postings for this role

5. Content Alignment Recommendations:
- Which experiences should I emphasize more?
- What achievements should I add or modify?
- Any irrelevant sections to minimize?
- **How to demonstrate career progression that naturally leads to the target role**
- How does the resume compare to industry standards found in your research?

6. Overall Strategy:
- Summary of top 3-5 changes to improve chances
- Formatting improvements for better ATS parsing
- **Career narrative that shows logical progression to current expertise**
- Industry insights from hiring website research and how to leverage them
- Final recommendations for tailoring this resume

7. Rewrite my resume:
- Provide the content for every section.
- Incorporate every modification suggested.
- **Use only real-world, industry-standard job titles verified through research**
- **Ensure all technologies/tools mentioned are chronologically accurate**
- **Show clear skill evolution from early career to present**
- **Align with industry standards observed in hiring website research**
- Please be specific with examples and provide actionable feedback

STRICT OUTPUT FORMAT:
- Strictly Stick to the LaTeX format i pasted. Not even change any indentation or formatting.
- Do not include any asterisks in the Output LaTeX code.
- You must return your response in exactly this format, using these specific headers:

---BEGIN_ANALYSIS---
# Changes Made
[Insert your detailed analysis, scores, and tables here in Markdown format]

---BEGIN_LATEX---
[Insert ONLY the raw LaTeX code here]

JOB DESCRIPTION:
{job_description}

LATEX RESUME CONTENT:
{latex_content}
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get-models", methods=["GET"])
def get_models():
    # Attempt to get key from headers or args if you want to load models before submission
    # For now, let's allow a default or handle the case where no key is provided yet
    client = get_gemini_client()
    
    if not client:
        return jsonify({"models": ["gemini-2.5-flash", "gemini-2.5-pro"]}) # Fallback list
    """Fetches a list of available Gemini models for the dropdown."""
    try:
        # Use the modern SDK to list models
        models = []
        # Filter for models that support content generation
        # and clean up the 'models/' prefix
       
        for m in client.models.list():
            for action in m.supported_actions:
                if action == "generateContent":
                    models.append(m.name)
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    client = get_gemini_client()
    if not client:
        return jsonify({"error": "No API key provided"}), 400
    # 1. Get Job Description from the form field
    job_description = request.form.get("job_description")
    
    # 2. Get the uploaded file
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400
        
    file = request.files["resume"]
    
    try:
        # Read and decode the LaTeX file
        latex_content = file.read().decode("utf-8")

        # 3. Build the prompt using the hardcoded expert instructions
        final_prompt = build_prompt(latex_content, job_description)
        selected_model = request.form.get("model_id", "gemini-2.5-flash")
        # print(selected_model)
        # 4. Generate content via Gemini
        response = client.models.generate_content(
            model=selected_model,
            contents=final_prompt
        )
        
        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/download-pdf", methods=["POST"])
def download_pdf(): 
 
    latex_code = request.json.get("latex") 
 
    with tempfile.TemporaryDirectory() as tmpdir: 
 
        # copy class 
        shutil.copy( 
            os.path.join(app.root_path, "templates", "resume.cls"), 
            tmpdir 
        ) 
 
        tex_path = os.path.join(tmpdir, "resume.tex") 
        pdf_path = os.path.join(tmpdir, "resume.pdf") 
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        try:
            # 3. Run Tectonic with continue-on-errors flag
            # tectonic_path = r"C:\Users\<username>\scoop\shims\tectonic.exe"
            result = subprocess.run(
                ["tectonic", "-X", "compile", "-Z", "continue-on-errors", "resume.tex"],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            # small delay for Windows file lock 
            time.sleep(0.3) 
    
            # ✅ send even if warnings occurred 
            if os.path.exists(pdf_path): 
                # Log any warnings but still return the PDF
                if result.returncode != 0 and result.stderr:
                    print(f"Warning: PDF generated with errors: {result.stderr}")
    
                with open(pdf_path, "rb") as f: 
                    pdf_bytes = f.read() 
    
                return Response( 
                    pdf_bytes, 
                    mimetype="application/pdf", 
                    headers={ 
                        "Content-Disposition": "attachment; filename=resume.pdf" 
                    } 
                ) 
    
            else: 
                # PDF not created - return error details
                error_msg = result.stderr if result.stderr else "PDF generation failed - unknown error"
                return jsonify({"error": error_msg}), 500             
        except FileNotFoundError:
            return jsonify({"error": "Setup Error", "details": "Tectonic not found on system path."}), 500
if __name__ == "__main__":
    app.run(debug=True)