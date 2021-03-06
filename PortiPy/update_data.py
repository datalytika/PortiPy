#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains classes that handle the data update efficiently.
Historical data of stocks and indices are updated via the pandas_datareader package.
Financal statements of stocks are also updated. The update has beed parallelized using threads.
"""

import os
import sys
import time
import datetime as dt
from threading import Thread

import numpy as np
import pandas as pd
import pandas_datareader.data as pdr

from qfipy.utilities import open_symbols_file, get_directory_size, progress_bar

__author__ = "Apostolos Kouzoukos"
__license__ = "MIT"
__email__ = "kouzoukos97@gmail.com"
__status__ = "Development"

class DataUpdater:
	"""
	This class handles the update of historical data of stocks and indices and financial statements
	of stocks.
	"""

	def __get_dates(self, years):
		"""
		This private method accepts as parameter an integer and returns the current date and 
		the date after the subtraction of (365 * years) days from today. Other methods use this 
		dates to retrieve the historical data in this interval.

		Parameters:
		----------
			years: int, the years to be substracted from the current date.
		Returns:
		-------
			start: str, the date after the subtraction of (365 * years) days from today.
			end: str, the current date.
		"""

		end = str(dt.datetime.now().year) + '-' + str(dt.datetime.now().month) + '-' + str(dt.datetime.now().day)
		start = dt.datetime.now() - dt.timedelta(days = years * 365)
		start = str(start.year) + '-' + str(start.month) + '-' + str(start.day)

		return start, end

	def __remove_data(self, directory):
		"""
		This private method removes the files from a directory.

		Parameters:
		----------
			directory: str, the name of the directory.
		"""

		if not os.path.isdir(directory):
			os.mkdir(directory)

		for f in os.listdir(directory):
			path = os.path.join(directory, f)

			if os.path.isfile(path):
				os.remove(path)

	def __get_historical_data(self, sym_list, start, end):
		"""
		This private method accepts a symbols list, a time interval and downloads the historical
		data of the stocks iteratively and saves the files in .csv format.

		Parameters:
		----------
			sym_list: list, a list of stock symbols.
			start: str, the start of the time interval.
			end: str, the end of time interval. 
		"""

		for sym in sym_list:
			while True:
				try:
					histDF = pdr.DataReader(sym, 'yahoo', start, end)
					histDF.to_csv('historical_data/' + sym + '.dat')

					break

				except Exception:
					print(sym)
					#pass

	def run_stock_data_update(self, index, remove = True):
		"""
		This method implements the parallelization of the historical data update of the stocks
		of a specific index. It creates 10 threads, with each thread handling a portion of the 
		whole symbols list. The historical data of major indices is also updated.
		The threads proceed to download the data in parallel, speeding up the whole process.

		Parameters:
		----------
			index: str, the symbol of the index.
			remove: boolean, if True, the current data is deleted, else is being overwritten. 
			Defaults to True.
		"""

		if remove:
			self.__remove_data('historical_data/')

		start, end = self.__get_dates(3)

		stock_symbols = open_symbols_file(index)
		indices_symbols = open_symbols_file('indices')

		n = len(stock_symbols)
		A = np.arange(0, n, n / 10, dtype = int)

		S = [stock_symbols[A[i]:A[i + 1]] for i in range(len(A) - 1)]
		S.append(stock_symbols[A[-1]:])

		T = [Thread(target = self.__get_historical_data, args = (s, start, end)) for s in S]
		T.append(Thread(target = self.__get_historical_data, args = (indices_symbols, start, end)))

		print("Downloading historical data...")

		n += len(indices_symbols)
		
		start = time.perf_counter()

		for t in T:
			t.start()

		progress_bar(0, n, prefix = 'Progress:', length = 50)

		'''for t in T:
			t.join()'''

		while len(os.listdir('historical_data/')) != n:
			progress_bar(len(os.listdir('historical_data')), n, prefix = 'Progress:', length = 50)
			time.sleep(0.1)

		progress_bar(n, n, prefix = 'Progress:', length = 50)
		print()

		total_time = str(round(time.perf_counter() - start, 1))
		files_count = str(len(os.listdir('historical_data')))
		files_size = str(round(get_directory_size('historical_data'), 2))

		print("Total {} files in {} sec ({} MB)".format(files_count, total_time, files_size))

def main():
	#os.system('cls')

	d1 = DataUpdater()

	'''indexQuote = sys.argv[1]
	DataUpdater().runStockDataUpdate(indexQuote)'''

	d1.run_stock_data_update('DJI')
	#d1.runFinancialStatementsUpdate('GSPC')

	for _ in range(2):
		print('\a', end = '\r')

if __name__ == '__main__':
	main()
