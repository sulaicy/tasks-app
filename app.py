"""
منصة متابعة المهام اليومية
Task Tracker - Python + Streamlit + SQLite + Plotly
تشغيل: streamlit run app.py
"""

import streamlit as st
import sqlite3
import hashlib
import uuid
from datetime import date, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from contextlib import contextmanager

# ─────────────────────────────────────────────
# إعداد الصفحة
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="منصة المهام",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# نظام الثيمات
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def is_dark():
    return st.session_state.theme == "dark"

def T():
    """إرجاع قاموس الألوان حسب الوضع الحالي"""
    if is_dark():
        return {
            "bg":           "#0f1117",
            "surface":      "#1a1d27",
            "surface2":     "#22263a",
            "border":       "#2e3347",
            "text":         "#dde1ec",
            "muted":        "#7b849a",
            "accent":       "#5b7cfa",
            "accent_soft":  "#1a233d",
            "success":      "#38a169",
            "success_soft": "#0d2318",
            "warning":      "#c47c20",
            "warning_soft": "#2c1e08",
            "danger":       "#e05252",
            "danger_soft":  "#2d0f0f",
            "chart_bg":     "#1a1d27",
            "chart_grid":   "#2e3347",
            "chart_font":   "#7b849a",
        }
    else:
        return {
            "bg":           "#f2f4f8",
            "surface":      "#ffffff",
            "surface2":     "#eef0f5",
            "border":       "#dde1ea",
            "text":         "#1c2033",
            "muted":        "#6b7280",
            "accent":       "#3b5fe0",
            "accent_soft":  "#e8edfc",
            "success":      "#2d8653",
            "success_soft": "#e8f5ee",
            "warning":      "#a0680f",
            "warning_soft": "#fef3e0",
            "danger":       "#c23b3b",
            "danger_soft":  "#fce8e8",
            "chart_bg":     "#ffffff",
            "chart_grid":   "#e5e7ed",
            "chart_font":   "#6b7280",
        }

def inject_css():
    t = T()
    dark = is_dark()
    hide_keyboard_hint()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
* {{ font-family: 'Tajawal', sans-serif !important; }}
html, body, [class*="css"] {{ direction: rtl; }}

.stApp                      {{ background: {t['bg']} !important; color: {t['text']} !important; }}
.stApp > header             {{ background: {t['surface']} !important; border-bottom: 1px solid {t['border']} !important; box-shadow: none !important; }}
.main .block-container      {{ padding-top: 1.5rem; max-width: 1100px; }}
section[data-testid="stSidebar"] {{ background: {t['surface']} !important; border-left: 1px solid {t['border']} !important; }}

h1, h2, h3, h4 {{ color: {t['text']} !important; }}

.task-card {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 8px;
    transition: border-color .18s, box-shadow .18s;
}}
.task-card:hover {{
    border-color: {t['accent']};
    box-shadow: 0 2px 10px rgba(91,124,250,0.10);
}}
.task-card-done {{
    background: {t['success_soft']};
    border: 1px solid {t['success']};
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 8px;
    opacity: 0.88;
}}

.badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
    line-height: 1.7;
}}
.badge-blue   {{ background: {t['accent_soft']};  color: {t['accent']};  }}
.badge-green  {{ background: {t['success_soft']}; color: {t['success']}; }}
.badge-gold   {{ background: {t['warning_soft']}; color: {t['warning']}; }}
.badge-purple {{ background: {'#251840' if dark else '#f0eafe'}; color: {'#9f7aea' if dark else '#6d3fcf'}; }}

.stButton > button {{
    background: {t['accent']} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 18px !important;
    transition: opacity .18s, transform .15s !important;
    box-shadow: 0 2px 6px rgba(59,95,224,0.18) !important;
}}
.stButton > button:hover {{
    opacity: 0.86 !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

.stTextInput input,
.stNumberInput input,
textarea {{
    background: {t['surface2']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 9px !important;
    color: {t['text']} !important;
}}
.stTextInput input:focus,
.stNumberInput input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 2px {t['accent_soft']} !important;
}}

.stSelectbox > div > div > div {{
    background: {t['surface2']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 9px !important;
    color: {t['text']} !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {t['surface2']};
    border-radius: 10px;
    padding: 4px 6px;
    gap: 2px;
    border: 1px solid {t['border']};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {t['muted']} !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    padding: 7px 16px !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: {t['surface']} !important;
    color: {t['accent']} !important;
    box-shadow: 0 1px 5px rgba(0,0,0,0.08) !important;
}}

.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {t['accent']}, {t['success']}) !important;
    border-radius: 100px !important;
}}
.stProgress > div > div {{
    background: {t['surface2']} !important;
    border-radius: 100px !important;
}}

div[data-testid="metric-container"] {{
    background: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}}
div[data-testid="metric-container"] label {{
    color: {t['muted']} !important;
    font-size: 13px !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {t['accent']} !important;
    font-weight: 800 !important;
    font-size: 30px !important;
}}

details {{
    background: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 11px !important;
    padding: 2px 10px !important;
    margin-bottom: 6px !important;
}}
summary {{
    color: {t['text']} !important;
    font-weight: 600 !important;
    padding: 10px 0 !important;
}}

div[data-testid="stForm"] {{
    background: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    padding: 18px !important;
}}

hr {{ border: none !important; border-top: 1px solid {t['border']} !important; margin: 14px 0 !important; }}

::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {t['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {t['border']}; border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: {t['muted']}; }}

/* ── إخفاء نص keyboard_ar من الأزرار ── */
[data-testid="InputInstructions"],
[class*="InputInstructions"],
[class*="inputInstructions"],
[class*="keyboard"],
[aria-label*="keyboard"],
button > div > small,
button small,
.stButton small,
.stButton > button > div > small,
.stFormSubmitButton small,
.stFormSubmitButton > button > div > small,
div[data-testid="stFormSubmitButton"] small,
div[data-testid="stBaseButton-secondary"] small,
div[data-testid="stBaseButton-primary"] small,
small {{ display: none !important; visibility: hidden !important; width: 0 !important; height: 0 !important; overflow: hidden !important; }}
</style>
""", unsafe_allow_html=True)

def hide_keyboard_hint():
    """إخفاء نص keyboard_ar الذي يظهر على الأزرار في Streamlit"""
    st.markdown("""
<script>
// إخفاء نص keyboard عبر JavaScript
function removeKeyboardHints() {
    const allSmall = document.querySelectorAll('small, [class*="InputInstructions"], [class*="keyboard"]');
    allSmall.forEach(el => { el.style.display = 'none'; });
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
        const smalls = btn.querySelectorAll('small, [class*="keyboard"]');
        smalls.forEach(s => { s.style.display = 'none'; });
    });
}
// تشغيل فوري وعند كل تحديث
removeKeyboardHints();
setInterval(removeKeyboardHints, 500);
const observer = new MutationObserver(removeKeyboardHints);
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

def style_chart(fig):
    t = T()
    fig.update_layout(
        paper_bgcolor=t["chart_bg"],
        plot_bgcolor=t["chart_bg"],
        font=dict(family="Tajawal", color=t["chart_font"], size=13),
        xaxis=dict(gridcolor=t["chart_grid"], zerolinecolor=t["chart_grid"], linecolor=t["border"]),
        yaxis=dict(gridcolor=t["chart_grid"], zerolinecolor=t["chart_grid"], linecolor=t["border"]),
        margin=dict(t=40, b=30, l=10, r=10),
        legend=dict(bgcolor=t["chart_bg"], bordercolor=t["border"]),
    )
    return fig

# ─────────────────────────────────────────────
# قاعدة البيانات
# ─────────────────────────────────────────────
DB = "tasks.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            group_id TEXT
        );
        CREATE TABLE IF NOT EXISTS groups_ (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            task_type TEXT DEFAULT 'check',
            points INTEGER DEFAULT 10,
            unit TEXT DEFAULT '',
            points_per_unit REAL DEFAULT 1.0,
            target_units REAL DEFAULT 1.0,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS completions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            date_ TEXT NOT NULL,
            units REAL DEFAULT 1.0,
            points REAL DEFAULT 0.0,
            UNIQUE(user_id, task_id, date_)
        );
        """)
        exists = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, name, role) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), "admin", hash_pw("admin123"), "المدير", "admin")
            )

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def today(): return date.today().isoformat()
def gen_id(): return str(uuid.uuid4())[:8]
def last_7_days():
    return [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

# ─────────────────────────────────────────────
# دوال قاعدة البيانات
# ─────────────────────────────────────────────
def get_user(username, password):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (username, hash_pw(password))
        ).fetchone()
        return dict(row) if row else None

def get_all_users():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM users WHERE role != 'admin'").fetchall()]

def add_user(name, username, password, group_id=None):
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (id,username,password_hash,name,role,group_id) VALUES (?,?,?,?,?,?)",
                (gen_id(), username, hash_pw(password), name, "user", group_id or None)
            )
            return True
        except sqlite3.IntegrityError:
            return False

def delete_user(uid):
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.execute("DELETE FROM completions WHERE user_id=?", (uid,))

def update_user_group(uid, group_id):
    with get_db() as conn:
        conn.execute("UPDATE users SET group_id=? WHERE id=?", (group_id or None, uid))

def get_groups():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM groups_").fetchall()]

def add_group(name):
    with get_db() as conn:
        conn.execute("INSERT INTO groups_ (id,name) VALUES (?,?)", (gen_id(), name))

def delete_group(gid):
    with get_db() as conn:
        conn.execute("DELETE FROM groups_ WHERE id=?", (gid,))
        conn.execute("UPDATE users SET group_id=NULL WHERE group_id=?", (gid,))

def get_tasks(user_id=None):
    with get_db() as conn:
        if user_id:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE assigned_to='all' OR assigned_to=?", (user_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tasks").fetchall()
        return [dict(r) for r in rows]

def add_task(title, assigned_to, task_type, points, unit, points_per_unit, target_units):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO tasks (id,title,assigned_to,task_type,points,unit,points_per_unit,target_units,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (gen_id(), title, assigned_to, task_type, points, unit, points_per_unit, target_units, today())
        )

def delete_task(tid):
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (tid,))
        conn.execute("DELETE FROM completions WHERE task_id=?", (tid,))

def get_completions(user_id=None, date_=None):
    with get_db() as conn:
        q, params = "SELECT * FROM completions WHERE 1=1", []
        if user_id: q += " AND user_id=?"; params.append(user_id)
        if date_:   q += " AND date_=?";   params.append(date_)
        return [dict(r) for r in conn.execute(q, params).fetchall()]

def complete_check(user_id, task_id, points):
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO completions (id,user_id,task_id,date_,units,points) VALUES (?,?,?,?,?,?)",
                (gen_id(), user_id, task_id, today(), 1, points)
            )
        except sqlite3.IntegrityError:
            pass

def undo_task(user_id, task_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM completions WHERE user_id=? AND task_id=? AND date_=?",
            (user_id, task_id, today())
        )

def complete_numeric(user_id, task_id, units, pts):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO completions (id,user_id,task_id,date_,units,points) VALUES (?,?,?,?,?,?)",
            (gen_id(), user_id, task_id, today(), units, pts)
        )

def compute_user_stats(uid, tasks_all):
    comps = get_completions(uid, today())
    comp_map = {c["task_id"]: c for c in comps}
    user_tasks = [t for t in tasks_all if t["assigned_to"] == "all" or t["assigned_to"] == uid]
    done = sum(1 for t in user_tasks if t["id"] in comp_map)
    pts = sum(c["points"] for c in comps)
    max_pts = sum(
        t["points"] if t["task_type"] == "check" else t["points_per_unit"] * t["target_units"]
        for t in user_tasks
    )
    pct = int(pts / max_pts * 100) if max_pts > 0 else 0
    return pts, done, len(user_tasks), pct, comp_map

# ─────────────────────────────────────────────
# مكونات مشتركة
# ─────────────────────────────────────────────
def theme_toggle_btn():
    icon = "☀️ نهاري" if is_dark() else "🌙 ليلي"
    if st.button(icon, key="theme_toggle"):
        st.session_state.theme = "light" if is_dark() else "dark"
        st.rerun()

def header_bar(user):
    t = T()
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1:
        role_label = "مدير النظام" if user["role"] == "admin" else "مستخدم"
        st.markdown(
            f'<h2 style="margin:0">👋 <span style="color:{t["accent"]}">{user["name"]}</span>'
            f' <span style="font-size:14px;color:{t["muted"]};font-weight:400">— {role_label}</span></h2>',
            unsafe_allow_html=True
        )
    with c2:
        theme_toggle_btn()
    with c3:
        if st.button("🚪 خروج", key="logout_btn"):
            st.session_state.user = None
            st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

def progress_html(pct):
    t = T()
    return (
        f'<div style="background:{t["surface2"]};border-radius:100px;height:6px;overflow:hidden;margin:5px 0">'
        f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{t["accent"]},{t["success"]});'
        f'border-radius:100px"></div></div>'
    )

def leaderboard_html(lb, groups, highlight_uid=None):
    t = T()
    medals = ["🥇", "🥈", "🥉"]
    html = ""
    for i, row in enumerate(lb):
        medal = medals[i] if i < 3 else str(i + 1)
        is_me = row.get("id") == highlight_uid
        bg     = t["accent_soft"] if is_me else t["surface"]
        border = t["accent"]      if is_me else t["border"]
        g_name = next((g["name"] for g in groups if g["id"] == row.get("group_id")), "")
        g_tag  = f'<span class="badge badge-purple">{g_name}</span>' if g_name else ""
        html += (
            f'<div style="background:{bg};border:1px solid {border};border-radius:11px;'
            f'padding:12px 16px;margin-bottom:7px;display:flex;align-items:center;gap:12px">'
            f'<span style="font-size:20px;min-width:30px;text-align:center">{medal}</span>'
            f'<div style="flex:1;min-width:0">'
            f'<div style="font-weight:700;font-size:14px;margin-bottom:3px;color:{t["text"]}">{row["name"]} {g_tag}</div>'
            f'{progress_html(row["pct"])}'
            f'</div>'
            f'<div style="text-align:center;min-width:60px">'
            f'<div style="color:{t["accent"]};font-weight:800;font-size:19px">{int(row["pts"])}</div>'
            f'<div style="color:{t["muted"]};font-size:11px">{row["pct"]}%</div>'
            f'</div></div>'
        )
    return html or f'<p style="color:{t["muted"]}">لا يوجد مستخدمون بعد.</p>'

# ─────────────────────────────────────────────
# صفحة تسجيل الدخول
# ─────────────────────────────────────────────
def login_page():
    inject_css()
    t = T()

    _, col_btn = st.columns([8, 1])
    with col_btn:
        theme_toggle_btn()

    _, col_mid, _ = st.columns([1, 1.1, 1])
    with col_mid:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:{t["surface"]};border:1px solid {t["border"]};border-radius:16px;'
            f'padding:36px 32px;text-align:center;margin-bottom:16px">'
            f'<p style="font-size:46px;margin:0 0 6px">⚡</p>'
            f'<h1 style="color:{t["accent"]};font-size:24px;margin:0 0 6px">منصة المهام</h1>'
            f'<p style="color:{t["muted"]};font-size:14px;margin:0">سجّل دخولك للمتابعة</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        with st.form("login"):
            username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
            password = st.text_input("🔒 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
            submitted = st.form_submit_button("دخول ←", use_container_width=True)

        if submitted:
            user = get_user(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

        st.markdown(
            f'<div style="background:{t["surface2"]};border:1px solid {t["border"]};border-radius:9px;'
            f'padding:10px;text-align:center;font-size:13px;color:{t["muted"]};margin-top:8px">'
            f'الآدمن: <b style="color:{t["accent"]}">admin</b> / <b style="color:{t["accent"]}">admin123</b>'
            f'</div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────
# لوحة المستخدم
# ─────────────────────────────────────────────
def user_dashboard(user):
    inject_css()
    t = T()
    header_bar(user)

    tasks_all = get_tasks(user["id"])
    pts, done, total, pct, comp_map = compute_user_stats(user["id"], tasks_all)

    tab_dash, tab_tasks = st.tabs(["📊  لوحة التحكم", "✅  مهامي اليوم"])

    with tab_dash:
        c1, c2, c3 = st.columns(3)
        c1.metric("⭐ نقاطي اليوم", int(pts))
        c2.metric("✅ منجز", f"{done}/{total}")
        c3.metric("📈 الإنجاز", f"{pct}%")
        st.progress(pct / 100)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # رسم شخصي
        days = last_7_days()
        df_p = pd.DataFrame([
            {"اليوم": d, "النقاط": sum(c["points"] for c in get_completions(user["id"], d))}
            for d in days
        ])
        fig_p = go.Figure(go.Scatter(
            x=df_p["اليوم"], y=df_p["النقاط"],
            mode="lines+markers",
            line=dict(color=t["accent"], width=2.5),
            marker=dict(size=7, color=t["accent"]),
            fill="tozeroy", fillcolor=t["accent_soft"],
        ))
        fig_p.update_layout(title="تقدمي – آخر 7 أيام", showlegend=False)
        st.plotly_chart(style_chart(fig_p), use_container_width=True)

        # رسم مجموعتي
        groups = get_groups()
        my_group = next((g for g in groups if g["id"] == user.get("group_id")), None)
        if my_group:
            st.markdown(f'<h3>👥 مجموعتي: {my_group["name"]}</h3>', unsafe_allow_html=True)
            members = [u for u in get_all_users() if u.get("group_id") == my_group["id"]]
            gd = [{"الاسم": m["name"], "النقاط": sum(c["points"] for c in get_completions(m["id"], today()))} for m in members]
            if gd:
                df_g = pd.DataFrame(gd)
                fig_g = px.bar(df_g, x="الاسم", y="النقاط", color_discrete_sequence=[t["success"]])
                fig_g.update_traces(marker_line_width=0)
                fig_g.update_layout(title="أداء المجموعة – اليوم", showlegend=False)
                st.plotly_chart(style_chart(fig_g), use_container_width=True)

        # لوحة الشرف
        st.markdown('<h3>🏆 لوحة الشرف – اليوم</h3>', unsafe_allow_html=True)
        all_tasks = get_tasks()
        all_users = get_all_users()
        lb = sorted([
            {**u,
             "pts": sum(c["points"] for c in get_completions(u["id"], today())),
             "pct": compute_user_stats(u["id"], all_tasks)[3]}
            for u in all_users
        ], key=lambda x: x["pts"], reverse=True)
        st.markdown(leaderboard_html(lb, groups, highlight_uid=user["id"]), unsafe_allow_html=True)

    with tab_tasks:
        st.markdown(f'<p style="color:{t["muted"]};margin-bottom:12px">اليوم: {today()}</p>', unsafe_allow_html=True)

        if not tasks_all:
            st.info("لا توجد مهام مُعيَّنة لك اليوم.")
            return

        done_count = sum(1 for tk in tasks_all if tk["id"] in comp_map)
        st.markdown(
            f'<span class="badge badge-green">✓ {done_count} منجز</span> '
            f'<span class="badge badge-gold">○ {len(tasks_all)-done_count} متبقٍ</span>',
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        for task in tasks_all:
            done_comp = comp_map.get(task["id"])
            is_done   = done_comp is not None
            all_badge = '<span class="badge badge-purple">للجميع</span>' if task["assigned_to"] == "all" else ""

            if task["task_type"] == "check":
                pts_badge  = f'<span class="badge badge-gold">⭐ {task["points"]} نقطة</span>'
                done_badge = '<span class="badge badge-green">✓ منجزة</span>' if is_done else ""
                title_style = f'color:{t["muted"]};text-decoration:line-through' if is_done else f'color:{t["text"]}'
                st.markdown(
                    f'<div class="{"task-card-done" if is_done else "task-card"}">'
                    f'<b style="font-size:15px;{title_style}">{task["title"]}</b>'
                    f'<div style="margin-top:7px">{pts_badge}{all_badge}{done_badge}</div>'
                    f'</div>', unsafe_allow_html=True
                )
                if is_done:
                    if st.button("↩ تراجع", key=f"undo_{task['id']}"):
                        undo_task(user["id"], task["id"]); st.rerun()
                else:
                    if st.button(f"✅ أنجزت: {task['title']}", key=f"chk_{task['id']}"):
                        complete_check(user["id"], task["id"], task["points"]); st.rerun()

            else:
                max_pts = task["points_per_unit"] * task["target_units"]
                with st.expander(
                    f'{"✅" if is_done else "○"} {task["title"]} — {task["target_units"]:.0f} {task["unit"]}',
                    expanded=not is_done
                ):
                    st.markdown(
                        f'<p style="color:{t["muted"]};font-size:13px;margin-bottom:10px">'
                        f'{task["points_per_unit"]} نقطة / {task["unit"]} &nbsp;|&nbsp; '
                        f'الهدف: {task["target_units"]:.0f} {task["unit"]} = {max_pts:.0f} نقطة</p>',
                        unsafe_allow_html=True
                    )
                    if is_done:
                        st.success(f"✓ أنجزت {done_comp['units']:.0f} {task['unit']} = {done_comp['points']:.0f} نقطة")
                        if st.button("↩ تعديل", key=f"undo_n_{task['id']}"):
                            undo_task(user["id"], task["id"]); st.rerun()
                    else:
                        with st.form(key=f"form_{task['id']}"):
                            units = st.number_input(
                                f"عدد {task['unit']} المُنجزة",
                                min_value=0.0, max_value=float(task["target_units"]),
                                value=0.0, step=1.0
                            )
                            if st.form_submit_button("📌 تسجيل الإنجاز", use_container_width=True):
                                if units > 0:
                                    complete_numeric(user["id"], task["id"], units, units * task["points_per_unit"])
                                    st.rerun()

# ─────────────────────────────────────────────
# لوحة الآدمن
# ─────────────────────────────────────────────
def admin_dashboard(user):
    inject_css()
    t = T()
    header_bar(user)

    tabs = st.tabs(["📊  لوحة التحكم", "👤  المستخدمون", "👥  المجموعات", "📋  المهام"])

    with tabs[0]:
        all_users   = get_all_users()
        all_tasks   = get_tasks()
        groups      = get_groups()
        comps_today = get_completions(date_=today())
        total_pts   = sum(c["points"] for c in comps_today)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👤 المستخدمون", len(all_users))
        c2.metric("📋 المهام",     len(all_tasks))
        c3.metric("⭐ نقاط اليوم", int(total_pts))
        c4.metric("👥 المجموعات", len(groups))
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # إجمالي 7 أيام
        days = last_7_days()
        df_d = pd.DataFrame([
            {"اليوم": d, "النقاط": sum(c["points"] for c in get_completions(date_=d))}
            for d in days
        ])
        fig_d = px.bar(df_d, x="اليوم", y="النقاط",
                       title="إجمالي النقاط – آخر 7 أيام",
                       color_discrete_sequence=[t["accent"]])
        fig_d.update_traces(marker_line_width=0)
        st.plotly_chart(style_chart(fig_d), use_container_width=True)

        col_l, col_r = st.columns(2)

        with col_l:
            if groups:
                gd = [{"المجموعة": g["name"],
                        "النقاط": sum(sum(c["points"] for c in get_completions(m["id"], today()))
                                      for m in [u for u in all_users if u.get("group_id") == g["id"]])}
                      for g in groups]
                df_g = pd.DataFrame(gd)
                fig_g = px.bar(df_g, x="المجموعة", y="النقاط",
                               title="تقدم المجموعات – اليوم",
                               color_discrete_sequence=[t["success"]])
                fig_g.update_traces(marker_line_width=0)
                st.plotly_chart(style_chart(fig_g), use_container_width=True)

        with col_r:
            user_stats = sorted([
                {"id": u["id"], "الاسم": u["name"],
                 "النقاط": compute_user_stats(u["id"], all_tasks)[0],
                 "pct": compute_user_stats(u["id"], all_tasks)[3]}
                for u in all_users
            ], key=lambda x: x["النقاط"], reverse=True)
            if user_stats:
                df_u = pd.DataFrame(user_stats)
                fig_u = px.bar(df_u, x="الاسم", y="النقاط",
                               title="أداء الأفراد – اليوم",
                               color_discrete_sequence=[t["warning"]])
                fig_u.update_traces(marker_line_width=0)
                st.plotly_chart(style_chart(fig_u), use_container_width=True)

        st.markdown('<h3>🏆 لوحة الشرف</h3>', unsafe_allow_html=True)
        lb = sorted([
            {**u,
             "pts": sum(c["points"] for c in get_completions(u["id"], today())),
             "pct": compute_user_stats(u["id"], all_tasks)[3]}
            for u in all_users
        ], key=lambda x: x["pts"], reverse=True)
        st.markdown(leaderboard_html(lb, groups), unsafe_allow_html=True)

    with tabs[1]:
        groups = get_groups()
        group_opts = {"بدون مجموعة": ""} | {g["name"]: g["id"] for g in groups}

        with st.expander("➕  إضافة مستخدم جديد"):
            with st.form("add_user"):
                c1, c2 = st.columns(2)
                new_name     = c1.text_input("الاسم الكامل")
                new_username = c2.text_input("اسم المستخدم")
                c3, c4 = st.columns(2)
                new_pw  = c3.text_input("كلمة المرور")
                new_grp = c4.selectbox("المجموعة", list(group_opts.keys()))
                if st.form_submit_button("إضافة المستخدم", use_container_width=True):
                    if new_name and new_username and new_pw:
                        ok = add_user(new_name, new_username, new_pw, group_opts[new_grp] or None)
                        st.success("✅ تم إضافة المستخدم") if ok else st.error("❌ اسم المستخدم موجود مسبقاً")
                        if ok: st.rerun()
                    else:
                        st.warning("يرجى تعبئة جميع الحقول")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        all_users = get_all_users()
        if not all_users:
            st.info("لا يوجد مستخدمون بعد.")

        for u in all_users:
            pts   = sum(c["points"] for c in get_completions(u["id"], today()))
            g_name = next((g["name"] for g in groups if g["id"] == u.get("group_id")), "—")
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.markdown(
                f'<b style="font-size:15px">{u["name"]}</b>'
                f'<br><span style="color:{t["muted"]};font-size:13px">@{u["username"]}</span>',
                unsafe_allow_html=True
            )
            c2.markdown(
                f'<span class="badge badge-gold">⭐ {int(pts)} اليوم</span>'
                f'<br><span class="badge badge-purple">{g_name}</span>',
                unsafe_allow_html=True
            )
            sel_grp = c3.selectbox(
                "المجموعة", list(group_opts.keys()),
                index=list(group_opts.values()).index(u.get("group_id") or ""),
                key=f"grp_{u['id']}", label_visibility="collapsed"
            )
            if c4.button("🗑", key=f"del_u_{u['id']}", use_container_width=True):
                delete_user(u["id"]); st.rerun()
            if group_opts[sel_grp] != (u.get("group_id") or ""):
                update_user_group(u["id"], group_opts[sel_grp] or None); st.rerun()
            st.divider()

    with tabs[2]:
        with st.expander("➕  إضافة مجموعة جديدة"):
            with st.form("add_group"):
                gname = st.text_input("اسم المجموعة", placeholder="مثال: فريق التطوير")
                if st.form_submit_button("إضافة", use_container_width=True):
                    if gname: add_group(gname); st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        groups    = get_groups()
        all_users = get_all_users()
        if not groups:
            st.info("لا توجد مجموعات بعد.")

        for g in groups:
            members  = [u for u in all_users if u.get("group_id") == g["id"]]
            gpts     = sum(sum(c["points"] for c in get_completions(m["id"], today())) for m in members)
            names_str = "، ".join(m["name"] for m in members) or "لا يوجد أعضاء"
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.markdown(
                f'<b style="font-size:15px">{g["name"]}</b>'
                f'<br><span style="color:{t["muted"]};font-size:13px">{len(members)} عضو: {names_str}</span>',
                unsafe_allow_html=True
            )
            c2.markdown(f'<span class="badge badge-gold">⭐ {int(gpts)} اليوم</span>', unsafe_allow_html=True)
            if c3.button("🗑 حذف", key=f"del_g_{g['id']}", use_container_width=True):
                delete_group(g["id"]); st.rerun()
            st.divider()

    with tabs[3]:
        all_users = get_all_users()
        all_tasks = get_tasks()
        user_opts = {"الجميع": "all"} | {u["name"]: u["id"] for u in all_users}

        with st.expander("➕  إضافة مهمة جديدة"):
            with st.form("add_task"):
                t_title    = st.text_input("عنوان المهمة", placeholder="مثال: قراءة كتاب")
                c1, c2     = st.columns(2)
                t_assigned = c1.selectbox("تعيين إلى", list(user_opts.keys()))
                t_type     = c2.selectbox("نوع المهمة", ["✅ إنجاز عادي", "🔢 كمي (بعدد)"])

                t_pts, t_unit, t_ppu, t_target = 10, "", 1.0, 1.0
                if "عادي" in t_type:
                    t_pts = st.number_input("النقاط عند الإنجاز", min_value=1, value=10)
                else:
                    c3, c4, c5 = st.columns(3)
                    t_unit   = c3.text_input("الوحدة", placeholder="صفحة / دقيقة / ...")
                    t_ppu    = c4.number_input("نقطة / وحدة", min_value=0.1, value=1.0, step=0.5)
                    t_target = c5.number_input("الهدف اليومي", min_value=1.0, value=20.0, step=1.0)
                    if t_unit:
                        st.markdown(
                            f'<div style="background:{t["accent_soft"]};border:1px solid {t["accent"]};'
                            f'border-radius:9px;padding:9px 14px;font-size:13px;color:{t["accent"]};margin-top:4px">'
                            f'🎯 الهدف: {t_target:.0f} {t_unit} = {t_ppu * t_target:.0f} نقطة كحد أقصى</div>',
                            unsafe_allow_html=True
                        )

                if st.form_submit_button("إضافة المهمة ←", use_container_width=True):
                    if t_title:
                        task_type = "check" if "عادي" in t_type else "numeric"
                        add_task(t_title, user_opts[t_assigned], task_type, t_pts, t_unit, t_ppu, t_target)
                        st.success("✅ تمت إضافة المهمة"); st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        comps_today = get_completions(date_=today())
        if not all_tasks:
            st.info("لا توجد مهام بعد.")

        for task in all_tasks:
            task_comps = [c for c in comps_today if c["task_id"] == task["id"]]
            assignee   = "الجميع" if task["assigned_to"] == "all" else next(
                (u["name"] for u in all_users if u["id"] == task["assigned_to"]), "—"
            )
            info = (f'⭐ {task["points"]} نقطة' if task["task_type"] == "check"
                    else f'📊 {task["points_per_unit"]} نق/{task["unit"]} × {task["target_units"]:.0f}')
            c1, c2 = st.columns([5, 1])
            c1.markdown(
                f'<div style="background:{t["surface"]};border:1px solid {t["border"]};'
                f'border-radius:11px;padding:13px 18px;margin-bottom:4px">'
                f'<b style="font-size:15px">{task["title"]}</b><br>'
                f'<div style="margin-top:7px">'
                f'<span class="badge badge-blue">👤 {assignee}</span>'
                f'<span class="badge badge-gold">{info}</span>'
                f'<span class="badge badge-green">✅ {len(task_comps)} اليوم</span>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            if c2.button("🗑", key=f"del_t_{task['id']}", use_container_width=True):
                delete_task(task["id"]); st.rerun()
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# نقطة الدخول
# ─────────────────────────────────────────────
def main():
    init_db()
    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        login_page()
    elif st.session_state.user["role"] == "admin":
        admin_dashboard(st.session_state.user)
    else:
        user_dashboard(st.session_state.user)

if __name__ == "__main__":
    main()
