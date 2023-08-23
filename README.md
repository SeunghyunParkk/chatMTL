# chatMTL

An Interactive ChatBot Interface to Engage with MTL Blog Content

This script provides a user-friendly interface allowing users to dive deep into the content sourced from the MTL Blog website. It leverages the Llama model to curate responses inspired by the latest news articles from a range of categories.

## Features

- **Interactive GUI**: A user-friendly interface for seamless interactions.
- **Dynamic Content Access**: Directly scrapes and processes content from MTL Blog.
- **State-of-the-Art Conversational Model**: Leverages the Llama model for responsive and relevant chat outputs.
- **CSV Logging**: Records user interactions, feedback, and session details in a CSV format.

## Installation

1. Ensure you have Python 3.x installed.
2. Clone this repository:
   ```bash
   git clone [[https://github.com/hellohumansss/chatMTL.git](https://github.com/hellohumansss/chatMTL)]
   cd [your-repo-directory]
3. Install the necessary packages:
    ```bash
   pip install -r requirements.txt
4. Execute the script:
    ```bash
   python mtlblog_chatbot.py

The CSV file is created (if not already present) consisting of the session data of the chat,
which can be used to run analytics on top.

