import streamlit as st
import requests
import base64
import urllib.parse
from datetime import datetime

THEME_PRIMARY = "#4F46E5"  # Indigo
THEME_BG_LIGHT = "#F8FAFC"  # Light slate
THEME_BORDER = "#E2E8F0"

def inject_global_styles():
    """Inject custom CSS for improved UI without altering core logic."""
    st.markdown(
        f"""
        <style>
        .main > div {{ padding-top: 0 !important; }}
        .app-container {{ max-width: 1100px; margin: 0 auto; }}
        .card {{ background: {THEME_BG_LIGHT}; padding: 1.25rem 1.5rem; border: 1px solid {THEME_BORDER}; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 1.25rem; }}
        .post-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; }}
        .post-meta {{ font-size:0.85rem; color:#475569; }}
        .caption-overlay {{ font-style: italic; color:#334155; margin-top:0.35rem; }}
        .divider {{ height:1px; background:{THEME_BORDER}; margin:1.5rem 0; }}
        .page-title {{ font-weight:600; margin-bottom:0.75rem; }}
        .muted {{ color:#64748B; }}
        button[kind="primary"] {{ background:{THEME_PRIMARY} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="Simple Social", layout="wide")
inject_global_styles()

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.markdown("<div class='app-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='page-title'>🚀 Welcome to Simple Social</h2>", unsafe_allow_html=True)
    st.write("Create an account or log in to start sharing.")
    with st.container():
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        disabled = not (email and password)
        col_login, col_signup = st.columns([2,2])
        with col_login:
            if st.button("Login", type="primary", use_container_width=True, disabled=disabled):
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]
                    user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.success("Logged in successfully ✨")
                        st.experimental_set_query_params(page="feed")
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password")
        with col_signup:
            if st.button("Sign Up", type="secondary", use_container_width=True, disabled=disabled):
                signup_data = {"email": email, "password": password}
                response = requests.post("http://localhost:8000/auth/register", json=signup_data)
                if response.status_code == 201:
                    st.success("Account created. You can log in now.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")
        if disabled:
            st.info("Enter both email and password to proceed")
    st.markdown("</div>", unsafe_allow_html=True)


def upload_page():
    st.markdown("<div class='app-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='page-title'>📸 Share Something</h2>", unsafe_allow_html=True)
    st.write("Upload an image or video and add an optional caption.")
    with st.container():
        uploaded_file = st.file_uploader("Media file", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
        
        # ✅ Show message when a file is uploaded
        if uploaded_file is not None:
            st.success(f"✅ '{uploaded_file.name}' has been uploaded successfully!")

        caption = st.text_area("Caption", placeholder="What's on your mind?", height=100)
        share_disabled = uploaded_file is None
        if st.button("Share", type="primary", disabled=share_disabled):
            with st.spinner("Uploading..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"caption": caption}
                response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())
                if response.status_code == 200:
                    st.success("✅ Posted successfully!")
                    st.rerun()
                else:
                    st.error("Upload failed")
        if share_disabled:
            st.info("Select a media file to enable sharing")
    st.markdown("</div>", unsafe_allow_html=True)


def create_transformed_url(original_url, transformation_params=None, caption=None):
    """Return the image/video URL without overlaying text on it."""
    return original_url


def feed_page():
    st.markdown("<div class='app-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='page-title'>🏠 Feed</h2>", unsafe_allow_html=True)
    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json().get("posts", [])
        if not posts:
            st.info("No posts yet. Be the first to share something!")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        for post in posts:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                # Header
                created_display = post.get('created_at', '')[:19]
                try:
                    created_dt = datetime.fromisoformat(post.get('created_at', '')[:19])
                    created_human = created_dt.strftime('%b %d, %Y')
                except Exception:
                    created_human = created_display[:10]
                col_meta, col_actions = st.columns([5,1])
                with col_meta:
                    st.markdown(f"<div class='post-meta'><strong>{post['email']}</strong> • {created_human}</div>", unsafe_allow_html=True)
                with col_actions:
                    if post.get('is_owner', False):
                        if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                            del_resp = requests.delete(f"http://localhost:8000/posts/{post['id']}", headers=get_headers())
                            if del_resp.status_code == 200:
                                st.success("Post deleted")
                                st.rerun()
                            else:
                                st.error("Failed to delete")
                caption = post.get('caption', '')
                if post['file_type'] == 'image':
                    uniform_url = create_transformed_url(post['url'])
                    st.image(uniform_url, use_container_width=True)
                    if caption:
                        st.markdown(f"<div class='caption-overlay'>{caption}</div>", unsafe_allow_html=True)
                else:
                    uniform_video_url = create_transformed_url(post['url'])
                    st.video(uniform_video_url)
                    if caption:
                        st.markdown(f"<div class='caption-overlay'>{caption}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Failed to load feed")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    st.sidebar.title(f"👋 Hi {st.session_state.user['email']}")
    st.sidebar.caption("Welcome back. Use the navigation below.")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.experimental_set_query_params(page="login")
        st.rerun()
    st.sidebar.divider()
    page = st.sidebar.radio("Navigate", ["🏠 Feed", "📸 Upload"], index=0)
    if page.startswith("🏠"):
        feed_page()
    else:
        upload_page()
