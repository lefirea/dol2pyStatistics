import sys, os
import urllib.parse as uparse
import numpy as np
import pandas as pd
import base64
import unicodedata
import re

from copy import deepcopy
from table import Table

from flask import Flask, request, abort
app = Flask(__name__)


def getEastAsianWidthCount(text):
	count = 0
	for c in text:
		if unicodedata.east_asian_width(c) in "FWA":
			count += 2
		else:
			count += 1
	return count

def splitTableString(tableString, sep="\\t"):
	table = tableString.split(sep)
	
	numColumn = int(table[-1])
	fields = table[:numColumn]
	data = table[numColumn:-1]
	
	if data != []:
		while(data[-1] == ""):
			data = data[:-1]
	
	return fields, data

""" 各データの型推定 """
def typeCheck(fields, data):
	length = len(fields)
	
	types = [""] * length
	for i in range(len(data)):
		if re.match("^[0-9]+$", data[i]):  # 整数値
			if types[i % length] == "":
				types[i % length] = "int"
		elif re.match("^[0-9]+\.[0-9]+", data[i]):  # 実数値
			if types[i % length] in ["", "int"]:
				types[i % length] = "float"
		elif data[i] == "":
			if types[i % length] in ["", "int"]:
				types[i % length] = "int"
		else:
			types[i % length] = "str"
	
	return types

""" ドリトルから送られてきた1次元配列（を文字列にしたもの）をDataFrameに変換する """
def toDf(fields, data):
	length = len(fields)
	dic = {}
	for f in fields:
		dic[f] = []

	# 各データの型推定
	types = typeCheck(fields, data)
	for i in range(len(data)):
		# try:
		if types[i % length] == "int":
			dic[fields[i % length]].append(int(data[i]))
		elif types[i % length] == "float":
			dic[fields[i % length]].append(float(data[i]))
		elif types[i % length] == "str":
			dic[fields[i % length]].append(str(data[i]))
		else:
			dic[fields[i % length]].append(str(data[i]))
	
	df = pd.DataFrame(dic)
	return df

def toTable(fields, data):
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	
	return table

""" DataFrameを1次元配列（を文字列にしたもの）に変換する """
def toDolStat(table, use_index=False):
	df = table.table
	ret = {}
	if not use_index:
		ret["columns"] = df.columns.tolist()
		ret["body"] = []
		for y in range(0, df.shape[0]):
			for x in range(df.shape[1]):
				d = df.iat[y, x]
				if isinstance(d, int):
					d = int(d)
				elif isinstance(d, float):
					d = float(d)
				else:
					d = str(d)
				ret["body"].append(d)

		return ret
	else:
		ret["columns"] = [""] + df.columns.tolist()
		ret["body"] = []
		indexes = df.index.tolist()
		for y in range(0, df.shape[0]):
			ret["body"].append(indexes[y])
			for x in range(df.shape[1]):
				d = df.iat[y, x]
				if isinstance(d, int):
					d = int(d)
				elif isinstance(d, float):
					d = float(d)
				else:
					d = str(d)
				ret["body"].append(d)

		return ret

def img2SendData(imgPath):
	with open(imgPath, "rb") as f:
		data = base64.b64encode(f.read()).decode("utf-8")
	
	return data

def splitCommand(command):
	commands = []
	for c in command:
		s = c.split("(")
		commands.append([s[0], s[1][:-1]])
	return commands

@app.route("/")
def hello():
	name = "Good morning"
	return name

@app.route("/stat/createTable", methods=["GET"])
def createTable():
	print()
	fileContent = request.args.get("file_content")
	
	deli = request.args.get("deli")
	if "t" in deli:
		deli = "\\t"

	fileContent = fileContent.split("\\n")
	fileContent = [x.split(deli) for x in fileContent]

	ret = {}
	ret["columns"] = fileContent[0]
	ret["body"] = []
	for fc in fileContent[1:]:
		for c in fc:
			if c != "":
				ret["body"].append(c)
	
	return ret

@app.route("/stat/changeColumnName", methods=["GET"])
def changeColumnName():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	before = request.args.get("before")
	after = request.args.get("after")
	
	new = toTable(fields, data)
	if before in fields:
		new = new.changeColumnName(before, after)
	else:  # 指定された列名が存在しなかったらそのまま返す
		pass
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/extractRecord", methods=["GET"])
def extractRecord():
	print()
	param = request.args.get("table")
	param = param.split("\\t")

	column = request.args.get("column")
	keyword = request.args.get("keyword")
	print(keyword)

	numColumn = int(param[-1])
	fields = param[:numColumn]
	data = param[numColumn:-1]

	while(data[-1] == ""):
		data = data[:-1]

	df = toDf(fields, data)

	table = Table()
	table.table = df

	new = table.extractRecord(column + "==" + "\'" + keyword + "\'")

	ret = toDolStat(new)

	return ret

@app.route("/stat/extractColumn", methods=["GEt"])
def extractColumn():
	print()
	param = request.args.get("table")
	param = param.split("\\t")

	column = request.args.get("column")
	column = column.split("\\t")
	column = [c.replace("\\", "") for c in column]

	numColumn = int(param[-1])
	fields = param[:numColumn]
	data = param[numColumn:-1]

	while(data[-1] == ""):
		data = data[:-1]

	df = toDf(fields, data)

	table = Table()
	table.table = df
	new = table.extractColumn(column)

	ret = toDolStat(new)

	return ret

@app.route("/stat/concatTable", methods=["GET"])
def concatTable():
	print()
	param1 = request.args.get("table1")
	fields1, data1 = splitTableString(param1)
	
	param2 = request.args.get("table2")
	fields2, data2 = splitTableString(param2)
	
	table1 = toTable(fields1, data1)
	table2 = toTable(fields2, data2)
	
	new = table1.concatTable(table2)
	ret = toDolStat(new)
	
	return ret

@app.route("/stat/addRow", methods=["GET"])
def addRow():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	newRow = request.args.get("newrow")
	newRow = newRow.split("\\t")
	
	while newRow[-1] == "":
		newRow = newRow[:-1]
	
	for i in range(len(newRow)):
		newRow[i] = newRow[i].replace('\\', "")
		newRow[i] = newRow[i].replace(' "', "")
	
	data = data + newRow
	new = toTable(fields, data)
	
	ret = toDolStat(new)
	
	return ret

@app.route("/stat/sort", methods=["GET"])
def sort():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	ascending = request.args.get("ascending")
	
	if ascending == "小さい順":
		ascenging = True
	else:
		ascending = False
	
	new = toTable(fields, data)
	new = new.sort(column, ascending=ascending)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/dropDuplicate")
def dropDuplicate():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	new = toTable(fields, data)
	new = new.dropDuplicate()
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/sum", methods=["GET"])
def sumColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.sum(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/mean", methods=["GET"])
def meanColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.mean(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/median", methods=["GET"])
def medianColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.median(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/mode", methods=["GET"])
def modeColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.mode(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/min", methods=["GET"])
def minColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.min(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/max", methods=["GET"])
def maxColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.max(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/quantile", methods=["GET"])
def quantileColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	n = int(request.args.get("n"))
	
	new = toTable(fields, data)
	new = new.quantile(column, n / 4)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/var", methods=["GET"])
def varColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.var(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/unbiasedVar", methods=["GET"])
def unbiasedVarColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.unbiasedVar(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/cov", methods=["GET"])
def covColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns").split("\\t")
	while columns[-1] == "":
		columns = columns[:-1]
	columns = [c.replace("\\", "") for c in columns]
	
	new = toTable(fields, data)
	new = new.cov(columns)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/unbiasedCov", methods=["GET"])
def unbiasedCovColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns").split("\\t")
	while columns[-1] == "":
		columns = columns[:-1]
	columns = [c.replace("\\", "") for c in columns]
	
	new = toTable(fields, data)
	new = new.unbiasedCov(columns)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/dev", methods=["GET"])
def devColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.dev(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/std", methods=["GET"])
def stdColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.std(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/unbiasedStd", methods=["GET"])
def unbiasedStdColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	new = toTable(fields, data)
	new = new.unbiasedStd(column)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/corr", methods=["GET"])
def corrColumn():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns").split("\\t")
	while columns[-1] == "":
		columns = columns[:-1]
	columns = [c.replace("\\", "") for c in columns]
	
	new = toTable(fields, data)
	new = new.corr(columns)
	
	ret = toDolStat(new)
	return ret

@app.route("/stat/valueCount", methods=["GET"])
def valueCount():
	print()
	
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")

	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	
	new = table.valueCount(column)
	
	ret = toDolStat(new)

	return ret

@app.route("/stat/freqDist", methods=["GET"])
def freqDist():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	n = request.args.get("n")

	df = toDf(fields, data)

	table = Table()
	table.table = df
	
	if "未定義" in str(n):
		new = table.freqDist(column)
	else:
		new = table.freqDist(column, bins=int(n))

	ret = toDolStat(new)

	return ret

@app.route("/stat/freqDistTable", methods=["GET"])
def freqDistTable():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")

	df = toDf(fields, data)

	table = Table()
	table.table = df
	new = table.freqDistTable(column)

	ret = toDolStat(new)

	return ret

@app.route("/stat/crossCount", methods=["GET"])
def crossCount():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns").split("\\t")
	columns = [c.replace("\\", "") for c in columns]

	df = toDf(fields, data)

	table = Table()
	table.table = df
	new = table.crossCount(columns)

	ret = toDolStat(new, use_index=True)

	return ret

@app.route("/stat/crossCountWithSum", methods=["GET"])
def crossCountWithSum():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns").split("\\t")
	columns = [c.replace("\\", "") for c in columns]

	df = toDf(fields, data)

	table = Table()
	table.table = df
	new = table.crossCountWithSum(columns)

	ret = toDolStat(new, use_index=True)

	return ret

@app.route("/stat/plotBar", methods=["GET"])
def plotBar():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns")
	if columns != "":
		columns = columns.split("\\t")
		columns = [c.replace("\\", "") for c in columns]
	else:
		if fields[0] == "":
			columns = fields[1:]
		else:
		 	columns = fields
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	step = request.args.get("step")
	if step is not None:
		step = float(step)
	if step == 0:
		step = None
	
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	new = table.plotBar(columns, ylabel=ylabel, xlabel=xlabel, step=step).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/plotBarWithStack", methods=["GET"])
def plotBarWithStack():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	columns = request.args.get("columns")
	if columns != "":
		columns = columns.split("\\t")
		columns = [c.replace("\\", "") for c in columns]
		if len(columns) == 1:
			columns = columns[0]
	else:
		if fields[0] == "":
			columns = fields[1:]
		else:
		 	columns = None
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	step = request.args.get("step")
	if step is not None:
		step = float(step)
	if step == 0:
		step = None
	
	df = toDf(fields, data)
	
	index = list(df[""])
	df = df[df.columns.tolist()[1:]]
	df.index = index
	
	table = Table()
	table.table = df
	new = table.plotBarWithStack(columns, ylabel=ylabel, xlabel=xlabel, step=step).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/plotHistGram", methods=["GET"])
def plotHistGram():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	step = request.args.get("step")
	if step is not None:
		step = float(step)
	if step == 0:
		step = None
	
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	new = table.plotHistGram(column, ylabel=ylabel, xlabel=xlabel, step=step).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/plotScatter", methods=["GET"])
def plotScatter():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column1 = request.args.get("column1")
	column2 = request.args.get("column2")
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	step = request.args.get("step")
	if step is not None:
		step = float(step)
	if step == 0:
		step = None
	
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	new = table.plotScatter([column1, column2], ylabel=ylabel, xlabel=xlabel, step=step).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/plotPie", methods=["GET"])
def plotPie():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	legend = table.table[""].tolist()
	new = table.plotPie(column, legend, ylabel=ylabel, xlabel=xlabel).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/plotBelt", methods=["GET"])
def plotBelt():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column = request.args.get("column")
	if column == "":
		if fields[0] == "":
			column = fields[1:]
		else:
			column = None
	else:
		column = [column]
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	step = request.args.get("step")
	if step is not None:
		step = float(step)
	if step == 0:
		step = None
	
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	legend = table.table[""].tolist()
	new = table.plotBelt(column, legend, ylabel=ylabel, xlabel=xlabel, step=step).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/plotBox", methods=["GET"])
def plotBox():
	print()
	param = request.args.get("table")
	fields, data = splitTableString(param)
	
	column1 = request.args.get("column1")
	column2 = request.args.get("column2")
	
	ylabel = request.args.get("ylabel")
	xlabel = request.args.get("xlabel")
	
	step = request.args.get("step")
	if step is not None:
		step = float(step)
	if step == 0:
		step = None
	
	df = toDf(fields, data)
	
	table = Table()
	table.table = df
	new = table.plotBox([column1, column2], ylabel=ylabel, xlabel=xlabel, step=step).showGraph()
	graphPath = new.graphPath
	
	Base64Img = img2SendData(graphPath)
	
	ret = toDolStat(new, use_index=True)
	ret["graph"] = Base64Img
	
	os.remove(graphPath)

	return ret

@app.route("/stat/show", methods=["GET"])
def show():
	print()
	param = request.args.get("table")
	param = param.split("\\t")

	numColumn = int(param[-1])
	param = param[:-1]
	maxLength = [getEastAsianWidthCount(str(param[i])) for i in range(numColumn)]
	length = deepcopy(maxLength)

	while param[-1] == "":
		param = param[:-1]
	
	for i in range(numColumn, len(param)):
		length.append(getEastAsianWidthCount(str(param[i])))
		maxLength[(i-numColumn) % numColumn] = max(maxLength[(i - numColumn) % numColumn], length[-1])
	
	ret = "|" + " " * (maxLength[0] - length[0]) + param[0]
	for i in range(1, numColumn):
		ret += "|" + " " * (maxLength[i] - length[i]) + param[i]
	n = sum(maxLength) + numColumn - 1
	ret += "\n"
	ret += "-" * n
	ret += "\n"

	for i in range(numColumn, len(param)):
		if (i - numColumn) % numColumn == 0:
			ret += " " * (maxLength[(i - numColumn) % numColumn] - length[i]) + param[i]
		else:
			ret += "|" + " " * (maxLength[(i - numColumn) % numColumn] - length[i]) + param[i]
			
		if (i - numColumn) % numColumn == (numColumn - 1):
			ret += "\n"

	return ret


if __name__ == "__main__":
	app.run(debug=True, port=80)
