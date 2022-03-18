"""
functions for visualizing data
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression


def plot_weight_rep(agg_df, routine):

    # subset data
    df = agg_df[agg_df.Type==routine]

    # convert the datetime index to ordinal values, which can be used to plot a regression line
    df.index = df.index.map(pd.Timestamp.toordinal)

    # convert the regression line start date to ordinal
    x1 = df.index[0]

    # data slice for the regression line
    data=df.loc[x1:].reset_index()

    # plot the weight data
    ax1 = df.plot(y='Weight', style='.', c='r', figsize=(15, 6), grid=True, legend=False,
                  title=f'{routine} performance over time')

    ax1 = df.plot(y='Rep', style='.', c='b', figsize=(15, 6), grid=True, legend=False, ax=ax1)

    # add a regression line
    ax1 = sns.regplot(data=data, x='Date', y='Weight', ax=ax1, color='r',
                      scatter_kws={'s': 7}, scatter=False, label='Weight Trend')
    ax1 = sns.regplot(data=data, x='Date', y='Rep', ax=ax1, color='b',
                      scatter_kws={'s': 7}, scatter=False, label='Rep Trend')

    ax1.set_xlim(df.index[0], df.index[-1])

    # convert the axis back to datetime
    xticks = ax1.get_xticks()
    labels = [pd.Timestamp.fromordinal(int(label)).date() for label in xticks]
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(labels)

    ax1.legend()

    plt.show()

    return ax1
