from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from gtts import gTTS
import base64
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lexivoice - Free Text-to-Speech Tool</title>
    <style>
        /* Basic styling (same as before, with spinner styles added) */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            background: #f4f4f9;
            color: #333;
        }
        header {
            background: #007bff;
            color: #fff;
            padding: 1em 0;
            text-align: center;
            position: relative;
        }
        header h1 {
            margin-bottom: 0.5em;
        }
        nav ul {
            list-style: none;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }
        nav ul li {
            margin: 0 1em;
        }
        nav ul li a {
            color: #fff;
            text-decoration: none;
            font-weight: bold;
        }
        .ad-banner {
            margin: 10px auto;
            width: 90%;
            max-width: 800px;
            text-align: center;
        }
        section {
            padding: 2em;
            margin: 1em auto;
            background: #fff;
            width: 90%;
            max-width: 800px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h2 {
            margin-bottom: 1em;
            color: #007bff;
        }
        textarea {
            width: 100%;
            height: 100px;
            margin-bottom: 5px;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        audio {
            width: 100%;
            margin-top: 1em;
        }
        .contact-form label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .contact-form input,
        .contact-form textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .contact-form button {
            background-color: #28a745;
        }
        footer {
            background: #333;
            color: #fff;
            text-align: center;
            padding: 1em 0;
            margin-top: 2em;
            position: relative;
        }
        footer a {
            color: #fff;
            text-decoration: underline;
        }
        .note {
            font-size: 0.9em;
            color: #555;
            margin-bottom: 5px;
        }
        /* Loading Spinner Styles */
        .loading-spinner {
            display: none; /* Hidden by default */
            width: 30px;
            height: 30px;
            border: 3px solid rgba(0, 0, 0, 0.3);
            border-top: 3px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px auto; /* Center above button */
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .character-count {
            font-size: 0.9em;
            color: #777;
            text-align: right;
            margin-bottom: 5px;
        }
        .error-message {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>

<header>
    <h1>Lexivoice</h1>
    <nav>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#how-to-use">How to Use</a></li>
            <li><a href="#faq">FAQ</a></li>
            <li><a href="#use-cases">Use Cases</a></li>
            <li><a href="#about-us">About Us</a></li>
            <li><a href="#contact">Contact Support</a></li>
        </ul>
    </nav>
    <!-- Advertisement Banner in Header -->
    <div class="ad-banner">
        <!-- Replace the following with your actual ad code -->
        <script async src="https://example-ad-network.com/ads.js"></script>
        <ins class="adsbyexample"
             style="display:block; text-align:center;"
             data-ad-client="ca-example"
             data-ad-slot="1234567890"
             data-ad-format="auto"></ins>
        <script>
             (adsbyexample = window.adsbyexample || []).push({});
        </script>
    </div>
</header>

<section id="home">
    <h2>Text to Speech Tool</h2>
    <textarea id="text-input" placeholder="Type your text here..." maxlength="1000"></textarea>
    <p class="character-count"><span id="char-count">0</span> / 1000 characters</p> 
    <p class="note">Note: Free version allows a maximum of 1000 characters. Please contact us for unlimited characters and ads free experience.</p>
    
    <!-- Advertisement Banner in Home Section -->
    <div class="ad-banner">
        <!-- Replace the following with your actual ad code -->
        <script async src="https://example-ad-network.com/ads.js"></script>
        <ins class="adsbyexample"
             style="display:block; text-align:center;"
             data-ad-client="ca-example"
             data-ad-slot="0987654321"
             data-ad-format="auto"></ins>
        <script>
             (adsbyexample = window.adsbyexample || []).push({});
        </script>
    </div>

    <label for="language-select">Select Accent:</label>
    <select id="language-select">
        <option value="en">English (US)</option>
        <option value="en">English (UK)</option>
        <option value="es">Spanish (Spain)</option>
        <option value="fr">French (France)</option>
        <option value="de">German (Germany)</option>
        <option value="it">Italian (Italy)</option>
    </select>

    <div class="loading-spinner" id="loading-spinner"></div>
    <button onclick="speakAndDownload()">Speak & Generate MP3</button>
    <audio id="audio" controls></audio>
    <br>
    <a id="download-link" href="#" download="speech.mp3" style="display:none;">Download MP3</a>
    <p id="error-message" class="error-message" style="display:none;"></p>
</section>

<section id="how-to-use">
    <h2>How to Use</h2>
    <p>
        1. Type or paste your desired text in the text box above (max 350 letters).<br>
        2. Select your desired language/voice from the dropdown.<br>
        3. Click the "Speak & Generate MP3" button to convert your text into spoken audio.<br>
        4. Listen to the audio using the built-in player and click the "Download MP3" link to save it.
    </p>
</section>

<section id="faq">
    <h2>Frequently Asked Questions</h2>
    <h3>Q: Is Lexivoice free?</h3>
    <p>A: Yes, Lexivoice is completely free and supported by ads.</p>
    <h3>Q: How does the text-to-speech functionality work?</h3>
    <p>A: We use a secure backend process to convert text to MP3 audio, which is then played in your browser.</p>
    <h3>Q: Is there a character limit?</h3>
    <p>A: Yes, the free version allows a maximum of 350 letters.</p>
    <h3>Q: Can I use this tool for commercial purposes?</h3>
    <p>A: Lexivoice is free for personal use. Please contact us for commercial inquiries.</p>
</section>

<section id="use-cases">
    <h2>Use Cases</h2>
    <ul>
        <li><strong>Accessibility:</strong> Helping individuals with visual impairments or reading difficulties.</li>
        <li><strong>Language Learning:</strong> Allowing users to listen to correct pronunciation and improve listening skills.</li>
        <li><strong>Content Creation:</strong> Generating voice-overs for videos, podcasts, or presentations.</li>
        <li><strong>Personal Productivity:</strong> Converting text into audio for on-the-go listening.</li>
        <li><strong>Educational Purposes:</strong> Assisting in teaching languages and public speaking practice.</li>
    </ul>
</section>

<section id="about-us">
    <h2>About Us</h2>
    <p>
        Lexivoice is a passion project developed to empower users by converting text into clear, engaging audio. Our mission is to make information accessible and engaging for everyone—from students and educators to content creators and individuals who prefer auditory learning. By combining cutting-edge text-to-speech technology with a user-friendly interface, we strive to provide a tool that enhances learning, creativity, and accessibility.
    </p>
</section>

<section id="contact">
    <h2>Contact Support</h2>
    <form class="contact-form" onsubmit="return sendContactForm(event)">
        <label for="name">Name:</label>
        <input type="text" id="name" required>
        <label for="email">Email:</label>
        <input type="email" id="email" required>
        <label for="subject">Subject:</label>
        <input type="text" id="subject" required>
        <label for="message">Message:</label>
        <textarea id="message" rows="5" required></textarea>
        <button type="submit">Send Message</button>
    </form>
    <p id="contact-response"></p>
</section>

<footer>
    <!-- Advertisement Banner in Footer -->
    <div class="ad-banner">
        <!-- Replace the following with your actual ad code -->
        <script async src="https://example-ad-network.com/ads.js"></script>
        <ins class="adsbyexample"
             style="display:block; text-align:center;"
             data-ad-client="ca-example"
             data-ad-slot="1122334455"
             data-ad-format="auto"></ins>
        <script>
             (adsbyexample = window.adsbyexample || []).push({});
        </script>
    </div>
    <p>Powered by <a href="https://lexivoice.com" target="_blank">lexivoice.com</a></p>
</footer>

<script>
    function speakAndDownload() {
        let text = document.getElementById("text-input").value.trim();
        let language = document.getElementById("language-select").value; // Get selected language
        const loadingSpinner = document.getElementById("loading-spinner");
        const audioPlayer = document.getElementById("audio");
        const downloadLink = document.getElementById("download-link");
        const errorMessageDisplay = document.getElementById("error-message");

        errorMessageDisplay.style.display = "none"; // Hide error message initially

        if (!text) {
            alert("Please enter some text!");
            return;
        }

        loadingSpinner.style.display = "block"; // Show loading spinner
        downloadLink.style.display = "none"; // Hide download link while loading
        audioPlayer.src = ""; // Clear previous audio source

        fetch('/api/getSpeech', { // Relative URL: same origin as the served page
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text, language: language })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingSpinner.style.display = "none"; // Hide loading spinner after success
            if (data.audioContent) {
                const audioSource = `data:audio/mp3;base64,${data.audioContent}`;
                audioPlayer.src = audioSource;
                audioPlayer.play();
                downloadLink.href = audioSource;
                downloadLink.style.display = "inline-block";
            } else if (data.error) {
                errorMessageDisplay.textContent = "API Error: " + data.error;
                errorMessageDisplay.style.display = "block";
            } else {
                errorMessageDisplay.textContent = "Unknown error occurred.";
                errorMessageDisplay.style.display = "block";
            }
        })
        .catch(error => {
            loadingSpinner.style.display = "none"; // Hide loading spinner on error
            errorMessageDisplay.textContent = "Network error. Please try again.";
            errorMessageDisplay.style.display = "block";
            console.error("Fetch error:", error);
        });
    }

    function sendContactForm(event) {
        event.preventDefault();
        document.getElementById("contact-response").innerText = "Thank you for reaching out! We will get back to you soon.";
        document.getElementById("name").value = "";
        document.getElementById("email").value = "";
        document.getElementById("subject").value = "";
        document.getElementById("message").value = "";
        return false;
    }

    // Character Counter Functionality
    const textInput = document.getElementById('text-input');
    const charCountSpan = document.getElementById('char-count');

    textInput.addEventListener('input', function() {
        const textLength = this.value.length;
        charCountSpan.textContent = textLength;

        if (textLength > 1000) {
            this.value = this.value.substring(0, 1000); // Trim the text to 1000 chars
            charCountSpan.textContent = 1000; // Update counter to max limit
        }
    });
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_CONTENT)

@app.route("/api/getSpeech", methods=["POST"])
def get_speech():
    data = request.get_json()
    text = data.get('text')
    language = data.get('language', 'en')  # default to English if not provided

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Use gTTS to convert text to speech
        tts = gTTS(text, lang=language)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_bytes = buf.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return jsonify({'audioContent': audio_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)