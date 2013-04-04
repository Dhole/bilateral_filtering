#! /usr/bin/python2.7

import Image, sys, time, gzip, os

root2 = 1.4142

#Gets pairs of neighbours distance
def get_neighbours(x, y, size_x, size_y, mode):
	neighbours = []

	#4-neighbours
	if x - 1 >= 0:
		neighbours.append(x - 1 + y * size_x)
		neighbours.append(1)
	if x + 1 <= size_x:
		neighbours.append(x + 1 + y * size_x)
		neighbours.append(1)
	if y - 1 >= 0:
		neighbours.append(x + (y - 1) * size_x)
		neighbours.append(1)
	if y + 1 <= size_y:
		neighbours.append(x + (y + 1) * size_x)
		neighbours.append(1)

	#8-neighbours
	if mode == 8:
		if (x - 1 >= 0) & (y - 1 >= 0):
			neighbours.append(x - 1 + (y - 1) * size_x)
			neighbours.append(root2)
		if (x - 1 >= 0) & (y + 1 <= size_y):
			neighbours.append(x - 1 + (y + 1) * size_x)
			neighbours.append(root2)
		if (x + 1 <= size_x) & (y + 1 <= size_y):
			neighbours.append(x + 1 + (y + 1) * size_x)
			neighbours.append(root2)
		if (x + 1 <= size_x) & (y - 1 >= 0):
			neighbours.append(x + (y - 1) * size_x)
			neighbours.append(root2)

	return ' '.join(map(str, neighbours))

input_image = sys.argv[1]
out_file = sys.argv[2]
mode = int(sys.argv[3])

im = Image.open(input_image)
im = im.convert("L")
pix = im.load()

out_txt = open(out_file, 'w')
size_x = im.size[0]
size_y = im.size[1]

#Write image info
out_txt.write('# size_x ' + str(size_x) + '\n')
out_txt.write('# size_y ' + str(size_y) + '\n')

#Write the graph
for y in xrange(size_y):
	for x in xrange(size_x):
		value = pix[x,y]
		neighbours = get_neighbours(x, y, size_x, size_y, mode)
		#line : vID pixel_value neighbour1 distance1 neighbour2 distance2 ...
		line = str(x + y * size_x) +  " " + str(value)
		line = line + " " + str(x + y * size_x) +  " 0 " + neighbours + "\n"
		out_txt.write(line)
out_txt.close()

#Compress the graph with gzip
f_in = open(out_file, 'rb')
f_out = gzip.open(out_file + '.gz', 'wb')
f_out.writelines(f_in)
f_out.close()
f_in.close()

#Delete the uncompressed graph
os.remove(out_file)

#im.save("tmp.jpg", "JPEG")