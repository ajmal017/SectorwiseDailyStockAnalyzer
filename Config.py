from datetime import datetime, timedelta

#####################################
# STOCK
#####################################

# defines
MIN_VECTOR_LEN = 200
BACKOFF_LENGTH = 6  # meaning 5 days
DAILY_MONTH_DATA_BACKOFF = timedelta(days=31 * 6)
WEEKLY_YEAR_DATA_BACKOFF = timedelta(days=365 * 1)
MONTHLY_YEAR_DATA_BACKOFF = timedelta(days=365 * 3)
TEMP = timedelta(days=150)

# trendStrength
featuresTblColNames = ['trend', 'weeklyMove', 'monthlyMove', 'emaIntersection', 'currCloseBeyondLastExt', 'proximity2TrendReversal', 'riskRatio']

#####################################
# STOCK ANALYSIS
#####################################

ANALYSIS_TYPE = 'short'  # 'long'
RS_THS = 0.7
TREND_STRENGTH_THS = 0.5  # 0.0 for debug only
ANALYSIS_THS = 0  # 0 used for debug only
now = datetime.now()
EXTENDED_DEBUG = False
DAILY_ONLY_BASED = False
DEBUG_CONDITIONS = False  # disable by DEFAULT
if not DAILY_ONLY_BASED:
    DEBUG_CONDITIONS = True # in case not running on daily only conditions

RATE_1_SCORE = 20
RATE_2_SCORE = 30
RATE_3_SCORE = 25
RATE_4_SCORE = 25

iSHARES_SECTORS = "iShares"
nINESECTORS = "nineSectors"

SECTORS_SET = nINESECTORS
table_data = [['Sector', 'Raking']]
sectorsPassingCond = [['Ticker', 'Sector', 'Condition', 'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']]
errorStocks = [['Ticker', 'Sector']]
cond = 1
