"""
Modules:
    requests: Engages in HTTP requests to fetch content from the MTL Blog.
    BeautifulSoup: Enables the extraction of web content via web scraping techniques.
    llama_cpp: Incorporates the Llama model to drive the chatbot's conversational abilities.
    tkinter, ttk, scrolledtext: Constructs the GUI for the chatbot interface.
    re: Assists in text cleansing through regex operations.
    threading: Facilitates parallel execution, enhancing response fetching.
    datetime: Captures and manages time-related information.
    csv: Manages CSV operations for data storage.
    uuid: Generates unique session IDs for user interactions.

Classes:
    ChatbotInterface: Orchestrates the primary user-chatbot interaction dynamics.

Functions: - scrape_text(url: str) -> str: Extracts raw content from the designated MTL Blog URL. - clean_text(text:
str) -> str: Refines the extracted text to emphasize relevant data. - save_to_txt(text: str, category: str) -> None:
Archives the cleaned text into categorized files. - load_from_txt(category: str) -> str: Recovers the categorized
text content for reference. - chat_with_llm(content: str, question: str) -> str: Engages the Llama model to offer a
tailored response to user inquiries.

Workflow: On launch, the script collects the latest news stories from predefined MTL Blog categories, processes the
content, and saves them as text files. Subsequently, the chatbot interface comes alive, offering users the chance to
raise queries pertaining to the saved news content.

Notes:
    - It's crucial to set the Llama model path correctly.
    - Ensure all required packages are installed.
    - Ensure appropriate permissions for file operations are in place.
    - The chatbot is equipped to handle both rule-driven and open-ended conversations.
"""

# Importing required modules and libraries
import requests
from bs4 import BeautifulSoup
from llama_cpp import Llama
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.font import Font
import re
import threading
from datetime import date, datetime
import csv
import uuid

# Initializing the LLM model for chatbot intelligence
LLM = Llama(model_path="./llama-2-7b-chat.ggmlv3.q8_0.bin", n_ctx=2000)


# Function to scrape raw text content from the given MTL Blog URL
def scrape_text(target_url):
    response = requests.get(target_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    result_text = soup.get_text()
    return result_text


# Function to clean and process the scraped content, retaining only relevant information
def clean_text(raw_text):
    # Remove content before and including "Montreal | Laval | Québec City"
    raw_text = raw_text.split("Montreal | Laval | Québec City", 1)[-1]

    # Remove content after and including "Keep readingShow"
    raw_text = raw_text.rsplit("Keep readingShow", 1)[0]

    # Remove all non-alphanumeric characters except spaces
    raw_text = re.sub(r'[^A-Za-z0-9\s]', '', raw_text)

    # Limit to the first 1000 words
    raw_text = ' '.join(raw_text.split()[:1000])

    # Normalize whitespace
    raw_text = ' '.join(raw_text.split())

    return raw_text


# Function to save the cleaned text content into a text file categorized by its type
def save_to_txt(content, cat_type):
    with open(f'mtlblog_{cat_type}.txt', 'w', encoding='utf-8') as f:
        f.write(content)


# Function to load text content from a file based on the specified category
def load_from_txt(cat_type):
    with open(f'mtlblog_{cat_type}.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    return content


# Function to interact with the Llama model and get a relevant response based on user query and content
def chat_with_llm(content, question):
    prompt = (f"System: As of {today}, based on the news content: '{content}', "
              f"formulate a short response (less than 100 words) to the User query pertaining to said content: "
              f"'{question}'. "
              f"Assistant: ")

    output = LLM(prompt, max_tokens=0)
    assistant_reply = output["choices"][0]["text"]

    return assistant_reply


# The main Chatbot Interface class that handles user-bot interactions
class ChatbotInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set a window size
        self.geometry("700x500")
        self.title("chatMTL")

        # Colors and Styles for window and elements
        main_bg = "#f5f5f5"  # light grayish
        chat_bg = "#ffffff"  # white
        button_bg = "#4CAF50"  # light green

        # Define the fonts and colors for user and bot messages
        self.user_font = Font(family="Helvetica", size=14)
        self.bot_font = Font(family="Helvetica", size=14)
        self.user_color = '#FF5733'  # light red
        self.bot_color = '#3333FF'  # light blue

        self.configure(bg=main_bg)  # Set the background color of the window

        # Chat Area
        self.chat_area = scrolledtext.ScrolledText(self, bg=chat_bg, fg='black', wrap=tk.WORD, height=15)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # User Input Area
        input_frame = tk.Frame(self, bg=main_bg)
        input_frame.pack(padx=10, pady=10, fill=tk.BOTH)

        self.message_field = ttk.Entry(input_frame)
        self.message_field.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.X, expand=True)

        style = ttk.Style()
        style.configure("TButton", background=button_bg, font=("Helvetica", 12, "bold"))
        style.map("TButton", background=[('active', "#3A8F40")])

        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message, style="TButton")
        self.send_button.pack(padx=10, pady=10, side=tk.RIGHT)

        self.message_field.bind('<Return>', self.send_message)

        # Initializing the states
        self.data = ''
        self.start_time = None
        self.threads = []
        self.selected_category = None
        self.session_id = str(uuid.uuid4())
        self.user_message_count = 0
        self.bot_message_count = 0
        self.user_name = None
        self.user_dob = None
        self.state = 'ask_name'
        self.feedback = None
        self.detailed_feedback = None
        self.greeting_message()

    # Event handler function for the 'Send' button. Sends user message to the bot.
    def send_message(self, event):
        message = self.message_field.get()
        if message:
            self.user_message_count += 1
            if not self.start_time:
                self.start_time = datetime.now()
            self.display_message("User", message, self.user_color, self.user_font)
            self.message_field.delete(0, 'end')

            # Start a new thread to fetch the bots response
            thread = threading.Thread(target=self.fetch_bot_response, args=(message,))
            self.threads.append(thread)
            thread.start()

    # Function to fetch the bots response based on user's message
    def fetch_bot_response(self, message):
        response = self.get_response(message)
        self.display_message("Bot", response, self.bot_color, self.bot_font)

    # Function to display messages (both user and bot) in the chat window
    def display_message(self, sender, message, color, font):
        self.chat_area.configure(state='normal')
        tag_name = f"{sender.lower()}_tag"
        if tag_name not in self.chat_area.tag_names():
            # Create a new tag for this sender
            self.chat_area.tag_configure(tag_name, foreground=color)

        # Insert the message with the appropriate tag
        self.chat_area.insert(tk.END, f"{sender}: {message}\n", (tag_name, font))

        # Disable editing of the chat area
        self.chat_area.configure(state='disabled')

    # Displays the initial greeting message when the chatbot interface starts
    def greeting_message(self):
        response = "Bonjour! 🍁 Welcome to chatMTL, your digital gateway to all things Montreal.\nMay I have your name?"
        self.bot_message_count += 1
        self.display_message("Bot", response, self.bot_color, self.bot_font)

    # Prompts user to select a category of interest
    def prompt_category(self):
        categories_list = '\n'.join([f"{i + 1}. {cat.replace('-', ' ').title()}" for i, cat in enumerate(categories)])
        response = f"Montreal is bustling with stories! Which alley of MTL Blog would you like to explore today?\n{categories_list}"
        self.bot_message_count += 1
        self.display_message("Bot", response, self.bot_color, self.bot_font)

    # Function to handle different states of conversation and generate appropriate bot responses
    def get_response(self, message):
        response = ''
        if self.state == 'ask_name':
            self.user_name = message
            self.state = 'ask_dob'
            self.bot_message_count += 1
            response = f"Thanks, {self.user_name}. Montreal loves a celebration! When's yours? (DOB in YYYY-MM-DD):"
        elif self.state == 'ask_dob':
            try:
                # Check if the entered date is in the correct format
                datetime.strptime(message, '%Y-%m-%d')
                self.user_dob = message
                self.state = 'category_prompt'
                self.prompt_category()
                return 'Choose a category:'
            except ValueError:
                # If not, prompt the user to enter the date of birth again
                self.bot_message_count += 1
                response = "Oops! Seems we got our dates jumbled. Montreal loves precision!\nCould you share your birthday again in YYYY-MM-DD format?"
        if self.state == 'category_prompt':
            try:
                selected_index = int(message) - 1
                if 0 <= selected_index < len(categories):
                    selected_category = categories[selected_index]
                    self.data = load_from_txt(selected_category)
                    self.state = 'question_prompt'
                    self.selected_category = selected_category.replace('-', ' ').title()
                    self.bot_message_count += 1
                    response = f"Ready to explore Montreal's {self.selected_category} scene? 🍁\nAsk away, and I'll guide you through!"
                else:
                    response = "Oops! Seems like a little detour. 🌆\nPlease choose a number that matches our categories list."
                    self.bot_message_count += 1
            except ValueError:
                response = "Whoops! That's not on our Montreal map. 🗺\nPlease enter a valid number for the category you're interested in."
                self.bot_message_count += 1
        elif self.state == 'question_prompt':
            response = chat_with_llm(self.data, message)
            response += '\n'
            response += 'Got more Montreal curiosities? 🍁 Let me know how I can assist further!'
            self.state = 'more_help_prompt'
            self.bot_message_count += 1
        elif self.state == 'more_help_prompt':
            if "yes" in message.lower():
                response = f"Anything else about {self.selected_category} in Montreal that piques your interest? 🌆 Share it with me!"
                self.state = 'question_prompt'
                self.bot_message_count += 1
            elif "no" in message.lower():
                response = "It's been great chatting with you about Montreal! 😊 Was our conversation helpful?"
                self.state = 'capture_feedback'
                self.bot_message_count += 1
            else:
                response = "Kindly respond with a simple 'yes' or 'no'."
                self.bot_message_count += 1
        elif self.state == 'capture_feedback':
            feedback = message.lower()
            if feedback in ['yes', 'no']:
                self.feedback = feedback
                if feedback == 'yes':
                    self.state = 'capture_details'
                    self.bot_message_count += 1
                    response = "Thank you for the positive feedback! Can you please tell me more about what you did like?"
                else:
                    self.state = 'capture_details'
                    self.bot_message_count += 1
                    response = "Regretfully, I missed the mark this time. Can you please tell me where I can improve?"
            else:
                self.bot_message_count += 1
                response = "Kindly respond with a simple 'yes' or 'no' for feedback."
        elif self.state == 'capture_details':
            self.detailed_feedback = message.lower()
            end_time = datetime.now()
            session_duration = str(end_time - self.start_time)
            self.save_to_csv(session_duration)
            response = 'Thank you for the feedback. Your interactions help me continuously improve and ' \
                       'provide a better experience. I deeply appreciate your time and feedback.'
            self.state = 'exit'
        elif self.state == 'exit':
            current_thread = threading.current_thread()
            for thread in self.threads:
                if thread is not current_thread:
                    thread.join()  # Wait for all threads to complete, excluding the current thread
            self.destroy()

        return response

    # Function to export session data, feedback, and other details to a CSV file
    def save_to_csv(self, session_duration):
        filename = "session_data.csv"
        fields = ['session_id', 'timestamp', 'user_name', 'user_dob', 'session_duration', 'selected_category',
                  'user_msg_count', 'bot_msg_count',
                  'feedback', 'detailed_feedback']

        # Check if the file exists. If not, write headers.
        file_exists = True
        try:
            with open(filename, 'r'):
                pass
        except FileNotFoundError:
            file_exists = False

        with open(filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fields)

            if not file_exists:
                writer.writeheader()  # Write header only once when the file is created

            writer.writerow({
                'session_id': self.session_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_name': self.user_name,
                'user_dob': self.user_dob,
                'session_duration': session_duration,
                'selected_category': self.selected_category if self.selected_category else "N/A",
                'user_msg_count': self.user_message_count,
                'bot_msg_count': self.bot_message_count,
                'feedback': 'good' if self.feedback == 'yes' else 'bad',
                'detailed_feedback': self.detailed_feedback
            })


# Main execution thread
if __name__ == "__main__":
    # Fetch today's date for reference in conversations
    today = date.today().strftime('%Y-%m-%d')

    # Scrape the latest news stories for all categories and save them for reference
    categories = ['news', 'eat-drink', 'things-to-do', 'travel', 'sports', 'lifestyle',
                  'money', 'deals', 'real-estate']
    for category in categories:
        url = f'https://www.mtlblog.com/{category}'
        text = scrape_text(url)
        save_to_txt(clean_text(text), category)

    # Start the chatbot user interface for user interactions
    app = ChatbotInterface()
    app.mainloop()
