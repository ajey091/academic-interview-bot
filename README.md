# Academic Interview Bot - Child Language Development

This is a PyQt6-based application that simulates an academic job interview for a tenure-track faculty position in child language development. It uses Google Gemini for question generation and feedback, and OpenAI for text-to-speech and transcription.

## Features

*   Asks dynamically generated interview questions.
*   Records user responses.
*   Transcribes audio responses using OpenAI Whisper.
*   Generates feedback on responses, including critiques and alternative responses, using Google Gemini.
*   Provides an overall summary feedback.
*   Saves the interview transcript to both a text file and a PDF.

## Requirements

*   Python 3.7+
*   The following Python packages (install using `pip install -r requirements.txt`):
    *   PyQt6
    *   sounddevice
    *   numpy
    *   soundfile
    *   openai
    *   scipy
    *   pygame
    *   google-generativeai
    *   reportlab

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd <your_repository_directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Obtain API Keys:**
    *   **Google Gemini:** Obtain an API key from [Google AI Studio](https://ai.google.dev/).
    *   **OpenAI:** Obtain an API key from the [OpenAI website](https://platform.openai.com/).

2.  **Set API Keys (Environment Variables - Recommended):**
    *   **Best Practice:**  Set your API keys as environment variables. This prevents accidentally committing your keys to a public repository.
        *   **Linux/macOS:**
            ```bash
            export GOOGLE_API_KEY="your_google_api_key"
            export OPENAI_API_KEY="your_openai_api_key"
            ```
        *   **Windows (PowerShell):**
            ```powershell
            $env:GOOGLE_API_KEY = "your_google_api_key"
            $env:OPENAI_API_KEY = "your_openai_api_key"
            ```
        *   **Windows (cmd):**
            ```cmd
            set GOOGLE_API_KEY=your_google_api_key
            set OPENAI_API_KEY=your_openai_api_key
            ```
    *    **Alternative (Less Secure):** You *could* create a `.env` file in your project directory. This file would contain:
          ```
          GOOGLE_API_KEY=your_google_api_key
          OPENAI_API_KEY=your_openai_api_key
          ```
          Then, install the `python-dotenv` package (`pip install python-dotenv`), and add these lines at the *very beginning* of your Python script:
          ```python
          from dotenv import load_dotenv
          import os
          load_dotenv()
          ```
        This method is less secure because it's easier to accidentally commit the `.env` file.

3.  **Run the application:**
    ```bash
    python your_script_name.py
    ```
    (Replace `your_script_name.py` with the actual name of your Python file.)

## Contributing

Feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

[Choose a license and add information here.  MIT License is a common choice for open-source projects.]