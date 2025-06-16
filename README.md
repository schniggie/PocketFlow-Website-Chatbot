<h1 align="center">Build an AI Chatbot for Your Website</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
 <a href="https://discord.gg/hUHHE9Sa6T">
    <img src="https://img.shields.io/discord/1346833819172601907?logo=discord&style=flat">
</a>
> *Tired of customers leaving your website without finding the answers they need? This tutorial shows you how to build an intelligent AI chatbot that crawls your website content and provides instant, accurate answers to visitor questions.*

<p align="center">
  <a href="https://github.com/The-Pocket/PocketFlow" target="_blank">
    <img 
      src="./assets/banner.png" width="800"
    />
  </a>
</p>

This is a tutorial project for [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework. The chatbot intelligently explores multiple web pages, makes decisions about which content is relevant, and provides comprehensive answers based on the discovered information.

- **🎉 Online Service Available!** Try our free service at [https://askthispage.com/](https://askthispage.com/) and build an AI chatbot for your website in just 5 minutes!

- **📺 Technical deep dive coming soon!** Subscribe to [my YouTube channel](https://www.youtube.com/@ZacharyLLM?sub_confirmation=1) to get notified when it's released.

## How It Works

1. **Run the Server**: Follow the Getting Started guide below to run the chatbot locally for testing, then deploy it to production. Or simply use our deployed service at [https://askthispage.com/](https://askthispage.com/)

2. **Enter Your Website URL**: Input the URL of your website to preview how the chatbot will look and behave with your content

   <p align="center">
     <img src="./assets/step2.png" width="600" alt="Step 2: Enter Website URL">
   </p>

3. **Try the Chatbot**: Test the AI chatbot's responses. We also provide JavaScript code to easily embed the chatbot into your website

   <p align="center">
     <img src="./assets/step3.png" width="600" alt="Step 3: Try the Chatbot">
   </p>

   Our AI chatbot relies on web crawling (see [`web_crawler.py`](utils/web_crawler.py)) to understand your content. Please note these limitations:
   - Pages with complex JavaScript rendering may not be fully accessible
   - Pages requiring human verification (like CAPTCHAs) cannot be processed
   - For authenticated pages, you'll need to implement custom authentication logic in [`chatbot.js`](static/chatbot.js) and [`server.py`](server.py)

## 🚀 Getting Started

1. **Install Packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Browser for Crawler:**
   The `utils` directory contains a web crawler that depends on Playwright. To ensure all utilities can run, install its browser dependencies:
   ```bash
   python -m playwright install --with-deps chromium
   ```

3. **Set API Key:**
   Set the environment variable for your Google Gemini API key.
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   *(Replace `"your-api-key-here"` with your actual key)*

4. **Verify API Key (Optional):**
   Run a quick check using the utility script. If successful, it will print a short joke.
   ```bash
   python utils/call_llm.py
   ```
   *(Note: This requires a valid API key to be set.)*

5. **Run the Support Bot (Command Line):**
   ```bash
   python main.py <start_url1> [start_url2] ... "<question>" [instruction]
   ```

   **Examples:**
   ```bash
   # Basic usage with single URL
   python main.py https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro "What is the pricing for Gemini 2.5 pro?"
   
   # Multiple URLs with custom instruction
   python main.py https://github.com/scikit-learn/scikit-learn https://scikit-learn.org/stable/ "How do I install this?" "Focus on technical documentation and setup guides"
   
   # Specific instructions for different use cases
   python main.py https://azure.microsoft.com/en-us/ "What are your pricing plans?" "Look for pricing information and compare different tiers"
   
   python main.py https://github.com/the-pocket/PocketFlow "How does PocketFlow work?" "Prioritize README and documentation files"
   ```

6. **Run the Web Interface (Optional):**
   Start the web server to use the interactive browser-based interface.
   ```bash
   python server.py
   ```
   Then, open your web browser and navigate to `http://localhost:8000`. You can enter URLs and your question in the form to see the bot work in real-time.

## Architecture

The AI chatbot uses an intelligent agent-based architecture with three main components:

- **CrawlAndExtract**: Batch processes multiple URLs to extract content and discover links
- **AgentDecision**: Makes intelligent decisions about whether to answer or explore more pages
- **DraftAnswer**: Generates comprehensive answers based on collected knowledge

```mermaid
flowchart LR
    A[CrawlAndExtract] --> B{AgentDecision}
    B -- answer --> C[DraftAnswer]
    B -- explore --> A
    C --> D[End: Provide Answer]
    
    style D fill:#dff,stroke:#333,stroke-width:2px
```

For detailed architecture information, see the [design documentation](docs/design.md) and [implementation](nodes.py).
