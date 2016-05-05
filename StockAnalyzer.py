from Stock import *
from Utils import *
import time
import gc
import thread
import random
import os
import csv
import urllib2
from pandas import DataFrame

ANALYSIS_TYPE = 'short'  # 'long'
RS_THS = 0.7
now = datetime.now()
EXTENDED_DEBUG = True
DEBUG_CONDITIONS = True

class IntersectBasedAnalysisClass:

    stocksList = []
    numStocksInList = 0
    stock = StockClass()
    stocks4Analysis = []
    erroneousStocks = []
    out_file = 0
    sectors_list = ['IBB', 'IYR', 'IYW', 'ICF', 'IYH', 'IYT', 'ITB', 'REM', 'IYF', 'IYE', 'IYJ',
                    'IHE', 'IHI', 'IDU', 'IYM', 'IYG', 'IAT', 'IYZ', 'SOXX', 'IYK', 'IHF', 'IYC',
                    'IEO', 'IEZ', 'ITA', 'REZ', 'IAI', 'IAK', 'FTY']

    def getStocksList(self, i_update=False, i_listOrigin='NASDAQ', i_debug=False):
        if (i_update):
            refreshStocksList()
        if (i_listOrigin == 'NASDAQ'):
            listOfStocks = readFileContent('NASDAQ', '|', 0)
            listOfStocks.drop(listOfStocks.tail(1).index, inplace=True)
            self.numStocksInList = len(listOfStocks['Symbol'])
            self.stocksList = random.sample(listOfStocks['Symbol'], self.numStocksInList)
        else:
            listOfStocks = readFileContent('OTHERS', '|', 0)
            listOfStocks.drop(listOfStocks.tail(1).index, inplace=True)
            self.numStocksInList = len(listOfStocks['ACT Symbol'])
            self.stocksList = random.sample(listOfStocks['ACT Symbol'], self.numStocksInList)

        # self.stocksList = ['SSP']
        # self.numStocksInList = 1
        if i_debug:
            if EXTENDED_DEBUG:
                print i_listOrigin, self.numStocksInList
                print self.stocksList
                # out_file.write(self.numStocksInList)
                # out_file.write(i_listOrigin)
                # out_file.write(self.stocksList)

    def getSectorsData(self):
        for sector in self.sectors_list:
            if EXTENDED_DEBUG:
                print '#### Start handling ', sector, ' ####'
                self.out_file.write("#### Start handling %s ####\n" & (sector))
            self.stock.getData(i_symbol=sector, i_destDictKey=sector)
            self.stock.getMovementType(i_destDictKey=sector)
            self.stock.reversalPointsDetector(i_destDictKey=sector)
            if EXTENDED_DEBUG:
                print '#### End handling ', sector, ' ####'
                self.out_file.write("#### End handling %s ####\n" & (sector))

    def getSpyData(self):
        if EXTENDED_DEBUG:
            print "#### Start handling SPY ####"
            self.out_file.write("#### Start handling SPY ####\n")
        self.stock.getData(i_symbol='SPY', i_destDictKey='SPY')
        self.stock.getMovementType(i_destDictKey='SPY')
        self.stock.reversalPointsDetector(i_destDictKey='SPY')
        if EXTENDED_DEBUG:
            print "#### End handling SPY ####"
            self.out_file.write("#### End handling SPY ####\n")

    def checkIfUpdate(self):
        # day = datetime.today().day
        lastEntryDate = self.stock.getDataDate()
        print lastEntryDate
        self.out_file.write("Last entry's day: %d/%d\n" % (lastEntryDate.month, lastEntryDate.day))

    def analyze(self, i_analysisType):
        time.sleep(2)
        if EXTENDED_DEBUG:
            print "#### Start handling SPY ####"
            self.out_file.write("#### Start handling SPY ####\n")
        self.stock.getData(i_symbol='SPY', i_destDictKey='SPY')
        self.stock.getMovementType(i_destDictKey='SPY')
        self.stock.reversalPointsDetector(i_destDictKey='SPY')
        if EXTENDED_DEBUG:
            print "#### End handling SPY ####"
            self.out_file.write("#### End handling SPY ####\n")

        f = open('SectorHoldings.dat', 'r')
        sectorHoldingsUrls = f.readlines()

        for holding in sectorHoldingsUrls:
            print holding
            idx = 0
            response = urllib2.urlopen(holding)
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
            print self.stocksList

            for symbolName in self.stocksList:
                # stock = Stock(name=symbolName)
                self.stock.__init__(name=symbolName)

                # get data of required symbol
                idx = idx + 1
                if EXTENDED_DEBUG:
                    print '#### [', idx, '/', self.numStocksInList, ']: Start handling [', symbolName, '] ####'
                    self.out_file.write("#### [ %d / %d ]: Start handling [ %s ] ####\n" % (idx, self.numStocksInList, symbolName))
                else:
                    print '[', idx, '/', self.numStocksInList, ']'
                    self.out_file.write("[ %d / %d ]\n" % (idx, self.numStocksInList))
                try:
                    self.stock.getData(i_symbol=symbolName, i_destDictKey='symbol')
                except:
                    self.erroneousStocks.append(symbolName)
                    save_obj(self.erroneousStocks, 'erroneousStocks_' + ANALYSIS_TYPE)
                    if EXTENDED_DEBUG:
                        print '!!!! GetData ERROR !!!!'
                        self.out_file.write('!!!! GetData ERROR !!!!\n')
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

                l_conditions = [self.stock.m_data['symbol']['analysis']['d']['intersectInd'],               # condition 0
                                self.stock.m_data['symbol']['analysis']['d']['rs'] >= RS_THS,               # condition 1
                                ((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) and
                                 (self.stock.m_data['symbol']['analysis']['w']['moveType'] == 1) and
                                 (self.stock.m_data['symbol']['analysis']['m']['moveType'] == 1)),          # condition 2
                                ((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1) and
                                 (self.stock.m_data['symbol']['analysis']['w']['moveType'] == -1) and
                                 (self.stock.m_data['symbol']['analysis']['m']['moveType'] == -1)),         # condition 3
                                self.stock.m_data['symbol']['analysis']['d']['proximity2TrendReversal'],    # condition 4
                                ((self.stock.m_data['symbol']['analysis']['d']['lastWeeklyHigh'] and
                                 self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) or
                                 (self.stock.m_data['symbol']['analysis']['d']['lastWeeklyLow'] and
                                 self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1)),          # condition 5
                                (self.stock.m_data['symbol']['analysis']['d']['riskRatio'] > 0.5),          # condition 6
                                ((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 2) and
                                 (self.stock.m_data['symbol']['analysis']['w']['moveType'] == 1)),          # condition 7
                                ((self.stock.m_data['symbol']['analysis']['d']['trendType'] == 1) and
                                 (self.stock.m_data['symbol']['analysis']['w']['moveType'] == -1))          # condition 8
                                ]

                if DEBUG_CONDITIONS:
                    self.out_file.write("Condition 1: IntersectInd=%d\n" % self.stock.m_data['symbol']['analysis']['d']['intersectInd'])
                    self.out_file.write("Condition 2: RS=%f\n" % self.stock.m_data['symbol']['analysis']['d']['rs'])
                    self.out_file.write("Condition 3: d_trendType=%d, w_moveType=%d, m_moveType=%d\n" %
                                        (self.stock.m_data['symbol']['analysis']['d']['trendType'],
                                         self.stock.m_data['symbol']['analysis']['w']['moveType'],
                                         self.stock.m_data['symbol']['analysis']['m']['moveType']))
                    self.out_file.write("Condition 4: proximity=%d\n" % self.stock.m_data['symbol']['analysis']['d']['proximity2TrendReversal'])
                    self.out_file.write("Condition 5: lastWHigh=%f, lastWLow=%f, trendType=%d\n" %
                                        (self.stock.m_data['symbol']['analysis']['d']['lastWeeklyHigh'],
                                         self.stock.m_data['symbol']['analysis']['d']['lastWeeklyLow'],
                                         self.stock.m_data['symbol']['analysis']['d']['trendType']))
                    self.out_file.write("Condition 6: riskR=%f\n" % self.stock.m_data['symbol']['analysis']['d']['riskRatio'])

                if EXTENDED_DEBUG:
                    print 'Conditions: ', l_conditions
                    self.out_file.write("Conditions: %d %d %d %d %d %d %d-> [%d/%d]\n" % (l_conditions[0],
                                                                                          l_conditions[1],
                                                                                          l_conditions[2],
                                                                                          l_conditions[3],
                                                                                          l_conditions[4],
                                                                                          l_conditions[5],
                                                                                          l_conditions[6],
                                                                                          sum(l_conditions),
                                                                                          len(l_conditions)))
                if (l_conditions[7] or l_conditions[8]) and \
                   l_conditions[6] and l_conditions[4]:
                    # save_obj(self.stock, symbolName)
                    self.stocks4Analysis.append(symbolName)
                    save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                    self.out_file.write("*[%s] Conditions: %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                                 l_conditions[0],
                                                                                                 l_conditions[1],
                                                                                                 l_conditions[2],
                                                                                                 l_conditions[3],
                                                                                                 l_conditions[4],
                                                                                                 l_conditions[5],
                                                                                                 l_conditions[6],
                                                                                                 sum(l_conditions),
                                                                                                 len(l_conditions)))
                if l_conditions[0] and l_conditions[1] and \
                   (l_conditions[2] or l_conditions[3]):
                    # save_obj(self.stock, symbolName)
                    self.stocks4Analysis.append(symbolName)
                    save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                    self.out_file.write("**[%s] Conditions: %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                                  l_conditions[0],
                                                                                                  l_conditions[1],
                                                                                                  l_conditions[2],
                                                                                                  l_conditions[3],
                                                                                                  l_conditions[4],
                                                                                                  l_conditions[5],
                                                                                                  l_conditions[6],
                                                                                                  sum(l_conditions),
                                                                                                  len(l_conditions)))
                if l_conditions[0] and l_conditions[1] and \
                   (l_conditions[2] or l_conditions[3]) and \
                   l_conditions[4]:
                    # save_obj(self.stock, symbolName)
                    self.stocks4Analysis.append(symbolName)
                    save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                    self.out_file.write("***[%s] Conditions: %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                                   l_conditions[0],
                                                                                                   l_conditions[1],
                                                                                                   l_conditions[2],
                                                                                                   l_conditions[3],
                                                                                                   l_conditions[4],
                                                                                                   l_conditions[5],
                                                                                                   l_conditions[6],
                                                                                                   sum(l_conditions),
                                                                                                   len(l_conditions)))
                if l_conditions[0] and l_conditions[1] and \
                   (l_conditions[2] or l_conditions[3]) and \
                   l_conditions[4] and \
                   l_conditions[5]:
                    # save_obj(self.stock, symbolName)
                    self.stocks4Analysis.append(symbolName)
                    save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                    self.out_file.write("****[%s] Conditions: %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                                    l_conditions[0],
                                                                                                    l_conditions[1],
                                                                                                    l_conditions[2],
                                                                                                    l_conditions[3],
                                                                                                    l_conditions[4],
                                                                                                    l_conditions[5],
                                                                                                    l_conditions[6],
                                                                                                    sum(l_conditions),
                                                                                                    len(l_conditions)))
                if l_conditions[0] and l_conditions[1] and \
                   (l_conditions[2] or l_conditions[3]) and \
                   l_conditions[4] and \
                   l_conditions[5] and l_conditions[6]:
                    # save_obj(self.stock, symbolName)
                    self.stocks4Analysis.append(symbolName)
                    save_obj(self.stocks4Analysis, 'stocks4Analysis_'+ANALYSIS_TYPE)
                    self.out_file.write("*****[%s] Conditions: %d %d %d %d %d %d %d -> [%d/%d]\n" % (symbolName,
                                                                                                     l_conditions[0],
                                                                                                     l_conditions[1],
                                                                                                     l_conditions[2],
                                                                                                     l_conditions[3],
                                                                                                     l_conditions[4],
                                                                                                     l_conditions[5],
                                                                                                     l_conditions[6],
                                                                                                     sum(l_conditions),
                                                                                                     len(l_conditions)))

                if EXTENDED_DEBUG:
                    print '#### End handling [', symbolName, '] ####'
                    self.out_file.write("#### End handling [ %s ] ####\n" % symbolName)
            break

    def restoreSymbol(self, i_symbol):
        self.stocks4Analysis = load_obj(i_symbol)

    def main(self):
        # while True:
            dayOfWeek = datetime.today().weekday()
            hour = datetime.today().hour
            minute = datetime.today().minute
            # if (dayOfWeek >= 1) and (dayOfWeek <= 5) and ((hour+3) == 14) and (minute == 00):
            if (1):
                self.getSectorsData()
                self.out_file = open('output_'+str(now.day)+'_'+str(now.month)+'_'+str(now.year)+'_'+str(now.hour)+'.txt', "w")
                self.getSpyData()
                self.checkIfUpdate()
                self.getStocksList(i_listOrigin='NASDAQ', i_debug=True)
                self.analyze(i_analysisType=ANALYSIS_TYPE)
                # self.getStocksList(i_listOrigin='OTHERS', i_debug=True)
                # self.analyze(i_analysisType=ANALYSIS_TYPE)
                self.out_file.close()
            else:
                print 'DaylOfWeek: ', dayOfWeek, ' hour: ', hour+3, ' minute: ', minute, 'sleep 60s - waiting...'
                time.sleep(60)

# ----------------- Main program -------------------
#os.system("taskkill /im python.exe")
#os.system("taskkill /im python.exe")
#os.system("taskkill /im python.exe")
isBaseAnalysis = IntersectBasedAnalysisClass()
isBaseAnalysis.main()
# isBaseAnalysis.restoreSymbol('stocks4Analysis')
