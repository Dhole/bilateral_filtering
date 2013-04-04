#! /usr/bin/python2.7

import Image, sys, time, gzip, os, numpy, math, array

input_image = sys.argv[1]
out_file = sys.argv[2]

win = 5
sig_d = 2
sig_r = 0.5
size_x = 0
size_y = 0

mid_win = (win - 1) / 2
dist_w = numpy.zeros((win,win))

#Compute exponential distances
for j in xrange(win):
	for i in xrange(win):
		dist = math.sqrt((mid_win - i)**2 + (mid_win - j)**2)
		dist_w[i][j] = math.exp(-dist**2 / (2 * sig_d**2))

#Compute exponential differential table
e_diff = []
for i in xrange(256):
	e_diff.append(math.exp(-i**2 / (2 * sig_r**2)))
	

def get_diff_w(x, y, pix):
	diff_w = numpy.zeros((win,win))
	for j in xrange(-mid_win, mid_win + 1):
		for i in xrange(-mid_win, mid_win + 1):
			#Check boundaries
			if (x + i >= 0) & (y + j >= 0) &(x + i < size_x) & (y + j < size_y):
				#print x, y
				#print x+i, y+j
				diff = pix[x,y] - pix[x + i, y + j]
				diff_w[i + mid_win][j + mid_win] = e_diff[diff]
	return diff_w
		
#Load image
im = Image.open(input_image)
im = im.convert("L")
pix = im.load()

out_graph = open(out_file + '.txt', 'w')
size_x = im.size[0]
size_y = im.size[1]

#Write image info
out_graph.write('# size_x ' + str(size_x) + '\n')
out_graph.write('# size_y ' + str(size_y) + '\n')

#Write the graph
for y in xrange(size_y):
	for x in xrange(size_x):
		value = pix[x,y]
		line = str(x + y * size_x) + " " + str(value)
		diff_w = get_diff_w(x, y, pix)
		weights = diff_w * dist_w
		weights = weights / weights.sum()
		#line : Vi Vj Wij
		for j in xrange(win):
			for i in xrange(win):
				if not weights[i][j] == 0:
					x2 = x + i - mid_win
					y2 = y + j - mid_win
					line = line + " " + str(x2 + y2 * size_x)
					line = line + " " + str(weights[i][j])

		out_graph.write(line +  "\n")
	print str(float(y) * 100 / size_y) + "%"
	
out_graph.close()

#Compress the graph with gzip
print "Graph finished, compressing..."

f_in = open(out_file + '.txt', 'rb')
f_out = gzip.open(out_file + '.txt.gz', 'wb')
f_out.writelines(f_in)
f_out.close()
f_in.close()

#Delete the uncompressed graph
os.remove(out_file + '.txt')