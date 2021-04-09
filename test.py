from table import Table


""" テーブルオブジェクト作成 """
table = Table()

""" 2.1.1 外部データの読み込みによる作成 """
# tugaku = Table().readFile("school.tsv").showTable()  # 読み込みと表示
#
# tugaku = Table().readFile("school.tsv")  # 読み込み
# tugaku.changeColumnName("出席番号", "学籍番号").showTable()  # 列名を書き換えて表示

""" 2.1.2 プログラム中でデータを作る """
# tugaku = Table().createTable(["出席番号", "通学手段", "住所", "読書冊数", "自宅までの距離", "年度"])
# tugaku.addRow([1, "徒歩", "西宮市", 0.5, 0.28, 2015])
# tugaku.addRow([2, "バス", "西宮市", 1, 5.7, 2015])
# tugaku.addRow([3, "電車", "大阪市", 3, 14.7, 2016])
# tugaku.addRow([4, "電車", "京都市", 2, 37.1, 2016])
# tugaku.addRow([5, "徒歩", "西宮市", 0.5, 1.2, 2016]).showTable()

""" 2.3.1 選択：レコード（行）の抽出 """
# tugaku = Table().readFile("school.tsv")
# tugaku.extractRecord("住所=='神戸市'")  # 条件を指定して行を取り出す
# tugaku.showTable()
#
# tugaku = Table().readFile("school.tsv")
# result = tugaku.extractRecord("住所=='西宮市'")
# result.mean("自宅までの距離").showTable()

""" 2.3.2 射影：フィールド（列）の抽出 """
# tugaku = Table().readFile("school.tsv")
# result = tugaku.extractColumn(["住所", "自宅までの距離"])
# result.showTable()

""" 2.3.3 結合：デーブルオブジェクト同士の結合 """
# jusho = Table().createTable(["出席番号", "通学手段", "住所", "自宅までの距離"])
# jusho.addRow(["徒歩", "西宮市", 0.28])
# jusho.addRow(["バス", "西宮市", 5.7])
#
# dokusho = Table().createTable(["出席番号", "読書データ", "年度"])
# dokusho.addRow([1, 0.5, 2015])
# dokusho.addRow([2, 1, 2015])
#
# tugaku = jusho.concatTable(dokusho).showTable()

""" 2.3.4 レコードの追加 """
# tugaku = Table().readFile("school.tsv")
# tugaku.addRow([73, "徒歩", "西宮市", 0.5, 1.2, 2016])
# tugaku.addRow([74, "電車", "神戸市", 2, 10.2, 2016])
# tugaku.showTable()

""" 2.3.5 レコードの並べ替え：昇順・降順 """
# tugaku = Table().readFile("school.tsv")
# tugaku.sort("自宅までの距離", ascending=True).showTable()
# tugaku.sort("自宅までの距離", ascending=False).showTable()

""" 2.3.6 重複の削除 """
# tugaku = Table().readFile("school.tsv")
# result = tugaku.extractColumn("住所")
# result.drop_duplicate().showTable()

""" 2.4.1 合計値 """
# tugaku = Table().readFile("school.tsv")
# tugaku.sum("自宅までの距離").showTable()

""" 2.4.2 平均値 """
# tugaku = Table().readFile("school.tsv")
# tugaku.mean("自宅までの距離").showTable()

""" 2.4.3 中央値 """
# tugaku = Table().readFile("school.tsv")
# tugaku.median("自宅までの距離").showTable()

""" 2.4.4 最頻値 """
# tugaku = Table().readFile("school.tsv")
# tugaku.mode("自宅までの距離").showTable()

""" 2.4.5 最小値 """
# tugaku = Table().readFile("school.tsv")
# tugaku.min("自宅までの距離").showTable()

""" 2.4.6 最大値 """
# tugaku = Table().readFile("school.tsv")
# tugaku.max("自宅までの距離").showTable()

""" 2.4.7 四分位数 """
# tugaku = Table().readFile("school.tsv")
# tugaku.quantile("自宅までの距離", 0.25).showTable()
# tugaku.quantile("自宅までの距離", 0.75).showTable()

""" 2.4.8 分散 """
# tugaku = Table().readFile("school.tsv")
# tugaku.var("自宅までの距離").showTable()

""" 2.4.9 不偏分散 """
# tugaku = Table().readFile("school.tsv")
# tugaku.unbiasedVar("自宅までの距離").showTable()

""" 2.4.10 共分散 """
# tugaku = Table().readFile("school.tsv")
# tugaku.cov(["自宅までの距離", "読書冊数"]).showTable()

""" 2.4.11 不偏共分散 """
# tugaku = Table().readFile("school.tsv")
# tugaku.unbiasedCov(["自宅までの距離", "読書冊数"]).showTable()

""" 2.4.12 偏差 """
# tugaku = Table().readFile("school.tsv")
# tugaku.dev("自宅までの距離").showTable()

""" 2.4.13 標準偏差 """
# tugaku = Table().readFile("school.tsv")
# tugaku.std("自宅までの距離").showTable()

""" 2.4.14 不偏標準偏差 """
# tugaku = Table().readFile("school.tsv")
# tugaku.unbiasedStd("自宅までの距離").showTable()

""" 2.4.15 相関係数 """
# tugaku = Table().readFile("school.tsv")
# tugaku.corr(["自宅までの距離", "読書冊数"]).showTable(index=True)  # 行名を表示する

""" 2.4.16 度数 """
# tugaku = Table().readFile("school.tsv")
# tugaku.valueCount("住所").showTable()

""" 2.4.17 度数分布 """
# # 度数分布
# tugaku = Table().readFile("school.tsv")
# tugaku.freqDist("自宅までの距離").showTable()
#
# # 度数分布表
# tugaku = Table().readFile("school.tsv")
# tugaku.freqDistTable("自宅までの距離").showTable()

""" 2.4.18 クロス集計 """
# # クロス集計
# tugaku = Table().readFile("school.tsv")
# tugaku.crossCount(["通学手段", "住所"]).showTable(index=True)
#
# # クロス集計表
# tugaku = Table().readFile("school.tsv")
# tugaku.crossCountWithSum(["通学手段", "住所"]).showTable(index=True)

""" 2.5.1 棒グラフ """
# # 度数分布から
# tugaku = Table().readFile("school.tsv")
# tugaku.freqDist("通学手段").plotBar().showGraph()
#
# # クロス集計から
# tugaku = Table().readFile("school.tsv")
# tugaku.crossCount(["通学手段", "住所"]).plotBar(["西宮市", "京都市"]).showGraph()

""" 2.5.2 積み上げ棒グラフ """
# tugaku = Table().readFile("school.tsv")
# result = tugaku.crossCount(["通学手段", "年度"])
# result.plotBarWithStack().showGraph()
#
# tugaku = Table().readFile("school.tsv")
# result = tugaku.crossCount(["通学手段", "年度"])
# result.plotBarWithStack(2015).showGraph()

""" 2.5.3 ヒストグラム """
# tugaku = Table().readFile("school.tsv")
# tugaku.plotHistGram("自宅までの距離").showGraph()

""" 2.5.4 散布図 """
# tugaku = Table().readFile("school.tsv")
# tugaku.plotScatter(["自宅までの距離", "読書冊数"]).showGraph()

""" 2.5.5 円グラフ """
# tugaku = Table().readFile("school.tsv")
# result = tugaku.crossCount(["通学手段", "年度"])
# result.plotPie(2015).showGraph()

""" 2.5.6 帯グラフ """
# TODO: 棒間の線が描画できない問題
# tugaku = Table().readFile("school.tsv")
# result = tugaku.crossCount(["通学手段", "年度"])  # .showTable(index=True)
# result.plotBelt().showGraph()
# result.plotBelt([2015]).showGraph()

""" 2.5.7 箱ひげ図 """
# TODO: 使ってる関数の関係で、グラフタイトルが残ってしまう＆変更できない問題
# tugaku = Table().readFile("school.tsv")
# tugaku.plotBox(["通学手段", "自宅までの距離"]).showGraph()

""" 2.6.1 縦軸間隔 """
# TODO: 機能してない？（要調査）
# tugaku = Table().readFile("school.tsv")
# tugaku.plotScatter(["自宅までの距離", "読書冊数"]).setVerticalInterval(1).showGraph()

""" 2.6.2 横軸タイトル """
# tugaku = Table().readFile("school.tsv")
# tugaku.plotScatter(["自宅までの距離", "読書冊数"]).setXLabel("通学距離").showGraph()

""" 2.6.3 縦軸タイトル """
# tugaku = Table().readFile("school.tsv")
# tugaku.plotScatter(["自宅までの距離", "読書冊数"]).setYLabel("一月の読書冊数").showGraph()

""" 2.6.4 位置の指定 """
# TODO: 実行画面での位置を変更するのでパス

""" 2.6.5 移動する """
# TODO: 実行画面での位置を変更するのでパス

""" 2.6.5 描画 """
# tugaku = Table().readFile("school.tsv")
# tugaku.plotScatter(["自宅までの距離", "読書冊数"]).showGraph()
