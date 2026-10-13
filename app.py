"""
NLP Text Cleaner - IDE edition (VS Code / diff-viewer look)

Run:       streamlit run nlp_text_cleaner_ide.py
Optional:  pip install emoji      -> enables "Convert to text" for emojis
Optional:  copy config.toml into a .streamlit/ folder next to this file (dark theme)
"""
import html
import json
import re
import string
import difflib
from collections import Counter

import nltk
import streamlit as st
import contractions
from nltk.corpus import stopwords

try:
    import emoji as emoji_lib
    HAS_EMOJI_LIB = hasattr(emoji_lib, "replace_emoji")
except ImportError:
    emoji_lib = None
    HAS_EMOJI_LIB = False

st.set_page_config(
    page_title="NLP Cleaner · IDE",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------
# Styling (VS Code Dark+ palette, JetBrains Mono / Fira Code)
# ---------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Fira+Code:wght@400;500&display=swap');

:root{
  --bg:#1e1e1e; --panel:#252526; --bar:#333333; --line:#3c3c3c; --text:#d4d4d4; --dim:#858585;
  --blue:#569cd6; --lblue:#9cdcfe; --teal:#4ec9b0; --yellow:#dcdcaa; --orange:#ce9178;
  --green:#b5cea8; --purple:#c586c0; --red:#f44747; --accent:#007acc;
  --mono:'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
.stApp,[data-testid="stAppViewContainer"]{background:var(--bg);color:var(--text);}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1180px;}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp textarea,.stApp button,.stApp [data-baseweb="tab"]{font-family:var(--mono);}
.stApp label,.stApp label p{color:var(--text);}

/* title bar + hero */
.titlebar{display:flex;align-items:center;gap:8px;background:var(--bar);padding:9px 14px;
  border-radius:10px 10px 0 0;border:1px solid var(--line);border-bottom:none;
  font-family:var(--mono);font-size:12.5px;color:var(--dim);}
.dot{width:12px;height:12px;border-radius:50%;display:inline-block;}
.dot.r{background:#ff5f56}.dot.y{background:#ffbd2e}.dot.g{background:#27c93f}
.titlebar .title{margin-left:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.hero{background:linear-gradient(135deg,#1f2a44 0%,#2b1f44 55%,#1e3a3a 100%);
  border:1px solid var(--line);border-radius:0 0 10px 10px;padding:22px 24px;margin-bottom:18px;font-family:var(--mono);}
.hero .l1{font-size:clamp(15px,3.6vw,26px);font-weight:700;line-height:1.5;}
.hero .l2{font-size:clamp(11px,2.6vw,14px);margin-top:6px;}
.kw{color:var(--purple)}.fn{color:var(--yellow)}.par{color:var(--lblue)}.ty{color:var(--teal)}
.cm{color:#6a9955}.sx{color:var(--orange)}.nm{color:var(--green)}.op{color:var(--blue)}

.sec{font-family:var(--mono);font-size:13px;color:#6a9955;margin:6px 0 6px;}
.pill{display:inline-block;padding:3px 10px;margin:3px 5px 3px 0;border-radius:6px;background:#2d2d30;
  border:1px solid var(--line);color:var(--yellow);font-family:var(--mono);font-size:12px;}

/* stat cards */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:14px 0 18px;}
.stat{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--c);
  border-radius:8px;padding:12px 14px;font-family:var(--mono);}
.stat .k{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.08em;}
.stat .v{font-size:24px;font-weight:700;color:var(--c);line-height:1.3;}
.stat .sd{font-size:12px;color:var(--dim);}

/* diff panes */
.diff-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.pane{background:#1e1e1e;border:1px solid var(--line);border-radius:8px;overflow:hidden;min-width:0;}
.pane-head{display:flex;justify-content:space-between;align-items:center;gap:8px;background:var(--bar);
  padding:7px 12px;font-family:var(--mono);font-size:12px;color:var(--text);border-bottom:1px solid var(--line);}
.pane-head .tag{padding:1px 8px;border-radius:999px;font-size:11px;white-space:nowrap;}
.tg-del{background:rgba(244,71,71,.18);color:#ff8f8f;}
.tg-add{background:rgba(78,201,176,.18);color:var(--teal);}
.pane-body{padding:8px 0;max-height:420px;overflow:auto;font-family:var(--mono);font-size:13px;
  line-height:1.65;font-variant-ligatures:none;}
.row{display:flex;}
.row:hover{background:rgba(255,255,255,.04);}
.ln{flex:0 0 42px;text-align:right;padding-right:12px;color:#5a5a5a;user-select:none;}
.code{flex:1;min-width:0;white-space:pre-wrap;word-break:break-word;padding-right:12px;color:var(--text);tab-size:4;}
.ws{color:#4b4b4b;}
.df-del{background:rgba(244,71,71,.28);color:#ffb3b3;border-radius:2px;}
.df-add{background:rgba(78,201,176,.25);color:#b5f5e4;border-radius:2px;}
.df-del .ws,.df-add .ws{color:inherit;opacity:.7;}
.t-num{color:var(--green)}.t-pun{color:var(--yellow)}.t-emo{color:var(--orange)}

/* chips */
.chip{display:inline-block;padding:3px 10px;margin:3px 4px 3px 0;border-radius:6px;font-family:var(--mono);
  font-size:12.5px;border:1px solid;}
.c-word{color:var(--lblue);background:rgba(86,156,214,.12);border-color:rgba(86,156,214,.4);}
.c-stop{color:#ff8f8f;background:rgba(244,71,71,.12);border-color:rgba(244,71,71,.4);text-decoration:line-through;}
.c-num{color:var(--green);background:rgba(181,206,168,.12);border-color:rgba(181,206,168,.4);}
.c-emo{color:var(--orange);background:rgba(206,145,120,.14);border-color:rgba(206,145,120,.4);}
.c-url{color:var(--purple);background:rgba(197,134,192,.12);border-color:rgba(197,134,192,.4);}

/* frequency bars */
.fq{display:flex;align-items:center;gap:10px;margin:7px 0;font-family:var(--mono);font-size:13px;}
.fq .w{flex:0 0 38%;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.fq .bar{flex:1;height:10px;background:#2d2d30;border-radius:5px;overflow:hidden;}
.fq .bar i{display:block;height:100%;border-radius:5px;}
.fq .n{flex:0 0 28px;text-align:right;color:var(--dim);}

/* status bar */
.statusbar{display:flex;flex-wrap:wrap;gap:6px 18px;background:var(--accent);color:#fff;padding:6px 14px;
  border-radius:6px;font-family:var(--mono);font-size:12px;margin-top:18px;}

/* streamlit widgets */
.stTextArea textarea{background:#1e1e1e !important;color:var(--orange) !important;border:1px solid var(--line) !important;
  font-family:var(--mono) !important;font-size:14px !important;line-height:1.6;font-variant-ligatures:none;}
.stTextArea textarea:focus{border-color:var(--accent) !important;box-shadow:0 0 0 1px var(--accent) !important;}
[data-testid="stExpander"]{background:var(--panel);border:1px solid var(--line);border-radius:8px;}
[data-testid="stExpander"] summary{font-family:var(--mono);color:var(--yellow);}
button[data-baseweb="tab"]{color:#969696;}
button[data-baseweb="tab"][aria-selected="true"]{color:#fff;}
div[data-baseweb="tab-highlight"]{background:var(--accent) !important;}
div[data-baseweb="tab-list"]{gap:4px;overflow-x:auto;}
.stButton>button{width:100%;border-radius:6px;font-weight:600;border:1px solid var(--line);background:#2d2d30;color:var(--text);}
.stButton>button:hover{border-color:var(--accent);color:#fff;}
.stDownloadButton>button{width:100%;background:var(--accent);color:#fff;border:none;border-radius:6px;font-weight:600;}

/* mobile */
@media (max-width:768px){
  .block-container{padding:.6rem .6rem 2rem;}
  .diff-grid{grid-template-columns:1fr;}
  .stats{grid-template-columns:repeat(2,1fr);}
  .stat .v{font-size:20px;}
  .pane-body{font-size:12px;max-height:300px;}
  .ln{flex-basis:34px;padding-right:8px;}
  .hero{padding:16px;}
  .titlebar .title{font-size:11px;}
  .fq .w{flex-basis:45%;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------
# NLP helpers
# ---------------------------------------------------------------
@st.cache_resource
def load_stopwords():
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


STOP_WORDS = load_stopwords()

EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"   # pictographs, emoticons, transport, symbols, extended-A
    "\U0001F1E6-\U0001F1FF"   # flags
    "\u2600-\u27BF"           # misc symbols + dingbats
    "\u2300-\u23FF"           # misc technical (watch, hourglass, alarm)
    "\u2B00-\u2BFF"           # stars, arrows
    "\u25AA-\u25FE"           # geometric shapes
    "\u200d\ufe0f\u20e3"      # joiner, variation selector, keycap
    "]+"
)
# ASCII punctuation + common typographic punctuation (emojis are NOT touched)
PUNCT_RE = re.compile(r"[!-/:-@\[-`{-~\u2018\u2019\u201c\u201d\u2013\u2014\u2026\u00a1\u00bf\u00ab\u00bb]")
HTML_RE = re.compile(r"<!--.*?-->|</?[a-zA-Z][^>]*>", re.DOTALL)
URL_RE = re.compile(r"(https?://\S+|www\.\S+)")
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")

EMOJI_OPTIONS = ["Keep", "Remove"] + (["Convert to text"] if HAS_EMOJI_LIB else [])


def emoji_to_text(text):
    return emoji_lib.replace_emoji(
        text,
        replace=lambda chars, data: " " + data["en"].strip(":").replace("_", " ") + " ",
    )


def clean_text(text, o):
    """Apply selected steps. Order matters:
    HTML / URLs / emails / emojis first (their characters are punctuation-like),
    contractions before punctuation (keeps the apostrophe until expanded)."""
    if o["html"]:
        text = HTML_RE.sub(" ", text)
    if o["urls"]:
        text = URL_RE.sub(" ", text)
    if o["emails"]:
        text = EMAIL_RE.sub(" ", text)
    if o["emoji"] == "Remove":
        text = EMOJI_RE.sub(" ", text)
    elif o["emoji"] == "Convert to text" and HAS_EMOJI_LIB:
        text = emoji_to_text(text)
    if o["lower"]:
        text = text.lower()
    if o["contr"]:
        text = text.replace("\u2019", "'").replace("\u2018", "'")
        text = contractions.fix(text)
    if o["nums"]:
        text = re.sub(r"\d+", " ", text)
    if o["punct"]:
        text = PUNCT_RE.sub(" ", text)
    if o["ws"]:
        text = re.sub(r"\s+", " ", text).strip()
    return text


def is_stop_word(w):
    return w.strip(string.punctuation).lower() in STOP_WORDS


def split_stopwords(text):
    words = text.split()
    flags = [is_stop_word(w) for w in words]
    filtered = [w for w, f in zip(words, flags) if not f]
    return words, flags, filtered


# ---------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------
def esc(s):
    """Escape for HTML and protect against Streamlit markdown ($math$, :shortcodes:)."""
    return html.escape(s).replace("$", "&#36;").replace(":", "&#58;")


TOKEN_RE = re.compile(r"\n|[^\S\n]+|\w+|[^\w\s]")


def token_html(tok, changed, kind, show_ws):
    cls = ""
    if changed:
        cls = "df-del" if kind == "del" else "df-add"
    if tok.isspace():
        if show_ws:
            txt = "".join("·" if c == " " else "→" if c == "\t" else "" for c in tok)
            inner = f'<span class="ws">{txt}</span>'
        else:
            inner = html.escape(tok)
    else:
        inner = esc(tok)
        if not changed:
            if EMOJI_RE.fullmatch(tok):
                cls = "t-emo"
            elif tok.isdigit():
                cls = "t-num"
            elif not any(c.isalnum() or c == "_" for c in tok):
                cls = "t-pun"
    return f'<span class="{cls}">{inner}</span>' if cls else inner


def render_pane(tokens, marks, kind, show_ws):
    lines = [[]]
    for tok, ch in zip(tokens, marks):
        if tok == "\n":
            if show_ws:
                mark = '<span class="ws">↵</span>'
                if ch:
                    mark = f'<span class="{"df-del" if kind == "del" else "df-add"}">{mark}</span>'
                lines[-1].append(mark)
            lines.append([])
        else:
            lines[-1].append(token_html(tok, ch, kind, show_ws))
    rows = "".join(
        f'<div class="row"><span class="ln">{i}</span><span class="code">{"".join(p) or "&#8203;"}</span></div>'
        for i, p in enumerate(lines, 1)
    )
    return rows


def build_diff(original, final, show_ws):
    a, b = TOKEN_RE.findall(original), TOKEN_RE.findall(final)
    ma, mb = [False] * len(a), [False] * len(b)
    too_big = len(a) + len(b) > 6000
    if not too_big:
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("delete", "replace"):
                for i in range(i1, i2):
                    ma[i] = True
            if tag in ("insert", "replace"):
                for j in range(j1, j2):
                    mb[j] = True
    removed = sum(1 for t, m in zip(a, ma) if m and not t.isspace())
    added = sum(1 for t, m in zip(b, mb) if m and not t.isspace())

    def pane(name, tag_cls, tag_txt, body):
        return (
            f'<div class="pane"><div class="pane-head"><span>📄 {name}</span>'
            f'<span class="tag {tag_cls}">{tag_txt}</span></div>'
            f'<div class="pane-body">{body}</div></div>'
        )

    left = pane("original.txt", "tg-del", f"−{removed} tokens", render_pane(a, ma, "del", show_ws))
    right = pane("cleaned.txt", "tg-add", f"+{added} tokens", render_pane(b, mb, "add", show_ws))
    return f'<div class="diff-grid">{left}{right}</div>', too_big


def chip_class(w, is_stop):
    if is_stop:
        return "c-stop"
    if EMOJI_RE.fullmatch(w):
        return "c-emo"
    if re.fullmatch(r"\d+", w):
        return "c-num"
    if re.match(r"(https?://|www\.)", w) or re.fullmatch(r"\S+@\S+\.\S+", w):
        return "c-url"
    return "c-word"


MAX_CHIPS = 400


def chips_html(words, flags=None):
    if not words:
        return "<i style='color:#858585'>no tokens</i>"
    flags = flags or [False] * len(words)
    out = "".join(
        f'<span class="chip {chip_class(w, f)}">{esc(w)}</span>'
        for w, f in list(zip(words, flags))[:MAX_CHIPS]
    )
    if len(words) > MAX_CHIPS:
        out += f'<span class="pill">… +{len(words) - MAX_CHIPS} more</span>'
    return out


# ---------------------------------------------------------------
# State: options + sample text
# ---------------------------------------------------------------
SAMPLE = (
    "<p>Hello World!! 😀 I can't believe it's 2026 already 🎉🔥.</p>\n"
    "<p>Visit https://example.com or www.test.org,\n"
    "or mail me at someone@gmail.com for 100% FREE tips 💯 ...</p>"
)
BOOL_KEYS = [
    "opt_html", "opt_urls", "opt_emails", "opt_lower", "opt_contr",
    "opt_nums", "opt_punct", "opt_ws", "opt_stop",
]
for k in BOOL_KEYS:
    st.session_state.setdefault(k, True)
st.session_state.setdefault("opt_emoji", "Remove")
st.session_state.setdefault("opt_vis", True)
st.session_state.setdefault("user_text", SAMPLE)


def set_all(val):
    for k in BOOL_KEYS:
        st.session_state[k] = val
    st.session_state["opt_emoji"] = "Remove" if val else "Keep"


def load_sample():
    st.session_state["user_text"] = SAMPLE


def clear_text():
    st.session_state["user_text"] = ""


# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown(
    '<div class="titlebar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>'
    '<span class="title">nlp_cleaner.py — NLP Text Cleaner</span></div>'
    '<div class="hero">'
    '<div class="l1"><span class="kw">def</span> <span class="fn">clean_text</span>'
    '(<span class="par">raw</span>: <span class="ty">str</span>) <span class="op">-&gt;</span> '
    '<span class="ty">str</span>:</div>'
    '<div class="l2"><span class="cm"># toggle steps, paste text, inspect the diff live</span></div>'
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Settings panel (in the main page so it works on mobile too)
# ---------------------------------------------------------------
with st.expander("⚙  settings.json", expanded=True):
    b1, b2, _b3 = st.columns([1, 1, 2])
    b1.button("✔ Select all", on_click=set_all, args=(True,))
    b2.button("✖ Clear all", on_click=set_all, args=(False,))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="sec">// noise</div>', unsafe_allow_html=True)
        st.toggle("Remove HTML tags", key="opt_html")
        st.toggle("Remove URLs", key="opt_urls")
        st.toggle("Remove email addresses", key="opt_emails")
        st.radio("Emojis 😀", EMOJI_OPTIONS, key="opt_emoji", horizontal=True)
        if not HAS_EMOJI_LIB:
            st.caption("pip install emoji → unlocks “Convert to text”")
    with c2:
        st.markdown('<div class="sec">// normalize</div>', unsafe_allow_html=True)
        st.toggle("Lowercase", key="opt_lower")
        st.toggle("Expand contractions (don't → do not)", key="opt_contr")
        st.toggle("Remove numbers", key="opt_nums")
        st.toggle("Remove punctuation", key="opt_punct")
    with c3:
        st.markdown('<div class="sec">// cleanup + view</div>', unsafe_allow_html=True)
        st.toggle("Collapse extra whitespace", key="opt_ws")
        st.toggle("Remove stopwords", key="opt_stop")
        st.toggle("Show invisibles (· → ↵)", key="opt_vis")

# ---------------------------------------------------------------
# Input
# ---------------------------------------------------------------
st.markdown('<div class="sec">// input.txt   (Ctrl+Enter to apply)</div>', unsafe_allow_html=True)
user_input = st.text_area(
    "input",
    key="user_text",
    height=170,
    label_visibility="collapsed",
    placeholder="Paste text with HTML, URLs, emails, emojis, numbers, punctuation...",
)
i1, i2, _i3 = st.columns([1, 1, 2])
i1.button("✨ Load sample", on_click=load_sample)
i2.button("🗑 Clear", on_click=clear_text)

if not user_input.strip():
    st.info("Type or paste some text above (or click **Load sample**).")
    st.stop()

# ---------------------------------------------------------------
# Processing
# ---------------------------------------------------------------
opts = {
    "html": st.session_state["opt_html"],
    "urls": st.session_state["opt_urls"],
    "emails": st.session_state["opt_emails"],
    "emoji": st.session_state["opt_emoji"],
    "lower": st.session_state["opt_lower"],
    "contr": st.session_state["opt_contr"],
    "nums": st.session_state["opt_nums"],
    "punct": st.session_state["opt_punct"],
    "ws": st.session_state["opt_ws"],
}
do_stop = st.session_state["opt_stop"]
show_ws = st.session_state["opt_vis"]

cleaned = clean_text(user_input, opts)
words, flags, filtered = split_stopwords(cleaned)
final_words = filtered if do_stop else words
final_text = " ".join(filtered) if do_stop else cleaned
stops_removed = sum(flags) if do_stop else 0

# applied-steps pills
steps = []
if opts["html"]:
    steps.append("strip_html()")
if opts["urls"]:
    steps.append("remove_urls()")
if opts["emails"]:
    steps.append("remove_emails()")
if opts["emoji"] == "Remove":
    steps.append("remove_emojis()")
elif opts["emoji"] == "Convert to text":
    steps.append("emojis_to_text()")
if opts["lower"]:
    steps.append("lower()")
if opts["contr"]:
    steps.append("expand_contractions()")
if opts["nums"]:
    steps.append("remove_numbers()")
if opts["punct"]:
    steps.append("remove_punct()")
if opts["ws"]:
    steps.append("collapse_whitespace()")
if do_stop:
    steps.append("remove_stopwords()")

st.markdown('<div class="sec">// pipeline</div>', unsafe_allow_html=True)
st.markdown(
    "".join(f'<span class="pill">{s}</span>' for s in steps)
    or '<span class="pill">passthrough (no steps enabled)</span>',
    unsafe_allow_html=True,
)

# stat cards
oc, fc = len(user_input), len(final_text)
ow, fw = len(user_input.split()), len(final_words)
reduction = (1 - fc / max(oc, 1)) * 100
stat_cards = [
    ("characters", fc, f"{fc - oc:+d} from {oc}", "#569cd6"),
    ("words", fw, f"{fw - ow:+d} from {ow}", "#4ec9b0"),
    ("stopwords removed", stops_removed, f"of {len(words)} tokens", "#ce9178"),
    ("size change", f"{reduction:.0f}%", "smaller" if reduction >= 0 else "larger", "#c586c0"),
]
st.markdown(
    '<div class="stats">'
    + "".join(
        f'<div class="stat" style="--c:{c}"><div class="k">{k}</div><div class="v">{v}</div>'
        f'<div class="sd">{d}</div></div>'
        for k, v, d, c in stat_cards
    )
    + "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Output tabs
# ---------------------------------------------------------------
tab_diff, tab_tok, tab_freq, tab_json = st.tabs(["⇄ Diff", "🔤 Tokens", "📊 Frequency", "{ } Export"])

with tab_diff:
    diff_html, too_big = build_diff(user_input, final_text, show_ws)
    st.markdown(
        '<span class="pill" style="color:#ff8f8f">■ removed / changed</span>'
        '<span class="pill" style="color:#4ec9b0">■ added / changed</span>'
        '<span class="pill">· space &nbsp; → tab &nbsp; ↵ newline</span>',
        unsafe_allow_html=True,
    )
    if too_big:
        st.caption("Text is very large, so diff highlighting was skipped to keep the app fast.")
    st.markdown(diff_html, unsafe_allow_html=True)

with tab_tok:
    st.markdown('<div class="sec">// tokens before stopword removal</div>', unsafe_allow_html=True)
    st.markdown(chips_html(words, flags if do_stop else None), unsafe_allow_html=True)
    st.markdown('<div class="sec">// tokens after stopword removal</div>', unsafe_allow_html=True)
    if do_stop:
        st.markdown(chips_html(filtered), unsafe_allow_html=True)
    else:
        st.info("Stopword removal is switched off in settings.json.")
    st.markdown(
        '<span class="chip c-word">word</span><span class="chip c-stop">stopword</span>'
        '<span class="chip c-num">number</span><span class="chip c-emo">emoji</span>'
        '<span class="chip c-url">url / email</span>',
        unsafe_allow_html=True,
    )

with tab_freq:
    st.markdown('<div class="sec">// top tokens</div>', unsafe_allow_html=True)
    top = Counter(final_words).most_common(8)
    if not top:
        st.info("No tokens left to count.")
    else:
        palette = ["#569cd6", "#4ec9b0", "#dcdcaa", "#ce9178", "#c586c0", "#b5cea8", "#9cdcfe", "#d7ba7d"]
        peak = top[0][1]
        st.markdown(
            "".join(
                f'<div class="fq"><span class="w">{esc(w)}</span>'
                f'<div class="bar"><i style="width:{n / peak * 100:.0f}%;background:{palette[i % 8]}"></i></div>'
                f'<span class="n">{n}</span></div>'
                for i, (w, n) in enumerate(top)
            ),
            unsafe_allow_html=True,
        )

with tab_json:
    payload = {
        "original": user_input,
        "cleaned": final_text,
        "tokens": final_words,
        "steps": steps,
        "stats": {"chars_before": oc, "chars_after": fc, "words_before": ow, "words_after": fw},
    }
    json_str = json.dumps(payload, indent=2, ensure_ascii=False)
    st.code(json_str, language="json")
    d1, d2 = st.columns(2)
    d1.download_button("⬇ cleaned.txt", final_text, file_name="cleaned.txt", mime="text/plain")
    d2.download_button("⬇ result.json", json_str, file_name="result.json", mime="application/json")

# status bar
st.markdown(
    '<div class="statusbar">'
    "<span>⎇ main</span>"
    f"<span>✔ {len(steps)} steps</span>"
    f"<span>Ln {final_text.count(chr(10)) + 1}, Col {fc}</span>"
    "<span>UTF-8</span><span>Python</span>"
    "</div>",
    unsafe_allow_html=True,
)
