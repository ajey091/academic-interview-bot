import sys
import json
import random
import time
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                           QWidget, QTextEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
import sounddevice as sd
import numpy as np
import soundfile as sf
import openai
from scipy.io.wavfile import write
import pygame
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os  # Import the os module


# Load API keys from environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check if API keys are set
if not GOOGLE_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY and OPENAI_API_KEY environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)
openai.api_key = OPENAI_API_KEY

class InterviewBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic Interview Bot - Child Language Development")
        self.setGeometry(100, 100, 800, 600)

        pygame.mixer.init()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.current_question_index = -1
        self.responses = []
        self.recording = False
        self.interview_completed = False
        self.questions = []

        self.status_label = QLabel("Click 'Start Interview' to begin")
        self.transcript_area = QTextEdit()
        self.transcript_area.setReadOnly(True)

        self.start_button = QPushButton("Start Interview")
        self.record_button = QPushButton("Record Response")
        self.record_button.setEnabled(False)
        self.stop_button = QPushButton("Stop Interview")
        self.stop_button.setEnabled(False)

        layout.addWidget(self.status_label)
        layout.addWidget(self.transcript_area)
        layout.addWidget(self.start_button)
        layout.addWidget(self.record_button)
        layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start_interview)
        self.record_button.clicked.connect(self.toggle_recording)
        self.stop_button.clicked.connect(self.complete_interview)

        self.feedback_criteria = {
            "research_clarity": "Clarity in explaining research program",
            "theoretical_knowledge": "Understanding of theoretical frameworks",
            "methodology": "Research methodology expertise",
            "future_vision": "Vision for future research",
            "teaching_ability": "Teaching and mentoring potential",
            "funding_awareness": "Grant funding awareness",
            "problem_solving": "Problem-solving ability",
            "communication": "Communication skills"
        }

    def start_interview(self):
        if self.current_question_index == -1:
            self.current_question_index = 0
            self.questions.append(self.generate_initial_question())
            self.start_button.setText("Next Question")
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.ask_current_question()
        elif not self.interview_completed:
            self.current_question_index += 1
            self.ask_current_question()


    def generate_initial_question(self):
        prompt = """
        Generate a single, initial interview question for a tenure-track faculty position in child language development at Stanford University.
        The person you're interviewing is currently a tenure-track faculty member at a different R1 research institute (University of California, Los Angeles),
        who works with deaf children and children with cochlear implants.
        They also do computational work on language development, specifically computational modeling of language acquisition.

        The question should be broad enough to start the conversation and assess one or more of the following:

        1. Research program clarity and potential
        2. Theoretical knowledge
        3. Methodological expertise
        4. Future research vision
        5. General excitement about the position

        Return only the question, without any extra text.
        Start with a greeting, and the initial question can be relatively simple and
        straightforward, but the follow-up questions should be more polished.
        Also ask deep, open-ended and non-basic questions eventually.
        """
        model = genai.GenerativeModel('gemini-1.5-flash-002')  # Corrected model name
        response = model.generate_content(prompt)
        return response.text.strip()


    def generate_followup_question(self, previous_response):
        prompt = f"""
        Generate a follow-up interview question for a tenure-track faculty position in child language development,
        based on the candidate's previous response:

        Previous Response: {previous_response}

        The question should delve deeper into the candidate's response and assess aspects like research, theory, methodology, or future plans.  Return only the question, without any extra text.
        """
        model = genai.GenerativeModel('gemini-1.5-flash-002')
        response = model.generate_content(prompt)
        return response.text.strip()


    def ask_current_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.status_label.setText(f"Question {self.current_question_index + 1}")
            self.transcript_area.append(f"\nInterviewer: {question}\n")
            self.text_to_speech(question)


    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.setText("Stop Recording")

        self.audio_data = []
        self.sample_rate = 44100

        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_data.extend(indata.copy())

        self.stream = sd.InputStream(callback=audio_callback,
                                   channels=1,
                                   samplerate=self.sample_rate)
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        self.record_button.setText("Record Response")

        self.stream.stop()
        self.stream.close()

        audio_data = np.concatenate(self.audio_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response_{timestamp}.wav"
        write(filename, self.sample_rate, audio_data)

        response_text = self.transcribe_audio(filename)
        self.responses.append(response_text)
        self.transcript_area.append(f"You: {response_text}\n")

        followup = self.generate_followup_question(response_text)
        self.questions.append(followup)

    def text_to_speech(self, text):
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            speed=1.25  # Adjust speed as desired
        )
        speech_file_path = Path("speech.mp3")
        response.stream_to_file(speech_file_path)
        pygame.mixer.music.load(speech_file_path)
        pygame.mixer.music.play()


    def transcribe_audio(self, audio_file):
        with open(audio_file, "rb") as audio:
             transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        return transcript.text


    def complete_interview(self):
        self.interview_completed = True
        self.start_button.setEnabled(False)
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        feedback = self.generate_feedback()

        self.transcript_area.append("\n=== Interview Feedback ===\n")
        self.transcript_area.append(feedback)

        self.save_interview_data()
        self.save_interview_data_pdf()
        self.status_label.setText("Interview Completed. Feedback generated.")


    def generate_feedback(self):
        per_question_feedback = ""
        for i, (question, response) in enumerate(zip(self.questions, self.responses)):
            prompt = f"""
            Analyze the following question and response from an academic job interview for a tenure-track faculty position in child language development:

            Question: {question}
            Response: {response}

            Provide:
            1. A concise critique of the response, highlighting strengths and weaknesses.
            2. A potential alternative response that addresses the weaknesses and improves the overall answer.

            Return the feedback in the following format:

            Critique: [Critique text here]
            Alternative Response: [Alternative response text here]
            """
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            response = model.generate_content(prompt)
            per_question_feedback += f"Question {i+1}: {question}\n{response.text}\n\n"

        all_responses = " ".join(self.responses)
        summary_prompt = f"""
        Provide a summary and overall feedback on the following academic job interview for a tenure-track faculty position in child language development.  Consider these criteria:

        {self.feedback_criteria}

        All responses given by the candidate: {all_responses}

        Provide an overall assessment, addressing strengths, weaknesses, and areas for improvement. Be concise.
        """
        model = genai.GenerativeModel('gemini-1.5-flash-002')
        summary_response = model.generate_content(summary_prompt)

        return f"{per_question_feedback}\n--- Overall Summary Feedback ---\n{summary_response.text}"


    def save_interview_data(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_transcript_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write(self.transcript_area.toPlainText())

    def save_interview_data_pdf(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_transcript_{timestamp}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        transcript_text = self.transcript_area.toPlainText()
        for line in transcript_text.split('\n'):
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 12))

        doc.build(story)


def main():
    app = QApplication(sys.argv)
    window = InterviewBot()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()