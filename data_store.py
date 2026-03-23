def activity(
    act_id,
    name,
    desc,
    cost_money,
    cost_stamina,
    cost_time,
    act_type,
    start_window,
    time_note="",
):
    return {
        "id": act_id,
        "name": name,
        "desc": desc,
        "cost_money": cost_money,
        "cost_stamina": cost_stamina,
        "cost_time": cost_time,
        "type": act_type,
        "start_window": start_window,
        "time_note": time_note,
    }


def activity_is_available(act, current_hour):
    start_hour, latest_start = act.get("start_window", (8, 21))
    return start_hour <= current_hour <= latest_start


def activity_time_label(act):
    start_hour, latest_start = act.get("start_window", (8, 21))
    return f"{start_hour:02d}:00 - {latest_start:02d}:00 可出发"


GAME_DATA = {
    "Bangkok": {
        "name_cn": "曼谷",
        "description": "天使之城，堵车、寺庙、夜生活和商场同时存在。",
        "activities": [
            activity("bkk_palace", "大皇宫 & 玉佛寺", "适合一早出发，避开人潮和正午暴晒。", 500, 35, 3, "scenic", (8, 13)),
            activity("bkk_wat_arun", "郑王庙（黎明寺）", "白天光线最好，傍晚拍照也很美。", 100, 20, 2, "scenic", (8, 16)),
            activity(
                "bkk_chatuchak",
                "乍都乍周末市场",
                "真实世界主要是周末白天最热闹；游戏里简化成日间可逛。",
                1000,
                50,
                4,
                "scenic",
                (9, 14),
                "真实参考偏周末白天。",
            ),
            activity("bkk_massage", "卧佛寺泰式按摩", "适合中午或下午补体力。", 600, -25, 2, "relax", (10, 20)),
            activity("bkk_khaosan", "考山路夜生活", "越晚越热闹，但太晚开始会很伤体力。", 500, 15, 3, "night", (20, 23)),
            activity("bkk_chinatown", "唐人街探店", "更像傍晚到夜里的觅食路线。", 800, 10, 3, "food", (17, 21)),
            activity("bkk_iconsiam", "IconSiam 吹冷气", "商场型活动，适合白天最热的时候。", 0, -10, 3, "relax", (10, 19)),
            activity("bkk_nana", "Nana Plaza 闲逛", "标准夜生活时段。", 1000, 20, 3, "night", (20, 23)),
            activity("bkk_lumpini", "伦披尼公园看蜥蜴", "早晨和下午比较舒服，中午容易太晒。", 0, 15, 2, "scenic", (7, 16)),
        ],
    },
    "Chiang Mai": {
        "name_cn": "清迈",
        "description": "泰北慢生活中心，寺庙、咖啡馆和山路节奏完全不同。",
        "activities": [
            activity("cm_doi_suthep", "素贴山双龙寺", "最好早一点上山，山路和爬阶都更舒服。", 100, 40, 4, "scenic", (7, 15)),
            activity("cm_old_city", "古城塔佩门散步", "白天随时适合，但午后比较从容。", 20, 10, 1, "scenic", (8, 17)),
            activity("cm_night_bazaar", "长康路夜市", "标准夜市时段。", 300, 15, 3, "night", (18, 21)),
            activity("cm_coffee", "宁曼路网红咖啡", "咖啡馆更适合上午晚些时候到下午。", 150, -15, 4, "relax", (10, 15)),
            activity(
                "cm_elephant",
                "大象保育营",
                "多数真实行程一大早集合出发；游戏里保留这个节奏。",
                2500,
                50,
                6,
                "scenic",
                (7, 9),
                "真实参考偏清晨集合。",
            ),
        ],
    },
    "Pattaya": {
        "name_cn": "芭提雅",
        "description": "海滨娱乐城市，白天适合出海，晚上适合看秀和逛街。",
        "activities": [
            activity("pty_walking_street", "步行街夜游", "越晚越有味道。", 1000, 25, 4, "night", (20, 23)),
            activity("pty_truth", "真理圣殿", "白天参观最合适，太晚不建议开始。", 500, 30, 3, "scenic", (8, 14)),
            activity("pty_beach", "格兰岛一日游", "出海型活动通常要上午出发。", 600, 40, 6, "scenic", (8, 10)),
            activity("pty_tiffany", "蒂芬妮人妖秀", "晚间秀场活动，适合作为夜里第一站。", 1200, 5, 2, "scenic", (18, 21)),
            activity("pty_massage", "海滨马杀鸡", "下午吹海风放松最舒服。", 300, -10, 2, "relax", (11, 18)),
        ],
    },
    "Hua Hin": {
        "name_cn": "华欣",
        "description": "皇室度假海边城市，节奏偏慢，更适合白天轻松玩、晚上逛市集。",
        "activities": [
            activity("hh_station", "最美火车站", "白天顺路打卡最合适。", 0, 10, 1, "scenic", (8, 17)),
            activity("hh_beach", "骑马逛海滩", "这类项目通常早上更舒服，太阳还没太毒。", 400, 20, 2, "scenic", (7, 10)),
            activity(
                "hh_night_market",
                "禅意夜市（Cicada）",
                "真实世界偏周末傍晚到夜间；游戏里简化成固定夜市时段。",
                300,
                15,
                3,
                "food",
                (17, 21),
                "真实参考偏周末夜间。",
            ),
            activity("hh_vana_nava", "Vana Nava 水上乐园", "更像中午到下午的水上项目。", 1200, 30, 3, "scenic", (11, 15)),
            activity("hh_chill", "海边躺椅午睡", "典型午后偷懒活动。", 100, -20, 3, "relax", (13, 16)),
        ],
    },
    "Phuket": {
        "name_cn": "普吉岛",
        "description": "最成熟的泰国海岛目的地，白天玩海，傍晚看日落，晚上看秀。",
        "activities": [
            activity("hkt_patong", "芭东海滩", "白天至傍晚都能去，午后更热闹。", 0, 10, 3, "scenic", (9, 17)),
            activity("hkt_old_town", "普吉镇老街", "店铺和咖啡馆更适合白天到黄昏。", 200, 20, 3, "scenic", (10, 17)),
            activity("hkt_promthep", "神仙半岛日落", "核心就是看日落，太早去意义不大。", 100, 25, 4, "scenic", (15, 17)),
            activity(
                "hkt_show",
                "幻多奇乐园",
                "官方是傍晚开园的夜间主题乐园。",
                1800,
                30,
                4,
                "night",
                (17, 19),
                "Phuket FantaSea 官方为傍晚到夜间营业。",
            ),
            activity("hkt_surf", "卡塔海滩冲浪", "更像白天项目，太晚海上活动不合理。", 1000, 50, 3, "scenic", (10, 16)),
        ],
    },
    "Krabi": {
        "name_cn": "甲米",
        "description": "石灰岩海岸线和跳岛更出名，很多项目天然偏向上午出发。",
        "activities": [
            activity("kb_aonang", "奥南海滩", "白天任意时段都适合停留。", 0, 10, 2, "scenic", (9, 17)),
            activity("kb_climb", "莱利海滩攀岩", "攀岩更适合上午，避开最晒时段。", 1500, 60, 4, "scenic", (8, 13)),
            activity("kb_pool", "翡翠池", "自然景点白天最合适，太晚开始不划算。", 200, -10, 3, "relax", (8, 14)),
            activity("kb_tiger", "虎窟寺", "爬阶类项目最好清晨开始。", 0, 70, 4, "scenic", (7, 10)),
            activity("kb_boat", "四岛游", "典型跳岛日游，基本要上午出发。", 800, 40, 6, "scenic", (8, 10)),
        ],
    },
    "Koh Samui": {
        "name_cn": "苏梅岛",
        "description": "海岛度假感强，白天看海和寺庙，晚上才轮到夜市与派对。",
        "activities": [
            activity("ks_chaweng", "查汶海滩", "白天和傍晚都适合。", 0, 10, 3, "scenic", (9, 17)),
            activity("ks_fullmoon", "帕岸岛满月派对", "深夜活动，不建议太早出发。", 2000, 80, 8, "night", (20, 22)),
            activity("ks_spa", "顶级森林 SPA", "通常是中午到下午的预约型放松项目。", 3000, -40, 3, "relax", (11, 17)),
            activity(
                "ks_fisher",
                "渔人村夜市",
                "现实里偏周五夜市；游戏里简化成夜间可逛。",
                500,
                20,
                3,
                "food",
                (17, 21),
                "真实参考偏周五夜市。",
            ),
            activity("ks_temple", "大佛寺", "白天都可以去，但中午暴晒感更强。", 0, 15, 1, "scenic", (8, 17)),
        ],
    },
    "Phi Phi Islands": {
        "name_cn": "皮皮岛",
        "description": "更偏海上项目和观景路线，真正有意义的活动时间点很明显。",
        "activities": [
            activity("pp_view", "皮皮岛观景台", "清晨和傍晚最好，但白天也能爬。", 30, 40, 2, "scenic", (7, 17)),
            activity("pp_maya", "玛雅湾（The Beach）", "船程活动通常上午或午后早些时候出发。", 400, 30, 3, "scenic", (8, 14)),
            activity("pp_party", "海滩火舞派对", "纯夜生活活动。", 800, 40, 5, "night", (20, 23)),
            activity("pp_diving", "深潜体验", "潜水船通常上午出海。", 2500, 50, 4, "scenic", (8, 11)),
            activity("pp_sleep", "沙滩吊床", "午后发呆最合理。", 0, -15, 2, "relax", (12, 17)),
        ],
    },
    "Koh Lanta": {
        "name_cn": "兰塔岛",
        "description": "慢节奏海岛，白天适合环岛和出海，夜里适合安静喝一杯。",
        "activities": [
            activity("lanta_motor", "租摩托环岛", "日间路线，最好别太晚开始。", 250, 30, 5, "scenic", (9, 14)),
            activity("lanta_park", "国家公园灯塔", "自然景点白天更合理。", 200, 25, 3, "scenic", (8, 15)),
            activity("lanta_sunset", "日落餐厅", "傍晚开始才有意义。", 800, -10, 3, "food", (17, 20)),
            activity("lanta_rok", "洛克岛一日游", "典型早出晚归的海岛团。", 1500, 50, 7, "scenic", (8, 9)),
            activity("lanta_bar", "雷鬼酒吧", "夜间小酒吧时段。", 400, 10, 3, "night", (20, 23)),
        ],
    },
    "Koh Lipe": {
        "name_cn": "丽贝岛",
        "description": "更远也更纯粹，活动天然被海和日出日落主导。",
        "activities": [
            activity("lipe_sunrise", "日出海滩", "核心就是清晨时段。", 0, 15, 2, "scenic", (6, 8)),
            activity("lipe_walking", "步行街", "更像傍晚到夜里的觅食散步路线。", 500, 15, 2, "food", (17, 21)),
            activity("lipe_snorkel", "近海浮潜", "白天海况更稳，通常上午或中午前后。", 0, 30, 3, "scenic", (9, 14)),
            activity("lipe_blue", "寻找蓝眼泪", "典型夜间活动。", 0, 20, 2, "scenic", (20, 22)),
            activity("lipe_stone", "叠石岛", "更适合下午和傍晚。", 600, 35, 4, "scenic", (13, 16)),
        ],
    },
}


CITY_PRICE_MULTIPLIER = {
    "Bangkok": 1.0,
    "Chiang Mai": 0.8,
    "Pattaya": 1.1,
    "Hua Hin": 1.2,
    "Phuket": 1.5,
    "Krabi": 1.0,
    "Koh Samui": 1.6,
    "Phi Phi Islands": 1.3,
    "Koh Lanta": 0.9,
    "Koh Lipe": 1.4,
}


TIME_NEAR = 2
TIME_MID = 4
TIME_FAR = 10
TIME_EXTREME = 14

STAMINA_EASY = 15
STAMINA_TIRED = 35
STAMINA_DYING = 60

TRAVEL_ROUTES = {}

cities = list(GAME_DATA.keys())
for start in cities:
    TRAVEL_ROUTES[start] = {}
    for end in cities:
        if start == end:
            continue

        mode = "飞机/大巴联程"
        time = TIME_FAR
        stamina = STAMINA_TIRED

        if "Bangkok" in [start, end]:
            other = end if start == "Bangkok" else start
            if other in ["Pattaya", "Hua Hin"]:
                mode = "大巴/小巴"
                time = TIME_NEAR + 1
                stamina = STAMINA_EASY
            elif other in ["Chiang Mai", "Phuket", "Krabi", "Koh Samui"]:
                mode = "飞机"
                time = 4
                stamina = 25
            elif other == "Koh Lipe":
                mode = "飞机+车船"
                time = 9
                stamina = 50
            elif other in ["Phi Phi Islands", "Koh Lanta"]:
                mode = "飞机+船"
                time = 7
                stamina = 40

        elif "Chiang Mai" in [start, end]:
            other = end if start == "Chiang Mai" else start
            if other == "Phuket":
                mode = "直飞"
                time = 3
                stamina = 20
            elif other == "Koh Lipe":
                mode = "飞机+转机+车船"
                time = TIME_EXTREME
                stamina = STAMINA_DYING
            else:
                mode = "飞机+车船联运"
                time = 10
                stamina = 45

        andaman_group = ["Phuket", "Krabi", "Phi Phi Islands", "Koh Lanta"]
        if start in andaman_group and end in andaman_group:
            mode = "快艇/渡轮"
            time = 3
            stamina = 20
            if "Phi Phi Islands" in [start, end]:
                time = 2

        elif "Koh Samui" in [start, end]:
            other = end if start == "Koh Samui" else start
            if other in andaman_group:
                mode = "飞机/车船联运"
                time = 6
                stamina = 35

        elif "Koh Lipe" in [start, end]:
            other = end if start == "Koh Lipe" else start
            if other == "Koh Lanta":
                mode = "时季快艇"
                time = 4
                stamina = 30
            else:
                mode = "长途转运"
                time = 12
                stamina = 55

        TRAVEL_ROUTES[start][end] = {
            "mode": mode,
            "cost_time": time,
            "cost_stamina": stamina,
        }

TRAVEL_ROUTES["Pattaya"]["Hua Hin"] = {"mode": "皇家渡轮", "cost_time": 2, "cost_stamina": 15}
TRAVEL_ROUTES["Hua Hin"]["Pattaya"] = {"mode": "皇家渡轮", "cost_time": 2, "cost_stamina": 15}
