# Basic Python Script Example

The simplest possible Aperture integration - a command-line chatbot that builds user understanding.

## Features

- 💬 Interactive command-line chat
- 🧠 Automatic user intelligence extraction
- 📊 `insights` command to see what Aperture knows
- 🔗 Direct links to "Why this response?" pages
- 🚀 Less than 100 lines of code

## Setup

1. **Install dependencies:**

```bash
pip install aperture-ai python-dotenv
```

2. **Set environment variables:**

Create `.env` file:

```bash
APERTURE_API_KEY=your_aperture_key
OPENAI_API_KEY=your_openai_key
```

3. **Run the script:**

```bash
python chatbot.py
```

## Commands

- **Normal chat**: Just type your message
- **`insights`**: See what Aperture has learned about you
- **`quit`**: Exit the chatbot

## Example Session

```
🤖 Welcome to Aperture-powered Chatbot!
==================================================
Enter your name: Alice

Hello Alice! Let's chat.

You: I'm trying to deploy my app on AWS but keep running into errors