import pandas as pd
import numpy as np


def _timeFramesDict():
    return dict(d=pd.DataFrame(), w=pd.DataFrame(), m=pd.DataFrame())


def _dailyAnalysisParams():
    return dict(localMins=np.empty(shape=0), localMaxs=np.empty(shape=0),
                moveType=0, # 2 = up, 1 = down
                trendType=0,  # 2 = Up, 1 = down, 0 = init
                trendStrength=0, imin=[], imax=[], imin_p=[], imax_p=[],
                ema34=[], ema14=[], ema200=[], ema50=[], rs=0,
                intersectVec=[], intersectInd=False,
                lastWeeklyHigh=0.0, lastWeeklyLow=0.0,
                proximity2TrendReversal=False, riskRatio=0.0)


def _weeklyAnalysisParams():
    return dict(localMins=np.empty(shape=0), localMaxs=np.empty(shape=0),
                moveType=0, imin=[], imax=[], imin_p=[], imax_p=[],
                ema34=[], ema14=[])


def _monthlyAnalysisParams():
    return dict(localMins=np.empty(shape=0), localMaxs=np.empty(shape=0),
                moveType=0, imin=[], imax=[], imin_p=[], imax_p=[])


def _analysisDict():
    return dict(d=_dailyAnalysisParams(), w=_weeklyAnalysisParams(), m=_monthlyAnalysisParams())


def _infoDict():
    return dict(data=_timeFramesDict(), analysis=_analysisDict())


Data = {'symbol': _infoDict(),
        'SPY': _infoDict(),
        'IBB': _infoDict(),
        'IYR': _infoDict(),
        'IYW': _infoDict(),
        'ICF': _infoDict(),
        'IYH': _infoDict(),
        'IYT': _infoDict(),
        'ITB': _infoDict(),
        'REM': _infoDict(),
        'IYF': _infoDict(),
        'IYE': _infoDict(),
        'IYJ': _infoDict(),
        'IHE': _infoDict(),
        'IHI': _infoDict(),
        'IDU': _infoDict(),
        'IYM': _infoDict(),
        'IYG': _infoDict(),
        'IAT': _infoDict(),
        'IYZ': _infoDict(),
        'SOXX': _infoDict(),
        'IYK': _infoDict(),
        'IHF': _infoDict(),
        'IYC': _infoDict(),
        'IEO': _infoDict(),
        'IEZ': _infoDict(),
        'ITA': _infoDict(),
        'REZ': _infoDict(),
        'IAI': _infoDict(),
        'IAK': _infoDict(),
        'FTY': _infoDict(),

        'XLB': _infoDict(),
        'XLE': _infoDict(),
        'XLP': _infoDict(),
        'XLF': _infoDict(),
        'XLV': _infoDict(),
        'XLI': _infoDict(),
        'XLY': _infoDict(),
        'XLK': _infoDict(),
        'XLU': _infoDict()}
