# Resume AI Tailor (Gemini Resume Optimizer)

A powerful tool that uses Google's Gemini AI to analyze your resume against a specific job description and rewrite it in LaTeX format for optimal ATS compatibility and impact.

## Features

-   **AI-Powered Analysis**: Uses Gemini 2.5 (Flash/Pro) to critique your resume against a target Job Description.
-   **Intelligent Rewriting**: Automatically rewrites your resume content in LaTeX, optimizing keywords and structure.
-   **ATS Scoring**: Provides a compatibility score and detailed breakdown of strengths and weaknesses.
-   **PDF Generation**: Compiles the optimized LaTeX code into a professional PDF resume using Tectonic.
-   **Modern UI**: Clean, responsive interface for easy interaction.

## Prerequisites

Before running the application, ensure you have the following installed:

1.  **Python 3.8+**
2.  **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/).
3.  **Tectonic**: A modern, self-contained LaTeX engine.
    -   *Windows*: `scoop install tectonic` (using Scoop) or download from [GitHub](https://github.com/tectonic-typesetting/tectonic/releases).
    -   *macOS*: `brew install tectonic`
    -   *Linux*: See [official installation guide](https://tectonic-typesetting.github.io/en-US/install.html).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Resume-AI-Tailor
    ```

2.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### Tectonic Path
Currently, the application uses a hardcoded path for the `tectonic.exe` executable in `app.py`.

1.  Open `app.py`.
2.  Locate the `download_pdf` function (around line 227).
3.  Update the `tectonic_path` variable to point to your local Tectonic executable:
    ```python
    # Example
    tectonic_path = r"C:\Path\To\Your\tectonic.exe" 
    # check where it is with `where tectonic` (Windows) or `which tectonic` (Mac/Linux)
    ```

### Environment Variables (Optional)
You can create a `.env` file in the root directory to store your API key instead of entering it in the UI every time:
```env
GOOGLE_API_KEY=your_api_key_here
```
*Note: The application prioritizes the key entered in the UI.*

## Usage

1.  **Start the application**:
    ```bash
    python app.py
    ```

2.  **Open your browser**:
    Navigate to `http://127.0.0.1:5000`.

3.  **Optimize your resume**:
    -   Paste your **Gemini API Key**.
    -   Click **Load Models** and select a model (e.g., `gemini-2.5-flash`).
    -   Paste the target **Job Description**.
    -   Upload your current resume (LaTeX `.tex` or text file).
    -   Click **Analyze & Rewrite**.

4.  **View Results**:
    -   Review the detailed **Analysis** of your resume.
    -   See the **Modified LaTeX Output**.
    -   Click **Download PDF** to get your new resume.

## Project Structure

-   `app.py`: Main Flask application backend.
-   `templates/`: HTML templates and LaTeX class files.
    -   `index.html`: Frontend user interface.
    -   `resume.cls`: LaTeX class file for resume formatting.
-   `requirements.txt`: Python dependencies.

## License

[MIT](LICENSE)