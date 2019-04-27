import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import numpy as np
import plotly
from numpy import *
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import *
from data_structures import Data
from config import *
import matplotlib
import calendar

np.seterr(all='raise')

class Analyzer:
    generalData = dict(name='', endDate='', startDate='')
    m_data = Data
    m_features = pd.DataFrame()

    # initialize the basic parameters of the "Stock" class:
    #     1. set the symbol name to ''
    #     2. set the end date of the history data to now
    #     3. calculate the start date for the history date per data frequency type
    #     4. get history stock data for SPY
    def __init__(self, name='', end=datetime.now()):
        self.generalData['name'] = name
        # self.generalData['sector'] = sector
        self.generalData['endDate'] = datetime(end.year, end.month, end.day)
        self.generalData['startDate'] = self.generalData['endDate'] - DAILY_MONTH_DATA_BACKOFF

    # analyze the movement type of the stock, output one of the following:
    #     1. up
    #     2. down
    #     3. undefined
    def getMovementType(self, i_destDictKey, i_freq='d', i_dataWidth=0):
        if i_dataWidth == 0:
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low']
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High']
        else:
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low'][:i_dataWidth]
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High'][:i_dataWidth]

        lastIdx = len(l_dataLow) - 1
        moveType = 0  # undefined
        if (lastIdx > 0):
            if ((l_dataLow[lastIdx] < l_dataLow[lastIdx - 1]) and
               (l_dataHigh[lastIdx] < l_dataHigh[lastIdx - 1])):
                moveType = -1  # down
            elif ((l_dataLow[lastIdx] > l_dataLow[lastIdx - 1]) and
                  (l_dataHigh[lastIdx] > l_dataHigh[lastIdx - 1])):
                moveType = 1  # up

        self.m_data[i_destDictKey]['analysis'][i_freq]['moveType'] = moveType

    # iterate through the minimum and maximum point and analyze
    # which one can be marked as reversal
    #     1. iterates through minimum values
    #     2. iterate through maximum values
    def reversalPointsDetector(self, i_destDictKey, i_freq='d', i_debug=False, i_dataWidth=0, i_out=None):
        # localMins = self.m_data[i_destDictKey]['analysis'][i_freq]['localMins']
        # localMaxs = self.m_data[i_destDictKey]['analysis'][i_freq]['localMaxs']
        if (i_dataWidth == 0):
            l_dataDate = self.m_data[i_destDictKey]['data'][i_freq]['Date']
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low']
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High']
            l_dataClose = self.m_data[i_destDictKey]['data'][i_freq]['Close']
            l_dataOpen = self.m_data[i_destDictKey]['data'][i_freq]['Open']
        else:
            l_dataDate = self.m_data[i_destDictKey]['data'][i_freq]['Date'][:i_dataWidth]
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low'][:i_dataWidth]
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High'][:i_dataWidth]
            l_dataClose = self.m_data[i_destDictKey]['data'][i_freq]['Close'][:i_dataWidth]
            l_dataOpen = self.m_data[i_destDictKey]['data'][i_freq]['Open'][:i_dataWidth]

        dataLen = len(l_dataDate)

        k = 1

        while k < dataLen:
            # k = k + 1
            kPlus1 = k + 1
            kPlus2 = k + 2
            kMinus1 = k - 1
            searchMinima = False
            searchMaxima = False
            innerCandleLen = 0

            # find the inner candles (for kPlus1) in order to skip them during the analysis
            while (kPlus1 < dataLen) and (l_dataLow[kPlus1] >= l_dataLow[k]) and (l_dataHigh[kPlus1] <= l_dataHigh[k]):
                kPlus1 += 1
                kPlus2 += 1
                innerCandleLen += 1
            # terminate the function in case end of data reached
            if (kPlus1 >= dataLen):
                break
            # find the inner candles (for kPlus2) in order to skip them during the analysis
            while (kPlus2 < dataLen) and (l_dataLow[kPlus2] >= l_dataLow[kPlus1]) and (l_dataHigh[kPlus2] <= l_dataHigh[kPlus1]):
                kPlus2 += 1
            # terminate the function in case end of data reached
            if (kPlus2 >= dataLen):
                break

            # # TODO: needs testing
            # jump over inner candles for k-1
            kMinus2 = kMinus1 - 1
            while (kMinus2 > 0) and (l_dataLow[kMinus1] >= l_dataLow[kMinus2]) and (l_dataHigh[kMinus1] <= l_dataHigh[kMinus2]):
                kMinus1 -= 1
                kMinus2 -= 1

            # determine the search type (minima or maxima)
            if (l_dataLow[k] <= l_dataLow[kMinus1]) and (l_dataLow[k] <= l_dataLow[kPlus1]):
                searchMinima = True
            elif (l_dataHigh[k] >= l_dataHigh[kMinus1]) and (l_dataHigh[k] >= l_dataHigh[kPlus1]):
                searchMaxima = True

            imin = self.m_data[i_destDictKey]['analysis'][i_freq]['imin']
            imax = self.m_data[i_destDictKey]['analysis'][i_freq]['imax']

            # Analyse min reversals
            # #1: 3-4-5
            if searchMinima and \
               (l_dataHigh[kPlus1] > l_dataHigh[k]) and \
               (l_dataHigh[kPlus2] > l_dataHigh[kPlus1]) and \
               (l_dataClose[kPlus2] > l_dataLow[kPlus1]):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin'].append(newK)
                    if i_debug:
                        print("3-4-5", k, searchMinima, searchMaxima)
                        i_out.write("3-4-5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            if searchMinima and \
               (l_dataHigh[kPlus1] > l_dataHigh[k]):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin_p'].append(newK)
                    if i_debug:
                        print("3-4-5", k, searchMinima, searchMaxima)
                        i_out.write("3-4-5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #2: Key-Reversal
            if searchMinima and \
               (l_dataOpen[k] < l_dataClose[kMinus1]) and \
               (l_dataClose[k] > l_dataClose[kMinus1]) and \
               (l_dataClose[kPlus1] > l_dataHigh[k]):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin'].append(k)
                    if i_debug:
                        print("Key-Reversal", k, searchMinima, searchMaxima)
                        i_out.write("Key-Reversal -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            if searchMinima and \
               (l_dataOpen[k] < l_dataClose[kMinus1]) and \
               (l_dataClose[k] > l_dataClose[kMinus1]):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin_p'].append(k)
                    if i_debug:
                        print("Key-Reversal", k, searchMinima, searchMaxima)
                        i_out.write("Key-Reversal -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #3: Outside-Key-Reversal
            if searchMinima and \
               (l_dataOpen[k] < l_dataLow[kMinus1]) and \
               (l_dataClose[k] > l_dataHigh[kMinus1]):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin'].append(newK)
                    if i_debug:
                        print("Outside-Key-Reversal", k, searchMinima, searchMaxima)
                        i_out.write("Outside-Key-Reversal -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #4:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            isHammer = (l_dataOpen[k] > (l_dataHigh[k] - candleSize / 3)) and \
                       (l_dataClose[k] > (l_dataHigh[k] - candleSize / 3))

            if searchMinima and \
               (isHammer and (l_dataClose[kPlus1] > l_dataHigh[k])):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin'].append(newK)
                    if i_debug:
                        print("#4", k, searchMinima, searchMaxima)
                        i_out.write("#4 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            candleSize = l_dataHigh[k] - l_dataLow[k]
            isHammer = (l_dataOpen[k] > (l_dataHigh[k] - candleSize / 3)) and \
                       (l_dataClose[k] > (l_dataHigh[k] - candleSize / 3))

            if searchMinima and \
               (isHammer):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin_p'].append(newK)
                    if i_debug:
                        print("#4", k, searchMinima, searchMaxima)
                        i_out.write("#4 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #5:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            isStar = (l_dataOpen[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataOpen[k] < (l_dataHigh[k] - candleSize / 3)) and \
                     (l_dataClose[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataClose[k] < (l_dataHigh[k] - candleSize / 3))

            if searchMinima and \
               (isStar and (l_dataClose[kPlus1] > l_dataHigh[k])):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin'].append(newK)
                    if i_debug:
                        print("#5", k, searchMinima, searchMaxima)
                        i_out.write("#5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            # #5:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            isStar = (l_dataOpen[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataOpen[k] < (l_dataHigh[k] - candleSize / 3)) and \
                     (l_dataClose[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataClose[k] < (l_dataHigh[k] - candleSize / 3))

            if searchMinima and \
               (isStar):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin_p'].append(newK)
                    if i_debug:
                        print("#5", k, searchMinima, searchMaxima)
                        i_out.write("#5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #6:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            if candleSize == 0:
                candleSize = 0.001
            marubozuSize = l_dataClose[k] - l_dataOpen[k]
            marubozuWhite = (marubozuSize > 0) and  \
                            (marubozuSize / candleSize >= 0.9)

            if searchMinima and \
               (marubozuWhite and (l_dataClose[kPlus1] > l_dataHigh[k])):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin'].append(newK)
                    if i_debug:
                        print("#6", k, searchMinima, searchMaxima)
                        i_out.write("#6 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            # #6:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            if candleSize == 0:
                candleSize = 0.001
            marubozuSize = l_dataClose[k] - l_dataOpen[k]
            marubozuWhite = (marubozuSize > 0) and  \
                            (marubozuSize / candleSize >= 0.9)

            if searchMinima and \
               (marubozuWhite):
                newK = self.GetMinimaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imin_p'].append(newK)
                    if i_debug:
                        print("#6", k, searchMinima, searchMaxima)
                        i_out.write("#6 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # Analyse max reversals
            # #1: 3-4-5
            if searchMaxima and \
               (l_dataLow[kPlus1] < l_dataLow[k]) and \
               (l_dataLow[kPlus2] < l_dataLow[kPlus1]) and \
               (l_dataClose[kPlus2] < l_dataHigh[kPlus1]):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax'].append(newK)
                    if i_debug:
                        print("3-4-5", k, searchMinima, searchMaxima)
                        i_out.write("3-4-5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            if searchMaxima and \
               (l_dataLow[kPlus1] < l_dataLow[k]):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax_p'].append(newK)
                    if i_debug:
                        print("3-4-5", k, searchMinima, searchMaxima)
                        i_out.write("3-4-5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #2: Key-Reversal
            if searchMaxima and \
               (l_dataOpen[k] > l_dataClose[kMinus1]) and \
               (l_dataClose[k] < l_dataClose[kMinus1]) and \
               (l_dataClose[kPlus1] < l_dataLow[k]):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax'].append(newK)
                    if i_debug:
                        print("Key-Reversal", k, searchMinima, searchMaxima)
                        i_out.write("Key-Reversal -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            if searchMaxima and \
               (l_dataOpen[k] > l_dataClose[kMinus1]) and \
               (l_dataClose[k] < l_dataClose[kMinus1]):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax_p'].append(newK)
                    if i_debug:
                        print("Key-Reversal", k, searchMinima, searchMaxima)
                        i_out.write("Key-Reversal -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #3: Outside-Key-Reversal
            if searchMaxima and \
               (l_dataOpen[k] > l_dataHigh[kMinus1]) and \
               (l_dataClose[k] < l_dataLow[kMinus1]):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax'].append(newK)
                    if i_debug:
                        print("Outside-Key-Reversal", k, searchMinima, searchMaxima)
                        i_out.write("Outside-Key-Reversal -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #4:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            bodySize = abs(l_dataOpen[k] - l_dataClose[k])
            bottomShadow = min(l_dataOpen[k], l_dataClose[k]) - l_dataLow[k]
            isInvertedHammer = (bodySize < candleSize / 3) and (bottomShadow < bodySize / 4)

            if searchMaxima and \
               (isInvertedHammer and (l_dataClose[kPlus1] < l_dataLow[k])):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax'].append(newK)
                    if i_debug:
                        print("#4", k, searchMinima, searchMaxima)
                        i_out.write("#4 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            candleSize = l_dataHigh[k] - l_dataLow[k]
            bodySize = abs(l_dataOpen[k] - l_dataClose[k])
            bottomShadow = min(l_dataOpen[k], l_dataClose[k]) - l_dataLow[k]
            isInvertedHammer = (bodySize < candleSize / 3) and (bottomShadow < bodySize / 4)

            if searchMaxima and \
               (isInvertedHammer):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax_p'].append(newK)
                    if i_debug:
                        print("#4", k, searchMinima, searchMaxima)
                        i_out.write("#4 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #5:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            isStar = (l_dataOpen[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataOpen[k] < (l_dataHigh[k] - candleSize / 3)) and \
                     (l_dataClose[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataClose[k] < (l_dataHigh[k] - candleSize / 3))

            if searchMaxima and \
               (isStar and (l_dataClose[kPlus1] < l_dataLow[k])):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax'].append(newK)
                    if i_debug:
                        print("#5", k, searchMinima, searchMaxima)
                        i_out.write("#5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            candleSize = l_dataHigh[k] - l_dataLow[k]
            isStar = (l_dataOpen[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataOpen[k] < (l_dataHigh[k] - candleSize / 3)) and \
                     (l_dataClose[k] > (l_dataLow[k] + candleSize / 3)) and \
                     (l_dataClose[k] < (l_dataHigh[k] - candleSize / 3))

            if searchMaxima and \
               (isStar):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax_p'].append(newK)
                    if i_debug:
                        print("#5", k, searchMinima, searchMaxima)
                        i_out.write("#5 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            # #6:
            candleSize = l_dataHigh[k] - l_dataLow[k]
            marubozuSize = l_dataOpen[k] - l_dataClose[k]
            marubozuBlack = (marubozuSize > 0) and  \
                            (marubozuSize / candleSize >= 0.9)

            if searchMaxima and \
               (marubozuBlack and (l_dataClose[kPlus1] < l_dataLow[k])):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax'].append(newK)
                    if i_debug:
                        print("#6", k, searchMinima, searchMaxima)
                        i_out.write("#6 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue
            if searchMaxima and \
               (marubozuBlack):
                newK = self.GetMaximaIndexInRange(imin, imax, k, i_destDictKey, i_freq)
                if (newK != -1):
                    self.m_data[i_destDictKey]['analysis'][i_freq]['imax_p'].append(newK)
                    if i_debug:
                        print("#6", k, searchMinima, searchMaxima)
                        i_out.write("#6 -> k=%d, searchMinima=%d, searchMaxima=%d\n" % (k, searchMinima, searchMaxima))
                k = k + 1 + innerCandleLen
                continue

            k = k + 1 + innerCandleLen

        if i_debug:
            print("[reversalPointsDetector] - imin: ", self.m_data[i_destDictKey]['analysis'][i_freq]['imin'])
            print("[reversalPointsDetector] - imax: ", self.m_data[i_destDictKey]['analysis'][i_freq]['imax'])
            # i_out.write("[reversalPointsDetector] - imin:\n".join(self.m_data[i_destDictKey]['analysis'][i_freq]['imin']))
            # i_out.write("[reversalPointsDetector] - imax:\n".join(self.m_data[i_destDictKey]['analysis'][i_freq]['imax']))

    def rs(self, i_freq='d', i_dataWidth=0, i_ref='SPY', i_src='symbol'):
        if (i_dataWidth == 0):
            symbolDataClose = self.m_data[i_src]['data'][i_freq]['Close']
            sectorDataClose = self.m_data[i_ref]['data'][i_freq]['Close']
        else:
            symbolDataClose = self.m_data[i_src]['data'][i_freq]['Close'][:i_dataWidth]
            sectorDataClose = self.m_data[i_ref]['data'][i_freq]['Close'][:i_dataWidth]

        indexDiff = min(floor(len(sectorDataClose) / 4), floor(len(symbolDataClose) / 4))
        # indicesSectorData = [range(len(sectorDataClose) - int(indexDiff), len(sectorDataClose))]
        indicesSectorData = []
        for idx in range(len(sectorDataClose) - int(indexDiff), len(sectorDataClose)):
            indicesSectorData.append(idx)

        # indicesSymbolData = [range(len(symbolDataClose) - int(indexDiff), len(symbolDataClose))]
        indicesSymbolData = []
        for idx in range(len(symbolDataClose) - int(indexDiff), len(symbolDataClose)):
            indicesSymbolData.append(idx)

        if (indexDiff == 0):
            correlation = 0
        else:
            u1 = sum(sectorDataClose[indicesSectorData]) / indexDiff
            u2 = sum(symbolDataClose[indicesSymbolData]) / indexDiff

            cov = sum((sectorDataClose[indicesSectorData] - u1) * (symbolDataClose[indicesSymbolData] - u2))
            v1 = sum((sectorDataClose[indicesSectorData] - u1) ** 2)
            v2 = sum((symbolDataClose[indicesSymbolData] - u2) ** 2)
            s1 = sqrt(v1)
            s2 = sqrt(v2)

            if s1 * s2 < 0.000001:
                correlation = 0
            else:
                correlation = cov / (s1 * s2)
        self.m_data[i_src]['analysis'][i_freq]['rs'] = correlation

    # def ema(self,window):
    def ema(self, i_destDictKey, i_period, i_freq='d', i_type='simple', i_dataWidth=0, i_debug=False, i_out=None):
        if (i_dataWidth == 0):
            values = (self.m_data[i_destDictKey]['data'][i_freq]['Low'] +
                      self.m_data[i_destDictKey]['data'][i_freq]['High'] +
                      2. * self.m_data[i_destDictKey]['data'][i_freq]['Close']) / 4
        else:
            values = (self.m_data[i_destDictKey]['data'][i_freq]['Low'][:i_dataWidth] +
                      self.m_data[i_destDictKey]['data'][i_freq]['High'][:i_dataWidth] +
                      2. * self.m_data[i_destDictKey]['data'][i_freq]['Close'][:i_dataWidth]) / 4

        if (len(values) <= MIN_VECTOR_LEN):
            if i_debug:
                print('[EMA] padding arrays')
                i_out.write('[EMA] padding arrays\n')
            z = np.zeros(MIN_VECTOR_LEN)
            v = []
            v.extend(z)
            v.extend(values)
            values = v

        values = np.asarray(values)
        if type == 'simple':
            weights = np.ones(i_period)
        else:
            weights = np.exp(np.linspace(-1., 0., i_period))

        weights /= weights.sum()

        res = np.convolve(values, weights, mode='full')[:len(values)]

        # res = np.zeros(len(values))
        res[:i_period] = res[i_period]

        if (i_period == 34):
            self.m_data[i_destDictKey]['analysis'][i_freq]['ema34'] = res
        elif (i_period == 14):
            self.m_data[i_destDictKey]['analysis'][i_freq]['ema14'] = res
        elif (i_period == 200):
            self.m_data[i_destDictKey]['analysis'][i_freq]['ema200'] = res
        elif (i_period == 50):
            self.m_data[i_destDictKey]['analysis'][i_freq]['ema50'] = res

    # this function must be called after "reversalPointsDetector"
    def trend(self, i_destDictKey, i_freq='d', i_debug=False, i_dataWidth=0, i_out=None):
        if (i_dataWidth == 0):
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low']
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High']
        else:
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low'][:i_dataWidth]
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High'][:i_dataWidth]

        l_imin = self.m_data[i_destDictKey]['analysis'][i_freq]['imin']
        l_imax = self.m_data[i_destDictKey]['analysis'][i_freq]['imax']
        upTrend = False
        downTrend = False
        trendStrength = 0
        iminLastIdx = len(l_imin) - 1
        imaxLastIdx = len(l_imax) - 1

        try:
            if (iminLastIdx > 0) and (imaxLastIdx > 0):
                if (l_imin[iminLastIdx] > l_imax[imaxLastIdx]):  # last is MIN
                    upTrend = (l_dataLow[l_imin[iminLastIdx]] > l_dataLow[l_imin[iminLastIdx - 1]]) and \
                              (l_dataLow[l_imin[iminLastIdx - 1]] > l_dataLow[l_imin[iminLastIdx - 2]]) and \
                              (l_dataHigh[l_imax[imaxLastIdx]] > l_dataHigh[l_imax[imaxLastIdx - 1]]) and \
                              (l_dataHigh[l_imax[imaxLastIdx - 1]] > l_dataHigh[l_imax[imaxLastIdx - 2]])
                    trendStrength = (l_dataLow[l_imin[iminLastIdx]] - l_dataLow[l_imin[iminLastIdx - 1]]) / (l_dataHigh[l_imax[imaxLastIdx]] - l_dataLow[l_imin[iminLastIdx - 1]])
                elif (l_imin[iminLastIdx] < l_imax[imaxLastIdx]):  # last is MAX
                    downTrend = (l_dataLow[l_imin[iminLastIdx]] < l_dataLow[l_imin[iminLastIdx - 1]]) and \
                                (l_dataLow[l_imin[iminLastIdx - 1]] < l_dataLow[l_imin[iminLastIdx - 2]]) and \
                                (l_dataHigh[l_imax[imaxLastIdx]] < l_dataHigh[l_imax[imaxLastIdx - 1]]) and \
                                (l_dataHigh[l_imax[imaxLastIdx - 1]] < l_dataHigh[l_imax[imaxLastIdx - 2]])
                    trendStrength = (l_dataHigh[l_imax[imaxLastIdx]] - l_dataHigh[l_imax[imaxLastIdx - 1]]) / (l_dataLow[l_imin[iminLastIdx]] - l_dataHigh[l_imax[imaxLastIdx - 1]])
                elif i_debug:
                    print("[Trend] ERROR_1")
                    i_out.write('[Trend] ERROR_1\n')
            elif i_debug:
                print("[Trend] ERROR_2")
                i_out.write('[Trend] ERROR_2\n')
        except:
            upTrend = False
            downTrend = False


        # save the trend strength only in case of symbol data analysis for the daily stock timeframe
        if (upTrend or downTrend) and \
           (i_destDictKey == 'symbol') and (i_freq == 'd'):
            self.m_data[i_destDictKey]['analysis'][i_freq]['trendStrength'] = trendStrength

        if (upTrend) and (not downTrend):
            self.m_data[i_destDictKey]['analysis'][i_freq]['trendType'] = 2  # up-trend
        elif (not upTrend) and (downTrend):
            self.m_data[i_destDictKey]['analysis'][i_freq]['trendType'] = 1  # down-trend
        else:
            self.m_data[i_destDictKey]['analysis'][i_freq]['trendType'] = 0
        if i_debug:
            print("[trend] - Trend type: ", self.m_data[i_destDictKey]['analysis'][i_freq]['trendType'])
            i_out.write("[trend] - Trend type: %d\n" % (self.m_data[i_destDictKey]['analysis'][i_freq]['trendType']))

    def emaIntersect(self, i_destDictKey='symbol', i_freq='d', i_type='short', i_data_width=0):
        if i_type == 'long':
            f = self.m_data[i_destDictKey]['analysis'][i_freq]['ema50']
            g = self.m_data[i_destDictKey]['analysis'][i_freq]['ema200']
        elif i_type == 'short':
            f = self.m_data[i_destDictKey]['analysis'][i_freq]['ema14']
            g = self.m_data[i_destDictKey]['analysis'][i_freq]['ema34']

        if (i_data_width > 0):
            f = f[:i_data_width]
            g = g[:i_data_width]

        if len(f) == 0 or len(g) == 0:
            return "[ERROR]: emaIntersect vectors are empty"
        # res = np.zeros(len(f))
        res = np.pad(np.diff(np.array(f > g).astype(int)), (1, 0), 'constant', constant_values=(0,))

        self.m_data[i_destDictKey]['analysis'][i_freq]['intersectVec'] = res
        arrTail = res[-BACKOFF_LENGTH:-1]

        if (np.count_nonzero(arrTail)):
            self.m_data[i_destDictKey]['analysis'][i_freq]['intersectInd'] = True

    def GetMinimaIndexInRange(self, i_imin, i_imax, i_k, i_destDictKey, i_freq, i_dataWidth=0):
        if (i_dataWidth == 0):
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low']
        else:
            l_dataLow = self.m_data[i_destDictKey]['data'][i_freq]['Low'][:i_dataWidth]

        if (not i_imin and not i_imax):
            newK = i_k
        else:
            maxIndex = max(i_imin + i_imax)
            if (maxIndex in i_imin):
                newK = -1  # meaning that previous extrimum was minimum too
            else:
                try:
                    # newK = l_dataLow[maxIndex + 1:i_k + 1].argmin()
                    newK = l_dataLow[maxIndex + 1:i_k + 1].idxmin()
                    # newK = maxIndex + newK
                    # print("newK: ", newK)
                except:
                    newK = i_k
                # if not (type(newK) is np.int64):
                    # newK = newK[0]  # get the first one if several numbers are returned
                # newK = maxIndex + newK
            # else:
                # newK = i_k
        return newK

    def GetMaximaIndexInRange(self, i_imin, i_imax, i_k, i_destDictKey, i_freq, i_dataWidth=0):
        if (i_dataWidth == 0):
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High']
        else:
            l_dataHigh = self.m_data[i_destDictKey]['data'][i_freq]['High'][:i_dataWidth]

        if (not i_imin and not i_imax):
            newK = i_k
        else:
            maxIndex = max(i_imin + i_imax)

            if (maxIndex in i_imax):
                newK = -1  # meaning that previous extrimum was minimum too
            else:
                try:
                    # newK = l_dataHigh[maxIndex + 1:i_k + 1].argmax()
                    newK = l_dataHigh[maxIndex + 1:i_k + 1].idxmax()
                    # newK = maxIndex + newK
                except:
                    newK = i_k
                # if not (type(newK) is np.int64):
                #     newK = newK[0]  # get the first one if several numbers are returned
            # else:
            #     newK = i_k
        return newK

    # Find the last relevant weekly/monthly point in time according to the given data points in daily timeframe
    # TODO: need to fully support i_dataWidth
    def findLastTimeFrameMove(self, i_destDictKey, i_destFreq, i_dataWidth=0):
        if i_dataWidth > 0:
            if i_destFreq == 'm':
                l_dataLen = i_dataWidth / 31
                self.getMovementType(i_destDictKey, i_destFreq, i_dataWidth=l_dataLen)
            elif i_destFreq == 'w':
                l_dataLen = i_dataWidth / 7
                self.getMovementType(i_destDictKey, i_destFreq, i_dataWidth=l_dataLen)

    # Check whether the latest high/low value in the daily timeframe is higher/lower than the last week's high/low.
    # TODO: need to fully support i_dataWidth
    def findLastTimeFrameExceeding(self, i_destDictKey, i_destFreq, i_dataWidth=0, i_debug=False, i_out=None):
        l_data = self.m_data[i_destDictKey]['data']
        if i_destFreq == 'w':
            self.m_data[i_destDictKey]['analysis']['d']['lastWeeklyHigh'] = l_data['d']['High'].iloc[-1] >= l_data['w']['High'].iloc[-1]
            self.m_data[i_destDictKey]['analysis']['d']['lastWeeklyLow'] = l_data['d']['Low'].iloc[-1] <= l_data['w']['Low'].iloc[-1]
            if i_debug:
                print("[findLastTimeFrame][d] - StartIdx: ", startIdx, "EndIdx: ", endIdx)
                i_out.write("[findLastTimeFrame] - StartIdx: %d, EndIdx: %d\n" % (startIdx, EndIdx))
        elif i_destFreq == 'm':
            self.m_data[i_destDictKey]['analysis']['w']['lastWeeklyHigh'] = l_data['w']['High'].iloc[-1] >= l_data['m']['High'].iloc[-1]
            self.m_data[i_destDictKey]['analysis']['w']['lastWeeklyLow'] = l_data['w']['Low'].iloc[-1] <= l_data['m']['Low'].iloc[-1]
            if i_debug:
                print("[findLastTimeFrame][w] - StartIdx: ", startIdx, "EndIdx: ", endIdx)
                i_out.write("[findLastTimeFrame] - StartIdx: %d, EndIdx: %d\n" % (startIdx, EndIdx))

    # Construct the "features" dataframe based on information in "analysis" dataframe
    def updatToFeaturesDB(self, i_idx=0, i_debug=False, i_out=None):
        l_data = self.m_data['symbol']['analysis']['d']
        self.m_features['trend'][i_idx] = l_data['trendType']  # 2 = up, 1 = down
        self.m_features['weeklyMove'][i_idx] = self.m_data['symbol']['analysis']['w']['moveType']  # 2 = up, 1 = down
        self.m_features['monthlyMove'][i_idx] = self.m_data['symbol']['analysis']['m']['moveType']  # 2 = up, 1 = down
        self.m_features['emaIntersection'][i_idx] = sum(l_data['intersectVec'])
        if self.m_features['trend'][i_idx] == 2:
            self.m_features['currCloseBeyondLastExt'][i_idx] = l_data['lastWeeklyHigh']
        elif self.m_features['trend'][i_idx] == 1:
            self.m_features['currCloseBeyondLastExt'][i_idx] = l_data['lastWeeklyLow']
        self.m_features['proximity2TrendReversal'][i_idx] = l_data['proximity2TrendReversal']
        self.m_features['riskRatio'][i_idx] = l_data['riskRatio']

        if i_debug:
            print("[updatToFeaturesDB]: ", i_idx,
                  self.m_features.trend[i_idx],
                  self.m_features.weeklyMove[i_idx],
                  self.m_features.monthlyMove[i_idx],
                  self.m_features.emaIntersection[i_idx],
                  self.m_features.currCloseBeyondLastExt[i_idx],
                  self.m_features.proximity2TrendReversal[i_idx],
                  self.m_features.riskRatio[i_idx])
            i_out.write("[updatToFeaturesDB]: idx:%d, trend:%d, wMove:%d, mMove:%d, emaI:%d, currCloseBeyondLastExt:%d, proximity2TrendReversal:%d, riskRatio:%f\n"
                        % (i_idx,
                           self.m_features.trend[i_idx],
                           self.m_features.weeklyMove[i_idx],
                           self.m_features.monthlyMove[i_idx],
                           self.m_features.emaIntersection[i_idx],
                           self.m_features.currCloseBeyondLastExt[i_idx],
                           self.m_features.proximity2TrendReversal[i_idx],
                           self.m_features.riskRatio[i_idx]))

    def proximityToTrendReversal(self, i_destDictKey, i_freq='d', i_debug=0, i_dataWidth=0, i_out=None):
        if (i_dataWidth == 0):
            l_dataDate = self.m_data[i_destDictKey]['data'][i_freq]['Date']
        else:
            l_dataDate = self.m_data[i_destDictKey]['data'][i_freq]['Date'][:i_dataWidth]

        dataLen = len(l_dataDate)

        i_imin = self.m_data[i_destDictKey]['analysis'][i_freq]['imin']
        i_imax = self.m_data[i_destDictKey]['analysis'][i_freq]['imax']

        if len(i_imin) > 0 and len(i_imax) > 0:
            maxIndex = max(i_imin + i_imax)
            if self.m_data[i_destDictKey]['analysis'][i_freq]['trendType'] > 0:
                self.m_data[i_destDictKey]['analysis'][i_freq]['proximity2TrendReversal'] = (dataLen - 1 - maxIndex) < 4
            if (i_debug):
                print('[proximityToTrendReversal]: ', 'dataLen: ', dataLen, ' maxIndex: ', maxIndex)
                i_out.write("[proximityToTrendReversal]: dataLen:%d, maxIndex:%d\n" % (dataLen, maxIndex))
        else:
            if i_debug:
                print('[proximityToTrendReversal] ERROR')
                i_out.write("[proximityToTrendReversal] ERROR\n")
            self.m_data[i_destDictKey]['analysis'][i_freq]['proximity2TrendReversal'] = False

    def riskRatioCalc(self, i_destDictKey, i_freq='d', i_debug=0, i_dataWidth=0, i_out=None):
        analysisData = self.m_data[i_destDictKey]['analysis'][i_freq]
        data = self.m_data[i_destDictKey]['data'][i_freq]
        R = 0.0

        if (i_dataWidth == 0):
            if analysisData['trendType'] == 2:
                minIdx = analysisData['imin'][-1]
                R = 1 - data['Low'].iloc[minIdx] / data['Close'].iloc[-1]
                if i_debug:
                    print("R_data: ", data['Low'].iloc[minIdx], data['Close'].iloc[-1])
                    i_out.write("R_data: (1 - %f) : %f\n" % (data['Low'].iloc[minIdx], data['Close'].iloc[-1]))
            elif analysisData['trendType'] == 1:
                maxIdx = analysisData['imax'][-1]
                R = 1 - data['High'].iloc[maxIdx] / data['Close'].iloc[-1]
                if i_debug:
                    print("R_data: ", data['High'].iloc[maxIdx], data['Close'].iloc[-1])
                    i_out.write("R_data: (1 - %f) : %f\n" % (data['High'].iloc[maxIdx], data['Close'].iloc[-1]))
        self.m_data[i_destDictKey]['analysis'][i_freq]['riskRatio'] = abs(R)
        if i_debug:
            print("R: ", R)
            i_out.write("R: %f\n" % (R))
