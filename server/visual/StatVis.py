import matplotlib.pyplot as plt
import numpy as np
import os


class StatVis():
	#the histogram graph for large datasets does not render properly with the bar graph so a regular line plot is used
	def vis_data(self, graph_type, xlabel, ylabel, title, y_data, path, x_data = None , scale = None):

		print("ploting data...")
		if scale != None:
			plt.ylim(0,scale)
		#if there is no x data passed then we are assuming that the graph will be done per request
		if x_data == None:
			if graph_type == 'scatter':
				plt.scatter(range(0,len(y_data)), y_data, s=.7)
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.title(title.split('/')[-1])
				plt.savefig(path+ "/" + title+".png")
				plt.close()
				#plt.show()

			if graph_type == 'line':
				plt.plot(range(0,len(y_data)), y_data)
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.title(title.split('/')[-1])
				plt.savefig(path+ "/" + title + ".png")
				plt.close()
				#plt.show()

		else:
			if graph_type == 'line':
				plt.plot(x_data, y_data)
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)

				plt.title(title.split('/')[-1].split(' ')[0])
				plt.savefig(os.path.abspath(path)+ "/" + title.split('/')[-1] +".png", bbox_inches='tight', dpi=300)

				plt.close()
				#plt.show()

			if graph_type == 'histogram':
				#print(x_data, y_data, "in plot method")
				plt.bar(x_data, y_data)
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.yscale('log',basey=2)

				title = title.split('/')[-1]
				title = title.replace(':', ' ')
				plt.title(title)
				

				plt.savefig(os.path.abspath(path) + "/" + title.split('/')[-1] + ".png", bbox_inches='tight', dpi=300)
				#plt.show()
				plt.close()
				#plt.show() 

			if graph_type == 'scatter':
				#print(len(x_data) )
				#print(len(y_data) )
				plt.scatter(x_data, y_data, s=.7)
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.title(title.split('/')[-1].split(' ')[0])
				plt.savefig(os.path.abspath(path) + "/" + title.split('/')[-1] + ".png", bbox_inches='tight', dpi=300)
				plt.close()
				#plt.show()

	def vis_data_multi(self, graph_type, xlabel, ylabel, title, y_data, multi_labels, path, x_data = None, scale = None, fill=None):

		if scale != None:
			plt.ylim(0,scale)

		print('IN MULTI')
		#print("===============================")
		colors = ['c', 'm', 'y', 'g']
		count = 0
		if x_data == None:
			if graph_type == 'scatter':
				for plots in y_data:
					plt.scatter(range(0,len(plots)), plots, s=.7, color=colors[count], label=multi_labels[count])
					count+=1
					if count == 3:
						break
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.legend(loc="upper left")
				plt.title(title.split('/')[-1])
				plt.savefig(os.path.abspath(path)+ "/" + title+".png")
				plt.close()
				#plt.show()

			if graph_type == 'line':
				#plt.plot(range(0,len(y_data)), y_data)
				for plots in y_data:
					plt.plot(range(0,len(plots)), plots, color=colors[count], label=multi_labels[count])
					count+=1
					if count == 3:
						break
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.legend(loc="upper left")
				plt.title(title.split('/')[-1])
				plt.savefig(os.path.abspath(path)+ "/" + title+".png")
				plt.close()
				#plt.show()

		else:
			if graph_type == 'histogram' or graph_type == 'line':
				#print(ylabel)
				for plots in y_data:
					#print(multi_labels)
					plt.plot(x_data, plots, color=colors[count], label=multi_labels[count])
					count += 1
					if count == 3:
						break
				if fill:
					print("fill")
					#print( y_data )
					plt.fill_between(x_data, y_data[0], y_data[1], where=y_data[0] >= y_data[1], color='g')
					plt.fill_between(x_data, y_data[0], y_data[1], where=y_data[0] <= y_data[1], color='r')
				print("whats going on")
				#plt.plot(x_data, y_data)
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.legend(loc="upper left")
				plt.title(title.split('/')[-1])
				print(title)
				plt.savefig(os.path.abspath(path)+ "/" + title+".png")
				plt.close()
				#plt.show()

			if graph_type == 'scatter':
				#print(len(x_data) )
				#print(len(y_data) )
				#plt.scatter(x_data, y_data, s=.7)
				if graph_type == 'scatter':
					for plots in y_data:
						plt.scatter(x_data, plots, s=.7, color=colors[count], label=multi_labels[count])
						count+=1
						if count == 3:
							break
				plt.xlabel(xlabel)
				plt.ylabel(ylabel)
				plt.legend(loc="upper left")
				plt.title(title.split('/')[-1])
				plt.savefig(os.path.abspath(path)+ "/" + title+".png")
				plt.close()
				#plt.show()


