import streamlit as st
from game_state import game
from data_store import GAME_DATA
from ai_manager import ai_bot

# ==================== 1. 配置 ====================
st.set_page_config(page_title="AI 泰国穷游 Pro", page_icon="🇹🇭", layout="wide")

# ==================== 2. 初始化页 (Setup) ====================
if st.session_state.get("player") is None:
    st.title("🇹🇭 AI 泰国穷游模拟器")
    st.markdown("### 🎒 自定义你的旅程")
    
    c1, c2 = st.columns(2)
    with c1:
        start_city = st.selectbox("出发城市", list(GAME_DATA.keys()))
        start_month = st.selectbox("旅行月份", list(range(1, 13)), index=9)
        start_time = st.slider("落地时间", 0, 23, 10)
    with c2:
        budget = st.number_input("预算 (THB)", 5000, 100000, 30000, step=1000)
        days = st.number_input("天数", 1, 30, 5)

    if st.button("🚀 开始旅程", type="primary"):
        with st.spinner("AI 正在准备行程数据..."):
            game.start_game(start_city, budget, start_time, days, start_month)
            st.rerun()
    
    st.divider()
    with st.expander("⚙️ API 设置 (可选)"):
        st.info("本项目依赖 **智谱 AI**。如果你有自己的 Key，请填入；否则使用公共额度。")
        key_input = st.text_input("智谱 API Key", type="password", placeholder="sk-...")
        if key_input:
            st.session_state["user_api_key"] = key_input
            st.success("✅ Key 已保存")
    st.stop()

# ==================== 3. 核心资源获取 (时间系统升级) ====================
player = game.data
current_city = player["city"]
city_desc = GAME_DATA[current_city]['description']
current_weather = player["weather"]
curr_h = player['time']

# --- 🕒 细化时间段逻辑 ---
if 5 <= curr_h < 12:
    time_phase = "morning"
    time_label = "🌅 上午"
    theme_color = "#4CAF50" # 绿意盎然
elif 12 <= curr_h < 17:
    time_phase = "noon"
    time_label = "☀️ 下午"
    theme_color = "#FF9800" # 烈日橙
elif 17 <= curr_h < 19:
    time_phase = "sunset"
    time_label = "🌆 黄昏"
    theme_color = "#9C27B0" # 紫霞
else:
    time_phase = "night"
    time_label = "🌙 夜晚"
    theme_color = "#2196F3" # 深蓝

# --- 背景图死锁逻辑 ---
# 注意：Key 加入了 time_phase，所以当时间从下午变黄昏，Key 会变，图会刷
current_state_key = f"{current_city}_{current_weather}_{time_phase}"

if "bg_image_url" not in st.session_state:
    st.session_state.bg_image_url = ""
if "bg_state_key" not in st.session_state:
    st.session_state.bg_state_key = ""

if st.session_state.bg_state_key != current_state_key:
    with st.spinner(f"AI 正在绘制场景: {current_city} ({time_label})..."):
        new_image_url = ai_bot.generate_city_card(current_city, city_desc, current_weather, time_phase)
        st.session_state.bg_image_url = new_image_url
        st.session_state.bg_state_key = current_state_key

image_url = st.session_state.bg_image_url
bgm_url = ai_bot.get_bgm(current_city)

# ==================== 4. CSS 样式 (完全沉浸版) ====================
st.markdown(f"""
<style>
    /* 1. 全屏背景图 */
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        transition: background-image 0.5s ease-in-out;
    }}

    /* 2. 关键修复：隐藏顶部 Header 的白底和装饰条 */
    header[data-testid="stHeader"] {{
        background: transparent !important; /* 背景变透明 */
        visibility: hidden; /* 彻底隐藏 (如果想保留右上角菜单，改用 background: transparent) */
    }}
    
    /* 隐藏顶部的彩色装饰线 */
    [data-testid="stDecoration"] {{
        display: none;
    }}

    /* 3. 暴力去除内容区顶部留白 */
    .block-container {{
        padding-top: 1rem !important; /* 让内容尽可能靠上 */
        padding-bottom: 2rem !important;
    }}
    
    /* 4. 侧边栏样式 */
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.85);
        border-right: 1px solid rgba(255,255,255,0.1);
        margin-top: 0 !important; /* 确保侧边栏也顶头 */
    }}
    
    /* 5. 全局文字白色 + 阴影 */
    h1, h2, h3, h4, p, span, div, label, .stMarkdown {{
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}
    
    /* 针对大标题的特殊处理 */
    h1 {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}

    /* 6. 按钮玻璃态 */
    .stButton>button {{
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        backdrop-filter: blur(5px);
        border-radius: 12px;
    }}
    .stButton>button:hover {{
        background: rgba(255, 255, 255, 0.35) !important;
        border-color: white !important;
        transform: scale(1.02);
    }}

    /* 7. 去除容器背景 */
    [data-testid="stVerticalBlock"] > div {{
        background-color: transparent !important;
        border: none !important;
    }}
    
    /* 8. 时间胶囊样式 */
    .time-capsule {{
        background-color: rgba(0,0,0,0.6);
        border-left: 5px solid {theme_color};
        padding: 10px 20px;
        border-radius: 10px;
        display: inline-block;
        text-align: right;
        backdrop-filter: blur(5px);
        float: right;
    }}
    .time-big {{
        font-size: 32px;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        line-height: 1;
        color: {theme_color} !important;
        text-shadow: 0 0 10px {theme_color}44 !important;
    }}
    .time-small {{
        font-size: 14px;
        color: #ddd !important;
        margin-top: 5px;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== 5. 页面渲染 ====================

# --- 顶部标题区 (时间显性化) ---
c1, c2 = st.columns([2, 1])
with c1:
    st.title(f"📍 {GAME_DATA[current_city]['name_cn']}")
    st.markdown(f"*{city_desc}*")
    w_icon = {"sunny":"☀️","cloudy":"☁️","rainy":"🌧️"}.get(current_weather, "✨")
    st.info(f"{w_icon} {current_weather.capitalize()}")

with c2:
    # 使用 HTML 渲染醒目的时间胶囊
    st.markdown(f"""
    <div class="time-capsule">
        <div class="time-big">{int(curr_h):02d}:00</div>
        <div class="time-small">Day {player['day']} | {time_label}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 侧边栏 ---
with st.sidebar:
    st.header("🎒 背包")
    st.subheader(f"💰 {player['money']:,}")
    st.subheader(f"⚡ {player['stamina']}/100")
    st.divider()
    st.markdown("🎵 **BGM**")
    auto_play = st.toggle("自动播放", value=True)
    st.audio(bgm_url, start_time=0, autoplay=auto_play, loop=True)
    st.divider()
    with st.expander("🔑 API 设置"):
        user_key = st.text_input("API Key", type="password", key="sidebar_api_input")
        if user_key: st.session_state["user_api_key"] = user_key
    st.divider()
    if st.button("🔄 重开游戏"):
        st.session_state.player = None
        st.rerun()

# --- 核心游戏区 ---
if player["time"] == 8 and not player["hotel_settled"]:
    st.subheader("🏨 选择住宿")
    opts = game.get_hotel_options()
    cols = st.columns(3)
    for i, h in enumerate(opts):
        with cols[i]:
            if st.button(f"{h['name']}\n{h['price']}฿", key=f"h_{i}"):
                if player["money"] >= h['price']:
                    game._update(money=h['price'], time=1)
                    player["hotel_settled"] = True
                    st.rerun()
                else: st.toast("没钱！")
    st.stop()

t1, t2, t3 = st.tabs(["🎡 游玩", "🚀 移动", "🛌 休息"])

with t1:
    valid_acts = []
    curr = player['time']
    for act in GAME_DATA[current_city]['activities']:
        if act['type']=='scenic' and act['id'] in player['visited_activities']: continue
        is_open = False
        if act['type']=='scenic': is_open=(8<=curr<17)
        elif act['type']=='night': is_open=(curr>=18)
        else: is_open=(8<=curr<22)
        if is_open: valid_acts.append(act)
    
    if not valid_acts: st.warning("暂无活动")
    
    for act in valid_acts:
        c_info, c_btn = st.columns([3, 1])
        with c_info:
            st.markdown(f"**{act['name']}**")
            st.caption(f"💰{act['cost_money']} | ⏳{act['cost_time']}h | ⚡{act['cost_stamina']}")
        with c_btn:
            st.write("")
            if st.button("Go", key=f"go_{act['id']}"):
                if player["money"]<act["cost_money"]: st.toast("钱不够")
                elif player["stamina"]<act["cost_stamina"]: st.toast("累")
                else:
                    game.do_activity(act['id'], act['cost_money'], act['cost_stamina'], act['cost_time'], act['name'])
                    st.rerun()
        st.markdown("---")

with t2:
    moves = game.get_travel_choices()
    curr_h = player['time']
    is_night = curr_h >= 18 or curr_h < 8
    if not moves: st.info("孤岛，无路可走")
    for tgt, info in moves.items():
        mode = info['mode']
        is_flight_kw = any(k in mode for k in ["飞机", "航班", "直飞"])
        has_ground_kw = any(k in mode for k in ["船", "车", "巴", "火车", "联运"])
        is_pure_flight = is_flight_kw and not has_ground_kw
        is_allowed = (not is_night) or (is_night and is_pure_flight)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**➡️ {GAME_DATA[tgt]['name_cn']}**")
            if not is_allowed: st.caption(f"🚫 {mode} (夜间停运)")
            else: st.caption(f"{info['mode']} ({info['cost_time']}h) | ⚡-{info['cost_stamina']}")
        with c2:
            st.write("")
            if st.button("出发", key=f"mv_{tgt}", disabled=not is_allowed):
                if player["stamina"]<info["cost_stamina"]: st.toast("体力不够")
                else:
                    game.travel_to(tgt)
                    st.rerun()
        st.markdown("---")
        
    if st.button("🏠 结束行程回家", type="primary"):
        game.finish_game()
        st.rerun()

with t3:
    if 6<=player['time']<18:
        h = st.slider("午睡", 1, 4, 2)
        if st.button("睡觉"):
            game.sleep(h)
            st.rerun()
    if st.button("💤 睡到明天 (08:00)"):
        game.sleep(None)
        st.rerun()

if player["game_over"]:
    is_success = player.get("success", False)
    final_money = player['money']
    visited_count = len(player['visited_activities'])
    total_days = player['day']
    
    with st.spinner("AI 正在生成旅行纪念册..."):
        end_image_url = ai_bot.generate_ending_card(is_success, current_city)
    
    if is_success: st.balloons()
    else: st.snow()

    st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{ display: none; }}
        .block-container {{ padding-top: 0 !important; }}
        .stApp {{ background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("{image_url}"); }}
        
        .end-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            padding: 40px;
            margin: 5vh auto;
            max-width: 700px;
            text-align: center;
            color: #333 !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }}
        .end-card * {{ color: #333 !important; text-shadow: none !important; }}
        .memory-photo {{
            width: 100%;
            border-radius: 16px;
            margin-bottom: 20px;
            transform: rotate(-2deg);
            border: 8px solid white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 25px;
        }}
        .stat-val {{ font-size: 24px; font-weight: bold; color: #0066cc !important; }}
    </style>
    """, unsafe_allow_html=True)

    html_content = f"""
    <div class="end-card">
        <img src="{end_image_url}" class="memory-photo">
        <h1>{"🎉 完美旅程" if is_success else "🥀 旅程结束"}</h1>
        <p style="font-size: 18px; margin: 20px 0;">“{player['fail_reason']}”</p>
        <div class="stat-grid">
            <div><div class="stat-val">{total_days} 天</div><div>生存时间</div></div>
            <div><div class="stat-val">{visited_count} 个</div><div>打卡地点</div></div>
            <div><div class="stat-val">{final_money:,} ฿</div><div>剩余资金</div></div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🔄 开启新旅程", type="primary"):
            st.session_state.player = None
            st.rerun()
    st.stop()
