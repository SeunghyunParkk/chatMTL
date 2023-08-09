import requests
from bs4 import BeautifulSoup
from llama_cpp import Llama
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.font import Font
import re
import threading

# Load the LLM model
LLM = Llama(model_path="C:/Users/ethan/iCloudDrive/llama-2-7b-chat.ggmlv3.q8_0.bin", n_ctx=3000)


# Scrape news text from MTL Blog
def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text


def clean_text(text):
    # Remove everything before and including "Montreal | Laval | Québec City"
    substring_start = "Montreal | Laval | Québec City"
    start_index = text.find(substring_start)
    text = text[start_index + len(substring_start):]

    # Remove everything after and including "Keep readingShow"
    substring_end = "Keep readingShow"
    end_index = text.rfind(substring_end)
    text = text[:end_index]

    # Remove all special characters
    text = re.sub(r'\W', ' ', text)

    # Split into words
    words = text.split()

    # Take the first 700 words
    words = words[:700]

    # Join back into a string
    text = ' '.join(words)

    text = re.sub(r'[^A-Za-z0-9\s]', '', text)  # Retains spaces between words
    text = ' '.join(text.split())
    return text


# Save the data to a text file
def save_to_txt(text, category):
    with open(f'mtlblog_{category}.txt', 'w', encoding='utf-8') as f:
        f.write(text)


# Load the text data
def load_from_txt(category):
    with open(f'mtlblog_{category}.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def chat_with_llm(content, question):
    prompt = (f"System: Based on the news content: '{content}', "
              f"formulate a short response to the User query pertaining to said content: '{question}'. "
              f"Assistant: ")

    output = LLM(prompt, max_tokens=0)
    assistant_reply = output["choices"][0]["text"]

    return assistant_reply


class ChatbotInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.configure(bg='black')  # Set the background color of the window
        self.title("chatMTL")

        # Define the fonts and colors for user and bot messages
        self.user_font = Font(family="Helvetica", size=14)
        self.bot_font = Font(family="Helvetica", size=14)
        self.user_color = 'red'
        self.bot_color = 'white'

        self.chat_area = scrolledtext.ScrolledText(self, bg='black', fg='white', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10)

        self.message_field = ttk.Entry(self)
        self.message_field.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.X, expand=True)

        style = ttk.Style()
        style.configure("TButton", foreground="black", background="black")
        self.send_button = ttk.Button(self, text="Send", command=self.send_message, style="TButton")
        self.send_button.pack(padx=10, pady=10, side=tk.RIGHT)

        self.message_field.bind('<Return>', self.send_message)

        self.conversational_response = 0

    def send_message(self, event=None):
        message = self.message_field.get()
        if message:
            self.display_message("User", message, self.user_color, self.user_font)
            self.message_field.delete(0, 'end')

            # Start a new thread to fetch the bot's response
            threading.Thread(target=self.fetch_bot_response, args=(message,)).start()

    def fetch_bot_response(self, message):
        response = self.get_response(message)
        self.display_message("Bot", response, self.bot_color, self.bot_font)

    def display_message(self, sender, message, color, font):
        self.chat_area.configure(state='normal')
        tag_name = f"{sender.lower()}_tag"
        if not tag_name in self.chat_area.tag_names():
            # Create a new tag for this sender
            self.chat_area.tag_configure(tag_name, foreground=color)

        # Insert the message with the appropriate tag
        self.chat_area.insert(tk.END, f"{sender}: {message}\n", (tag_name, font))

        # Disable editing of the chat area
        self.chat_area.configure(state='disabled')

    def get_response(self, message):
        # Conversational responses with LLM
        if self.conversational_response == 1:
            response = chat_with_llm(self.data, message)
            self.conversational_response = 0
            return response

        # Rule-based responses
        else:
            if "hello" in message.lower():
                return "Hello! How can I assist you today?"
            elif "how are you" in message.lower():
                return "I'm a bot, so I don't have feelings, but thank you for asking!"
            elif "news" in message.lower():
                self.data = load_from_txt('news')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent news. What do you want to know?"
            elif "eat" in message.lower() or "drink" in message.lower() or "food" in message.lower():
                self.data = load_from_txt('eat-drink')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent food and drink news. What do you want to know?"
            elif "things to do" in message.lower() or "events" in message.lower() or "entertainment" in message.lower():
                self.data = load_from_txt('things-to-do')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent 'things to do' news. What do you want to know?"
            elif "travel" in message.lower():
                self.data = load_from_txt('travel')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent travel news. What do you want to know?"
            elif "sports" in message.lower():
                self.data = load_from_txt('sports')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent sports news. What do you want to know?"
            elif "lifestyle" in message.lower():
                self.data = load_from_txt('lifestyle')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent lifestyle news. What do you want to know?"
            elif "money" in message.lower():
                self.data = load_from_txt('money')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent money news. What do you want to know?"
            elif "deals" in message.lower():
                self.data = load_from_txt('deals')
                self.conversational_response = 1
                return "Sure, I can provide information based on the latest deals. What do you want to know?"
            elif "real-estate" in message.lower():
                self.data = load_from_txt('real-estate')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent real estate news. What do you want to know?"
            elif "conversations" in message.lower():
                self.data = load_from_txt('conversations')
                self.conversational_response = 1
                return "Sure, I can provide information based on recent conversations. What do you want to know?"
            else:
                return ("Please choose a category first: news, eat/drink, things to do, travel, sports, lifestyle, "
                        "money, deals, real-estate, or conversations.")


if __name__ == "__main__":
    # Scrape the most recent news stories from each category
    categories = ['news', 'eat-drink', 'things-to-do', 'travel', 'sports', 'lifestyle',
                  'money', 'deals', 'real-estate', 'conversations']
    for category in categories:
        url = f'https://www.mtlblog.com/{category}'
        text = scrape_text(url)
        save_to_txt(clean_text(text), category)

    app = ChatbotInterface()
    app.mainloop()
