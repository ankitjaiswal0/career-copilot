import streamlit as st
import requests
import base64
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GenAI Career Copilot (Demo)",
    layout="centered",
)

# --------------- GLOBAL STYLES ---------------
st.markdown(
    """
    <style>
        /* Background gradient */
        .stApp {
            background: radial-gradient(circle at top left, #1f2937 0, #020617 45%, #000000 100%);
            color: #e5e7eb;
        }
        /* Main container width tweak */
        .main-block {
            background: rgba(15, 23, 42, 0.9);
            padding: 1.4rem 1.8rem;
            border-radius: 1.4rem;
            box-shadow: 0 18px 60px rgba(0,0,0,0.45);
            border: 1px solid rgba(148,163,184,0.25);
        }
        .main-title {
            font-size: 32px;
            font-weight: 800;
            padding: 0.3rem 0.9rem;
            border-radius: 999px;
            background: linear-gradient(90deg, #6366f1, #ec4899);
            color: white;
            display: inline-block;
            margin-bottom: 0.25rem;
        }
        .sub-title {
            color: #a5b4fc;
            font-size: 14px;
            margin-bottom: 1.0rem;
        }
        .status-badge {
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 999px;
            display: inline-block;
            margin-top: 0.3rem;
        }
        .status-ok {
            background-color: #22c55e22;
            color: #22c55e;
            border: 1px solid #22c55e55;
        }
        .status-bad {
            background-color: #ef444422;
            color: #f97373;
            border: 1px solid #ef444466;
        }
        .nav-label {
            font-size: 13px;
            font-weight: 600;
            color: #9ca3af;
            margin-bottom: 0.1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------- SESSION STATE ---------------
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --------------- LAMBDA URLS -----------------
# TODO: yaha apne AWS Lambda Function URLs daalo
VERIFY_FACE_URL = "https://xru2gt4vzolo752g7xylmf3dgu0xsbdh.lambda-url.ap-south-1.on.aws/"
INTERVIEW_URL   = "https://2isibspwo3qgk5alvitt5tjmke0vgmcw.lambda-url.ap-south-1.on.aws/" 
RESUME_URL      = "https://qavfe67lfapzrzdi2jgq6cxcy40eapri.lambda-url.ap-south-1.on.aws/"    
DOC_VERIFY_URL  = "https://d76b2gotwwogvformfrbn5q2oy0eehwt.lambda-url.ap-south-1.on.aws/"

# --------------- HEADER ----------------------
col_header_left, col_header_right = st.columns([3, 1.2], gap="large")

with col_header_left:
    st.markdown('<div class="main-title">GenAI Career Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Face Login · Interview Prep · Resume Builder · Document Verification</div>',
        unsafe_allow_html=True,
    )

with col_header_right:
    if st.session_state.is_logged_in:
        st.markdown(
            f'<div class="status-badge status-ok">✅ Logged in as <b>{st.session_state.logged_in_user}</b></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge status-bad">🔒 Not logged in</div>',
            unsafe_allow_html=True,
        )

st.write("")  # spacing

# --------------- TOP NAVIGATION --------------
st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)
tabs = ["Login", "Interview Prep", "Resume Builder", "Doc Verify", "Instructions"]

current_tab = st.radio(
    "",
    tabs,
    horizontal=True,
    key="top_nav",
)

protected_tabs = ["Interview Prep", "Resume Builder", "Doc Verify"]

if current_tab in protected_tabs and not st.session_state.is_logged_in:
    with st.container():
        st.markdown('<div class="main-block">', unsafe_allow_html=True)
        st.warning("🔒 Please complete **Face Login** first to access this section.")
        st.info("Go to the **Login** tab, verify your face, then select this section again.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
# 1️⃣ LOGIN TAB
# ============================================================
if current_tab == "Login":
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header("1️⃣ Face-based Login (Amazon Rekognition)")

    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.write("Upload a selfie to compare with stored reference image in S3 (e.g., `refs/demo_user.jpg`).")

        user_id = st.text_input("User ID", value="demo_user")
        file = st.file_uploader("Selfie image", type=["jpg", "jpeg", "png"])

        if st.button("Verify Face", type="primary"):
            if file is None:
                st.error("Please upload a selfie image.")
            else:
                img_bytes = file.read()
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                payload = {"user_id": user_id, "image_base64": b64}

                try:
                    response = requests.post(VERIFY_FACE_URL, json=payload)
                    data = response.json()

                    st.subheader("Backend Response")
                    st.json(data)

                    matched = False
                    if isinstance(data, dict):
                        matched = bool(
                            data.get("matched")
                            or data.get("Match")
                            or data.get("face_match")
                        )

                    if matched:
                        st.success("✅ Face verified! You are now logged in.")
                        st.session_state.is_logged_in = True
                        st.session_state.logged_in_user = user_id
                    else:
                        st.error("❌ Face did not match the reference image.")
                except Exception as e:
                    st.error(f"Request failed: {e}")
                    if "response" in locals():
                        st.write("Raw response:")
                        st.code(response.text)

    with right:
        st.info(
            "Demo usage:\n\n"
            "- In S3 bucket, keep a reference image like `refs/demo_user.jpg`.\n"
            "- Enter User ID = `demo_user` and upload the same image here.\n"
            "- Backend Lambda uses Rekognition (or mock) to compare faces."
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 2️⃣ INTERVIEW PREP TAB
# ============================================================
elif current_tab == "Interview Prep":
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header("2️⃣ Interview Question Generator")

    st.caption("Company + Role → Backend Lambda (mock / Bedrock-ready) → JSON list of questions.")

    company = st.selectbox("Company", ["Google", "Amazon", "Microsoft", "Others"])
    role = st.selectbox("Role", ["SDE", "ML Engineer", "Data Scientist", "DevOps", "QA"])

    if st.button("Generate Questions", type="primary"):
        payload = {"company": company, "role": role}
        try:
            response = requests.post(INTERVIEW_URL, json=payload)
            data = response.json()
            st.subheader("Generated Questions")
            st.json(data)
        except Exception as e:
            st.error(f"Request failed: {e}")
            if "response" in locals():
                st.write("Raw response:")
                st.code(response.text)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 3️⃣ RESUME BUILDER TAB
# ============================================================
elif current_tab == "Resume Builder":
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header("3️⃣ Resume Builder (stored in S3)")

    col_left, col_right = st.columns([1.4, 1], gap="large")

    with col_left:
        default_user_id = st.session_state.logged_in_user or "demo_user_resume"
        user_id = st.text_input("User ID (for resume filename)", value=default_user_id)
        name = st.text_input("Full name")
        email = st.text_input("Email")
        skills = st.text_area("Skills (comma separated)")
        projects = st.text_area("Projects (one per line)\nExample: Project A - built X")

        if st.button("Generate Resume", type="primary"):
            resume_data = {
                "Name": name,
                "Email": email,
                "Skills": [s.strip() for s in skills.split(",") if s.strip()],
                "Projects": [p.strip() for p in projects.split("\n") if p.strip()],
            }

            payload = {"user_id": user_id, "resume_data": resume_data}

            try:
                response = requests.post(RESUME_URL, json=payload)
                out = response.json()
                st.success("✅ Resume generated and saved to S3.")
                st.subheader("Backend Response")
                st.json(out)

                pdf_url = out.get("pdf_url")
                if pdf_url:
                    st.markdown(f"📄 **Download:** [Open Resume File]({pdf_url})")
            except Exception as e:
                st.error(f"Request failed: {e}")
                if "response" in locals():
                    st.write("Raw response:")
                    st.code(response.text)

    with col_right:
        st.info(
            "This demo saves a simple text resume in the S3 bucket under the "
            "`resumes/` folder.\n\n"
            "In a full Bedrock-powered version, this Lambda can generate rich "
            "AI resumes and export them as PDFs."
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 4️⃣ DOC VERIFY TAB
# ============================================================
elif current_tab == "Doc Verify":
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header("4️⃣ Document Verification (Mock / Textract-ready)")

    st.write(
        "Paste the same **Resume JSON** used in Resume Builder, then upload a marksheet/degree/ID document.\n"
        "Backend currently runs a **mock verification** due to Textract subscription limits."
    )

    resume_json_text = st.text_area("Resume JSON", height=220)
    doc_file = st.file_uploader("Upload document image/pdf", type=["jpg", "jpeg", "png", "pdf"])

    if st.button("Verify Document", type="primary"):
        if not resume_json_text or not doc_file:
            st.error("Please provide both Resume JSON and a document file.")
        else:
            try:
                resume_json = json.loads(resume_json_text)
            except Exception:
                st.error(
                    "❌ Invalid JSON. Example:\n\n"
                    '{ "Name": "ankit", "Email": "you@example.com", '
                    '"Skills": ["python"], "Projects": ["projct a"] }'
                )
                resume_json = None

            if resume_json:
                try:
                    doc_bytes = doc_file.read()
                    b64 = base64.b64encode(doc_bytes).decode("utf-8")
                    payload = {"resume_json": resume_json, "doc_base64": b64}

                    response = requests.post(DOC_VERIFY_URL, json=payload)
                    data = response.json()

                    # Some lambdas return {"statusCode": ..., "body": "..."} → unwrap
                    if isinstance(data, dict) and "body" in data:
                        try:
                            data = json.loads(data["body"])
                        except Exception:
                            pass

                    st.subheader("Verification Result")
                    st.json(data)

                except Exception as e:
                    st.error(f"Request failed: {e}")
                    if "response" in locals():
                        st.write("Raw response:")
                        st.code(response.text)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ℹ️ INSTRUCTIONS TAB
# ============================================================
else:  # Instructions
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header("ℹ️ Setup & Demo Flow")

    st.markdown(
        """
### Overall Architecture

- **Frontend:** Streamlit app (this UI)
- **Backend:** 4 AWS Lambda functions exposed via Function URLs  
- **Storage:** Amazon S3 (`refs/`, `resumes/`, `docs/` folders)

### Live Features in this Demo

1. **Face Login (Rekognition / or mock)**
   - User uploads selfie → Lambda compares with S3 reference image
   - On success, app stores `is_logged_in = True` and unlocks other tabs

2. **Interview Prep (Mock, Bedrock-ready)**
   - Company + Role → Lambda returns JSON list of interview questions
   - Can be swapped to Bedrock model call later

3. **Resume Builder**
   - Takes basic profile info → Lambda stores resume file to S3 (`resumes/<user>.txt`)
   - App shows public download link (read-only S3 bucket policy for `resumes/`)

4. **Document Verification (Mock)**
   - Accepts Resume JSON + uploaded document
   - In this student account, Textract is not enabled, so backend simulates a match score
   - Code is written so Textract can be plugged in easily when the service is available

> **Note:** Only *Login* and *Instructions* are accessible before authentication.  
> *Interview Prep*, *Resume Builder* and *Doc Verify* are protected behind Face Login.
        """
    )

    st.markdown('</div>', unsafe_allow_html=True)
