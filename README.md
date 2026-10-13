# 🧠 NLP Text Cleaner

A **VS Code-styled** text preprocessing web app built with **Streamlit**. Paste raw text, switch cleaning steps on or off, and see exactly what changed in a live side-by-side diff.

🔗 **Live demo:** [[https://YOUR-APP-NAME.streamlit.app](https://nlp-text-cleaner.streamlit.app/)]

<!-- Add a screenshot: save it as screenshots/diff-view.png and uncomment the line below -->
<!-- ![App screenshot](screenshots/diff-view.png) -->

---

## ✨ Features

| Category | Options |
|---|---|
| **Noise removal** | HTML tags, URLs, email addresses, emojis (remove or convert to text) |
| **Normalization** | Lowercasing, contraction expansion (`don't` → `do not`), number removal, punctuation removal |
| **Cleanup** | Extra whitespace collapsing, stopword removal (NLTK English stopwords) |

**Interface**
- ⇄ **Diff viewer** – original vs. cleaned text with line numbers, red/green change highlighting and visible whitespace (`·` space, `→` tab, `↵` newline)
- 🔤 **Token view** – colour-coded chips for words, stopwords, numbers, emojis and URLs/emails
- 📊 **Frequency chart** – top tokens after cleaning
- `{ }` **Export** – download the result as `.txt` or `.json`
- 📱 **Responsive** – panes stack on mobile, settings live in the main page (no hidden sidebar)
- 🎨 VS Code Dark+ colour palette with JetBrains Mono / Fira Code fonts
- ⚡ **Live processing** – results update as soon as you toggle an option

---

## 🔄 Cleaning pipeline

Order matters, so the steps always run in this sequence:

```
HTML tags → URLs → Emails → Emojis → Lowercase → Contractions
→ Numbers → Punctuation → Whitespace → Stopwords
```

Why this order?
- HTML, URLs and emails contain characters like `< > : / @`. If punctuation were removed first, these patterns could no longer be matched.
- Contractions are expanded **before** punctuation removal, otherwise `don't` would become `dont` instead of `do not`.
- Punctuation removal leaves emojis untouched, so the emoji option stays independent.

---

## 🗂️ Project structure

```
Text_cleaner/
├── .streamlit/
│   └── config.toml        # dark theme settings
├── app.py                 # Streamlit application
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🚀 Run locally

```bash
# 1. Clone the repository
git clone https://github.com/Janavarshini-Ganesan/nlp-text-cleaner.git
cd nlp-text-cleaner

# 2. (Optional) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

The NLTK stopword list is downloaded automatically on the first run.

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app**, select the repository and set the main file to `app.py`.
4. Click **Deploy**.

---

## 🛠️ Tech stack

- **Python 3**
- **Streamlit** – web interface
- **NLTK** – English stopwords
- **contractions** – contraction expansion
- **emoji** – emoji-to-text conversion
- **re / difflib** – regex cleaning and diff generation
- **Custom CSS** – VS Code-style theme and responsive layout

---

## 📌 Example

**Input**
```html
<p>Hello World!! 😀 I can't believe it's 2026 already 🎉🔥.</p>
Visit https://example.com or mail me at someone@gmail.com for 100% FREE tips 💯
```

**Output** (all options enabled)
```
hello world believe already visit mail free tips
```

---

## 🔮 Possible improvements

- Stemming and lemmatization options
- Multi-language stopword support
- Custom stopword list upload
- Batch cleaning for CSV files

---

## 👩‍💻 Author

**Janavarshini G**
[GitHub](https://github.com/Janavarshini-Ganesan) · [LinkedIn](https://linkedin.com/in/janavarshini-ganesan)

---

⭐ If you found this useful, consider giving the repo a star!
