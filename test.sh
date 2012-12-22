#test runner, run all tests
#tests are not "verified" theyr'e just run through `time` so I can compare performance

#*NIX Library Path Stuff
#if 7z.so is in a non-standard location not on system path, remember to put it here
#remember ld doesn't search subdirs at all, so if /usr/lib is in the path, but 7z.so is at /usr/lib/p7zip/7z.so,
#it won't be found. (put the directory 7z.so is in, if 7z.so isn't named 7z.so rename it to 7z.so, (if on *NIX)
export LD_LIBRARY_PATH=/usr/lib/p7zip

#Python 2
for i in c ctypes cffi sub; do
	echo '::python2-'$i
	time python2 pytests.py $i >/dev/null
done

#Python 3
for i in ctypes cffi sub; do
	echo '::python3-'$i
	time python3 pytests.py $i >/dev/null
done

#need modules that I don't have for pypy (chardet for sub & cffi for cffi)
#for i in cffi sub; do
	#echo '::pypy-'$i
	#time pypy pytests.py $i >/dev/null
#done

echo '::c'
time ./ctest > /dev/null

echo '::c++'
time ./cpptest > /dev/null

#shtest is ridiculously slow, don't bother running
echo '::sh(dash)'
time dash shtest.sh > /dev/null
