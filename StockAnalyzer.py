from Stock import *
from Utils import *
from pandas import DataFrame
from finviz import getFinviz
from terminaltables import AsciiTable
from Config import *
import logging
import time
import csv
import urllib
import os.path

logging.basicConfig(level=logging.INFO, format='%(message)s',)
logger = logging.getLogger(__name__)

class IntersectBasedAnalysisClass:

    stocksList = []
    numStocksInList = 0
    stock = StockClass()
    stocks4Analysis = []
    erroneousStocks = []
    out_file = 0
    if SECTORS_SET == iSHARES_SECTORS:
        sectors_list = ['IBB', 'IYR', 'IYW', 'ICF', 'IYH', 'IYT', 'ITB', 'REM', 'IYF', 'IYE', 'IYJ',
                        'IHE', 'IHI', 'IDU', 'IYM', 'IYG', 'IAT', 'IYZ', 'SOXX', 'IYK', 'IHF', 'IYC',
                        'IEO', 'IEZ', 'ITA', 'REZ', 'IAI', 'IAK', 'FTY']
    elif SECTORS_SET == nINESECTORS:
        sectors_list = ['XLB', 'XLE', 'XLP', 'XLF', 'XLV',
                        'XLI', 'XLY', 'XLK', 'XLU']
    # 4DEBUG
    # sectors_list = ['XLB']

    sectors_to_analyze = []
    sectors_rating = []

    def getSectorsData(self):
        for sector in self.sectors_list:
            logger.debug('#### Start handling %s ####', sector)
            self.stock.getData(i_symbol=sector, i_destDictKey=sector)
            self.stock.getMovementType(i_destDictKey=sector, i_freq='d')
            self.stock.getMovementType(i_destDictKey=sector, i_freq='w')
            self.stock.getMovementType(i_destDictKey=sector, i_freq='m')  # optional
            self.stock.reversalPointsDetector(i_destDictKey=sector)
            self.stock.trend(i_destDictKey=sector, i_freq='d', i_debug=False)
            self.stock.rs(i_freq='d', i_ref='SPY', i_src=sector)
            self.stock.ema(i_destDictKey=sector, i_period=34)
            self.stock.ema(i_destDictKey=sector, i_period=14)
            # self.stock.ema(i_destDictKey=sector, i_period=200)
            # self.stock.ema(i_destDictKey=sector, i_period=50)
            logger.debug('#### End handling %s ####', sector)

    def getSpyData(self):
        logger.debug("#### Start handling SPY ####")
        self.out_file.write("#### Start handling SPY ####\n")

        self.stock.getData(i_symbol='SPY', i_destDictKey='SPY')
        self.stock.getMovementType(i_destDictKey='SPY')
        self.stock.reversalPointsDetector(i_destDictKey='SPY')
        self.stock.trend(i_destDictKey='SPY', i_freq='d', i_debug=False)
        self.stock.ema(i_destDictKey='SPY', i_period=34)
        self.stock.ema(i_destDictKey='SPY', i_period=14)
        # self.stock.ema(i_destDictKey='SPY', i_period=200)
        # self.stock.ema(i_destDictKey='SPY', i_period=50)

        logger.debug("#### End handling SPY ####")
        self.out_file.write("#### End handling SPY ####\n")

    def rateSectors(self):
        idx = 0
        for sector in self.sectors_list:
            rating = 0
            # self.stock.plotlyData(i_destDictKey=sector)

            if self.stock.m_data['SPY']['analysis']['d']['trendType'] == self.stock.m_data[sector]['analysis']['d']['trendType'] and \
               self.stock.m_data['SPY']['analysis']['d']['trendType'] > 0 and \
               self.stock.m_data[sector]['analysis']['d']['trendType'] > 0:
                rating = rating + RATE_1_SCORE

            if not DAILY_ONLY_BASED:
                if self.stock.m_data[sector]['analysis']['d']['trendType'] == 2:  # up
                    if self.stock.m_data[sector]['analysis']['w']['moveType'] == 2:  # up
                        rating = rating + RATE_2_SCORE * 0.5
                    if self.stock.m_data['SPY']['analysis']['w']['moveType'] == 2:  # up
                        rating = rating + RATE_2_SCORE * 0.125
                    if self.stock.m_data[sector]['analysis']['m']['moveType'] == 2:  # up
                        rating = rating + RATE_2_SCORE * 0.25
                    if self.stock.m_data['SPY']['analysis']['m']['moveType'] == 2:  # up
                        rating = rating + RATE_2_SCORE * 0.125
                elif self.stock.m_data[sector]['analysis']['d']['trendType'] == 1:  # down
                    if self.stock.m_data[sector]['analysis']['w']['moveType'] == 1:  # down
                        rating = rating + RATE_2_SCORE * 0.5
                    if self.stock.m_data['SPY']['analysis']['w']['moveType'] == 1:  # down
                        rating = rating + RATE_2_SCORE * 0.125
                    if self.stock.m_data[sector]['analysis']['m']['moveType'] == 1:  # down
                        rating = rating + RATE_2_SCORE * 0.25
                    if self.stock.m_data['SPY']['analysis']['m']['moveType'] == 1:  # down
                        rating = rating + RATE_2_SCORE * 0.125

            if self.stock.m_data[sector]['analysis']['d']['rs'] >= RS_THS:
                rating = rating + RATE_3_SCORE

            if DAILY_ONLY_BASED:
                if (self.stock.m_data[sector]['analysis']['d']['trendType'] == 2) and \
                   (self.stock.m_data[sector]['analysis']['d']['moveType'] == 2):  # up
                    rating = rating + RATE_4_SCORE * 0.7
                elif (self.stock.m_data[sector]['analysis']['d']['trendType'] == 1) and \
                     (self.stock.m_data[sector]['analysis']['d']['moveType'] == 1):  # up
                    rating = rating + RATE_4_SCORE * 0.7
            else:
                if (self.stock.m_data[sector]['analysis']['d']['trendType'] == 2) and \
                   (self.stock.m_data[sector]['analysis']['d']['moveType'] == 2) and \
                   (self.stock.m_data[sector]['analysis']['w']['moveType'] == 2):  # up
                    rating = rating + RATE_4_SCORE * 0.7
                elif (self.stock.m_data[sector]['analysis']['d']['trendType'] == 1) and \
                     (self.stock.m_data[sector]['analysis']['d']['moveType'] == 1) and \
                     (self.stock.m_data[sector]['analysis']['w']['moveType'] == 1):  # up
                    rating = rating + RATE_4_SCORE * 0.7

                if (self.stock.m_data[sector]['analysis']['d']['moveType'] == 2) and \
                   (self.stock.m_data[sector]['analysis']['w']['moveType'] == 2):  # up
                    rating = rating + RATE_4_SCORE * 0.3
                elif (self.stock.m_data[sector]['analysis']['d']['moveType'] == 1) and \
                     (self.stock.m_data[sector]['analysis']['w']['moveType'] == 1):  # up
                    rating = rating + RATE_4_SCORE * 0.3

            self.sectors_rating.append(rating)
            idx += 1
        # adjust the rating threshold and pick sectors for analysis
        idx = 0
        np_array = np.asarray(self.sectors_rating)
        ANALYSIS_THS = sum(self.sectors_rating) / len(np_array[np_array > 0])
        logger.info("Adjusted ANALYSIS_THS: %d", ANALYSIS_THS)
        for sector in self.sectors_list:
            logger.info("rating[%s]: %d", sector, self.sectors_rating[idx])
            rating = self.sectors_rating[idx]
            if rating >= ANALYSIS_THS:
                self.sectors_to_analyze.append(idx)
                table_data.append([sector, str(rating) + '/' + str(RATE_1_SCORE+RATE_2_SCORE+RATE_3_SCORE+RATE_4_SCORE)])
            idx += 1

        rankingTable = AsciiTable(table_data)
        rankingTable.inner_heading_row_border = True
        logger.info("%s", rankingTable.table)
        self.out_file.write(rankingTable.table)
        self.out_file.write('\n')
        logger.info('\n')

        logger.debug("Sectors to be analyzed: %s", self.sectors_to_analyze)
        logger.debug("Sectors ranking: %s", self.sectors_rating)
        self.out_file.write("Sectors to be analyzed and it rank:\n")
        for sector in self.sectors_to_analyze:
            self.out_file.write("%s:%f\n" % (self.sectors_list[sector], self.sectors_rating[sector]))

    def checkIfUpdate(self):
        # day = datetime.today().day
        lastEntryDate = self.stock.getDataDate()
        logger.info("Last entry date: %d/%d", lastEntryDate.day, lastEntryDate.month)
        self.out_file.write("Last entry's day: %d/%d\n" % (lastEntryDate.day, lastEntryDate.month))

    def can_read_list_from_file(self, sector):
        filename = "%s.dat" % sector
        current_time = datetime.today()
        current_month = current_time.month
        if os.path.isfile(filename):
            modification_date = time.localtime(os.stat(filename).st_mtime)
            modification_month = modification_date[1]
            if modification_month == current_month:
                return True
            else:
                os.remove(filename)
                return False

    def read_list_from_file(self, sector):
        filename = "%s.dat" % sector
        with open(filename, "r") as f:
            list = f.read().splitlines()
            return set(list)

    def write_to_file(self, sector, lst):
        filename = "%s.dat" % sector
        with open(filename, "w") as f:
            for item in lst:
                f.write("%s\n" % item)

    def analyze_sector(self, index):
        global SECTORS_SET
        global cond
        global sectorsPassingCond
        global errorStocks

        if SECTORS_SET == iSHARES_SECTORS:
            f = open('SectorHoldings.dat', 'r')
        elif SECTORS_SET == nINESECTORS:
            f = open('FinvizSectors.dat', 'r')

        sectorHoldingsUrls = f.readlines()
        holding = sectorHoldingsUrls[index]

        logger.info("\n")
        logger.info("Holding[%s]: %s", self.sectors_list[index], holding)
        self.debug_buffers[index].append("Holding[%d]: %s\n" % (index, holding))
        self.debug_buffers[index].append("Sector: %s, Rank: %f\n" % (self.sectors_list[index], self.sectors_rating[index]))

        idx = 0
        if SECTORS_SET == iSHARES_SECTORS:
            response = urllib.urlopen(holding)
            cr = csv.reader(response)
            # cr = pd.read_csv(response)
            data = []
            copyfromhere = False

            for row in cr:
                if 'Ticker' in row:
                    copyfromhere = True
                if copyfromhere:
                    data.append(row)
            df = DataFrame(data[1:-2], columns=data[0])

            self.stocksList = df['Ticker']
        elif SECTORS_SET == nINESECTORS:
            if self.can_read_list_from_file(self.sectors_list[index]):
                self.stocksList = self.read_list_from_file(self.sectors_list[index])
            else:
                self.stocksList = getFinviz(holding)
                self.write_to_file(self.sectors_list[index], self.stocksList)

        self.numStocksInList = len(self.stocksList)
        logger.info("Stocks list: %s", self.stocksList)

        # 4DEBUG
        # self.stocksList = ['BGH']

        for symbolName in self.stocksList:
            # stock = Stock(name=symbolName)
            self.stock.__init__(name=symbolName)

            # get data of required symbol
            idx = idx + 1
            cond = 1

            logger.info('#### [%d/%d]: Start handling [%s] ####', idx, self.numStocksInList, symbolName)
            self.debug_buffers[index].append("#### [ %d / %d ]: Start handling [ %s ] ####\n" % (idx, self.numStocksInList, symbolName))

            try:
                self.stock.getData(i_symbol=symbolName, i_destDictKey='symbol')
            except:
                self.erroneousStocks.append(symbolName)
                save_obj(self.erroneousStocks, 'erroneousStocks_' + ANALYSIS_TYPE)
                errorStocks.append([symbolName, self.sectors_list[index]])
                logger.warning('!!!! GetData ERROR !!!!')
                self.debug_buffers[index].append('!!!! GetData ERROR !!!!\n')
                continue

            # self.stock.findLocalMinMax(i_destDictKey='symbol')
            self.stock.getMovementType(i_destDictKey='symbol', i_freq='d')
            self.stock.getMovementType(i_destDictKey='symbol', i_freq='w')
            self.stock.getMovementType(i_destDictKey='symbol', i_freq='m')  # optional
            self.stock.reversalPointsDetector(i_destDictKey='symbol')
            self.stock.ema(i_destDictKey='symbol', i_period=34)
            self.stock.ema(i_destDictKey='symbol', i_period=14)
            self.stock.ema(i_destDictKey='symbol', i_period=200)
            self.stock.ema(i_destDictKey='symbol', i_period=50)
            self.stock.rs(i_freq='d')
            self.stock.emaIntersect()
            self.stock.trend(i_destDictKey='symbol', i_freq='d', i_debug=False)
            self.stock.findLastTimeFrameMove(i_destDictKey='symbol', i_destFreq='w')
            self.stock.findLastTimeFrameMove(i_destDictKey='symbol', i_destFreq='m')
            self.stock.proximityToTrendReversal(i_destDictKey='symbol', i_debug=False)
            self.stock.findLastTimeFrameExceeding(i_destDictKey='symbol', i_destFreq='w', i_debug=False)
            self.stock.riskRatioCalc(i_destDictKey='symbol', i_debug=False)
            self.stock.updatToFeaturesDB(i_debug=False)

            # stock.simplePlot(i_destDictKey='symbol')
            # stock.plotData(i_destDictKey='symbol', i_debug=True)
            # stock.plotlyData(i_destDictKey='symbol')

            if DAILY_ONLY_BASED:
                l_conditions = [int(self.stock.m_data['symbol']['analysis']['d']['intersectInd']),               # condition 0
                                int(self.stock.m_data['SPY']['analysis']['d']['rs'] >= RS_THS),               # condition 1
                                True,          # condition 2
                                True,         # condition 3
                                int(self.stock.m_data['symbol']['analysis']['d']['proximity2TrendReversal']),    # condition 4
                                int(((self.stock.m_data['symbol']['analysis']['d']['lastWeeklyHigh'] and
                                    self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) or
                                    (self.stock.m_data['symbol']['analysis']['d']['lastWeeklyLow'] and
                                    self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1))),          # condition 5
                                int((self.stock.m_data['symbol']['analysis']['d']['riskRatio'] > 0.5)),          # condition 6
                                True,          # condition 7
                                True,          # condition 8
                                int(self.stock.m_data['symbol']['analysis']['d']['trendStrength'] > TREND_STRENGTH_THS)  # condition 9
                                ]
            else:
                l_conditions = [int(self.stock.m_data['symbol']['analysis']['d']['intersectInd']),               # condition 0
                                int(self.stock.m_data['SPY']['analysis']['d']['rs'] >= RS_THS),               # condition 1
                                int(((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) and
                                    (self.stock.m_data['symbol']['analysis']['w']['moveType'] == 1) and
                                    (self.stock.m_data['symbol']['analysis']['m']['moveType'] == 1))),          # condition 2
                                int(((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1) and
                                    (self.stock.m_data['symbol']['analysis']['w']['moveType'] == -1) and
                                    (self.stock.m_data['symbol']['analysis']['m']['moveType'] == -1))),         # condition 3
                                int(self.stock.m_data['symbol']['analysis']['d']['proximity2TrendReversal']),    # condition 4
                                int(((self.stock.m_data['symbol']['analysis']['d']['lastWeeklyHigh'] and
                                    self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) or
                                    (self.stock.m_data['symbol']['analysis']['d']['lastWeeklyLow'] and
                                    self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1))),          # condition 5
                                int((self.stock.m_data['symbol']['analysis']['d']['riskRatio'] > 0.5)),          # condition 6
                                int(((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) and
                                    (self.stock.m_data['symbol']['analysis']['w']['moveType'] == 1))),          # condition 7
                                int(((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1) and
                                    (self.stock.m_data['symbol']['analysis']['w']['moveType'] == -1))),          # condition 8
                                int(self.stock.m_data['symbol']['analysis']['d']['trendStrength'] > TREND_STRENGTH_THS)  # condition 9
                                ]

            if DEBUG_CONDITIONS:
                self.debug_buffers[index].append("Condition 0: IntersectInd=%d\n" % self.stock.m_data['symbol']['analysis']['d']['intersectInd'])
                self.debug_buffers[index].append("Condition 1: RS=%f\n" % self.stock.m_data['SPY']['analysis']['d']['rs'])
                self.debug_buffers[index].append("Condition 2/3: d_trendType=%d, w_moveType=%d, m_moveType=%d\n" %
                                    (self.stock.m_data['symbol']['analysis']['d']['trendType'],
                                        self.stock.m_data['symbol']['analysis']['w']['moveType'],
                                        self.stock.m_data['symbol']['analysis']['m']['moveType']))
                self.debug_buffers[index].append("Condition 4: proximity=%d\n" % self.stock.m_data['symbol']['analysis']['d']['proximity2TrendReversal'])
                self.debug_buffers[index].append("Condition 5: lastWHigh=%f, lastWLow=%f, trendType=%d\n" %
                                    (self.stock.m_data['symbol']['analysis']['d']['lastWeeklyHigh'],
                                        self.stock.m_data['symbol']['analysis']['d']['lastWeeklyLow'],
                                        self.stock.m_data['symbol']['analysis']['d']['trendType']))
                self.debug_buffers[index].append("Condition 6: riskR=%f\n" % self.stock.m_data['symbol']['analysis']['d']['riskRatio'])
                self.debug_buffers[index].append("Condition 7/8: d_trendType=%d, w_moveType=%d\n" %
                                    (self.stock.m_data['symbol']['analysis']['d']['trendType'],
                                        self.stock.m_data['symbol']['analysis']['w']['moveType']))
                self.debug_buffers[index].append("Condition 9: trendStrength=%f, TREND_STRENGTH_THS=%f\n" % (self.stock.m_data['symbol']['analysis']['d']['trendStrength'], TREND_STRENGTH_THS))
                self.debug_buffers[index].append("SPY: d_trendType=%d, d_moveType=%d, w_moveType=%d, m_moveType=%d\n" %
                                    (self.stock.m_data['SPY']['analysis']['d']['trendType'],
                                        self.stock.m_data['SPY']['analysis']['d']['moveType'],
                                        self.stock.m_data['SPY']['analysis']['w']['moveType'],
                                        self.stock.m_data['SPY']['analysis']['m']['moveType']))

            logger.debug('Conditions: %d', l_conditions)
            self.debug_buffers[index].append("Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (l_conditions[0],
                                                                                l_conditions[1],
                                                                                l_conditions[2],
                                                                                l_conditions[3],
                                                                                l_conditions[4],
                                                                                l_conditions[5],
                                                                                l_conditions[6],
                                                                                l_conditions[7],
                                                                                l_conditions[8],
                                                                                l_conditions[9],
                                                                                sum(l_conditions),
                                                                                len(l_conditions)))
            if (l_conditions[7] or l_conditions[8]) and \
                l_conditions[6] and l_conditions[4]:
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 1][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                        l_conditions[0],
                                                                                        l_conditions[1],
                                                                                        l_conditions[2],
                                                                                        l_conditions[3],
                                                                                        l_conditions[4],
                                                                                        l_conditions[5],
                                                                                        l_conditions[6],
                                                                                        l_conditions[7],
                                                                                        l_conditions[8],
                                                                                        l_conditions[9],
                                                                                        sum(l_conditions),
                                                                                        len(l_conditions)))
            else:
                cond +=1
            if l_conditions[0] and l_conditions[1] and \
                (l_conditions[2] or l_conditions[3]):
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 2][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                            l_conditions[0],
                                                                                            l_conditions[1],
                                                                                            l_conditions[2],
                                                                                            l_conditions[3],
                                                                                            l_conditions[4],
                                                                                            l_conditions[5],
                                                                                            l_conditions[6],
                                                                                            l_conditions[7],
                                                                                            l_conditions[8],
                                                                                            l_conditions[9],
                                                                                            sum(l_conditions),
                                                                                            len(l_conditions)))
            else:
                cond += 1
            if l_conditions[0] and l_conditions[1] and \
                (l_conditions[2] or l_conditions[3]) and \
                l_conditions[4]:
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 3][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                            l_conditions[0],
                                                                                            l_conditions[1],
                                                                                            l_conditions[2],
                                                                                            l_conditions[3],
                                                                                            l_conditions[4],
                                                                                            l_conditions[5],
                                                                                            l_conditions[6],
                                                                                            l_conditions[7],
                                                                                            l_conditions[8],
                                                                                            l_conditions[9],
                                                                                            sum(l_conditions),
                                                                                            len(l_conditions)))
            else:
                cond += 1
            if l_conditions[0] and l_conditions[1] and \
                (l_conditions[2] or l_conditions[3]) and \
                l_conditions[4] and \
                l_conditions[5]:
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 4][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                            l_conditions[0],
                                                                                            l_conditions[1],
                                                                                            l_conditions[2],
                                                                                            l_conditions[3],
                                                                                            l_conditions[4],
                                                                                            l_conditions[5],
                                                                                            l_conditions[6],
                                                                                            l_conditions[7],
                                                                                            l_conditions[8],
                                                                                            l_conditions[9],
                                                                                            sum(l_conditions),
                                                                                            len(l_conditions)))
            else:
                cond += 1
            if l_conditions[0] and l_conditions[1] and \
                (l_conditions[2] or l_conditions[3]) and \
                l_conditions[4] and \
                l_conditions[5] and l_conditions[6]:
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 5][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                            l_conditions[0],
                                                                                            l_conditions[1],
                                                                                            l_conditions[2],
                                                                                            l_conditions[3],
                                                                                            l_conditions[4],
                                                                                            l_conditions[5],
                                                                                            l_conditions[6],
                                                                                            l_conditions[7],
                                                                                            l_conditions[8],
                                                                                            l_conditions[9],
                                                                                            sum(l_conditions),
                                                                                            len(l_conditions)))
            else:
                cond += 1
            if (l_conditions[7] or l_conditions[8]) and \
                l_conditions[6]:
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 6][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                            l_conditions[0],
                                                                                            l_conditions[1],
                                                                                            l_conditions[2],
                                                                                            l_conditions[3],
                                                                                            l_conditions[4],
                                                                                            l_conditions[5],
                                                                                            l_conditions[6],
                                                                                            l_conditions[7],
                                                                                            l_conditions[8],
                                                                                            l_conditions[9],
                                                                                            sum(l_conditions),
                                                                                            len(l_conditions)))
            else:
                cond += 1
            if (l_conditions[7] or l_conditions[8]) and \
                l_conditions[4]:
                # save_obj(self.stock, symbolName)
                self.stocks4Analysis.append(symbolName)
                sectorsPassingCond.append([symbolName, self.sectors_list[index], str(cond),
                                            l_conditions[0], l_conditions[1],
                                            l_conditions[2], l_conditions[3],
                                            l_conditions[4], l_conditions[5],
                                            l_conditions[6], l_conditions[7],
                                            l_conditions[8], l_conditions[9]])
                save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                self.debug_buffers[index].append("[COND 7][%s] Conditions: %d %d %d %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                            l_conditions[0],
                                                                                            l_conditions[1],
                                                                                            l_conditions[2],
                                                                                            l_conditions[3],
                                                                                            l_conditions[4],
                                                                                            l_conditions[5],
                                                                                            l_conditions[6],
                                                                                            l_conditions[7],
                                                                                            l_conditions[8],
                                                                                            l_conditions[9],
                                                                                            sum(l_conditions),
                                                                                            len(l_conditions)))
            else:
                cond += 1

            logger.debug('#### End handling [%s] ####', symbolName)
            self.debug_buffers[index].append("#### End handling [ %s ] ####\n" % symbolName)

    def analyze_sectors(self):
        global sectorsPassingCond
        global errorStocks

        # for holding in sectorHoldingsUrls:
        for index in self.sectors_to_analyze:
            self.analyze_sector(index)

        for buff in self.debug_buffers:
            for debug in buff:
                self.out_file.write(debug)

        logger.info('\n')
        self.out_file.write('\n')
        stocksRankingTable = AsciiTable(sectorsPassingCond)
        stocksRankingTable.inner_heading_row_border = True
        logger.info(stocksRankingTable.table)
        self.out_file.write(stocksRankingTable.table)

        errorStocksTable = AsciiTable(errorStocks)
        errorStocksTable.inner_heading_row_border = True
        logger.info('\n')
        logger.info('Stocks with ERRORs')
        logger.info(errorStocksTable.table)
        self.out_file.write('\n')
        self.out_file.write('Stocks with ERRORs\n')
        self.out_file.write(errorStocksTable.table)

    def restoreSymbol(self, i_symbol):
        self.stocks4Analysis = load_obj(i_symbol)

    def main(self):
        # while True:
            dayOfWeek = datetime.today().weekday()
            hour = datetime.today().hour
            minute = datetime.today().minute
            # if (dayOfWeek >= 1) and (dayOfWeek <= 5) and ((hour+3) == 14) and (minute == 00):
            if (1):
                filename = 'output_' + str(now.day) + '_' + str(now.month) + '_' + str(now.year) + '_' + str(now.hour) + '.txt'
                self.out_file = open(filename, "w")
                self.debug_buffers = [[], [], [], [], [], [], [], [], []]
                self.getSpyData()
                self.getSectorsData()
                self.checkIfUpdate()
                # narrow down the list of sectors for analysis
                self.rateSectors()
                self.analyze_sectors()
                self.out_file.close()
            else:
                logger.warning('DaylOfWeek: %s hour: %s minute: %s sleep 60s - waiting...', str(dayOfWeek), str(hour+3), str(minute))
                time.sleep(60)

# ----------------- Main program -------------------
# os.system("taskkill /im python.exe")
# os.system("taskkill /im python.exe")
# os.system("taskkill /im python.exe")
isBaseAnalysis = IntersectBasedAnalysisClass()
isBaseAnalysis.main()
# isBaseAnalysis.restoreSymbol('stocks4Analysis')
