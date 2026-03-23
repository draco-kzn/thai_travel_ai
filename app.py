import streamlit as st

from ai_manager import ai_bot
from data_store import CITY_GUIDES, GAME_DATA, activity_is_available, activity_time_label
from game_state import game
from travel_realtime import (
    build_realtime_flight_plan,
    format_date_for_api,
    get_city_realtime_meta,
    has_amadeus_credentials,
    infer_hotel_dates,
    infer_trip_date,
    search_live_flights,
    search_live_hotels,
)


st.set_page_config(page_title="AI 泰国穷游 Pro", page_icon="🇹🇭", layout="wide")

default_bg = "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"


if st.session_state.get("player"):
    player = game.data
    current_city = player["city"]
    city_desc = GAME_DATA[current_city]["description"]
    current_weather = player["weather"]
    curr_h = player["time"]

    if 5 <= curr_h < 12:
        time_phase, time_label, theme_color = "morning", "清晨", "#7BD389"
    elif 12 <= curr_h < 17:
        time_phase, time_label, theme_color = "noon", "午后", "#FFB703"
    elif 17 <= curr_h < 19:
        time_phase, time_label, theme_color = "sunset", "黄昏", "#F4A261"
    else:
        time_phase, time_label, theme_color = "night", "夜晚", "#74C0FC"

    current_state_key = f"{current_city}_{current_weather}_{time_phase}"
    if "bg_image_url" not in st.session_state:
        st.session_state.bg_image_url = ""
    if "bg_state_key" not in st.session_state:
        st.session_state.bg_state_key = ""

    if st.session_state.bg_state_key != current_state_key:
        with st.spinner(f"AI 正在绘制场景：{GAME_DATA[current_city]['name_cn']} · {time_label}"):
            st.session_state.bg_image_url = ai_bot.generate_city_card(
                current_city, city_desc, current_weather, time_phase
            )
            st.session_state.bg_state_key = current_state_key

    bg_image = st.session_state.bg_image_url
    bgm_url = ai_bot.get_bgm(current_city, time_phase)
else:
    bg_image = default_bg
    theme_color = "#7BD389"
    curr_h = 10


st.markdown(
    f"""
<style>
    .stApp {{
        background-image:
            linear-gradient(rgba(3, 8, 17, 0.35), rgba(3, 8, 17, 0.68)),
            radial-gradient(circle at top left, rgba(255, 209, 102, 0.18), transparent 30%),
            radial-gradient(circle at right center, rgba(116, 192, 252, 0.14), transparent 24%),
            url("{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        transition: background-image 0.5s ease-in-out;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        visibility: hidden;
    }}
    [data-testid="stDecoration"] {{
        display: none;
    }}
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1240px;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.82);
        border-right: 1px solid rgba(255,255,255,0.08);
        margin-top: 0 !important;
    }}
    h1, h2, h3, h4, p, span, div, label, .stMarkdown {{
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.55);
    }}
    h1 {{
        margin-top: 0 !important;
        padding-top: 0 !important;
        letter-spacing: -0.03em;
    }}
    [data-testid="stVerticalBlock"] > div {{
        background-color: transparent !important;
        border: none !important;
    }}
    .stButton > button {{
        background: rgba(255, 255, 255, 0.14) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.32) !important;
        backdrop-filter: blur(5px);
        border-radius: 14px;
        transition: all 0.18s ease;
    }}
    .stButton > button:hover {{
        background: rgba(255, 255, 255, 0.24) !important;
        border-color: rgba(255,255,255,0.72) !important;
        transform: translateY(-1px);
    }}
    .stButton > button[kind="primary"] {{
        width: 100%;
        min-height: 56px;
        border: none !important;
        border-radius: 18px !important;
        background: linear-gradient(135deg, #FFD166 0%, #F4A261 42%, #E76F51 100%) !important;
        color: #151515 !important;
        font-weight: 800 !important;
        box-shadow: 0 18px 35px rgba(231, 111, 81, 0.3);
        text-shadow: none !important;
    }}
    .stButton > button[kind="primary"] p {{
        color: #151515 !important;
        text-shadow: none !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 20px 42px rgba(231, 111, 81, 0.4);
    }}
    div[data-testid="stForm"] {{
        background: linear-gradient(180deg, rgba(9, 18, 27, 0.78), rgba(4, 10, 20, 0.84));
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 28px;
        padding: 22px 22px 12px;
        backdrop-filter: blur(14px);
        box-shadow: 0 18px 50px rgba(0,0,0,0.35);
    }}
    div[data-testid="stExpander"] {{
        background: rgba(0,0,0,0.45);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        overflow: hidden;
    }}
    div[data-testid="stExpander"] details summary p {{
        font-weight: 600;
    }}
    .time-capsule {{
        background: rgba(0,0,0,0.58);
        border-left: 5px solid {theme_color};
        padding: 12px 20px;
        border-radius: 16px;
        display: inline-block;
        text-align: right;
        backdrop-filter: blur(8px);
        float: right;
        box-shadow: 0 16px 32px rgba(0,0,0,0.28);
    }}
    .time-big {{
        font-size: 32px;
        font-weight: bold;
        font-family: monospace;
        line-height: 1;
        color: {theme_color} !important;
        text-shadow: none !important;
    }}
    .time-small {{
        font-size: 14px;
        color: #ddd !important;
        margin-top: 5px;
    }}
    .rules-card {{
        background: rgba(0, 0, 0, 0.84);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 28px;
        padding: 40px;
        margin: 8vh auto 1.5rem;
        max-width: 760px;
        text-align: center;
        backdrop-filter: blur(14px);
        box-shadow: 0 24px 60px rgba(0,0,0,0.55);
    }}
    .rules-title {{
        font-size: 36px;
        margin-bottom: 12px;
        color: #FFD166 !important;
    }}
    .rules-subtitle {{
        max-width: 560px;
        margin: 0 auto 24px;
        color: rgba(255,255,255,0.82) !important;
        font-size: 17px;
        line-height: 1.7;
    }}
    .rules-list {{
        text-align: left;
        font-size: 17px;
        line-height: 1.8;
        display: grid;
        gap: 12px;
    }}
    .rule-item {{
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 14px 16px;
    }}
    .entry-shell {{
        max-width: 1180px;
        margin: 3vh auto 0;
    }}
    .hero-card {{
        background: linear-gradient(155deg, rgba(8, 29, 43, 0.78), rgba(4, 10, 20, 0.88));
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 28px;
        padding: 36px;
        backdrop-filter: blur(16px);
        box-shadow: 0 24px 60px rgba(0,0,0,0.45);
        min-height: 100%;
    }}
    .hero-eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        background: rgba(255, 209, 102, 0.14);
        border: 1px solid rgba(255, 209, 102, 0.28);
        border-radius: 999px;
        color: #FFD166 !important;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        text-shadow: none !important;
    }}
    .hero-title {{
        margin: 18px 0 14px;
        font-size: clamp(2.7rem, 4vw, 4.8rem);
        line-height: 0.95;
    }}
    .hero-subtitle {{
        max-width: 620px;
        color: rgba(255,255,255,0.86) !important;
        font-size: 1.05rem;
        line-height: 1.8;
        margin-bottom: 24px;
    }}
    .hero-pills {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 24px;
    }}
    .hero-pill {{
        padding: 10px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.12);
        color: #F6F7EB !important;
        font-size: 14px;
    }}
    .hero-feature-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        margin-top: 18px;
    }}
    .hero-feature {{
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 16px;
    }}
    .hero-feature strong {{
        display: block;
        margin-bottom: 6px;
        color: #FFD166 !important;
        text-shadow: none !important;
    }}
    .helper-card {{
        margin-top: 18px;
        background: rgba(255,255,255,0.09);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 22px;
        padding: 18px 20px;
        backdrop-filter: blur(12px);
    }}
    .helper-title {{
        margin: 0 0 10px;
        font-size: 16px;
        color: #FFD166 !important;
        text-shadow: none !important;
    }}
    .helper-copy {{
        margin: 0;
        color: rgba(255,255,255,0.82) !important;
        line-height: 1.7;
    }}
    @media (max-width: 900px) {{
        .hero-card {{
            padding: 26px;
        }}
        .hero-feature-grid {{
            grid-template-columns: 1fr;
        }}
        .rules-card {{
            padding: 28px 22px;
            margin-top: 5vh;
        }}
    }}
</style>
""",
    unsafe_allow_html=True,
)


if "rules_accepted" not in st.session_state:
    st.session_state["rules_accepted"] = False


if not st.session_state["rules_accepted"]:
    st.markdown(
        """
    <div class="rules-card">
        <div class="rules-title">🎓 AI 泰国穷游 · 出发前须知</div>
        <div class="rules-subtitle">
            这不是普通旅行清单，而是一场由天气、体力、预算和临场选择共同决定的 AI 旅程。
            先花 20 秒看完规则，等会儿玩起来会顺很多。
        </div>
        <div class="rules-list">
            <div class="rule-item">1. 🤖 <b>全 AI 生成</b>：背景图、天气判断和结局图都由 AI 参与生成，首次进入新状态时会有短暂等待。</div>
            <div class="rule-item">2. 💰 <b>资源管理</b>：预算和体力都会决定你能不能继续旅行，乱花钱和硬撑都可能直接结束旅程。</div>
            <div class="rule-item">3. 🌙 <b>夜间交通限制</b>：18:00 到次日 08:00 只有纯航班可用，车船类路线会停运。</div>
            <div class="rule-item">4. 🌦️ <b>天气影响行动</b>：雨天出门会更累，景点和奔波类活动成本会上升。</div>
            <div class="rule-item">5. 🎧 <b>建议打开声音</b>：不同城市会切换不同 BGM，沉浸感会好很多。</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        if st.button("🚀 规则已了解，开始我的旅程", type="primary", use_container_width=True):
            st.session_state["rules_accepted"] = True
            st.rerun()

    st.stop()


if st.session_state.get("player") is None:
    left_col, right_col = st.columns([1.2, 0.9], gap="large")

    with left_col:
        st.markdown(
            """
        <div class="entry-shell">
            <div class="hero-card">
                <div class="hero-eyebrow">Thailand Travel Simulator</div>
                <div class="hero-title">AI 泰国穷游模拟器</div>
                <div class="hero-subtitle">
                    从一座城市落地，带着有限预算和体力，在天气、时间、住宿与交通限制里做出每一步选择。
                    这不是填表开局，而是先替自己设计一段会发生故事的旅程。
                </div>
                <div class="hero-pills">
                    <div class="hero-pill">10 座城市路线</div>
                    <div class="hero-pill">AI 场景生成</div>
                    <div class="hero-pill">动态天气</div>
                    <div class="hero-pill">预算与体力管理</div>
                </div>
                <div class="hero-feature-grid">
                    <div class="hero-feature">
                        <strong>城市感更强</strong>
                        每次切换城市、天气和时段，画面氛围都会跟着变化。
                    </div>
                    <div class="hero-feature">
                        <strong>选择真的有代价</strong>
                        想省钱、想打卡、想夜生活，三件事通常不能同时满足。
                    </div>
                    <div class="hero-feature">
                        <strong>路线不是摆设</strong>
                        夜里不是所有路线都能走，跨城决策会改变整趟旅行节奏。
                    </div>
                    <div class="hero-feature">
                        <strong>适合反复重开</strong>
                        换一个月份、落地城市和预算，旅程手感会完全不同。
                    </div>
                </div>
            </div>
            <div class="helper-card">
                <div class="helper-title">开局建议</div>
                <p class="helper-copy">
                    如果你只是第一次体验，建议从曼谷开始、预算 30,000 THB、5 天、上午抵达。
                    这个组合最容易感受到城市切换、资源管理和 AI 场景变化。
                </p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown("## 设计这趟旅程")
        st.caption("把出发条件定下来，然后我们直接开局。开始按钮放在配置面板底部，顺着填完就能走。")

        with st.form("start_trip_form"):
            start_city = st.selectbox("出发城市", list(GAME_DATA.keys()))
            start_month = st.selectbox("旅行月份", list(range(1, 13)), index=9)
            start_time = st.slider("落地时间", 0, 23, 10)
            budget = st.number_input("预算 (THB)", 5000, 100000, 30000, step=1000)
            days = st.number_input("天数", 1, 30, 5)
            city_guide = CITY_GUIDES[start_city]
            st.caption(f"适合：{city_guide['best_for']}")
            st.caption(f"节奏：{city_guide['pace']}")
            st.caption(f"交通提示：{city_guide['transport_tip']}")
            start_clicked = st.form_submit_button(
                "🛫 开始我的泰国之旅", type="primary", use_container_width=True
            )

        st.divider()
        with st.expander("⚙️ API 设置（可选）"):
            st.info("本项目依赖 **智谱 AI**。如果你有自己的 Key，可以填入；否则会使用默认降级模式。")
            key_input = st.text_input("智谱 API Key", type="password", placeholder="sk-...")
            if key_input:
                st.session_state["user_api_key"] = key_input

    if start_clicked:
        with st.spinner("AI 正在准备行程数据..."):
            game.start_game(start_city, budget, start_time, days, start_month)
            st.rerun()

    st.stop()


c1, c2 = st.columns([2, 1])
with c1:
    st.title(f"📍 {GAME_DATA[current_city]['name_cn']}")
    st.markdown(f"*{city_desc}*")
    w_icon = {"sunny": "☀️", "cloudy": "☁️", "rainy": "🌧️"}.get(current_weather, "✨")
    st.info(f"{w_icon} {current_weather.capitalize()}")
    city_guide = CITY_GUIDES.get(current_city)
    if city_guide:
        with st.expander("🧭 城市情报", expanded=False):
            st.markdown(f"**适合玩法**：{city_guide['best_for']}")
            st.markdown(f"**旅行节奏**：{city_guide['pace']}")
            st.markdown(f"**交通提示**：{city_guide['transport_tip']}")
            st.markdown(f"**推荐时段**：{city_guide['signature_window']}")

with c2:
    st.markdown(
        f"""
    <div class="time-capsule">
        <div class="time-big">{int(curr_h):02d}:00</div>
        <div class="time-small">Day {player['day']} · {time_label}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.divider()


with st.sidebar:
    st.header("🎒 背包")
    st.subheader(f"💰 {player['money']:,}")
    st.subheader(f"🔋 {player['stamina']}/100")
    st.divider()
    st.markdown("🎵 **BGM**")
    auto_play = st.toggle("自动播放", value=True)
    st.audio(bgm_url, start_time=0, autoplay=auto_play, loop=True)
    st.divider()
    if st.button("🔁 重新开始游戏", use_container_width=True):
        game.reset_game()
        st.session_state["rules_accepted"] = False
        st.rerun()


if player["time"] == 8 and not player["hotel_settled"]:
    st.subheader("🏨 选择住宿")
    hotel_meta = get_city_realtime_meta(current_city)
    hotel_check_in, hotel_check_out = infer_hotel_dates(player)

    with st.expander("🏨 实时酒店参考（Beta）", expanded=False):
        if not has_amadeus_credentials():
            st.info("配置 `AMADEUS_API_KEY` 和 `AMADEUS_API_SECRET` 后，这里会显示当前城市附近的实时酒店参考价。")
        elif not hotel_meta:
            st.warning("当前城市还没有配置实时酒店查询映射。")
        else:
            st.caption(
                f"{hotel_meta['hotel_label']} · {format_date_for_api(hotel_check_in)} -> "
                f"{format_date_for_api(hotel_check_out)}"
            )
            if st.button("刷新实时酒店报价", key=f"live_hotel_{current_city}", use_container_width=True):
                with st.spinner("正在查询实时酒店报价..."):
                    st.session_state["live_hotel_results"] = search_live_hotels(
                        current_city,
                        hotel_meta["lat"],
                        hotel_meta["lng"],
                        format_date_for_api(hotel_check_in),
                        format_date_for_api(hotel_check_out),
                    )
                    st.session_state["live_hotel_query"] = (
                        f"{current_city}:{format_date_for_api(hotel_check_in)}:{format_date_for_api(hotel_check_out)}"
                    )

            hotel_query_key = f"{current_city}:{format_date_for_api(hotel_check_in)}:{format_date_for_api(hotel_check_out)}"
            hotel_result = st.session_state.get("live_hotel_results")
            if st.session_state.get("live_hotel_query") == hotel_query_key and hotel_result:
                if not hotel_result["ok"]:
                    st.warning(f"酒店查询失败：{hotel_result['error']}")
                elif not hotel_result["data"]:
                    st.info("当前没有拿到可展示的实时酒店报价。")
                else:
                    st.caption("以下是附近酒店的实时参考价，游戏内住宿价格仍按模拟规则结算。")
                    for item in hotel_result["data"][:5]:
                        title = f"{item['hotel_name']} · {item['price']} {item['currency']}"
                        subtitle = item["room_type"]
                        if item["board_type"]:
                            subtitle = f"{subtitle} · {item['board_type']}"
                        st.markdown(f"**{title}**")
                        st.caption(subtitle)
                        st.markdown("---")

    opts = game.get_hotel_options()
    cols = st.columns(3)
    for i, hotel in enumerate(opts):
        with cols[i]:
            if st.button(
                f"{hotel['name']}\n{hotel['price']} THB",
                key=f"h_{i}",
                use_container_width=True,
            ):
                if game.settle_hotel(hotel):
                    st.rerun()
                else:
                    st.toast("余额不够，换一家吧。")
    st.stop()


t1, t2, t3 = st.tabs(["🎯 游玩", "🧭 移动", "🛌 休息"])


with t1:
    valid_acts = []
    for act in GAME_DATA[current_city]["activities"]:
        if act["type"] == "scenic" and act["id"] in player["visited_activities"]:
            continue

        if activity_is_available(act, curr_h):
            valid_acts.append(act)

    if not valid_acts:
        st.warning("当前时段没有可用活动。")

    for act in valid_acts:
        c_info, c_btn = st.columns([3, 1])
        with c_info:
            st.markdown(f"**{act['name']}**")
            st.caption(
                f"💰 {act['cost_money']} | ⏰ {act['cost_time']}h | 🔋 {act['cost_stamina']} | "
                f"🕒 {activity_time_label(act)}"
            )
            if act.get("time_note"):
                st.caption(f"备注：{act['time_note']}")
        with c_btn:
            st.write("")
            if st.button("Go", key=f"go_{act['id']}", use_container_width=True):
                if player["money"] < act["cost_money"]:
                    st.toast("钱不够。")
                elif player["stamina"] < act["cost_stamina"]:
                    st.toast("体力不够。")
                else:
                    game.do_activity(
                        act["id"],
                        act["cost_money"],
                        act["cost_stamina"],
                        act["cost_time"],
                        act["name"],
                    )
                    st.rerun()
        st.markdown("---")


with t2:
    moves = game.get_travel_choices()
    is_night = curr_h >= 18 or curr_h < 8

    if not moves:
        st.info("这里像一座孤岛，暂时没有可走的路线。")

    with st.expander("✈️ 实时航班参考（Beta）", expanded=False):
        if not has_amadeus_credentials():
            st.info("配置 `AMADEUS_API_KEY` 和 `AMADEUS_API_SECRET` 后，这里会显示当前路线的实时机票参考价。")
        elif not moves:
            st.caption("当前城市没有可查询的移动路线。")
        else:
            target_options = list(moves.keys())
            live_target = st.selectbox(
                "选择想查看实时机票的目的地",
                target_options,
                format_func=lambda city: GAME_DATA[city]["name_cn"],
                key=f"live_target_{current_city}",
            )
            trip_date = infer_trip_date(player["month"], player["day"])
            flight_plan = build_realtime_flight_plan(current_city, live_target)

            st.markdown(f"**{flight_plan['title']}**")
            st.caption(f"计划出发日：{format_date_for_api(trip_date)}")
            for note in flight_plan.get("notes", []):
                st.caption(note)

            if flight_plan["queryable"]:
                if flight_plan["kind"] == "direct_flight":
                    st.info("这是一段可以直接查机票的城市间航线。")
                else:
                    st.info("这是一段“航班 + 船/地面接驳”的组合路线，实时机票只覆盖其中的飞行段。")

                if st.button("刷新实时机票", key=f"live_flight_{current_city}_{live_target}", use_container_width=True):
                    with st.spinner("正在查询实时航班报价..."):
                        st.session_state["live_flight_results"] = search_live_flights(
                            flight_plan["origin_code"],
                            flight_plan["destination_code"],
                            format_date_for_api(trip_date),
                        )
                        st.session_state["live_flight_query"] = (
                            f"{current_city}:{live_target}:{format_date_for_api(trip_date)}"
                        )

                flight_query_key = f"{current_city}:{live_target}:{format_date_for_api(trip_date)}"
                flight_result = st.session_state.get("live_flight_results")
                if st.session_state.get("live_flight_query") == flight_query_key and flight_result:
                    if not flight_result["ok"]:
                        st.warning(f"航班查询失败：{flight_result['error']}")
                    elif not flight_result["data"]:
                        st.info("当前没有拿到可展示的实时航班报价。")
                    else:
                        st.caption("以下价格是实时参考价；如果这条路线含船或地面接驳，接驳成本不在机票价格里。")
                        sorted_results = sorted(
                            flight_result["data"],
                            key=lambda item: (float(item["price"]), item["stops"])
                            if str(item["price"]).replace(".", "", 1).isdigit()
                            else (999999.0, item["stops"]),
                        )
                        cheapest = sorted_results[0]
                        fastest = min(sorted_results, key=lambda item: item.get("duration_minutes", 10**9))
                        fewest_stops = min(sorted_results, key=lambda item: item["stops"])

                        for item in sorted_results:
                            badges = []
                            if item == cheapest:
                                badges.append("最低价")
                            if item == fastest:
                                badges.append("最快")
                            if item == fewest_stops:
                                badges.append("最少中转")

                            badge_text = f" · {' / '.join(badges)}" if badges else ""
                            st.markdown(f"**{item['price']} {item['currency']} · {item['carrier']}{badge_text}**")
                            st.caption(
                                f"{item['departure']} -> {item['arrival']} · "
                                f"{item['duration']} · 中转 {item['stops']} 次"
                            )
                            st.markdown("---")

    for tgt, info in moves.items():
        mode = info["mode"]
        is_flight_kw = any(k in mode for k in ["飞机", "航班", "直飞"])
        has_ground_kw = any(k in mode for k in ["船", "车", "巴", "火车", "联运"])
        is_pure_flight = is_flight_kw and not has_ground_kw
        is_allowed = (not is_night) or (is_night and is_pure_flight)

        move_c1, move_c2 = st.columns([3, 1])
        with move_c1:
            st.markdown(f"**➡️ {GAME_DATA[tgt]['name_cn']}**")
            if not is_allowed:
                st.caption(f"🚫 {mode}（夜间停运）")
            else:
                st.caption(f"{mode} · {info['cost_time']}h · 🔋 {info['cost_stamina']}")
        with move_c2:
            st.write("")
            if st.button("出发", key=f"mv_{tgt}", disabled=not is_allowed, use_container_width=True):
                if player["stamina"] < info["cost_stamina"]:
                    st.toast("体力不够，先休息一下。")
                else:
                    game.travel_to(tgt)
                    st.rerun()
        st.markdown("---")

    if st.button("🏠 结束行程回家", type="primary", use_container_width=True):
        game.finish_game()
        st.rerun()


with t3:
    if 6 <= curr_h < 18:
        nap_hours = st.slider("午睡时长", 1, 4, 2)
        if st.button("小睡一会儿", use_container_width=True):
            game.sleep(nap_hours)
            st.rerun()

    if st.button("🌙 一觉睡到明天 08:00", use_container_width=True):
        game.sleep(None)
        st.rerun()


if player["game_over"]:
    is_success = player.get("success", False)

    with st.spinner("AI 正在生成你的旅行纪念图..."):
        end_image_url = ai_bot.generate_ending_card(is_success, current_city)

    if is_success:
        st.balloons()
    else:
        st.snow()

    st.markdown(
        f"""
    <style>
        [data-testid="stSidebar"] {{ display: none; }}
        .block-container {{ padding-top: 0 !important; }}
        .stApp {{
            background-image:
                linear-gradient(rgba(0,0,0,0.82), rgba(0,0,0,0.82)),
                url("{end_image_url}");
        }}
        .end-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            padding: 40px;
            margin: 5vh auto;
            max-width: 720px;
            text-align: center;
            color: #333 !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        }}
        .end-card * {{
            color: #333 !important;
            text-shadow: none !important;
        }}
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
        .stat-val {{
            font-size: 24px;
            font-weight: bold;
            color: #0066cc !important;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    html_content = f"""
    <div class="end-card">
        <img src="{end_image_url}" class="memory-photo">
        <h1>{"🎉 完美旅程" if is_success else "🧳 旅程结束"}</h1>
        <p style="font-size: 18px; margin: 20px 0;">“{player['fail_reason']}”</p>
        <div class="stat-grid">
            <div><div class="stat-val">{player['day']} 天</div><div>旅行时长</div></div>
            <div><div class="stat-val">{len(player['visited_activities'])} 个</div><div>打卡地点</div></div>
            <div><div class="stat-val">{player['money']:,} THB</div><div>剩余资金</div></div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

    _, center_restart, _ = st.columns([1, 1, 1])
    with center_restart:
        if st.button("🔁 开启新旅程", type="primary", use_container_width=True):
            game.reset_game()
            st.session_state["rules_accepted"] = False
            st.rerun()
    st.stop()
