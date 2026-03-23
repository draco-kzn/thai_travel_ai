# data_store.py
# Version: 1.0 (10 City Full Edition)

# ==========================================
# 1. 城市节点与活动库 (City & Activities)
# ==========================================
# type: 'scenic'(景点/累), 'food'(吃), 'relax'(回血), 'night'(夜生活)
# cost_stamina: 正数=消耗, 负数=恢复

GAME_DATA = {
    "Bangkok": {
        "name_cn": "曼谷",
        "description": "天使之城，堵车与繁华并存。",
        "activities": [
            {"id": "bkk_palace", "name": "大皇宫 & 玉佛寺", "desc": "金碧辉煌，人山人海，热到中暑。", "cost_money": 500, "cost_stamina": 35, "cost_time": 3, "type": "scenic"},
            {"id": "bkk_wat_arun", "name": "郑王庙 (黎明寺)", "desc": "在昭披耶河畔拍人生照片。", "cost_money": 100, "cost_stamina": 20, "cost_time": 2, "type": "scenic"},
            {"id": "bkk_chatuchak", "name": "乍都乍周末市场", "desc": "世界上最大的跳蚤市场，走到腿断。", "cost_money": 1000, "cost_stamina": 50, "cost_time": 4, "type": "scenic"},
            {"id": "bkk_massage", "name": "卧佛寺泰式按摩", "desc": "正宗古法按摩，被按得嗷嗷叫但很爽。", "cost_money": 600, "cost_stamina": -25, "cost_time": 2, "type": "relax"},
            {"id": "bkk_khaosan", "name": "考山路夜生活", "desc": "背包客的宇宙中心，喝着啤酒交朋友。", "cost_money": 500, "cost_stamina": 15, "cost_time": 3, "type": "night"},
            {"id": "bkk_chinatown", "name": "唐人街探店", "desc": "燕窝鱼翅路边摊，霓虹灯下吃通宵。", "cost_money": 800, "cost_stamina": 10, "cost_time": 3, "type": "food"},
            {"id": "bkk_iconsiam", "name": "IconSiam 吹冷气", "desc": "豪华商场，如果不买奢侈品其实很省钱。", "cost_money": 0, "cost_stamina": -10, "cost_time": 3, "type": "relax"},
            {"id": "bkk_nana", "name": "Nana Plaza 闲逛", "desc": "感受曼谷成人世界的灯红酒绿。", "cost_money": 1000, "cost_stamina": 20, "cost_time": 3, "type": "night"},
            {"id": "bkk_lumpini", "name": "伦披尼公园看蜥蜴", "desc": "城市绿肺，可以看到巨大的泽巨蜥。", "cost_money": 0, "cost_stamina": 15, "cost_time": 2, "type": "scenic"}
        ]
    },
    "Chiang Mai": {
        "name_cn": "清迈",
        "description": "泰北玫瑰，慢生活的代名词。",
        "activities": [
            {"id": "cm_doi_suthep", "name": "素贴山双龙寺", "desc": "俯瞰古城全景，爬楼梯很累。", "cost_money": 100, "cost_stamina": 40, "cost_time": 4, "type": "scenic"},
            {"id": "cm_old_city", "name": "古城塔佩门喂鸽子", "desc": "在那面红墙打卡，小心被鸽子碰瓷。", "cost_money": 20, "cost_stamina": 10, "cost_time": 1, "type": "scenic"},
            {"id": "cm_night_bazaar", "name": "长康路夜市", "desc": "买点大象裤和手工艺品。", "cost_money": 300, "cost_stamina": 15, "cost_time": 3, "type": "night"},
            {"id": "cm_coffee", "name": "宁曼路网红咖啡", "desc": "一下午什么都不做，只发呆。", "cost_money": 150, "cost_stamina": -15, "cost_time": 4, "type": "relax"},
            {"id": "cm_elephant", "name": "大象保育营", "desc": "给大象洗澡，拒绝骑大象。", "cost_money": 2500, "cost_stamina": 50, "cost_time": 6, "type": "scenic"}
        ]
    },
    "Pattaya": {
        "name_cn": "芭提雅",
        "description": "东方夏威夷，罪恶之城。",
        "activities": [
            {"id": "pty_walking_street", "name": "步行街夜游", "desc": "著名的红灯区，大开眼界。", "cost_money": 1000, "cost_stamina": 25, "cost_time": 4, "type": "night"},
            {"id": "pty_truth", "name": "真理圣殿", "desc": "全木制建筑，震撼的艺术品。", "cost_money": 500, "cost_stamina": 30, "cost_time": 3, "type": "scenic"},
            {"id": "pty_beach", "name": "格兰岛一日游", "desc": "坐船出海，水比芭提雅主海滩清澈。", "cost_money": 600, "cost_stamina": 40, "cost_time": 6, "type": "scenic"},
            {"id": "pty_tiffany", "name": "蒂芬妮人妖秀", "desc": "泰国最著名的秀场之一。", "cost_money": 1200, "cost_stamina": 5, "cost_time": 2, "type": "scenic"},
            {"id": "pty_massage", "name": "海滨马杀鸡", "desc": "听着海浪声按摩。", "cost_money": 300, "cost_stamina": -10, "cost_time": 2, "type": "relax"}
        ]
    },
    "Hua Hin": {
        "name_cn": "华欣",
        "description": "皇室度假胜地，安静优雅。",
        "activities": [
            {"id": "hh_station", "name": "最美火车站", "desc": "红白相间的复古车站。", "cost_money": 0, "cost_stamina": 10, "cost_time": 1, "type": "scenic"},
            {"id": "hh_beach", "name": "骑马逛海滩", "desc": "华欣特色，沙滩骑马。", "cost_money": 400, "cost_stamina": 20, "cost_time": 2, "type": "scenic"},
            {"id": "hh_night_market", "name": "禅意夜市 (Cicada)", "desc": "最干净、最文艺的夜市。", "cost_money": 300, "cost_stamina": 15, "cost_time": 3, "type": "food"},
            {"id": "hh_park", "name": "圣托里尼乐园", "desc": "假装在希腊，适合拍照。", "cost_money": 150, "cost_stamina": 25, "cost_time": 3, "type": "scenic"},
            {"id": "hh_chill", "name": "海边躺椅午睡", "desc": "吹着海风睡觉。", "cost_money": 100, "cost_stamina": -20, "cost_time": 3, "type": "relax"}
        ]
    },
    "Phuket": {
        "name_cn": "普吉岛",
        "description": "泰国最大的岛屿，开发成熟。",
        "activities": [
            {"id": "hkt_patong", "name": "芭东海滩", "desc": "热闹、拥挤，但也最方便。", "cost_money": 0, "cost_stamina": 10, "cost_time": 3, "type": "scenic"},
            {"id": "hkt_old_town", "name": "普吉镇老街", "desc": "中葡风格建筑，文艺小资。", "cost_money": 200, "cost_stamina": 20, "cost_time": 3, "type": "scenic"},
            {"id": "hkt_promthep", "name": "神仙半岛日落", "desc": "普吉最美的日落观赏点。", "cost_money": 100, "cost_stamina": 25, "cost_time": 4, "type": "scenic"},
            {"id": "hkt_show", "name": "幻多奇乐园", "desc": "大型文化主题乐园。", "cost_money": 1800, "cost_stamina": 30, "cost_time": 4, "type": "night"},
            {"id": "hkt_surf", "name": "卡塔海滩冲浪", "desc": "尝试驾驭海浪。", "cost_money": 1000, "cost_stamina": 50, "cost_time": 3, "type": "scenic"}
        ]
    },
    "Krabi": {
        "name_cn": "甲米",
        "description": "攀岩胜地，喀斯特地貌。",
        "activities": [
            {"id": "kb_aonang", "name": "奥南海滩", "desc": "甲米的游客中心。", "cost_money": 0, "cost_stamina": 10, "cost_time": 2, "type": "scenic"},
            {"id": "kb_climb", "name": "莱利海滩攀岩", "desc": "世界级攀岩圣地，极其消耗体力。", "cost_money": 1500, "cost_stamina": 60, "cost_time": 4, "type": "scenic"},
            {"id": "kb_pool", "name": "翡翠池", "desc": "天然的森林温泉。", "cost_money": 200, "cost_stamina": -10, "cost_time": 3, "type": "relax"},
            {"id": "kb_tiger", "name": "虎窟寺", "desc": "爬1237级台阶，腿会废掉。", "cost_money": 0, "cost_stamina": 70, "cost_time": 4, "type": "scenic"},
            {"id": "kb_boat", "name": "四岛游", "desc": "经典的跳岛路线。", "cost_money": 800, "cost_stamina": 40, "cost_time": 6, "type": "scenic"}
        ]
    },
    "Koh Samui": {
        "name_cn": "苏梅岛",
        "description": "蜜月圣地，椰林树影。",
        "activities": [
            {"id": "ks_chaweng", "name": "查汶海滩", "desc": "细软白沙，夜生活丰富。", "cost_money": 0, "cost_stamina": 10, "cost_time": 3, "type": "scenic"},
            {"id": "ks_fullmoon", "name": "帕岸岛满月派对", "desc": "坐快艇去隔壁岛蹦迪通宵(假设日期合适)。", "cost_money": 2000, "cost_stamina": 80, "cost_time": 8, "type": "night"},
            {"id": "ks_spa", "name": "顶级森林SPA", "desc": "苏梅岛特色，极其昂贵但享受。", "cost_money": 3000, "cost_stamina": -40, "cost_time": 3, "type": "relax"},
            {"id": "ks_fisher", "name": "渔人村夜市", "desc": "周五限定，氛围很好。", "cost_money": 500, "cost_stamina": 20, "cost_time": 3, "type": "food"},
            {"id": "ks_temple", "name": "大佛寺", "desc": "苏梅岛的地标。", "cost_money": 0, "cost_stamina": 15, "cost_time": 1, "type": "scenic"}
        ]
    },
    "Phi Phi Islands": {
        "name_cn": "皮皮岛",
        "description": "电影《海滩》取景地，派对之岛。",
        "activities": [
            {"id": "pp_view", "name": "皮皮岛观景台", "desc": "爬山看双C海湾，很累。", "cost_money": 30, "cost_stamina": 40, "cost_time": 2, "type": "scenic"},
            {"id": "pp_maya", "name": "玛雅湾 (The Beach)", "desc": "绝美海滩，人很多。", "cost_money": 400, "cost_stamina": 30, "cost_time": 3, "type": "scenic"},
            {"id": "pp_party", "name": "海滩火舞派对", "desc": "通宵喝酒跳舞。", "cost_money": 800, "cost_stamina": 40, "cost_time": 5, "type": "night"},
            {"id": "pp_diving", "name": "深潜体验", "desc": "探索安达曼海底。", "cost_money": 2500, "cost_stamina": 50, "cost_time": 4, "type": "scenic"},
            {"id": "pp_sleep", "name": "沙滩吊床", "desc": "听海浪补觉。", "cost_money": 0, "cost_stamina": -15, "cost_time": 2, "type": "relax"}
        ]
    },
    "Koh Lanta": {
        "name_cn": "兰塔岛",
        "description": "宁静安详，适合躺平。",
        "activities": [
            {"id": "lanta_motor", "name": "租摩托环岛", "desc": "自由自在，小心路滑。", "cost_money": 250, "cost_stamina": 30, "cost_time": 5, "type": "scenic"},
            {"id": "lanta_park", "name": "国家公园灯塔", "desc": "岛的最南端，风景绝美。", "cost_money": 200, "cost_stamina": 25, "cost_time": 3, "type": "scenic"},
            {"id": "lanta_sunset", "name": "日落餐厅", "desc": "拥有泰国最美的日落。", "cost_money": 800, "cost_stamina": -10, "cost_time": 3, "type": "food"},
            {"id": "lanta_rok", "name": "洛克岛一日游", "desc": "水质如果冻般清澈。", "cost_money": 1500, "cost_stamina": 50, "cost_time": 7, "type": "scenic"},
            {"id": "lanta_bar", "name": "雷鬼酒吧", "desc": "听Live Music，放松身心。", "cost_money": 400, "cost_stamina": 10, "cost_time": 3, "type": "night"}
        ]
    },
    "Koh Lipe": {
        "name_cn": "丽贝岛",
        "description": "泰国的马尔代夫，路途遥远。",
        "activities": [
            {"id": "lipe_sunrise", "name": "日出海滩", "desc": "看第一缕阳光。", "cost_money": 0, "cost_stamina": 15, "cost_time": 2, "type": "scenic"},
            {"id": "lipe_walking", "name": "步行街", "desc": "岛上唯一的商业街。", "cost_money": 500, "cost_stamina": 15, "cost_time": 2, "type": "food"},
            {"id": "lipe_snorkel", "name": "近海浮潜", "desc": "游出去就有珊瑚。", "cost_money": 0, "cost_stamina": 30, "cost_time": 3, "type": "scenic"},
            {"id": "lipe_blue", "name": "寻找蓝眼泪", "desc": "夜晚沙滩上的荧光生物。", "cost_money": 0, "cost_stamina": 20, "cost_time": 2, "type": "scenic"},
            {"id": "lipe_stone", "name": "叠石岛", "desc": "非常有特色的石头海滩。", "cost_money": 600, "cost_stamina": 35, "cost_time": 4, "type": "scenic"}
        ]
    }
}

# ==========================================
# 2. 酒店价格倍率 (City Multiplier)
# ==========================================
CITY_PRICE_MULTIPLIER = {
    "Bangkok": 1.0,
    "Chiang Mai": 0.8,
    "Pattaya": 1.1,
    "Hua Hin": 1.2,
    "Phuket": 1.5,
    "Krabi": 1.0,
    "Koh Samui": 1.6, # 苏梅很贵
    "Phi Phi Islands": 1.3,
    "Koh Lanta": 0.9,
    "Koh Lipe": 1.4   # 运输成本高
}

# ==========================================
# 3. 交通路网矩阵 (Travel Matrix)
# ==========================================
# 逻辑说明：
# - 同区域 (Region): 时间短，体力消耗低
# - 跨区域: 时间长，体力消耗高
# - 丽贝岛 (Lipe): 特殊处理，到哪里都远

# 定义一些基础常量方便修改
TIME_NEAR = 2     # 邻近城市 (如曼谷-芭提雅)
TIME_MID = 4      # 中程 (如普吉-皮皮岛)
TIME_FAR = 10     # 远程/过夜 (如曼谷-清迈)
TIME_EXTREME = 14 # 极远 (如清迈-丽贝岛)

STAMINA_EASY = 15
STAMINA_TIRED = 35
STAMINA_DYING = 60 # 累死

# 生成完整的 10x10 矩阵逻辑
# 默认所有城市互通（模拟包含了 飞机/车/船 联程）
TRAVEL_ROUTES = {}

# 初始化所有城市对
cities = list(GAME_DATA.keys())
for start in cities:
    TRAVEL_ROUTES[start] = {}
    for end in cities:
        if start == end: continue
        
        # 默认值：远程
        mode = "飞机/大巴联程"
        time = TIME_FAR
        stamina = STAMINA_TIRED
        
        # === 1. 曼谷中心 (Bangkok Hub) ===
        if "Bangkok" in [start, end]:
            other = end if start == "Bangkok" else start
            if other in ["Pattaya", "Hua Hin"]:
                mode = "大巴/小巴"
                time = TIME_NEAR + 1 # 3小时
                stamina = STAMINA_EASY
            elif other in ["Chiang Mai", "Phuket", "Krabi", "Koh Samui"]:
                mode = "飞机"
                time = 4 # 含机场交通
                stamina = 25
            elif other == "Koh Lipe":
                mode = "飞机+车+船"
                time = 9
                stamina = 50
            elif other in ["Phi Phi Islands", "Koh Lanta"]:
                mode = "飞机+船"
                time = 7
                stamina = 40

        # === 2. 北部 (Chiang Mai) 到 南部海岛 ===
        elif "Chiang Mai" in [start, end]:
            # 到任何海岛都很远，通常要在曼谷转机，或者直飞普吉
            other = end if start == "Chiang Mai" else start
            if other == "Phuket":
                mode = "直飞"
                time = 3
                stamina = 20
            elif other == "Koh Lipe":
                mode = "飞机+转机+车+船"
                time = TIME_EXTREME # 14小时
                stamina = STAMINA_DYING
            else: # 到其他海岛
                mode = "飞机+车船联运"
                time = 10
                stamina = 45
                
        # === 3. 安达曼海内圈 (Phuket, Krabi, Phi Phi, Lanta) ===
        # 这些地方彼此很近，通常坐船
        andaman_group = ["Phuket", "Krabi", "Phi Phi Islands", "Koh Lanta"]
        if start in andaman_group and end in andaman_group:
            mode = "快艇/渡轮"
            time = 3 # 平均
            stamina = 20
            if "Phi Phi Islands" in [start, end]: # 皮皮岛去哪都近点
                time = 2
            
        # === 4. 苏梅岛 (Koh Samui) - 孤儿 ===
        # 苏梅在泰国湾，去安达曼海(普吉那边)要横跨大陆
        elif "Koh Samui" in [start, end]:
            other = end if start == "Koh Samui" else start
            if other in andaman_group:
                mode = "飞机/车船联运"
                time = 6
                stamina = 35
                
        # === 5. 丽贝岛 (Koh Lipe) - 远得要命 ===
        # 除了去合艾(不在列表)或者兰塔，去哪都远
        elif "Koh Lipe" in [start, end]:
            other = end if start == "Koh Lipe" else start
            if other == "Koh Lanta":
                mode = "旺季快艇"
                time = 4
                stamina = 30
            else:
                mode = "长途跋涉"
                time = 12
                stamina = 55

        # 写入字典
        TRAVEL_ROUTES[start][end] = {
            "mode": mode,
            "cost_time": time,
            "cost_stamina": stamina
        }

# 可以在这里手动微调某些特定路线
# 例如：芭提雅到华欣有直达渡轮
TRAVEL_ROUTES["Pattaya"]["Hua Hin"] = {"mode": "皇家渡轮", "cost_time": 2, "cost_stamina": 15}
TRAVEL_ROUTES["Hua Hin"]["Pattaya"] = {"mode": "皇家渡轮", "cost_time": 2, "cost_stamina": 15}