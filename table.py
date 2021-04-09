import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro',
                               'Yu Gothic',
                               'Meirio',
                               'Takao',
                               'IPAexGothic',
                               'IPAPGothic',
                               'VL PGothic',
                               'Noto Sans CJK JP']

class Table:
    def __init__(self):
        self.table = None

    def readFile(self, filename, sep="\t", encode="sjis"):
        self.table = pd.read_csv(filename, sep=sep, encoding=encode)
        return self

    def createTable(self, columnNames):
        table = {}
        for cn in columnNames:
            table[cn] = []

        self.table = pd.DataFrame(table)
        return self

    def addRow(self, rowData):
        columns = self.table.columns.tolist()
        if len(columns) > len(rowData):
            rowData += [np.nan] * (len(columns) - len(rowData))

        self.table = self.table.append(pd.Series(rowData, index=columns), ignore_index=True)
        return self

    def showTable(self, numLine=None, index=False):
        if self.table is None:
            print("テーブルを作ってください")
            return

        if self.table.shape[0] == 0:
            print("データがありません")
            return

        if numLine is None:
            print(self.table.to_string(index=index).replace(",", "\t"))
        else:
            print(self.table.head(numLine).to_string(index=index).replace(",", "\t"))

        return self

    def changeColumnName(self, beforeName, afterName):
        self.table = self.table.rename(columns={beforeName: afterName})
        return self

    def extractRecord(self, sentence):
        self.table = self.table.query(sentence)
        return self

    def extractColumn(self, columns):
        self.table = self.table[columns]
        return self

    def concatTable(self, tables):
        if isinstance(tables, list):
            self.table = pd.concat([self.table] + [table.table for table in tables],
                                   axis=1)
        else:
            self.table = pd.concat([self.table, tables.table], axis=1)

        return self

    def sort(self, column, ascending=True):
        # True:昇順, False:降順
        self.table = self.table.sort_values(column, ascending=ascending)
        return self

    def drop_duplicate(self, keep="first"):
        self.table = self.table.drop_duplicates(keep=keep)
        return self

    # TODO: データ整理の部分は上書きして大丈夫？
    def sum(self, column):
        s = self.table[column].sum()
        new = Table().createTable([column + "_合計値"]).addRow([s])

        return new

    def mean(self, column):
        m = self.table[column].mean()
        new = Table().createTable([column + "_平均値"]).addRow([m])

        return new

    def median(self, column):
        m = self.table[column].median()
        new = Table().createTable([column + "_中央値"]).addRow([m])

        return new

    def mode(self, column):
        m = self.table[column].mode().max()
        new = Table().createTable([column + "_最頻値"]).addRow([m])

        return new

    def min(self, column):
        m = self.table[column].min()
        new = Table().createTable([column + "_最小値"]).addRow([m])

        return new

    def max(self, column):
        m = self.table[column].max()
        new = Table().createTable([column + "_最大値"]).addRow([m])

        return new

    def quantile(self, column, p):
        title = ""
        if p == 0.25:
            title = "_第1四分位数"
        elif p == 0.75:
            title = "_第3四分位数"

        q = self.table[column].quantile(p)
        new = Table().createTable([column + title]).addRow([q])

        return new

    def var(self, column):
        v = self.table[column].var(ddof=False)
        new = Table().createTable([column + "_分散"]).addRow([v])

        return new

    def unbiasedVar(self, column):
        v = self.table[column].var(ddof=True)
        new = Table().createTable([column + "_不偏分散"]).addRow([v])

        return new

    def cov(self, columns):
        c = self.table[columns].cov(ddof=0).iloc[0, -1]
        title = columns[0] + "&" + columns[1]
        new = Table().createTable([title + "_共分散"]).addRow([c])

        return new

    def unbiasedCov(self, columns):
        c = self.table[columns].cov(ddof=1).iloc[0, -1]
        title = columns[0] + "&" + columns[1]
        new = Table().createTable([title + "_不偏共分散"]).addRow([c])

        return new

    def std(self, column):
        s = self.table[column].std(ddof=0)
        new = Table().createTable([column + "_標準偏差"]).addRow([s])

        return new

    def dev(self, column):
        # 平均値を計算してスカラーにする
        mean = self.mean(column).table.to_numpy()[0, 0]

        # 偏差を計算
        dev = self.table[column].to_numpy() - mean

        # 1行ずつ追加
        new = Table().createTable([column + "_偏差"])
        for x in dev:
            new.addRow([x])

        return new

    def unbiasedStd(self, column):
        s = self.table[column].std(ddof=1)
        new = Table().createTable([column + "_不偏標準偏差"]).addRow([s])

        return new

    def corr(self, columns):
        c = self.table[columns].corr()

        new = Table()
        new.table = c

        return new

    def valueCount(self, column):
        c = self.table[column].value_counts()

        new = Table().createTable([column, "度数"])
        index = c.index
        for i, x in zip(index, c):
            new.addRow([i, x])

        return new

    def freqDist(self, column, bins=None, sort=False):
        table = self.table[column]

        if bins is None:
            bins = int(round(1 + np.log2(table.shape[0])))

        try:
            c = table.value_counts(bins=bins, sort=sort)

            new  = Table().createTable(["階級", "度数"])
            for i, x in zip(c.index, c):
                left, right = i.left, i.right
                new.addRow([str(left) + "~" + str(right), x])
        except:
            new = self.valueCount(column)

        return new

    def freqDistTable(self, column, class_width=None):
        data = np.asarray(self.table[column])
        if class_width is None:
            class_size = int(np.log2(data.size).round()) + 1
            class_width = round((data.max() - data.min()) / class_size)

        bins = np.arange(0, data.max() + class_width, class_width)
        hist = np.histogram(data, bins)[0]
        cumsum = hist.cumsum()

        table = pd.DataFrame({'階級': [f'{bins[i]}以上{bins[i + 1]}未満'
                                             for i in range(hist.size)] + ["計"],
                             '度数': np.hstack([hist, hist.sum()]),
                              '相対度数': np.hstack([hist / cumsum[-1], (hist / cumsum[-1]).sum()])})

        new = Table()
        new.table = table

        return new

    def crossCount(self, columns):
        table = pd.crosstab(self.table[columns[0]], self.table[columns[1]])

        new = Table()
        new.table = table

        return new

    def crossCountWithSum(self, columns):
        new = self.crossCount(columns)

        s = {}
        for c in new.table.columns.tolist():
            s[c] = new.table[c].sum()
        new.table = new.table.append(pd.Series(s, name="合計"))

        return new

    def showGraph(self):
        plt.tight_layout()
        # plt.show()
        self.graphPath = "tmp/graph_{}.png".format(np.random.randint(2**16, 2**32))

        # 保存先のフォルダを作る
        os.makedirs("./tmp", exist_ok=True)
        plt.savefig(self.graphPath)

        return self

    def plotBar(self, columns=None, stacked=False):
        plt.cla()
        new = Table()
        new.table = deepcopy(self.table)

        if "度数" in new.table.columns.tolist():
            c = new.table.columns.tolist()
            s = {}
            for i, x in zip(new.table[c[0]], new.table[c[1]]):
                s[i] = x
            s = pd.Series(s)
            s.plot.bar(stacked=stacked)
        else:
            if columns is not None:
                isListColumn = False
                new.table = new.table.T
                if isinstance(columns, list):
                    c = columns[0]
                    isListColumn = True
                else:
                    c = columns

                if c in new.table.columns.tolist():
                    new.table = new.table[columns]
                elif c in new.table.index.tolist():
                    new.table = new.table.T
                    new.table = new.table[columns]

                if not isListColumn:
                    new.table = pd.DataFrame(new.table).T

            new.table.plot.bar(stacked=stacked)
        # plt.tight_layout()
        # plt.show()

        return new

    def plotBarWithStack(self, columns=None):
        new = self.plotBar(columns, stacked=True)
        return new

    def plotHistGram(self, column, barWidth=0.97):
        plt.cla()
        table = self.freqDist(column).table
        table.plot.bar(width=barWidth)
        plt.xticks(list(range(len(table))), table[table.columns.tolist()[0]].tolist())
        plt.xlabel("度数")
        plt.ylabel("値")
        # plt.tight_layout()
        plt.grid(axis="y")
        plt.legend().remove()

        # plt.show()

        return self

    def plotScatter(self, columns, showGrid=True):
        plt.cla()
        table = self.table[columns]

        plt.scatter(table[table.columns.tolist()[0]],
                    table[table.columns.tolist()[1]])

        plt.xlabel(table.columns.tolist()[0])
        plt.ylabel(table.columns.tolist()[1])

        if showGrid:
            plt.grid()

        # plt.tight_layout()
        # plt.show()

        return self

    def plotPie(self, column):
        plt.cla()
        table = self.table[column]

        percentage = []
        s = table.values.sum()
        for x in table.values:
            percentage.append("{:.1f}%".format(x / s * 100))

        plt.pie(table, startangle=90, labels=percentage)
        plt.legend(table.index.tolist(), bbox_to_anchor=(0.9, 0.7))
        # plt.tight_layout()
        # plt.show()

        return self

    def plotBelt(self, columns=None):
        plt.cla()
        if columns is None:
            columns = self.table.columns.tolist()
            table = self.table

            for c in columns:
                table[c] = table[c] / table[c].sum()
            table = table.T
            table.plot.barh(stacked=True)
        else:
            table = self.table[columns]

            for c in columns:
                table[c] = table[c] / table[c].sum()

            table.T.plot.barh(stacked=True)

        plt.grid(axis="x")
        plt.tight_layout()

        return self

    def plotBox(self, columns):
        plt.cla()
        table = self.table[columns]
        print(columns)

        table.boxplot(column=[columns[1]], by=columns[0], showmeans=True, grid=False)
        plt.title("")
        plt.xlabel(columns[0])
        plt.ylabel(columns[1])
        plt.grid(axis="y")

        return self

    def setVerticalInterval(self, val):
        return self

    def setXLabel(self, label):
        plt.xlabel(label)

        return self

    def setYLabel(self, label):
        plt.ylabel(label)

        return self

