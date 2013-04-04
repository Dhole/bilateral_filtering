#! /usr/bin/python2.7

import Image, sys, time, gzip, os

input_file = sys.argv[1]
out_file = sys.argv[2]

#f_in = gzip.open(input_file, 'rb')
f_in = open(input_file, 'rb')

last_pos = f_in.tell()
size_x = 900
size_y = 604
#Read image info
for line in f_in:
	if not line[0] == '#':
		f_in.seek(last_pos)
		break
	if line[0:8] == '# size_x':
		size_x = int(line.split(' ')[2])
	if line[0:8] == '# size_y':
		size_y = int(line.split(' ')[2])
	last_pos = f_in.tell()

im = Image.new('L', (size_x, size_y))
pix = im.load()

#Write pixels into image
for line in f_in:
	if not line[0] == '#':
		line = " ".join(line.split())
		pos = int(line.split(' ')[0])
		value = int(line.split(' ')[1])
		x = pos % size_x
		y = int(pos / size_x)
		pix[x, y] = value

im.save(out_file)