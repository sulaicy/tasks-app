"""
منصة متابعة المهام اليومية
Task Tracker - Built with Python, Streamlit, SQLite, Plotly
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
    page_title="منصة المهام ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS مخصص
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap');

* { font-family: 'Tajawal', sans-serif !important; }
html, body, [class*="css"] { direction: rtl; }

.main { background: #06080f; }
.stApp { background: #06080f; color: #e8eaf0; }
.stApp > header { background: #0e1320; border-bottom: 1px solid #1e2640; }

/* بطاقات */
.task-card {
    background: #0e1320;
    border: 1px solid #1e2640;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all .2s;
}
.task-card-done {
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 10px;
}
.stat-card {
    background: #0e1320;
    border: 1px solid #1e2640;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin: 2px;
}
.badge-gold { background: #3d2e0a; color: #e8b84b; }
.badge-green { background: #052e16; color: #22c55e; }
.badge-blue { background: #1e3a5f; color: #93c5fd; }
.badge-purple { background: #2e1065; color: #d8b4fe; }

/* أزرار */
.stButton > button {
    background: linear-gradient(135deg, #e8b84b, #c99a30);
    color: #06080f;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-family: 'Tajawal', sans-serif !important;
    padding: 8px 20px;
    transition: all .2s;
}
.stButton > button:hover { filter: brightness(1.1); transform: translateY(-1px); }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: #141926 !important;
    border: 1px solid #1e2640 !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: 'Tajawal', sans-serif !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: #0e1320;
    color: #8892a4;
    border-radius: 8px;
    margin-left: 4px;
    font-family: 'Tajawal', sans-serif !important;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #1e2640 !important;
    color: #e8b84b !important;
}
.stTabs [data-baseweb="tab-list"] { background: #0e1320; border-radius: 12px; padding: 6px; }

/* Progress bars */
.stProgress > div > div { background: linear-gradient(90deg, #e8b84b, #22c55e); border-radius: 100px; }

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: #0e1320;
    border-left: 1px solid #1e2640;
}

div[data-testid="metric-container"] {
    background: #0e1320;
    border: 1px solid #1e2640;
    border-radius: 14px;
    padding: 16px;
}
div[data-testid="metric-container"] > label { color: #8892a4; }
div[data-testid="metric-container"] > div { color: #e8b84b; font-weight: 900; }

h1, h2, h3 { color: #e8eaf0 !important; }

.gold-title { color: #e8b84b; font-size: 2rem; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

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
        # إنشاء حساب admin افتراضي
        exists = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, name, role) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), "admin", hash_pw("admin123"), "المدير", "admin")
            )

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def today() -> str:
    return date.today().isoformat()

def gen_id() -> str:
    return str(uuid.uuid4())[:8]

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
        rows = conn.execute("SELECT * FROM users WHERE role != 'admin'").fetchall()
        return [dict(r) for r in rows]

def add_user(name, username, password, group_id=None):
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, name, role, group_id) VALUES (?,?,?,?,?,?)",
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
        conn.execute("INSERT INTO groups_ (id, name) VALUES (?,?)", (gen_id(), name))

def delete_group(gid):
    with get_db() as conn:
        conn.execute("DELETE FROM groups_ WHERE id=?", (gid,))
        conn.execute("UPDATE users SET group_id=NULL WHERE group_id=?", (gid,))

def update_group(gid, name):
    with get_db() as conn:
        conn.execute("UPDATE groups_ SET name=? WHERE id=?", (name, gid))

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
        if date_: q += " AND date_=?"; params.append(date_)
        return [dict(r) for r in conn.execute(q, params).fetchall()]

def complete_check(user_id, task_id, points):
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO completions (id,user_id,task_id,date_,units,points) VALUES (?,?,?,?,?,?)",
                (gen_id(), user_id, task_id, today(), 1, points)
            )
        except sqlite3.IntegrityError:
            pass  # already done

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

# ─────────────────────────────────────────────
# مساعدات العرض
# ─────────────────────────────────────────────
def dark_chart(fig):
    fig.update_layout(
        paper_bgcolor="#06080f",
        plot_bgcolor="#06080f",
        font=dict(family="Tajawal", color="#8892a4"),
        xaxis=dict(gridcolor="#1e2640", zerolinecolor="#1e2640"),
        yaxis=dict(gridcolor="#1e2640", zerolinecolor="#1e2640"),
        margin=dict(t=30, b=30, l=10, r=10),
    )
    return fig

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
    pct = int((pts / max_pts * 100)) if max_pts > 0 else 0
    return pts, done, len(user_tasks), pct, comp_map

# ─────────────────────────────────────────────
# صفحة تسجيل الدخول
# ─────────────────────────────────────────────
def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div style="text-align:center;padding:40px 0 20px">', unsafe_allow_html=True)
        st.markdown('<p style="font-size:52px;margin:0">⚡</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="gold-title" style="text-align:center">منصة المهام</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#8892a4;text-align:center;margin-bottom:30px">سجّل دخولك للمتابعة</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 اسم المستخدم")
            password = st.text_input("🔒 كلمة المرور", type="password")
            submitted = st.form_submit_button("دخول ←", use_container_width=True)

        if submitted:
            user = get_user(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

        st.markdown("""
        <div style="background:#141926;border:1px solid #1e2640;border-radius:10px;
                    padding:12px;text-align:center;font-size:13px;color:#8892a4;margin-top:16px">
            حساب الآدمن الافتراضي: <b style="color:#e8b84b">admin</b> / <b style="color:#e8b84b">admin123</b>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# لوحة المستخدم
# ─────────────────────────────────────────────
def user_dashboard(user):
    tasks_all = get_tasks(user["id"])
    pts, done, total, pct, comp_map = compute_user_stats(user["id"], tasks_all)

    # هيدر
    col_a, col_b = st.columns([4, 1])
    with col_a:
        st.markdown(f'<h2>👋 أهلاً، <span style="color:#e8b84b">{user["name"]}</span></h2>', unsafe_allow_html=True)
    with col_b:
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    tab_dash, tab_tasks = st.tabs(["📊 لوحة التحكم", "✅ مهامي اليوم"])

    # ═══════════════ TAB: DASHBOARD ═══════════════
    with tab_dash:
        # إحصاءات
        c1, c2, c3 = st.columns(3)
        c1.metric("⭐ نقاطي اليوم", pts)
        c2.metric("✅ منجز", f"{done}/{total}")
        c3.metric("📈 نسبة الإنجاز", f"{pct}%")
        st.progress(pct / 100)

        st.divider()

        # رسم بياني شخصي - آخر 7 أيام
        days = last_7_days()
        personal_data = []
        for d in days:
            comps = get_completions(user["id"], d)
            p = sum(c["points"] for c in comps)
            personal_data.append({"التاريخ": d, "النقاط": p})

        df_personal = pd.DataFrame(personal_data)
        fig_personal = go.Figure(go.Scatter(
            x=df_personal["التاريخ"], y=df_personal["النقاط"],
            mode="lines+markers",
            line=dict(color="#e8b84b", width=3),
            marker=dict(size=8, color="#e8b84b"),
            fill="tozeroy", fillcolor="rgba(232,184,75,0.08)"
        ))
        fig_personal.update_layout(title="📈 تقدمي - آخر 7 أيام")
        st.plotly_chart(dark_chart(fig_personal), use_container_width=True)

        # رسم بياني للمجموعة
        groups = get_groups()
        my_group = next((g for g in groups if g["id"] == user.get("group_id")), None)
        if my_group:
            st.markdown(f'<h3>👥 مجموعتي: {my_group["name"]}</h3>', unsafe_allow_html=True)
            all_tasks = get_tasks()
            group_members = [u for u in get_all_users() if u["group_id"] == my_group["id"]]
            gd = []
            for m in group_members:
                comps = get_completions(m["id"], today())
                p = sum(c["points"] for c in comps)
                gd.append({"الاسم": m["name"], "النقاط": p})
            if gd:
                df_g = pd.DataFrame(gd)
                fig_g = px.bar(df_g, x="الاسم", y="النقاط",
                               color_discrete_sequence=["#a855f7"])
                fig_g.update_traces(marker_line_width=0)
                st.plotly_chart(dark_chart(fig_g), use_container_width=True)

        # لوحة الشرف
        st.divider()
        st.markdown('<h3>🏆 لوحة الشرف - اليوم</h3>', unsafe_allow_html=True)
        all_users = get_all_users()
        all_tasks = get_tasks()
        leaderboard = []
        for u in all_users:
            upts, udone, utotal, upct, _ = compute_user_stats(u["id"], all_tasks)
            g = next((g["name"] for g in groups if g["id"] == u.get("group_id")), "")
            leaderboard.append({"name": u["name"], "pts": upts, "pct": upct, "group": g, "is_me": u["id"] == user["id"]})
        leaderboard.sort(key=lambda x: x["pts"], reverse=True)

        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(leaderboard):
            medal = medals[i] if i < 3 else f"{i+1}"
            bg = "rgba(232,184,75,0.08)" if row["is_me"] else "#0e1320"
            border = "rgba(232,184,75,0.4)" if row["is_me"] else "#1e2640"
            g_tag = f'<span class="badge badge-purple">{row["group"]}</span>' if row["group"] else ""
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:12px;
                        padding:14px 18px;margin-bottom:8px;display:flex;align-items:center;gap:12px">
                <span style="font-size:22px;min-width:36px">{medal}</span>
                <div style="flex:1">
                    <b style="font-size:15px">{row['name']}</b> {g_tag}
                    <div style="background:#1e2640;border-radius:100px;height:6px;margin-top:6px;overflow:hidden">
                        <div style="width:{row['pct']}%;height:100%;background:linear-gradient(90deg,#e8b84b,#22c55e);border-radius:100px"></div>
                    </div>
                </div>
                <div style="text-align:center;min-width:70px">
                    <div style="color:#e8b84b;font-size:20px;font-weight:900">{row['pts']}</div>
                    <div style="color:#8892a4;font-size:11px">نقطة</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════ TAB: TASKS ═══════════════
    with tab_tasks:
        st.markdown(f'<h3>✅ مهام اليوم — {today()}</h3>', unsafe_allow_html=True)

        if not tasks_all:
            st.markdown('<div style="text-align:center;padding:60px;color:#8892a4"><p style="font-size:40px">🎉</p><p>لا توجد مهام اليوم</p></div>', unsafe_allow_html=True)
            return

        for task in tasks_all:
            done_comp = comp_map.get(task["id"])
            is_done = done_comp is not None

            with st.container():
                if task["task_type"] == "check":
                    c1, c2 = st.columns([6, 2])
                    with c1:
                        pts_badge = f'<span class="badge badge-gold">⭐ {task["points"]} نقطة</span>'
                        all_badge = '<span class="badge badge-purple">للجميع</span>' if task["assigned_to"] == "all" else ""
                        done_badge = '<span class="badge badge-green">✓ منجز</span>' if is_done else ""
                        style = "text-decoration:line-through;color:#8892a4" if is_done else "color:#e8eaf0"
                        st.markdown(f"""
                        <div class="{'task-card-done' if is_done else 'task-card'}">
                            <b style="{style};font-size:16px">{task['title']}</b><br>
                            <div style="margin-top:8px">{pts_badge}{all_badge}{done_badge}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        if is_done:
                            if st.button("↩ تراجع", key=f"undo_{task['id']}", use_container_width=True):
                                undo_task(user["id"], task["id"])
                                st.rerun()
                        else:
                            if st.button("✅ أنجزت!", key=f"check_{task['id']}", use_container_width=True):
                                complete_check(user["id"], task["id"], task["points"])
                                st.rerun()

                else:  # numeric
                    with st.expander(f"📊 {task['title']} {'✓' if is_done else ''}", expanded=not is_done):
                        max_pts = task["points_per_unit"] * task["target_units"]
                        st.markdown(f"""
                        <div style="color:#8892a4;font-size:13px;margin-bottom:10px">
                            {task['points_per_unit']} نقطة لكل {task['unit']} | الهدف: {task['target_units']} {task['unit']} = {max_pts:.0f} نقطة
                        </div>
                        """, unsafe_allow_html=True)

                        if is_done:
                            st.success(f"✓ أنجزت {done_comp['units']} {task['unit']} = {done_comp['points']:.0f} نقطة")
                            if st.button("↩ تعديل", key=f"undo_n_{task['id']}"):
                                undo_task(user["id"], task["id"])
                                st.rerun()
                        else:
                            with st.form(key=f"form_{task['id']}"):
                                units = st.number_input(
                                    f"عدد {task['unit']}",
                                    min_value=0.0,
                                    max_value=float(task["target_units"]),
                                    value=0.0,
                                    step=1.0
                                )
                                if st.form_submit_button("تسجيل الإنجاز", use_container_width=True):
                                    if units > 0:
                                        pts_earned = min(units, task["target_units"]) * task["points_per_unit"]
                                        complete_numeric(user["id"], task["id"], units, pts_earned)
                                        st.rerun()

# ─────────────────────────────────────────────
# لوحة الآدمن
# ─────────────────────────────────────────────
def admin_dashboard(user):
    col_a, col_b = st.columns([4, 1])
    with col_a:
        st.markdown('<h2>⚡ <span style="color:#e8b84b">لوحة تحكم الآدمن</span></h2>', unsafe_allow_html=True)
    with col_b:
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    tabs = st.tabs(["📊 لوحة التحكم", "👤 المستخدمون", "👥 المجموعات", "📋 المهام"])

    # ═══════════════ TAB: DASHBOARD ═══════════════
    with tabs[0]:
        all_users = get_all_users()
        all_tasks = get_tasks()
        groups = get_groups()
        comps_today = get_completions(date_=today())

        total_pts = sum(c["points"] for c in comps_today)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👤 المستخدمون", len(all_users))
        c2.metric("📋 المهام", len(all_tasks))
        c3.metric("⭐ نقاط اليوم", int(total_pts))
        c4.metric("👥 المجموعات", len(groups))

        st.divider()

        # إجمالي النقاط آخر 7 أيام
        days = last_7_days()
        daily_data = []
        for d in days:
            comps = get_completions(date_=d)
            p = sum(c["points"] for c in comps)
            daily_data.append({"اليوم": d, "النقاط": p})

        df_d = pd.DataFrame(daily_data)
        fig_d = px.bar(df_d, x="اليوم", y="النقاط",
                       title="📈 إجمالي النقاط - آخر 7 أيام",
                       color_discrete_sequence=["#e8b84b"])
        fig_d.update_traces(marker_line_width=0, marker_corner_radius=6)
        st.plotly_chart(dark_chart(fig_d), use_container_width=True)

        col_left, col_right = st.columns(2)

        # تقدم المجموعات
        with col_left:
            if groups:
                gd = []
                for g in groups:
                    members = [u for u in all_users if u.get("group_id") == g["id"]]
                    gpts = sum(
                        sum(c["points"] for c in get_completions(m["id"], today()))
                        for m in members
                    )
                    gd.append({"المجموعة": g["name"], "النقاط": gpts})
                df_g = pd.DataFrame(gd)
                fig_g = px.bar(df_g, x="المجموعة", y="النقاط",
                               title="👥 تقدم المجموعات - اليوم",
                               color_discrete_sequence=["#a855f7"])
                fig_g.update_traces(marker_line_width=0, marker_corner_radius=6)
                st.plotly_chart(dark_chart(fig_g), use_container_width=True)

        # أداء الأفراد
        with col_right:
            user_stats = []
            for u in all_users:
                upts, _, _, upct, _ = compute_user_stats(u["id"], all_tasks)
                user_stats.append({"الاسم": u["name"], "النقاط": upts, "pct": upct})
            user_stats.sort(key=lambda x: x["النقاط"], reverse=True)
            if user_stats:
                df_u = pd.DataFrame(user_stats)
                fig_u = px.bar(df_u, x="الاسم", y="النقاط",
                               title="🏆 أداء الأفراد - اليوم",
                               color_discrete_sequence=["#22c55e"])
                fig_u.update_traces(marker_line_width=0, marker_corner_radius=6)
                st.plotly_chart(dark_chart(fig_u), use_container_width=True)

        # لوحة الشرف
        st.divider()
        st.markdown('<h3>🏆 لوحة الشرف التفصيلية</h3>', unsafe_allow_html=True)
        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(user_stats):
            medal = medals[i] if i < 3 else f"{i+1}"
            st.markdown(f"""
            <div style="background:#0e1320;border:1px solid #1e2640;border-radius:12px;
                        padding:12px 18px;margin-bottom:8px;display:flex;align-items:center;gap:12px">
                <span style="font-size:20px;min-width:36px">{medal}</span>
                <div style="flex:1">
                    <b>{row['الاسم']}</b>
                    <div style="background:#1e2640;border-radius:100px;height:6px;margin-top:6px;overflow:hidden">
                        <div style="width:{row['pct']}%;height:100%;background:linear-gradient(90deg,#e8b84b,#22c55e);border-radius:100px"></div>
                    </div>
                </div>
                <div style="color:#e8b84b;font-weight:900;font-size:18px;min-width:80px;text-align:center">
                    {row['النقاط']:.0f} ⭐
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════ TAB: USERS ═══════════════
    with tabs[1]:
        st.markdown('<h3>👤 إدارة المستخدمين</h3>', unsafe_allow_html=True)
        groups = get_groups()
        group_opts = {"بدون مجموعة": ""} | {g["name"]: g["id"] for g in groups}

        with st.expander("➕ إضافة مستخدم جديد", expanded=False):
            with st.form("add_user_form"):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("الاسم الكامل")
                new_username = c2.text_input("اسم المستخدم")
                c3, c4 = st.columns(2)
                new_password = c3.text_input("كلمة المرور")
                new_group_label = c4.selectbox("المجموعة", list(group_opts.keys()))
                submitted = st.form_submit_button("إضافة", use_container_width=True)
                if submitted:
                    if new_name and new_username and new_password:
                        gid = group_opts[new_group_label]
                        ok = add_user(new_name, new_username, new_password, gid or None)
                        if ok:
                            st.success("✅ تم إضافة المستخدم")
                            st.rerun()
                        else:
                            st.error("❌ اسم المستخدم موجود مسبقاً")
                    else:
                        st.warning("يرجى تعبئة جميع الحقول")

        st.divider()
        all_users = get_all_users()
        for u in all_users:
            comps = get_completions(u["id"], today())
            pts = sum(c["points"] for c in comps)
            g = next((g["name"] for g in groups if g["id"] == u.get("group_id")), "بدون مجموعة")

            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                c1.markdown(f'<b>{u["name"]}</b><br><span style="color:#8892a4;font-size:13px">@{u["username"]}</span>', unsafe_allow_html=True)
                c2.markdown(f'<span class="badge badge-gold">⭐ {pts:.0f} اليوم</span><br><span class="badge badge-purple">{g}</span>', unsafe_allow_html=True)
                new_group = c3.selectbox("المجموعة", list(group_opts.keys()),
                                         index=list(group_opts.values()).index(u.get("group_id") or ""),
                                         key=f"grp_{u['id']}", label_visibility="collapsed")
                if c4.button("🗑 حذف", key=f"del_u_{u['id']}", use_container_width=True):
                    delete_user(u["id"])
                    st.rerun()
                if group_opts[new_group] != (u.get("group_id") or ""):
                    update_user_group(u["id"], group_opts[new_group] or None)
                    st.rerun()
                st.divider()

    # ═══════════════ TAB: GROUPS ═══════════════
    with tabs[2]:
        st.markdown('<h3>👥 إدارة المجموعات</h3>', unsafe_allow_html=True)
        groups = get_groups()
        all_users = get_all_users()

        with st.expander("➕ إضافة مجموعة جديدة", expanded=False):
            with st.form("add_group_form"):
                gname = st.text_input("اسم المجموعة")
                if st.form_submit_button("إضافة", use_container_width=True):
                    if gname:
                        add_group(gname)
                        st.rerun()

        st.divider()
        for g in groups:
            members = [u for u in all_users if u.get("group_id") == g["id"]]
            pts = sum(
                sum(c["points"] for c in get_completions(m["id"], today()))
                for m in members
            )
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.markdown(f'<b style="font-size:15px">{g["name"]}</b><br><span style="color:#8892a4;font-size:13px">{len(members)} عضو: {", ".join(m["name"] for m in members) or "—"}</span>', unsafe_allow_html=True)
                c2.markdown(f'<span class="badge badge-gold">⭐ {pts:.0f} اليوم</span>', unsafe_allow_html=True)
                if c3.button("🗑 حذف", key=f"del_g_{g['id']}", use_container_width=True):
                    delete_group(g["id"])
                    st.rerun()
                st.divider()

    # ═══════════════ TAB: TASKS ═══════════════
    with tabs[3]:
        st.markdown('<h3>📋 إدارة المهام</h3>', unsafe_allow_html=True)
        all_users = get_all_users()
        all_tasks = get_tasks()

        user_opts = {"الجميع": "all"} | {u["name"]: u["id"] for u in all_users}

        with st.expander("➕ إضافة مهمة جديدة", expanded=False):
            with st.form("add_task_form"):
                t_title = st.text_input("عنوان المهمة")
                c1, c2 = st.columns(2)
                t_assigned = c1.selectbox("تعيين إلى", list(user_opts.keys()))
                t_type = c2.selectbox("نوع المهمة", ["✅ إنجاز عادي", "🔢 كمي (بعدد)"])

                t_pts = 10
                t_unit = ""
                t_ppu = 1.0
                t_target = 1.0

                if "عادي" in t_type:
                    t_pts = st.number_input("النقاط", min_value=1, value=10)
                else:
                    c3, c4, c5 = st.columns(3)
                    t_unit = c3.text_input("الوحدة", placeholder="صفحة / دقيقة / ...")
                    t_ppu = c4.number_input("نقطة/وحدة", min_value=0.1, value=1.0, step=0.5)
                    t_target = c5.number_input("الهدف", min_value=1.0, value=20.0, step=1.0)

                if st.form_submit_button("إضافة المهمة", use_container_width=True):
                    if t_title:
                        task_type = "check" if "عادي" in t_type else "numeric"
                        add_task(t_title, user_opts[t_assigned], task_type, t_pts, t_unit, t_ppu, t_target)
                        st.success("✅ تم إضافة المهمة")
                        st.rerun()

        st.divider()
        comps_today = get_completions(date_=today())
        if not all_tasks:
            st.info("لا توجد مهام بعد. أضف مهمة من القسم أعلاه.")

        for task in all_tasks:
            task_comps = [c for c in comps_today if c["task_id"] == task["id"]]
            assignee = "الجميع" if task["assigned_to"] == "all" else next(
                (u["name"] for u in all_users if u["id"] == task["assigned_to"]), "—"
            )
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    if task["task_type"] == "check":
                        info = f'⭐ {task["points"]} نقطة'
                    else:
                        info = f'📊 {task["points_per_unit"]} نق/{task["unit"]} × {task["target_units"]}'
                    st.markdown(f"""
                    <div style="background:#0e1320;border:1px solid #1e2640;border-radius:12px;padding:14px 18px;margin-bottom:4px">
                        <b style="font-size:15px">{task['title']}</b><br>
                        <div style="margin-top:8px">
                            <span class="badge badge-blue">👤 {assignee}</span>
                            <span class="badge badge-gold">{info}</span>
                            <span class="badge badge-green">✅ {len(task_comps)} اليوم</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("🗑 حذف", key=f"del_t_{task['id']}", use_container_width=True):
                        delete_task(task["id"])
                        st.rerun()
                st.write("")

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
