# 页面配置（原始代码中的页面设置）
PAGE_LAYOUT = 'wide'
PAGE_TITLE = "Stock Dashboard"

# 默认参数（原始代码中的侧边栏默认值）
DEFAULT_TICKER = 'AAPL'
DEFAULT_PERIOD = '1y'
PERIOD_OPTIONS = ('1d', '3mo', '6mo', '1y', '5y', 'max')
DEFAULT_PERIOD_INDEX = 3  # 默认选1年
SIDEBAR_INFO = '默认股票代码为AAPL，默认时间周期为1年'

# 缓存配置（原始代码中的缓存时间）
CACHE_TTL = 7200  # 2小时缓存

# 绘图配置（原始代码中的图表参数）
CHART_HEIGHT = 600
SMA_WINDOW = 50  # 50日均线窗口
SMA_COLOR = 'orange'  # 均线颜色

# 新闻配置（原始代码中的新闻展示参数）
MAX_NEWS_DISPLAY = 5  # 最多展示5条新闻
THUMBNAIL_WIDTH = 150  # 新闻缩略图宽度
NEWS_COL_RATIO = [1, 4]  # 新闻列比例（缩略图:内容）


# ========== 新增：适配 st_autocomplete 的预设股票配置（核心新增） ==========
# 格式："代码 - 完整名称"（适配 autocomplete 联想/展示）
PRESET_STOCKS = [
    # ========== 全球主要指数 ==========
    "^GSPC - 标普500指数",
    "^IXIC - 纳斯达克综合指数",
    "^DJI - 道琼斯工业平均指数",
    "^RUT - 罗素2000指数",
    "^FTSE - 英国富时100指数",
    "^N225 - 日经225指数",
    "000001.SS - 上证综指",
    "399001.SZ - 深证成指",
    "^HSI - 恒生指数",
    "^STI - 新加坡海峡时报指数",
    "^BVSP - 巴西IBOVESPA指数",
    "CL=F - 纽约原油期货",
    "GC=F - 纽约黄金期货",
    "EURUSD=X - 欧元兑美元",

    # ========== S&P 500 核心龙头股 ==========
    "AAPL - Apple Inc (苹果公司)",
    "MSFT - Microsoft Corp (微软公司)",
    "AMZN - Amazon.com Inc (亚马逊)",
    "NVDA - NVIDIA Corp (英伟达)",
    "GOOGL - Alphabet Inc (Google-A类)",
    "GOOG - Alphabet Inc (Google-C类)",
    "META - Meta Platforms Inc (元宇宙)",
    "TSLA - Tesla Inc (特斯拉)",
    "BRK-B - Berkshire Hathaway Inc (伯克希尔哈撒韦-B类)",
    "UNH - UnitedHealth Group Inc (联合健康)",
    "JNJ - Johnson & Johnson (强生)",
    "V - Visa Inc (维萨)",
    "WMT - Walmart Inc (沃尔玛)",
    "PG - Procter & Gamble Co (宝洁)",
    "MA - Mastercard Inc (万事达卡)",
    "HD - Home Depot Inc (家得宝)",
    "CVX - Chevron Corp (雪佛龙)",
    "MRK - Merck & Co Inc (默克)",
    "ABBV - AbbVie Inc (艾伯维)",
    "PFE - Pfizer Inc (辉瑞)",

    # ========== 科技板块 ==========
    # 半导体
    "AMD - Advanced Micro Devices Inc (超威半导体)",
    "INTC - Intel Corp (英特尔)",
    "QCOM - Qualcomm Inc (高通)",
    "AVGO - Broadcom Inc (博通)",
    "TSM - Taiwan Semiconductor (台积电)",
    "AMAT - Applied Materials Inc (应用材料)",
    "KLAC - KLA Corp (科磊)",
    # 软件/互联网
    "ADBE - Adobe Inc (奥多比)",
    "PYPL - PayPal Holdings Inc (贝宝)",
    "CRM - Salesforce Inc (赛富时)",
    "INTU - Intuit Inc (财捷)",
    "SHOP - Shopify Inc (希音)",
    "SNPS - Synopsys Inc (新思科技)",
    # 硬件/通信
    "NFLX - Netflix Inc (奈飞)",
    "CMCSA - Comcast Corp (康卡斯特)",
    "T - AT&T Inc (美国电话电报)",
    "VZ - Verizon Communications (威瑞森)",
    "HPQ - HP Inc (惠普)",
    "DELL - Dell Technologies (戴尔)",

    # ========== 金融板块 ==========
    "JPM - JPMorgan Chase & Co (摩根大通)",
    "BAC - Bank of America Corp (美国银行)",
    "WFC - Wells Fargo & Co (富国银行)",
    "C - Citigroup Inc (花旗集团)",
    "GS - Goldman Sachs Group (高盛)",
    "MS - Morgan Stanley (摩根士丹利)",
    "AXP - American Express Co (美国运通)",
    "SCHW - Charles Schwab Corp (嘉信理财)",

    # ========== 能源板块 ==========
    "XOM - Exxon Mobil Corp (埃克森美孚)",
    "BP - BP plc (英国石油)",
    "SHEL - Shell plc (壳牌)",
    "COP - ConocoPhillips (康菲石油)",
    "EOG - EOG Resources Inc (EOG资源)",
    "HAL - Halliburton Co (哈里伯顿)",
    "SLB - Schlumberger NV (斯伦贝谢)",

    # ========== 工业板块 ==========
    "UPS - United Parcel Service (联合包裹)",
    "FDX - FedEx Corp (联邦快递)",
    "BA - Boeing Co (波音)",
    "LMT - Lockheed Martin Corp (洛克希德马丁)",
    "CAT - Caterpillar Inc (卡特彼勒)",
    "DE - Deere & Co (约翰迪尔)",
    "HON - Honeywell International (霍尼韦尔)",
    "RTX - RTX Corp (雷神技术)",

    # ========== 消费品板块 ==========
    "MCD - McDonald's Corp (麦当劳)",
    "YUM - Yum! Brands Inc (百胜集团)",
    "COST - Costco Wholesale (开市客)",
    "AMZN - Amazon.com Inc (亚马逊)",  # 重复但保留，核心消费属性
    "KO - Coca-Cola Co (可口可乐)",
    "PEP - PepsiCo Inc (百事可乐)",
    "NKE - Nike Inc (耐克)",
    "LVMUY - LVMH Moët Hennessy (酩悦轩尼诗路易威登)",
    "TGT - Target Corp (塔吉特)",
    "LOW - Lowe's Cos Inc (劳氏)",

    # ========== 医疗健康板块 ==========
    "LLY - Eli Lilly and Co (礼来)",
    "ABT - Abbott Laboratories (雅培)",
    "MDT - Medtronic plc (美敦力)",
    "ISRG - Intuitive Surgical (直觉外科)",
    "REGN - Regeneron Pharmaceuticals (再生元)",
    "VRTX - Vertex Pharmaceuticals (福泰制药)",
    "BIIB - Biogen Inc (渤健)",

    # ========== 中概股 ==========
    "BABA - Alibaba Group Holding Ltd (阿里巴巴)",
    "PDD - Pinduoduo Inc (拼多多)",
    "JD - JD.com Inc (京东)",
    "TCEHY - Tencent Holdings Ltd (腾讯控股)",
    "NIO - NIO Inc (蔚来汽车)",
    "LI - Li Auto Inc (理想汽车)",
    "XPEV - XPeng Inc (小鹏汽车)",
    "BIDU - Baidu Inc (百度)",
    "NTES - NetEase Inc (网易)",
    "MELI - MercadoLibre Inc (美客多)",
    "VIPS - Vipshop Holdings Ltd (唯品会)",
    "YELP - Yelp Inc (雅虎本地)",
    "IQ - iQiyi Inc (爱奇艺)",
    "TME - Tencent Music Entertainment (腾讯音乐)",
    "SINA - Sina Corp (新浪)",
    "WB - Weibo Corp (微博)"
]


# ========== 自选股与基准指数配置 ==========
# 自选股列表（仅代码），用于自选股观察列表模块
WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "BABA", "^GSPC", "^HSI"]

# 常用基准指数（代码 -> 名称）
BENCHMARK_OPTIONS = {
    "^GSPC": "标普500指数",
    "^IXIC": "纳斯达克综合指数",
    "^DJI": "道琼斯工业平均指数",
    "^HSI": "恒生指数",
    "000001.SS": "上证综指",
}



#config存在的必要性：
#1.集中管理配置参数，方便修改和维护；
#2.提高代码可读性，避免硬编码；
#3.支持不同环境配置（开发、测试、生产）；
#4.便于团队协作，确保一致的配置使用。