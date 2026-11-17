
import json
import requests
import streamlit as st


# ==================================================
# CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:8000/api/blog"
AUTH_API_URL = "http://127.0.0.1:8000/api/auth"

st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide"
)


# ==================================================
# SESSION STATE
# ==================================================

DEFAULTS = {
    # Authentication
    "access_token": None,
    "authenticated": False,
    "user": None,
    "auth_mode": "Login",
    "auth_error": None,
    "auth_success": None,
    "thread_id": None,

    # Human review
    "review_plan": None,
    "review_submitted": False,
    "edit_mode": False,

    # Workflow progress
    "completed_stages": [],
    "current_stage": None,

    # Blog content
    "draft_blog": None,
    "generated_blog": None,

    # Draft and critique status
    "sections_prepared": False,
    "draft_preparing": False,
    "critique_started": False,
    "critique_score": None,
    "critique_completed": False,

    # Application status
    "error": None,
    "generation_started": False,
    "workflow_waiting_for_review": False,
    "router_needs_research": None,
    "researched_urls": [],

    # Individual section generation progress
    "section_tasks": [],
    "section_progress": {},

    "scroll_to_progress": False,

    # Markdown Assistant
    "chat_documents": [],
    "selected_chat_file_id": None,
    "chat_messages": [],
    "chat_documents_loaded": False,
    "chat_error": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* =========================================
   LOGGED-IN USER HEADER
========================================= */

/* =========================================
   LOGGED-IN EMAIL - TOP LEFT
========================================= */

div[data-testid="stColumn"]:has(a[href^="mailto:"]) {
    position: fixed !important;
    top: 15px !important;
    left: 5px !important;
    width: auto !important;
    z-index: 99999 !important;
}

div[data-testid="stColumn"]:has(a[href^="mailto:"])
div[data-testid="stMarkdownContainer"] {
    text-align: left !important;
}


/* =========================================
   LOGOUT BUTTON - TOP RIGHT
========================================= */

/* Position only the Logout container */
.st-key-logout_header {
    position: fixed !important;
    top: 15px !important;
    right: 15px !important;
    width: auto !important;
    z-index: 99999 !important;
}

/* Logout button */
.st-key-logout_header div[data-testid="stButton"] {
    width: auto !important;
}

.st-key-logout_header button {
    width: auto !important;
    min-height: 40px !important;
    padding: 8px 18px !important;
    margin: 0 !important;
}

/* Hide Streamlit top navigation bar */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Hide toolbar */
div[data-testid="stToolbar"] {
    display: none !important;
}

/* Hide decoration bar */
div[data-testid="stDecoration"] {
    display: none !important;
}

/* Main container */
.block-container {
    max-width: 1400px;
    width: 95%;
    padding-top: 2rem !important;
    padding-bottom: 3rem;
}

/* Background */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #FFFBF5 !important;
}

/* Main title */
.stApp h1 {
    color: #7C2D12 !important;
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 8px;
}

/* Subtitle */
[data-testid="stCaptionContainer"] {
    text-align: center;
    color: #57534E !important;
    font-size: 16px;
    margin-bottom: 25px;
}

/* Section headings */
.stApp h3 {
    color: #7C2D12 !important;
    font-size: 23px;
    font-weight: 700;
}

/* Normal text */
.stApp p,
.stApp label,
.stApp .stMarkdown {
    color: #292524;
}

/* Text input */
div[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #D6BBA9 !important;
    border-radius: 8px;
    height: 48px;
    font-size: 15px;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #78716C !important;
    opacity: 1;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #EA580C !important;
    box-shadow: 0 0 0 1px #EA580C !important;
}

/* Text area */
div[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #D6BBA9 !important;
    border-radius: 8px;
}

/* Number input */
div[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* Buttons */
div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button {
    width: 100%;
    min-height: 48px;
    background-color: #C2410C !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
}

div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover {
    background-color: #9A3412 !important;
    color: #FFFFFF !important;
}

/* Disabled buttons */
div[data-testid="stButton"] button:disabled {
    background-color: #D6A17F !important;
    color: #FFFFFF !important;
    opacity: 0.8;
}

/* Dividers */
hr {
    border-color: #E7D8CB !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #E7D8CB;
    border-radius: 8px;
}

/* Content boxes */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #E7D8CB;
    border-radius: 10px;
}

/* =========================================
   GENERATION PROGRESS DASHBOARD
========================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border: 1px solid #E7D8CB;
    border-radius: 12px;
    padding: 12px;
}

/* Progress section headings */
.stApp h2 {
    color: #7C2D12 !important;
    font-weight: 750;
}

/* Status messages */
div[data-testid="stAlert"] {
    border-radius: 9px;
    border: 1px solid #E7D8CB;
}

/* Success status */
div[data-testid="stAlert"][kind="success"] {
    background-color: #F0FDF4;
}

/* Information status */
div[data-testid="stAlert"][kind="info"] {
    background-color: #FFF7ED;
}

/* Warning status */
div[data-testid="stAlert"][kind="warning"] {
    background-color: #FFFBEB;
}

/* Section progress text */
div[data-testid="stCaptionContainer"] {
    color: #78716C;
}

/* Expanders */
div[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #E7D8CB;
    border-radius: 10px;
}

/* Subtle divider */
hr {
    margin-top: 15px;
    margin-bottom: 15px;
    border-color: #E7D8CB !important;
}

/* Floating popover container */
div[data-testid="stPopover"] {
    position: fixed !important;
    left: 1300px !important;
    bottom: 24px !important;
    right: -30px !important;
    top: auto !important;
    z-index: 99999 !important;
}

/* Actual popover button */
div[data-testid="stPopover"] button {
    width: 60px !important;
    height: 60px !important;
    min-width: 60px !important;
    min-height: 60px !important;
    max-width: 60px !important;
    max-height: 60px !important;
    aspect-ratio: 1 / 1 !important;
    border-radius: 50% !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* Center the button content */
div[data-testid="stPopover"] button > div {
    justify-content: center !important;
    align-items: center !important;
}

/* Make the floating chatbot trigger look like a circular launcher */
div[data-testid="stPopover"] > button {
    width: 58px !important;
    height: 58px !important;
    min-height: 58px !important;
    border-radius: 50% !important;
    background: #C2410C !important;
    color: #FFFFFF !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 4px 16px rgba(124, 45, 18, 0.28) !important;
    font-size: 25px !important;
    padding: 0 !important;
}

div[data-testid="stPopover"] > button:hover {
    background: #9A3412 !important;
    transform: translateY(-2px);
}

/* Chat panel */
div[data-testid="stPopoverBody"] {
    left: -100px !important;
    width: 800px !important;
    min-width: 800px !important;
    max-width: 90vw !important;

    height: 600px !important;
    min-height: 600px !important;
    max-height: 85vh !important;

    overflow-y: auto !important;

    background: #FFFBF5 !important;
    border: 1px solid #E7D8CB !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 28px rgba(41, 37, 36, 0.18) !important;
}

.markdown-assistant-heading {
    color: #7C2D12;
    font-size: 19px;
    font-weight: 750;
    margin-bottom: 2px;
}
.markdown-assistant-subtitle {
    color: #78716C;
    font-size: 12px;
    margin-bottom: 12px;
}

/* Force chatbot circle background */
div[data-testid="stPopover"] button,
div[data-testid="stPopover"] button:focus,
div[data-testid="stPopover"] button:active {
    background-color: #7C2D12 !important;
    background: #7C2D12 !important;
    color: #FFFFFF !important;
    border-radius: 50% !important;
}

/* Remove dark background from inner elements */
div[data-testid="stPopover"] button > div,
div[data-testid="stPopover"] button span {
    background: transparent !important;
    color: #FFFFFF !important;
}

/* Hover */
div[data-testid="stPopover"] button:hover {
    background: #9A3412 !important;
}

/* Chatbot answer text */
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"],
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] li,
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] span {
    color: #292524 !important;
}

/* Chatbot answer headings */
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] h1,
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] h2,
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] h3 {
    color: #7C2D12 !important;
}

/* Target the popover trigger button */
div[data-testid="stPopover"] button[kind="secondary"] {
    width: 60px !important;
    height: 60px !important;
    min-width: 60px !important;
    min-height: 60px !important;
    max-width: 60px !important;
    max-height: 60px !important;

    padding: 0 !important;
    border-radius: 50% !important;
}

/* Increase robot emoji size */
div[data-testid="stPopover"] button[kind="secondary"] p {
    font-size: 50px !important;
    color: white !important;
    line-height: 1 !important;
    margin: 0 !important;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# AUTHENTICATION
# ==================================================

def api_headers():
    """Return the bearer token header for protected backend endpoints."""
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def clear_authentication():
    """Clear the local JWT and user-specific UI state on logout."""
    st.session_state.access_token = None
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.auth_error = None
    st.session_state.auth_success = None

    # Clear user-specific chatbot and workflow state from this browser session.
    st.session_state.chat_documents = []
    st.session_state.selected_chat_file_id = None
    st.session_state.chat_messages = []
    st.session_state.chat_documents_loaded = False
    st.session_state.chat_error = None
    st.session_state.thread_id = None
    st.session_state.review_plan = None
    st.session_state.generated_blog = None
    st.session_state.draft_blog = None


def login_user(email, password):
    """Authenticate against POST /api/auth/login and save the JWT."""
    response = requests.post(
        f"{AUTH_API_URL}/login",
        json={"email": email.strip(), "password": password},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    token = payload.get("access_token")
    if not token:
        raise ValueError("Login response did not contain an access_token.")

    st.session_state.access_token = token
    st.session_state.authenticated = True
    st.session_state.user = payload.get("user") or {"email": email.strip()}
    st.session_state.auth_error = None
    st.session_state.auth_success = None


def show_authentication_page():
    """Render signup/login and stop the app until authentication succeeds."""
    st.markdown(
        "<div style='text-align:center; margin-top:7vh;'>"
        "<h1 style='color:#7C2D12;'>✍️ AI Blog Generator</h1>"
        "<p style='color:#57534E;'>Sign in to create and manage your blogs.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    _, auth_col, _ = st.columns([1, 1.25, 1])
    with auth_col:
        st.markdown("### Welcome")

        selected_mode = st.radio(
            "Choose an option",
            ["Login", "Sign up"],
            horizontal=True,
            key="auth_mode_selector",
            label_visibility="collapsed",
        )
        st.session_state.auth_mode = selected_mode

        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
        if st.session_state.auth_success:
            st.success(st.session_state.auth_success)

        if selected_mode == "Login":
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button(
                    "Login",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not email.strip() or not password:
                    st.session_state.auth_error = (
                        "Please enter your email and password."
                    )
                    st.rerun()

                try:
                    login_user(email, password)
                    st.rerun()

                except requests.exceptions.HTTPError as exc:
                    detail = ""
                    if exc.response is not None:
                        try:
                            detail = exc.response.json().get("detail", "")
                        except ValueError:
                            detail = exc.response.text

                    st.session_state.auth_error = (
                        detail or "Invalid email or password."
                    )
                    st.rerun()

                except requests.exceptions.RequestException as exc:
                    st.session_state.auth_error = (
                        f"Could not connect to the backend: {exc}"
                    )
                    st.rerun()

                except (ValueError, TypeError) as exc:
                    st.session_state.auth_error = str(exc)
                    st.rerun()

        else:
            with st.form("signup_form"):
                name = st.text_input("Full name", placeholder="Your name")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                )
                submitted = st.form_submit_button(
                    "Create account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not name.strip() or not email.strip() or not password:
                    st.session_state.auth_error = (
                        "Please complete all fields."
                    )
                    st.rerun()

                if password != confirm_password:
                    st.session_state.auth_error = "Passwords do not match."
                    st.rerun()

                try:
                    signup_response = requests.post(
                        f"{AUTH_API_URL}/signup",
                        json={
                            "name": name.strip(),
                            "email": email.strip(),
                            "password": password,
                        },
                        timeout=20,
                    )
                    signup_response.raise_for_status()

                    # Signup creates the account; login obtains its JWT.
                    login_user(email, password)
                    st.rerun()

                except requests.exceptions.HTTPError as exc:
                    detail = ""
                    if exc.response is not None:
                        try:
                            detail = exc.response.json().get("detail", "")
                        except ValueError:
                            detail = exc.response.text

                    st.session_state.auth_error = (
                        detail or "Could not create the account."
                    )
                    st.rerun()

                except requests.exceptions.RequestException as exc:
                    st.session_state.auth_error = (
                        f"Could not connect to the backend: {exc}"
                    )
                    st.rerun()

                except (ValueError, TypeError) as exc:
                    st.session_state.auth_error = str(exc)
                    st.rerun()

    st.stop()


if (
    not st.session_state.get("authenticated")
    or not st.session_state.get("access_token")
):
    show_authentication_page()


# ==================================================
# WORKFLOW STAGES
# ==================================================

STAGES = [
    "Router",
    "Research",
    "Blog structure",
    "Writing blog sections",
    "Preparing draft",
    "Reviewing blog quality",
    "Improving blog",
    "Blog generation completed",
]

STAGE_ALIASES = {
    "router": "Router",
    "research": "Research",
    "submit_evidence": "Research",

    "blog structure": "Blog structure",
    "planner": "Blog structure",

    "writing blog sections": "Writing blog sections",
    "worker": "Writing blog sections",

    "preparing draft": "Preparing draft",
    "draft": "Preparing draft",
    "draft preparation": "Preparing draft",

    "reviewing blog quality": "Reviewing blog quality",
    "critique": "Reviewing blog quality",

    "improving blog": "Improving blog",
    "revision": "Improving blog",

    "reducer": "Blog generation completed",
    "blog generation completed": "Blog generation completed",
}





# ==================================================
# HEADER
# ==================================================

st.title("✍️ AI Blog Generator")

st.caption(
    "Transform your ideas into engaging blogs with "
    "AI-powered research, intelligent planning and automated writing."
)

header_user_col, header_logout_col = st.columns([8, 1.5])
with header_user_col:
    current_user = st.session_state.get("user") or {}
    current_email = current_user.get("email", "Signed in")
    st.caption(f"Logged in as: {current_email}")

with header_logout_col:
    with st.container(key="logout_header"):
        if st.button("Logout", key="logout_button"):
            clear_authentication()
            st.rerun()
st.divider()


# ==================================================
# BLOG INPUT
# ==================================================

st.markdown("### Enter a topic to start generating your blog.")

topic = st.text_input(
    "Blog Topic",
    placeholder=(
        "e.g. Artificial Intelligence, "
        "Generative AI, Machine Learning..."
    ),
    label_visibility="collapsed"
)

generate_button = st.button(
    "✨ Generate Blog",
    type="primary",
    disabled=not topic.strip()
)

# ==================================================
# AUTO SCROLL TO GENERATION PROGRESS
# ==================================================

def scroll_to_progress():

    if st.session_state.get("scroll_to_progress", False):

        st.components.v1.html(
            """
            <script>
                window.parent.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            </script>
            """,
            height=0,
        )

        st.session_state.scroll_to_progress = False


# ==================================================
# PLACEHOLDERS
# ==================================================

starting_placeholder = st.empty()

# Generation dashboard
progress_placeholder = st.empty()
sections_placeholder = st.empty()

status_placeholder = st.empty()

# Human review
review_placeholder = st.empty()

draft_placeholder = st.empty()
critique_placeholder = st.empty()

blog_placeholder = st.empty()

scroll_to_progress()

# ==================================================
# PROGRESS DISPLAY
# ==================================================

def show_stages():

    with progress_placeholder.container():

        st.divider()

        st.subheader("⚙️ Generation Progress")

        for index, stage in enumerate(STAGES, start=1):

            if stage in st.session_state.completed_stages:

                st.success(
                    f"✓ {stage} completed"
                )

            elif stage == st.session_state.current_stage:

                st.info(
                    f"⏳ {stage} in progress..."
                )

            else:

                st.write(
                    f"○ {stage}"
                )

        show_router_research_results()

    # Display section progress immediately below stages
    show_section_progress()


# ==================================================
# NORMALIZE STAGE
# ==================================================

def normalize_stage(message):

    message = message.strip()

    suffixes = (
        " completed",
        " generated",
        " started",
        " in progress",
    )

    for suffix in suffixes:

        if message.lower().endswith(suffix):

            message = message[:-len(suffix)].strip()
            break

    return STAGE_ALIASES.get(message.lower())


# ==================================================
# STAGE STARTED
# ==================================================

def handle_stage_started(message):

    stage = normalize_stage(message)

    if not stage:
        return

    if stage in st.session_state.completed_stages:
        return

    st.session_state.current_stage = stage

    if stage == "Router":

        starting_placeholder.info(
            "Starting blog generation..."
        )

    else:

        starting_placeholder.empty()

    show_stages()


# ==================================================
# STAGE COMPLETED
# ==================================================

def handle_stage_completed(message, event=None):

    stage = normalize_stage(message)

    if not stage:
        return

    if stage not in st.session_state.completed_stages:

        st.session_state.completed_stages.append(stage)

    if stage == "Router":

        starting_placeholder.empty()

        # Capture router response
        if event:

            data = event.get("data", {})

            if not isinstance(data, dict):
                data = {}

            needs_research = event.get(
                "needs_research",
                data.get("needs_research")
            )

            if needs_research is not None:

                st.session_state.router_needs_research = (
                    needs_research
                )

    if stage == "Research":

        # Capture researched page URLs
        if event:

            data = event.get("data", {})

            if not isinstance(data, dict):
                data = {}

            urls = event.get(
                "researched_urls",
                data.get("researched_urls", [])
            )

            if urls:

                st.session_state.researched_urls = [
                    item.get("url") if isinstance(item, dict) else item
                    for item in urls
                    if (
                        isinstance(item, str)
                        or (
                            isinstance(item, dict)
                            and item.get("url")
                        )
                    )
                ]

    if st.session_state.current_stage == stage:

        st.session_state.current_stage = None

    show_stages()

# ==================================================
# INDIVIDUAL SECTION PROGRESS
# ==================================================

def initialize_section_progress():
    """Create one progress entry for every task in the approved plan."""
    plan = st.session_state.review_plan or {}
    tasks = plan.get("tasks", [])

    st.session_state.section_tasks = tasks
    st.session_state.section_progress = {
        str(task.get("id", index + 1)): "writing"
        for index, task in enumerate(tasks)
    }

    show_section_progress()


def handle_section_completed(event):
    """Mark one worker's section as ready from a backend SSE event."""
    data = event.get("data", {})
    if not isinstance(data, dict):
        data = {}

    section_id = (
        event.get("task_id")
        or event.get("section_id")
        or event.get("id")
        or data.get("task_id")
        or data.get("section_id")
        or data.get("id")
    )

    if section_id is None:
        return

    section_id = str(section_id)

    # Ensure the section is present even if the plan was not retained.
    if section_id not in st.session_state.section_progress:
        st.session_state.section_progress[section_id] = "ready"

    st.session_state.section_progress[section_id] = "ready"

    # Preserve a title received from the backend if the plan has no match.
    title = (
        event.get("title")
        or event.get("section_title")
        or data.get("title")
        or data.get("section_title")
    )
    if title:
        for index, task in enumerate(st.session_state.section_tasks):
            task_id = str(task.get("id", index + 1))
            if task_id == section_id:
                task["title"] = title
                break

    show_section_progress()


def show_section_progress():
    """Render the live status of each section in the Streamlit UI."""
    tasks = st.session_state.section_tasks or []
    progress = st.session_state.section_progress or {}

    if not tasks and not progress:
        return

    with sections_placeholder.container():
        st.divider()
        st.subheader("✍️ Section Writing Progress")

        if tasks:
            for index, task in enumerate(tasks):
                section_id = str(task.get("id", index + 1))
                title = task.get("title", f"Section {section_id}")
                status = progress.get(section_id, "waiting")

                if status == "ready":
                    st.success(f"✓ Section {section_id}: {title} — Ready")
                elif status == "writing":
                    st.info(f"⏳ Section {section_id}: {title} — Writing...")
                else:
                    st.write(f"○ Section {section_id}: {title} — Waiting")

        else:
            for section_id, status in progress.items():
                label = "Ready" if status == "ready" else "Writing..."
                if status == "ready":
                    st.success(f"✓ Section {section_id} — {label}")
                else:
                    st.info(f"⏳ Section {section_id} — {label}")

        total = len(tasks) if tasks else len(progress)
        ready = sum(1 for status in progress.values() if status == "ready")
        st.caption(f"{ready} of 5 sections ready")


# ==================================================
# BLOG SECTIONS PREPARED
# ==================================================

def handle_sections_prepared():

    st.session_state.sections_prepared = True

    st.session_state.draft_preparing = True

    st.session_state.current_stage = "Preparing draft"

    if "Writing blog sections" not in st.session_state.completed_stages:

        st.session_state.completed_stages.append(
            "Writing blog sections"
        )

    show_stages()


# ==================================================
# DRAFT READY
# ==================================================

def handle_draft_ready(draft):

    st.session_state.draft_blog = draft

    st.session_state.draft_preparing = False

    st.session_state.current_stage = None

    if "Preparing draft" not in st.session_state.completed_stages:

        st.session_state.completed_stages.append(
            "Preparing draft"
        )

    show_stages()


# ==================================================
# CRITIQUE STARTED
# ==================================================

def handle_critique_started():

    st.session_state.critique_started = True

    st.session_state.current_stage = "Reviewing blog quality"

    show_stages()


# ==================================================
# CRITIQUE COMPLETED
# ==================================================

def handle_critique_completed(score):

    st.session_state.critique_score = score

    st.session_state.critique_completed = True

    st.session_state.critique_started = False

    if "Reviewing blog quality" not in st.session_state.completed_stages:

        st.session_state.completed_stages.append(
            "Reviewing blog quality"
        )

    st.session_state.current_stage = None

    show_stages()


# ==================================================
# PLAN NORMALIZATION
# ==================================================

def normalize_plan(plan):

    if isinstance(plan, str):

        plan = json.loads(plan)

    if isinstance(plan, dict):

        return plan

    raise ValueError(
        "Invalid blog plan received from backend."
    )


# ==================================================
# DISPLAY PLAN
# ==================================================

def display_plan(plan):

    st.markdown(
        f"### {plan.get('blog_title', 'Untitled Blog')}"
    )

    st.markdown(
        f"**Audience:** {plan.get('audience', 'Not specified')}"
    )

    st.markdown(
        f"**Tone:** {plan.get('tone', 'Not specified')}"
    )

    st.markdown(
        f"**Blog type:** {plan.get('blog_kind', 'Not specified')}"
    )

    constraints = plan.get("constraints", [])

    st.markdown("**Constraints:**")

    if isinstance(constraints, list) and constraints:

        for constraint in constraints:

            st.markdown(f"- {constraint}")

    elif constraints:

        st.write(constraints)

    else:

        st.write("No constraints specified.")

    st.divider()

    st.markdown("### Blog Sections")

    for index, task in enumerate(plan.get("tasks", [])):

        section_id = task.get("id", index + 1)

        section_title = task.get(
            "title",
            "Untitled Section"
        )

        with st.expander(
            f"Section {section_id}: {section_title}",
            expanded=True,
        ):

            st.markdown("**Goal**")

            st.write(
                task.get("goal", "No goal specified.")
            )

            st.markdown("**Points to cover**")

            bullets = task.get("bullets", [])

            if bullets:

                for bullet in bullets:

                    st.markdown(f"- {bullet}")

            else:

                st.write("No points specified.")

            st.markdown(
                f"**Target words:** "
                f"{task.get('target_words', 'Not specified')}"
            )

            tags = task.get("tags", [])

            if isinstance(tags, list):

                tags = ", ".join(tags)

            st.markdown(
                f"**Tags:** {tags if tags else 'None'}"
            )

            st.markdown(
                f"**Requires research:** "
                f"{'Yes' if task.get('requires_research') else 'No'}"
            )

            st.markdown(
                f"**Requires citations:** "
                f"{'Yes' if task.get('requires_citations') else 'No'}"
            )

            st.markdown(
                f"**Requires code:** "
                f"{'Yes' if task.get('requires_code') else 'No'}"
            )


# ==================================================
# EDIT PLAN FORM
# ==================================================

def edit_plan_form(plan):

    edited_plan = dict(plan)

    st.markdown("### Edit Blog Details")

    with st.form("edit_blog_plan_form"):

        edited_plan["blog_title"] = st.text_input(
            "Blog title",
            value=plan.get("blog_title", ""),
        )

        edited_plan["audience"] = st.text_input(
            "Audience",
            value=plan.get("audience", ""),
        )

        edited_plan["tone"] = st.text_input(
            "Tone",
            value=plan.get("tone", ""),
        )

        edited_plan["blog_kind"] = st.text_input(
            "Blog kind",
            value=plan.get("blog_kind", ""),
        )

        constraints = plan.get("constraints", [])

        if isinstance(constraints, list):

            constraints_text = "\n".join(constraints)

        else:

            constraints_text = str(constraints or "")

        edited_constraints = st.text_area(
            "Constraints (one per line)",
            value=constraints_text,
        )

        edited_plan["constraints"] = [
            item.strip()
            for item in edited_constraints.splitlines()
            if item.strip()
        ]

        st.divider()

        st.markdown("### Edit Blog Sections")

        edited_tasks = []

        for index, task in enumerate(plan.get("tasks", [])):

            st.markdown(
                f"#### Section {task.get('id', index + 1)}"
            )

            edited_task = dict(task)

            edited_task["title"] = st.text_input(
                "Section title",
                value=task.get("title", ""),
                key=f"edit_title_{index}",
            )

            edited_task["goal"] = st.text_area(
                "Section goal",
                value=task.get("goal", ""),
                key=f"edit_goal_{index}",
            )

            bullets = task.get("bullets", [])

            if not isinstance(bullets, list):

                bullets = []

            edited_bullets = st.text_area(
                "Points to cover (one per line)",
                value="\n".join(bullets),
                key=f"edit_bullets_{index}",
            )

            edited_task["bullets"] = [
                bullet.strip()
                for bullet in edited_bullets.splitlines()
                if bullet.strip()
            ]

            edited_task["target_words"] = st.number_input(
                "Target words",
                min_value=1,
                value=max(
                    1,
                    int(task.get("target_words", 100))
                ),
                step=10,
                key=f"edit_words_{index}",
            )

            tags = task.get("tags", [])

            if not isinstance(tags, list):

                tags = []

            edited_tags = st.text_input(
                "Tags (comma separated)",
                value=", ".join(tags),
                key=f"edit_tags_{index}",
            )

            edited_task["tags"] = [
                tag.strip()
                for tag in edited_tags.split(",")
                if tag.strip()
            ]

            edited_tasks.append(edited_task)

            st.divider()

        edited_plan["tasks"] = edited_tasks

        submitted = st.form_submit_button(
            "Submit Edited Plan",
            type="primary",
            use_container_width=True,
        )

    return submitted, edited_plan

# ==================================================
# ROUTER AND RESEARCH RESPONSE DISPLAY
# ==================================================

def show_router_research_results():

    # Router response
    if st.session_state.router_needs_research is not None:

        needs_research = st.session_state.router_needs_research

        if needs_research:
            st.info(
                f"🔍 Does the AI model need to do research? "
                f"**True**"
            )
        else:
            st.info(
                f"🔍 Does the AI model need to do research? "
                f"**False**"
            )

    # Research response
    if st.session_state.researched_urls:

        st.markdown("**🌐 Pages researched:**")

        for index, url in enumerate(
            st.session_state.researched_urls,
            start=1
        ):

            st.markdown(f"{index}. [{url}]({url})")


# ==================================================
# HUMAN REVIEW INTERRUPT
# ==================================================

def handle_interrupt(event):

    interrupt_data = event.get("data", {})

    if not isinstance(interrupt_data, dict):

        raise ValueError(
            "Invalid human-review interrupt data."
        )

    plan = interrupt_data.get("plan")

    if plan is None:

        raise ValueError(
            "Human-review interrupt did not contain a plan."
        )

    thread_id = event.get("thread_id")

    if thread_id:

        st.session_state.thread_id = thread_id

    if not st.session_state.thread_id:

        raise ValueError(
            "Thread ID is missing from the interrupt."
        )

    st.session_state.review_plan = normalize_plan(plan)

    st.session_state.review_submitted = False
    st.session_state.edit_mode = False

    st.session_state.workflow_waiting_for_review = True

    st.session_state.current_stage = None

    # Reset draft and critique information for the new plan
    st.session_state.draft_blog = None
    st.session_state.sections_prepared = False
    st.session_state.draft_preparing = False

    st.session_state.critique_started = False
    st.session_state.critique_score = None
    st.session_state.critique_completed = False

    starting_placeholder.empty()

    status_placeholder.warning(
        "Workflow paused. Please review the generated blog plan."
    )

    show_stages()


# ==================================================
# HANDLE STREAM EVENTS
# ==================================================

def consume_stream(response):

    """
    Consume backend Server-Sent Events.

    The review screen is only cleared after the backend confirms that
    section generation has started (sections_prepared), a new interrupt
    arrives, or the workflow completes.
    """

    received_event = False
    data_lines = []

    def process_event(raw_data):
        nonlocal received_event

        if not raw_data:
            return False

        try:
            event = json.loads(raw_data)
        except json.JSONDecodeError:
            st.warning(
                "Received an invalid event from the backend. "
                f"Response: {raw_data[:500]}"
            )
            return False

        if not isinstance(event, dict):
            st.warning("The backend event must be a JSON object.")
            return False

        received_event = True
        event_type = event.get("type")
        message = event.get("message", "")

        # --------------------------------------
        # STAGE EVENTS
        # --------------------------------------

        if event_type == "stage":

            normalized_message = str(message).lower().strip()

            if (
                normalized_message.endswith("completed")
                or normalized_message.endswith("generated")
            ):

                handle_stage_completed(message, event)

            elif (
                normalized_message.endswith("started")
                or normalized_message.endswith("in progress")
            ):

                handle_stage_started(message)


        elif event_type == "stage_started":

            handle_stage_started(message)


        elif event_type == "stage_completed":

            handle_stage_completed(message, event)

        # --------------------------------------
        # SECTIONS PREPARED
        # --------------------------------------

        elif event_type == "sections_prepared":
            # The backend has confirmed that writing can proceed.
            # Retain the approved plan's tasks to display individual progress.
            initialize_section_progress()
            st.session_state.review_plan = None
            st.session_state.review_submitted = False
            st.session_state.edit_mode = False
            st.session_state.workflow_waiting_for_review = False

            handle_sections_prepared()

        # --------------------------------------
        # INDIVIDUAL SECTION COMPLETED
        # --------------------------------------

        elif event_type in ("section_completed", "section_ready"):
            handle_section_completed(event)

        # --------------------------------------
        # DRAFT PREPARATION
        # --------------------------------------

        elif event_type == "draft_preparing":
            st.session_state.draft_preparing = True
            st.session_state.current_stage = "Preparing draft"
            show_stages()

        # --------------------------------------
        # DRAFT READY
        # --------------------------------------

        elif event_type == "draft":
            draft = event.get("draft", "")

            if not draft:
                st.warning("The backend sent an empty draft.")
            else:
                handle_draft_ready(draft)

        # --------------------------------------
        # CRITIQUE
        # --------------------------------------

        elif event_type == "critique_started":
            handle_critique_started()

        elif event_type == "critique_completed":
            score = event.get("score")

            if score is not None:
                handle_critique_completed(score)

        # --------------------------------------
        # HUMAN REVIEW INTERRUPT
        # --------------------------------------

        elif event_type == "interrupt":
            handle_interrupt(event)
            return True

        # --------------------------------------
        # WORKFLOW COMPLETED
        # --------------------------------------

        elif event_type == "complete":
            st.session_state.generated_blog = event.get("blog", "")

            # Final completion is authoritative: mark any remaining sections ready.
            for section_id in list(st.session_state.section_progress):
                st.session_state.section_progress[section_id] = "ready"
            show_section_progress()

            st.session_state.review_plan = None
            st.session_state.review_submitted = False
            st.session_state.edit_mode = False
            st.session_state.workflow_waiting_for_review = False

            st.session_state.draft_preparing = False
            st.session_state.critique_started = False
            st.session_state.current_stage = None

            if (
                "Blog generation completed"
                not in st.session_state.completed_stages
            ):
                st.session_state.completed_stages.append(
                    "Blog generation completed"
                )

            starting_placeholder.empty()
            show_stages()

        # --------------------------------------
        # ERROR
        # --------------------------------------

        elif event_type == "error":
            st.session_state.error = message or "Workflow failed."
            starting_placeholder.empty()

            # Allow the user to retry if the review is still pending.
            if st.session_state.review_plan is not None:
                st.session_state.review_submitted = False
                st.session_state.workflow_waiting_for_review = True

            return True

        return False

    try:
        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue

            if isinstance(line, bytes):
                line = line.decode("utf-8", errors="replace")

            line = line.strip()

            # Blank line terminates an SSE event. Support multi-line data.
            if not line:
                if data_lines:
                    should_stop = process_event("\\n".join(data_lines))
                    data_lines = []

                    if should_stop:
                        return

                continue

            # Ignore SSE comments and metadata fields.
            if line.startswith(":") or line.startswith("event:") or line.startswith("id:") or line.startswith("retry:"):
                continue

            if line.startswith("data:"):
                data_lines.append(line[len("data:"):].lstrip())
                continue

            # Also accept a raw JSON line, useful for simple streaming APIs.
            if line.startswith("{"):
                should_stop = process_event(line)
                if should_stop:
                    return

        # Process a final event that did not end with a blank line.
        if data_lines:
            process_event("\\n".join(data_lines))

        if not received_event:
            content_type = response.headers.get("content-type", "")
            st.session_state.error = (
                "The review/generation endpoint returned no readable "
                f"workflow events (Content-Type: {content_type or 'unknown'}). "
                "Check that the FastAPI endpoint streams SSE events using "
                "`data: <json>\\n\\n`."
            )

            if st.session_state.review_plan is not None:
                st.session_state.review_submitted = False
                st.session_state.workflow_waiting_for_review = True

    finally:
        response.close()


# ==================================================
# API: GENERATE BLOG
# ==================================================

def generate_blog(topic):

    try:

        response = requests.post(
            f"{API_URL}/generate",
            json={"topic": topic},
            headers=api_headers(),
            stream=True,
            timeout=(10, 600),
        )

        response.raise_for_status()

        consume_stream(response)

    except requests.exceptions.RequestException as exc:

        st.session_state.error = f"API request failed: {exc}"

    except (ValueError, KeyError, TypeError) as exc:

        st.session_state.error = f"Invalid server response: {exc}"


# ==================================================
# API: SUBMIT HUMAN REVIEW
# ==================================================

def submit_review(decision, edited_plan=None):

    if not st.session_state.thread_id:
        st.session_state.error = (
            "Cannot submit review: thread ID is missing."
        )
        st.session_state.review_submitted = False
        return

    response = None

    try:
        payload = {
            "thread_id": st.session_state.thread_id,
            "review": decision,
            "edited_plan": edited_plan,
        }

        if decision == "edit" and edited_plan is not None:
            st.session_state.review_plan = edited_plan

        response = requests.post(
            f"{API_URL}/review",
            json=payload,
            headers=api_headers(),
            stream=True,
            timeout=(10, 600),
        )

        response.raise_for_status()

        # Do NOT clear review_plan here.
        # Keep the review panel visible while the backend resumes LangGraph.
        # It will be cleared only when sections_prepared, interrupt, or
        # complete is received from the backend.

        st.session_state.error = None
        st.session_state.workflow_waiting_for_review = True

        # Clear content from any previous attempt, but preserve the plan.
        st.session_state.draft_blog = None
        st.session_state.generated_blog = None
        st.session_state.sections_prepared = False
        st.session_state.draft_preparing = False

        st.session_state.critique_started = False
        st.session_state.critique_score = None
        st.session_state.critique_completed = False

        show_stages()
        consume_stream(response)

    except requests.exceptions.RequestException as exc:
        st.session_state.error = f"Review request failed: {exc}"

        # Keep the review screen available so the user can retry.
        if st.session_state.review_plan is not None:
            st.session_state.review_submitted = False
            st.session_state.workflow_waiting_for_review = True

    except (ValueError, KeyError, TypeError) as exc:
        st.session_state.error = f"Invalid server response: {exc}"

        if st.session_state.review_plan is not None:
            st.session_state.review_submitted = False
            st.session_state.workflow_waiting_for_review = True

    finally:
        if response is not None:
            response.close()


# ==================================================
# RESET WORKFLOW
# ==================================================

def reset_generation():

    st.session_state.thread_id = None

    st.session_state.review_plan = None
    st.session_state.review_submitted = False
    st.session_state.edit_mode = False

    st.session_state.completed_stages = []

    st.session_state.current_stage = "Router"

    st.session_state.draft_blog = None
    st.session_state.generated_blog = None

    st.session_state.sections_prepared = False
    st.session_state.draft_preparing = False

    st.session_state.critique_started = False
    st.session_state.critique_score = None
    st.session_state.critique_completed = False

    st.session_state.error = None

    st.session_state.generation_started = True

    st.session_state.workflow_waiting_for_review = False
    st.session_state.router_needs_research = None
    st.session_state.researched_urls = []

    st.session_state.section_tasks = []
    st.session_state.section_progress = {}


# ==================================================
# GENERATE BUTTON ACTION
# ==================================================

if generate_button:

    reset_generation()

    show_stages()

    starting_placeholder.info(
        "Starting blog generation..."
    )

    with st.spinner("Connecting to the workflow..."):

        generate_blog(topic)

    st.rerun()


# ==================================================
# HUMAN REVIEW UI
# ==================================================

if st.session_state.review_plan:

    with review_placeholder.container():

        st.divider()

        st.subheader("👤 Human Review")

        st.info(
            "Your blog plan is ready. "
            "Review it before the writing process begins."
        )

        plan = st.session_state.review_plan

        # ------------------------------------------
        # EDIT MODE
        # ------------------------------------------

        if st.session_state.edit_mode:

            st.write(
                "Update the fields below. "
                "Leave unchanged values as they are."
            )

            submitted, edited_plan = edit_plan_form(plan)

            if submitted:

                st.session_state.review_submitted = True

                with st.spinner("Submitting edited plan..."):

                    submit_review(
                        "edit",
                        edited_plan,
                    )

                st.session_state.scroll_to_progress = True

                st.rerun()

            if st.button("Cancel Editing"):

                st.session_state.edit_mode = False

                st.rerun()

        # ------------------------------------------
        # NORMAL REVIEW MODE
        # ------------------------------------------

        elif not st.session_state.review_submitted:

            display_plan(plan)

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:

                if st.button(
                    "Approve Plan",
                    type="primary",
                    use_container_width=True,
                ):

                    st.session_state.review_submitted = True

                    with st.spinner("Submitting approval..."):

                        submit_review("approve")

                    st.session_state.scroll_to_progress = True

                    st.rerun()

            with col2:

                if st.button(
                    "Reject Plan",
                    use_container_width=True,
                ):

                    st.session_state.review_submitted = True

                    with st.spinner("Generating a new plan..."):

                        submit_review("reject")

                    st.session_state.scroll_to_progress = True

                    st.rerun()
            with col3:

                if st.button(
                    "Edit Plan",
                    use_container_width=True,
                ):

                    st.session_state.edit_mode = True

                    st.rerun()

        # ------------------------------------------
        # WAITING FOR WORKFLOW
        # ------------------------------------------

        else:

            st.success(
                "Your review decision has been submitted."
            )

            st.info(
                "Waiting for the workflow to continue..."
            )


# ==================================================
# DRAFT PREVIEW
# ==================================================

if (
    st.session_state.draft_preparing
    and not st.session_state.draft_blog
):

    with draft_placeholder.container():

        st.divider()

        st.subheader("📄 Preparing Blog Draft")

        st.info(
            "Your blog sections have been prepared. "
            "The initial draft is now being generated..."
        )

# ==================================================
# CRITIQUE EVALUATION
# ==================================================

if (
    st.session_state.critique_started
    and not st.session_state.critique_completed
):

    with critique_placeholder.container():

        st.divider()

        st.subheader("🔍 Critique Evaluation")

        st.info(
            "The critique agent is evaluating the generated draft. "
            "Checking content quality, accuracy, structure "
            "and readability..."
        )


if st.session_state.critique_completed:

    with critique_placeholder.container():

        st.divider()

        st.subheader("🔍 Critique Evaluation")

        st.success(
            f"✓ Critique evaluation completed! "
            f"Your blog received a score of "
            f"{st.session_state.critique_score}/10."
        )


# ==================================================
# CURRENT STATUS
# ==================================================

if st.session_state.generation_started:

    with status_placeholder.container():

        if st.session_state.error:

            st.error("Generation failed.")

        elif st.session_state.generated_blog:

            st.success("Blog generated successfully!")

        elif st.session_state.review_plan:

            st.warning("Waiting for human review.")

        elif st.session_state.workflow_waiting_for_review:

            st.warning("Waiting for human review.")

        elif st.session_state.critique_started:

            st.info("Critique agent is evaluating the draft...")

        elif st.session_state.draft_preparing:

            st.info("Preparing the initial blog draft...")

        elif st.session_state.current_stage:

            st.info(
                f"Currently running: "
                f"{st.session_state.current_stage}"
            )

        elif st.session_state.completed_stages:

            st.info("Workflow is continuing...")

        else:

            st.info("Waiting for workflow events...")


# ==================================================
# ERROR DISPLAY
# ==================================================

if st.session_state.error:

    st.error(st.session_state.error)


# ==================================================
# FINAL GENERATED BLOG
# ==================================================

if st.session_state.generated_blog:

    with blog_placeholder.container():

        st.divider()

        st.subheader("📝 Final Generated Blog")

        st.success(
            "Your blog has been successfully generated "
            "and reviewed by the critique agent!"
        )

        if st.session_state.critique_score is not None:

            st.markdown(
                f"**Final critique score: "
                f"{st.session_state.critique_score}/10**"
            )

        with st.container(border=True):

            st.markdown(
                st.session_state.generated_blog
            )

        st.download_button(
            label="⬇️ Download Blog",
            data=st.session_state.generated_blog,
            file_name="generated_blog.md",
            mime="text/markdown",
            use_container_width=True,
        )



# ==================================================
# MARKDOWN ASSISTANT - API CONFIGURATION
# ==================================================

# Expected backend endpoints:
# GET  /api/blog/chat/documents
# POST /api/blog/chat/
#
# Document-list response:
# {"documents": [{"id": "...", "title": "...", "version": 1}]}
#
# Chat request:
# {"file_id": "...", "question": "...", "top_k": 4}
#
# Chat response:
# {"answer": "...", "sources": [...]}


CHAT_API_URL = f"{API_URL}/chat"
CHAT_DOCUMENTS_URL = f"{CHAT_API_URL}/documents"


def load_chat_documents(force_refresh=False):
    """Load saved Markdown files for the chatbot's document selector."""
    if (
        st.session_state.chat_documents_loaded
        and not force_refresh
    ):
        return

    try:
        response = requests.get(
            CHAT_DOCUMENTS_URL,
            headers=api_headers(),
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()

        if isinstance(payload, list):
            documents = payload
        else:
            documents = payload.get("documents", [])
        if not isinstance(documents, list):
            raise ValueError(
                "The documents API must return a 'documents' list."
            )

        # Keep only documents with an ID and a display title.
        st.session_state.chat_documents = [
            document
            for document in documents
            if isinstance(document, dict)
            and document.get("id") is not None
        ]
        st.session_state.chat_documents_loaded = True
        st.session_state.chat_error = None

        available_ids = {
            str(document["id"])
            for document in st.session_state.chat_documents
        }

        selected_id = st.session_state.selected_chat_file_id
        if selected_id is not None and str(selected_id) not in available_ids:
            st.session_state.selected_chat_file_id = None
            st.session_state.chat_messages = []

    except requests.exceptions.RequestException as exc:
        st.session_state.chat_error = (
            f"Could not load Markdown files: {exc}"
        )
    except (ValueError, KeyError, TypeError) as exc:
        st.session_state.chat_error = (
            f"Invalid document-list response: {exc}"
        )


def send_chat_message(question):
    """Send a question to the backend using the selected Markdown file."""
    selected_file_id = st.session_state.selected_chat_file_id

    if not selected_file_id:
        st.session_state.chat_error = (
            "Please select a Markdown file first."
        )
        return

    question = question.strip()
    if not question:
        return

    st.session_state.chat_messages.append({
        "role": "user",
        "content": question,
    })

    try:
        response = requests.post(
            CHAT_API_URL,
            json={
                "file_id": selected_file_id,
                "question": question,
                "top_k": 4,
            },
            headers=api_headers(),
            timeout=(10, 180),
        )
        response.raise_for_status()
        payload = response.json()

        answer = payload.get("answer")
        if not answer:
            answer = "Not provided in the markdown file."

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer,
            "sources": payload.get("sources", []),
        })
        st.session_state.chat_error = None

    except requests.exceptions.RequestException as exc:
        st.session_state.chat_error = (
            f"Chat request failed: {exc}"
        )
        # Remove the unanswered user message so it can be retried.
        if (
            st.session_state.chat_messages
            and st.session_state.chat_messages[-1]["role"] == "user"
            and st.session_state.chat_messages[-1]["content"] == question
        ):
            st.session_state.chat_messages.pop()

    except (ValueError, KeyError, TypeError) as exc:
        st.session_state.chat_error = (
            f"Invalid chat response: {exc}"
        )


# ==================================================
# FLOATING MARKDOWN ASSISTANT
# ==================================================

with st.popover("🤖"):
    st.markdown(
        '<div class="markdown-assistant-heading">'
        'Markdown Assistant</div>'
        '<div class="markdown-assistant-subtitle">'
        'Ask questions about your previously generated blogs'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "↻ Refresh files",
        key="refresh_chat_documents",
        use_container_width=True,
    ):
        load_chat_documents(force_refresh=True)

    load_chat_documents()

    if st.session_state.chat_error:
        st.error(st.session_state.chat_error)

    documents = st.session_state.chat_documents

    if not documents:
        st.info(
            "No saved Markdown files are available yet. "
            "Generate a blog first, then refresh this list."
        )
    else:
        document_by_id = {
            str(document["id"]): document
            for document in documents
        }

        document_ids = list(document_by_id.keys())

        current_selected = st.session_state.selected_chat_file_id
        if current_selected is not None:
            current_selected = str(current_selected)

        selected_index = (
            document_ids.index(current_selected)
            if current_selected in document_ids
            else None
        )

        selected_id = st.selectbox(
            "Which Markdown file would you like to discuss?",
            options=document_ids,
            index=selected_index,
            placeholder="Select a generated Markdown file",
            format_func=lambda document_id: (
                f"{document_by_id[document_id].get('title', 'Untitled')}"
                f" (v{document_by_id[document_id].get('version', 1)})"
            ),
            key="chat_document_selector",
        )

        if selected_id != st.session_state.selected_chat_file_id:
            st.session_state.selected_chat_file_id = selected_id
            st.session_state.chat_messages = []
            if selected_id is not None:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": (
                        "Hello! Ask me anything about the selected "
                        "Markdown file. I will answer using that file only."
                    ),
                })

        if selected_id is None:
            st.info("Select a Markdown file to start chatting.")
        else:
            if not st.session_state.chat_messages:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": (
                        "Hello! Ask me anything about this Markdown file. "
                        "I will use only its content to answer."
                    ),
                })

            
            st.divider()

            # 1. Display existing conversation
            for message in st.session_state.chat_messages:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

                    sources = message.get("sources", [])
                    if sources:
                        with st.expander("Sources"):
                            for source_index, source in enumerate(
                                sources,
                                start=1,
                            ):
                                title = source.get(
                                    "title",
                                    "Selected Markdown file",
                                )
                                chunk_index = source.get("chunk_index")

                                st.caption(
                                    f"{source_index}. {title}"
                                    + (
                                        f" — chunk {chunk_index}"
                                        if chunk_index is not None
                                        else ""
                                    )
                                )


            # 2. Reserve space for temporary messages
            response_placeholder = st.empty()


            # 3. Create only ONE chat form
            with st.form(
                "markdown_assistant_chat_form",
                clear_on_submit=True,
            ):
                chat_question = st.text_input(
                    "Your question",
                    placeholder="Ask something about this Markdown...",
                    label_visibility="collapsed",
                )

                send_button = st.form_submit_button(
                    "Send",
                    type="primary",
                    use_container_width=True,
                )


            # 4. Handle message submission
            if send_button and chat_question.strip():

                with response_placeholder.container():

                    with st.chat_message("user"):
                        st.markdown(chat_question)

                    st.info("Searching in the selected Markdown...")

                send_chat_message(chat_question)

                st.rerun()