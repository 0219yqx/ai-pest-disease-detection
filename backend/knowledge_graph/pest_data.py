# ============================================================
# 常见农作物病虫害数据库
# 覆盖：水稻、小麦、玉米、棉花、大豆、花生、油菜、甘薯、马铃薯
# 每条记录含：机械防治、生物防治、化学防治三类方法
# ============================================================

PEST_DATABASE = {
    # ===== 水稻 =====
    "稻瘟病": {
        "name": "稻瘟病", "type": "病害", "crop": "水稻", "sci": "Magnaporthe oryzae",
        "symptoms": "叶片出现梭形病斑，边缘褐色中央灰白；穗颈瘟导致白穗，严重时全田枯白。",
        "cause": "高温多雨、氮肥过量、田间湿度大",
        "treatment_mechanical": "合理施肥控氮，浅水勤灌，发病初期及时拔除病株销毁。",
        "treatment_biological": "选用抗病品种；利用枯草芽孢杆菌等生防菌拌种。",
        "treatment_chemical": "发病初期喷施三环唑或稻瘟灵，间隔7-10天连喷2次。",
        "severity": 5, "season": "6-9月"
    },
    "稻飞虱": {
        "name": "稻飞虱", "type": "害虫", "crop": "水稻", "sci": "Nilaparvata lugens",
        "symptoms": "群集茎基部吸汁，叶片变黄枯萎，严重时出现虱烧状倒伏。",
        "cause": "高温多雨、氮肥过多、种植密度大",
        "treatment_mechanical": "合理密植，控制氮肥，保持田间浅水层，灯光诱杀成虫。",
        "treatment_biological": "保护蜘蛛、黑肩绿盲蝽等天敌；选用抗虫品种。",
        "treatment_chemical": "百穴虫量达500头时喷施吡蚜酮或烯啶虫胺。",
        "severity": 5, "season": "7-9月"
    },
    "纹枯病": {
        "name": "纹枯病", "type": "病害", "crop": "水稻", "sci": "Rhizoctonia solani",
        "symptoms": "近水面叶鞘出现灰绿色水渍状病斑，后扩展成云纹状大斑。",
        "cause": "高温高湿、氮肥过量、种植过密",
        "treatment_mechanical": "合理密植，浅水勤灌，够苗晒田，降低田间湿度。",
        "treatment_biological": "选用抗病品种；利用木霉菌制剂抑制病菌。",
        "treatment_chemical": "发病初期喷施噻呋酰胺或井冈霉素，重点喷施茎基部。",
        "severity": 4, "season": "7-9月"
    },
    "稻曲病": {
        "name": "稻曲病", "type": "病害", "crop": "水稻", "sci": "Ustilaginoidea virens",
        "symptoms": "稻穗上出现墨绿色球状菌核，破裂后散出黄绿色粉末。",
        "cause": "抽穗前后多雨、偏施氮肥",
        "treatment_mechanical": "合理施肥，避免偏施氮肥，及时拔除病穗。",
        "treatment_biological": "选用抗病品种；利用生防菌抑制病原菌。",
        "treatment_chemical": "抽穗前7-10天喷施井冈霉素或戊唑醇预防。",
        "severity": 4, "season": "8-9月"
    },
    "二化螟": {
        "name": "二化螟", "type": "害虫", "crop": "水稻", "sci": "Chilo suppressalis",
        "symptoms": "幼虫钻蛀茎秆，造成枯鞘、枯心和白穗。",
        "cause": "越冬基数大、气候适宜",
        "treatment_mechanical": "冬耕灭茬深翻，灯光诱杀成虫，及时处理稻草。",
        "treatment_biological": "释放赤眼蜂寄生卵块；保护青蛙等天敌。",
        "treatment_chemical": "卵孵化高峰期喷施氯虫苯甲酰胺或阿维菌素。",
        "severity": 4, "season": "5-8月"
    },
    "稻纵卷叶螟": {
        "name": "稻纵卷叶螟", "type": "害虫", "crop": "水稻", "sci": "Cnaphalocrocis medinalis",
        "symptoms": "幼虫将叶片纵卷成筒状取食叶肉，留下白色条斑。",
        "cause": "迁飞性害虫、夏季多雨",
        "treatment_mechanical": "灯光诱杀成虫，合理施肥避免贪青晚熟。",
        "treatment_biological": "保护纵卷叶螟绒茧蜂等天敌；选用抗虫品种。",
        "treatment_chemical": "1-2龄幼虫高峰期喷施甲维盐或阿维菌素。",
        "severity": 4, "season": "7-9月"
    },

    # ===== 小麦 =====
    "小麦条锈病": {
        "name": "小麦条锈病", "type": "病害", "crop": "小麦", "sci": "Puccinia striiformis",
        "symptoms": "叶片出现黄色条纹状夏孢子堆，破裂后散出黄色粉末。",
        "cause": "湿度大、温度15-25℃、种植密度大",
        "treatment_mechanical": "种植抗锈品种，合理轮作，控制种植密度。",
        "treatment_biological": "利用条锈病菌重寄生菌等生防资源；选用多基因抗性品种。",
        "treatment_chemical": "发病初期喷施三唑酮或戊唑醇，间隔10天连喷2次。",
        "severity": 5, "season": "3-5月"
    },
    "小麦白粉病": {
        "name": "小麦白粉病", "type": "病害", "crop": "小麦", "sci": "Blumeria graminis",
        "symptoms": "叶片表面出现白色粉状霉层，严重时叶片变黄卷曲。",
        "cause": "高温高湿、通风不良、氮肥过量",
        "treatment_mechanical": "合理密植，加强通风透光，适当控制氮肥。",
        "treatment_biological": "选用抗病品种；保护田间有益微生物群落。",
        "treatment_chemical": "病叶率达10%时喷施三唑酮或醚菌酯。",
        "severity": 4, "season": "3-6月"
    },
    "小麦赤霉病": {
        "name": "小麦赤霉病", "type": "病害", "crop": "小麦", "sci": "Fusarium graminearum",
        "symptoms": "穗部出现粉红色霉层，籽粒秕瘦，严重时小穗枯死。",
        "cause": "抽穗扬花期高温多雨",
        "treatment_mechanical": "深翻灭茬清除病残体，合理轮作，适时播种避开雨季。",
        "treatment_biological": "选用中抗及以上品种；利用生防木霉菌拌种。",
        "treatment_chemical": "齐穗至扬花期喷施戊唑醇或氰烯菌酯，遇雨补喷。",
        "severity": 5, "season": "4-5月"
    },
    "小麦吸浆虫": {
        "name": "小麦吸浆虫", "type": "害虫", "crop": "小麦", "sci": "Sitodiplosis mosellana",
        "symptoms": "幼虫吸食麦粒浆液，麦粒秕瘦空壳，严重时全穗无实粒。",
        "cause": "连作、春季多雨",
        "treatment_mechanical": "轮作换茬，深翻土壤灭蛹，土壤处理杀幼虫。",
        "treatment_biological": "保护宽腹姬小蜂等寄生性天敌。",
        "treatment_chemical": "孕穗期撒施毒死蜱颗粒剂，成虫期喷施高效氯氟氰菊酯。",
        "severity": 4, "season": "4-5月"
    },

    # ===== 玉米 =====
    "玉米螟": {
        "name": "玉米螟", "type": "害虫", "crop": "玉米", "sci": "Ostrinia furnacalis",
        "symptoms": "幼虫钻蛀茎秆和果穗，叶片出现排孔，茎秆易折断。",
        "cause": "越冬幼虫基数大、夏季高温",
        "treatment_mechanical": "秸秆回收处理越冬寄主，灯光诱杀成虫。",
        "treatment_biological": "心叶末期施用Bt白僵菌颗粒剂；释放赤眼蜂寄生卵块。",
        "treatment_chemical": "心叶末期撒施氯虫苯甲酰胺颗粒剂或喷施甲维盐。",
        "severity": 4, "season": "6-8月"
    },
    "玉米大斑病": {
        "name": "玉米大斑病", "type": "病害", "crop": "玉米", "sci": "Exserohilum turcicum",
        "symptoms": "叶片出现长梭形褐色大斑，长度可达15厘米，严重时叶片枯焦。",
        "cause": "高温高湿、连作、种植密度大",
        "treatment_mechanical": "轮作倒茬，清除病残体，合理密植。",
        "treatment_biological": "选用抗病品种；利用木霉菌等生防菌。",
        "treatment_chemical": "发病初期喷施吡唑醚菌酯或代森锰锌。",
        "severity": 4, "season": "7-9月"
    },
    "玉米锈病": {
        "name": "玉米锈病", "type": "病害", "crop": "玉米", "sci": "Puccinia sorghi",
        "symptoms": "叶片出现褐色夏孢子堆，破裂后散出锈粉，严重时叶片枯焦。",
        "cause": "高温多雨、种植密度大",
        "treatment_mechanical": "合理密植，清除田间病残体，增施磷钾肥。",
        "treatment_biological": "选用抗锈品种；利用重寄生菌等生防资源。",
        "treatment_chemical": "发病初期喷施三唑酮或戊唑醇。",
        "severity": 3, "season": "7-9月"
    },
    "玉米茎腐病": {
        "name": "玉米茎腐病", "type": "病害", "crop": "玉米", "sci": "Pythium/Fusarium/Erwinia",
        "symptoms": "茎基部变软腐烂，叶片自下而上枯黄，严重时植株倒伏。",
        "cause": "高温高湿、连作、虫伤",
        "treatment_mechanical": "轮作倒茬，合理密植，及时排除田间积水。",
        "treatment_biological": "选用抗病品种；利用生防菌拌种预防。",
        "treatment_chemical": "发病初期用噁霉灵或噻菌铜灌根。",
        "severity": 4, "season": "7-9月"
    },

    # ===== 棉花 =====
    "棉铃虫": {
        "name": "棉铃虫", "type": "害虫", "crop": "棉花", "sci": "Helicoverpa armigera",
        "symptoms": "幼虫取食叶片、花蕾和幼铃，造成落蕾落铃。",
        "cause": "高温干旱、寄主植物多",
        "treatment_mechanical": "深耕灭蛹，性诱剂诱杀成虫，及时整枝打杈。",
        "treatment_biological": "释放赤眼蜂；种植诱集带；保护捕食性天敌。",
        "treatment_chemical": "二代百株幼虫达10头时喷施氯虫苯甲酰胺或甲维盐。",
        "severity": 4, "season": "6-9月"
    },
    "棉花枯萎病": {
        "name": "棉花枯萎病", "type": "病害", "crop": "棉花", "sci": "Fusarium oxysporum",
        "symptoms": "叶片变黄萎蔫，维管束变褐，横切面可见褐色环。",
        "cause": "连作重茬、高温多雨",
        "treatment_mechanical": "轮作3年以上，选用无病土育苗，及时拔除病株。",
        "treatment_biological": "选用抗病品种嫁接；利用木霉菌等生防制剂。",
        "treatment_chemical": "发病初期灌根施用噁霉灵或多菌灵。",
        "severity": 5, "season": "6-8月"
    },
    "棉花黄萎病": {
        "name": "棉花黄萎病", "type": "病害", "crop": "棉花", "sci": "Verticillium dahliae",
        "symptoms": "叶片脉间变黄呈斑驳状，叶缘枯焦，严重时叶片脱落。",
        "cause": "土壤传播、温度适宜25-28℃",
        "treatment_mechanical": "轮作倒茬，增施有机肥改良土壤，加强排水。",
        "treatment_biological": "选用抗病品种；利用生防放线菌抑制病菌。",
        "treatment_chemical": "发病初期用噁霉灵·多菌灵灌根。",
        "severity": 5, "season": "6-9月"
    },

    # ===== 大豆 =====
    "大豆根腐病": {
        "name": "大豆根腐病", "type": "病害", "crop": "大豆", "sci": "Fusarium/Pythium/Rhizoctonia",
        "symptoms": "根系变褐腐烂，地上部矮小黄化，严重时植株枯死。",
        "cause": "土壤湿度过大、连作",
        "treatment_mechanical": "轮作3年以上，深翻土壤，排除田间积水。",
        "treatment_biological": "选用抗病品种；利用生防木霉菌拌种。",
        "treatment_chemical": "播种前用噁霉灵或多菌灵拌种，发病初期灌根。",
        "severity": 4, "season": "6-8月"
    },
    "大豆蚜虫": {
        "name": "大豆蚜虫", "type": "害虫", "crop": "大豆", "sci": "Aphis glycines",
        "symptoms": "群集嫩茎和叶片背面吸汁，叶片卷缩变黄，植株矮化。",
        "cause": "温度适宜、天敌减少",
        "treatment_mechanical": "黄板诱杀，清除田间杂草减少虫源。",
        "treatment_biological": "保护瓢虫、食蚜蝇等天敌；利用蚜茧蜂寄生。",
        "treatment_chemical": "百株蚜量达1000头时喷施吡虫啉或啶虫脒。",
        "severity": 3, "season": "6-8月"
    },
    "大豆紫斑病": {
        "name": "大豆紫斑病", "type": "病害", "crop": "大豆", "sci": "Cercospora kikuchii",
        "symptoms": "叶片出现紫红色点斑病斑，严重时叶片枯焦。",
        "cause": "高温高湿、连作",
        "treatment_mechanical": "轮作倒茬，清除病残体，合理密植。",
        "treatment_biological": "选用抗病品种；利用生防菌预防。",
        "treatment_chemical": "发病初期喷施苯醚甲环唑或代森锰锌。",
        "severity": 3, "season": "7-9月"
    },

    # ===== 花生 =====
    "花生叶斑病": {
        "name": "花生叶斑病", "type": "病害", "crop": "花生", "sci": "Cercospora arachidicola",
        "symptoms": "叶片出现褐色圆形病斑，后期病斑融合导致叶片枯焦。",
        "cause": "高温高湿、多雨",
        "treatment_mechanical": "轮作2年以上，清除病残体，合理密植。",
        "treatment_biological": "选用抗病品种；利用生防木霉菌。",
        "treatment_chemical": "发病初期喷施百菌清或代森锰锌，间隔10天连喷2次。",
        "severity": 3, "season": "6-9月"
    },
    "花生白绢病": {
        "name": "花生白绢病", "type": "病害", "crop": "花生", "sci": "Sclerotium rolfsii",
        "symptoms": "茎基部及果壳表面生白色绢丝层，后形成褐色菌核。",
        "cause": "高温高湿、土壤菌核多",
        "treatment_mechanical": "轮作2年以上，深翻土壤，加强排水降湿。",
        "treatment_biological": "利用木霉菌制剂抑制菌核萌发。",
        "treatment_chemical": "发病初期喷施噻呋酰胺或井冈霉素灌根。",
        "severity": 4, "season": "7-8月"
    },

    # ===== 油菜 =====
    "油菜菌核病": {
        "name": "油菜菌核病", "type": "病害", "crop": "油菜", "sci": "Sclerotinia sclerotiorum",
        "symptoms": "茎秆发生水渍状病斑，表面生白色绢丝，形成黑色菌核。",
        "cause": "湿度大、通风不良、连作",
        "treatment_mechanical": "轮作3年，加强排水，清除病株残体。",
        "treatment_biological": "利用盾壳霉寄生菌核；选用抗病品种。",
        "treatment_chemical": "初花期喷施菌核灵或啶酰菌胺，间隔7天连喷2次。",
        "severity": 4, "season": "3-5月"
    },

    # ===== 甘薯 =====
    "甘薯黑斑病": {
        "name": "甘薯黑斑病", "type": "病害", "crop": "甘薯", "sci": "Ceratocystis fimbriata",
        "symptoms": "薯块上出现黑色凹陷斑，后扩大腐烂，有苦味。",
        "cause": "贮藏期间温度适宜、伤口多",
        "treatment_mechanical": "选用无病种薯，贮藏前晾晒，控制窖温11-13℃。",
        "treatment_biological": "利用拮抗菌处理种薯。",
        "treatment_chemical": "种薯用多菌灵浸泡消毒，贮藏前喷施杀菌剂。",
        "severity": 3, "season": "贮藏期"
    },

    # ===== 马铃薯 =====
    "马铃薯晚疫病": {
        "name": "马铃薯晚疫病", "type": "病害", "crop": "马铃薯", "sci": "Phytophthora infestans",
        "symptoms": "叶片出现水渍状病斑，叶背灰白色霉层，薯块变褐腐烂。",
        "cause": "低温高湿、多雨",
        "treatment_mechanical": "选用无病种薯，高畦栽培，及时排水，清除中心病株。",
        "treatment_biological": "选用抗病品种；利用生防枯草芽孢杆菌。",
        "treatment_chemical": "发病初期喷施甲霜灵·锰锌或烯酰吗啉，间隔7天连喷3次。",
        "severity": 5, "season": "6-9月"
    },

    # ===== 通用/多种作物 =====
    "蚜虫": {
        "name": "蚜虫", "type": "害虫", "crop": "多种作物", "sci": "Aphidoidea",
        "symptoms": "群集嫩叶嫩茎吸汁，叶片卷曲发黄，分泌蜜露引发煤污病。",
        "cause": "温暖干燥、天敌数量少",
        "treatment_mechanical": "黄板诱杀，清除田间杂草，银灰膜驱避。",
        "treatment_biological": "保护瓢虫、食蚜蝇等天敌；利用蚜茧蜂寄生。",
        "treatment_chemical": "喷施吡虫啉或啶虫脒，注意轮换用药。",
        "severity": 3, "season": "4-10月"
    },
    "红蜘蛛": {
        "name": "红蜘蛛", "type": "害虫", "crop": "棉花/玉米", "sci": "Tetranychus spp.",
        "symptoms": "叶片灰白色失绿斑点，严重时叶片干枯脱落，叶背可见红色小点及丝网。",
        "cause": "高温干燥、干旱少雨",
        "treatment_mechanical": "合理灌溉避免干旱，清除田间杂草。",
        "treatment_biological": "保护捕食螨等天敌；释放捕食螨控制种群。",
        "treatment_chemical": "喷施阿维菌素或哒螨灵，重点喷施叶背。",
        "severity": 3, "season": "6-9月"
    },
    "地老虎": {
        "name": "地老虎", "type": "害虫", "crop": "多种作物", "sci": "Agrotis ipsilon",
        "symptoms": "幼虫在土中咬断幼苗根茎，导致植株枯死，造成缺苗断垄。",
        "cause": "越冬基数大、杂草多",
        "treatment_mechanical": "冬耕消灭越冬虫源，清除杂草，灯光诱杀成虫。",
        "treatment_biological": "利用白僵菌制剂处理土壤；保护步甲等天敌。",
        "treatment_chemical": "幼虫3龄前喷施氯虫苯甲酰胺或撒施毒饵诱杀。",
        "severity": 4, "season": "4-6月"
    },
}


# 河南省病虫害发生热点区域数据
HENAN_HOTSPOTS = [
    {"id": 1, "name": "郑州市", "lng": 113.6254, "lat": 34.7466, "level": "中度", "diseases": ["小麦条锈病", "小麦白粉病", "蚜虫"], "crop": "小麦"},
    {"id": 2, "name": "开封市", "lng": 114.3415, "lat": 34.7971, "level": "重度", "diseases": ["小麦赤霉病", "小麦条锈病"], "crop": "小麦"},
    {"id": 3, "name": "洛阳市", "lng": 112.4539, "lat": 34.6197, "level": "轻度", "diseases": ["玉米螟", "玉米大斑病"], "crop": "玉米"},
    {"id": 4, "name": "平顶山市", "lng": 113.2927, "lat": 33.7658, "level": "中度", "diseases": ["小麦白粉病", "红蜘蛛"], "crop": "小麦"},
    {"id": 5, "name": "安阳市", "lng": 114.3922, "lat": 36.0977, "level": "重度", "diseases": ["小麦条锈病", "小麦吸浆虫"], "crop": "小麦"},
    {"id": 6, "name": "鹤壁市", "lng": 114.2974, "lat": 35.7484, "level": "中度", "diseases": ["玉米螟", "蚜虫"], "crop": "玉米"},
    {"id": 7, "name": "新乡市", "lng": 113.9265, "lat": 35.3035, "level": "重度", "diseases": ["小麦赤霉病", "纹枯病"], "crop": "小麦"},
    {"id": 8, "name": "焦作市", "lng": 113.2419, "lat": 35.2159, "level": "中度", "diseases": ["玉米大斑病", "玉米螟"], "crop": "玉米"},
    {"id": 9, "name": "濮阳市", "lng": 115.0297, "lat": 35.7681, "level": "中度", "diseases": ["棉铃虫", "棉花枯萎病"], "crop": "棉花"},
    {"id": 10, "name": "许昌市", "lng": 113.8526, "lat": 34.0354, "level": "轻度", "diseases": ["蚜虫", "小麦白粉病"], "crop": "小麦"},
    {"id": 11, "name": "漯河市", "lng": 114.0162, "lat": 33.5817, "level": "中度", "diseases": ["小麦赤霉病", "纹枯病"], "crop": "小麦"},
    {"id": 12, "name": "三门峡市", "lng": 111.1942, "lat": 34.7772, "level": "轻度", "diseases": ["蚜虫", "红蜘蛛"], "crop": "玉米"},
    {"id": 13, "name": "南阳市", "lng": 112.5283, "lat": 32.9908, "level": "重度", "diseases": ["棉铃虫", "棉花黄萎病"], "crop": "棉花"},
    {"id": 14, "name": "商丘市", "lng": 115.6562, "lat": 34.4143, "level": "中度", "diseases": ["大豆紫斑病", "蚜虫"], "crop": "大豆"},
    {"id": 15, "name": "信阳市", "lng": 114.0910, "lat": 32.1286, "level": "重度", "diseases": ["稻瘟病", "稻飞虱", "纹枯病"], "crop": "水稻"},
    {"id": 16, "name": "周口市", "lng": 114.6963, "lat": 33.6206, "level": "中度", "diseases": ["小麦条锈病", "花生叶斑病"], "crop": "小麦"},
    {"id": 17, "name": "驻马店市", "lng": 114.0224, "lat": 32.9809, "level": "重度", "diseases": ["稻瘟病", "稻飞虱"], "crop": "水稻"},
    {"id": 18, "name": "济源市", "lng": 112.5902, "lat": 35.0675, "level": "轻度", "diseases": ["玉米螟", "地老虎"], "crop": "玉米"},
]


def get_pest_info(name: str):
    """根据病虫害名称获取详细信息"""
    return PEST_DATABASE.get(name)


def search_pests(keyword: str):
    """按关键词搜索病虫害"""
    keyword = keyword.lower()
    results = []
    for name, info in PEST_DATABASE.items():
        if (keyword in name.lower() or
                keyword in info.get("crop", "").lower() or
                keyword in info.get("symptoms", "").lower() or
                keyword in info.get("type", "").lower()):
            results.append(info)
    return results


def get_all_pests_enriched():
    """返回全部病虫害数据"""
    return [enrich_pest_record(v) for v in PEST_DATABASE.values()]


def enrich_pest_record(record: dict) -> dict:
    """为记录添加前端需要的段落字段"""
    r = dict(record)
    sev = r.get("severity", 3)
    season = r.get("season", "")

    # 症状段落（简短，一段话）
    if not r.get("symptoms_paragraph"):
        r["symptoms_paragraph"] = r.get("symptoms", "")

    # 原因段落（简短，一段话）
    if not r.get("cause_paragraph"):
        r["cause_paragraph"] = r.get("cause", "")

    # 历史发生规律
    if not r.get("history"):
        if sev >= 5:
            r["history"] = "属常发性重大病虫害，暖冬年份偏重发生，流行年份可造成严重损失。"
        elif sev >= 4:
            r["history"] = "每年均有不同程度发生，遇适宜气候条件可偏重流行。"
        else:
            r["history"] = "一般年份零星发生，做好日常预防可有效控制。"

    # 传播途径（兼容前端展示）
    if not r.get("spread"):
        r["spread"] = "气流/雨水传播"

    # 影响产量（兼容前端展示）
    if not r.get("impact"):
        if sev >= 5:
            r["impact"] = "减产 20-50%"
        elif sev >= 4:
            r["impact"] = "减产 10-25%"
        elif sev >= 3:
            r["impact"] = "减产 5-15%"
        else:
            r["impact"] = "减产 <5%"

    # 最佳防治时期
    if not r.get("bestTime"):
        r["bestTime"] = f"{season}为关键防治期，发病初期用药效果最佳。"

    return r


def get_knowledge_graph():
    """构建知识图谱数据（节点+边）"""
    nodes = []
    edges = []
    node_id_map = {}

    # 作物节点
    crops = set()
    for info in PEST_DATABASE.values():
        crop_str = info.get("crop", "")
        for c in crop_str.replace("，", ",").replace("/", ",").split(","):
            c = c.strip()
            if c and c not in ["多种作物"]:
                crops.add(c)

    for i, crop in enumerate(sorted(crops)):
        nid = f"crop_{i}"
        node_id_map[f"crop:{crop}"] = nid
        nodes.append({"id": nid, "label": crop, "type": "crop", "color": "#4CAF50"})

    # 病虫害节点
    for j, (name, info) in enumerate(PEST_DATABASE.items()):
        nid = f"pest_{j}"
        node_id_map[f"pest:{name}"] = nid
        color = "#F44336" if info.get("type") == "病害" else "#FF9800"
        nodes.append({"id": nid, "label": name, "type": info.get("type", "病害"),
                       "severity": info.get("severity", 3), "color": color})

    # 构建 crop→pest 边
    for name, info in PEST_DATABASE.items():
        pest_nid = node_id_map.get(f"pest:{name}")
        if not pest_nid:
            continue
        crop_str = info.get("crop", "")
        for c in crop_str.replace("，", ",").replace("/", ",").split(","):
            c = c.strip()
            crop_nid = node_id_map.get(f"crop:{c}")
            if crop_nid:
                edges.append({"from": crop_nid, "to": pest_nid, "label": "感染"})

    return {"nodes": nodes, "edges": edges}
