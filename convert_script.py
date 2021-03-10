import pickle
import csv
import os
from os import path

global countfile
countfile = 0

#taken from online:
#calculates the longest common subsequence of two strings
def lcs(X, Y): 
    # find the length of the strings 
    m = len(X) 
    n = len(Y) 
  
    # declaring the array for storing the dp values 
    L = [[None]*(n + 1) for i in range(m + 1)] 
  
    for i in range(m + 1): 
        for j in range(n + 1): 
            if i == 0 or j == 0 : 
                L[i][j] = 0
            elif X[i-1] == Y[j-1]: 
                L[i][j] = L[i-1][j-1]+1
            else: 
                L[i][j] = max(L[i-1][j], L[i][j-1]) 
    return L[m][n] 

#flattens a list
def flatten(l):
	res = []
	for subl in l:
		for x in subl:
			res.append(x)
	return res

def isnonstring(s):
	try:
		int(s)
		return True
	except:
		try:
			float(s)
			return True
		except:
			return False

def table_to_string(t):
	return '\n'.join([' '.join(line) for line in t])

#standardizes all known whitespace - any number of tabs and spaces - into a single character
def replace_whitespace(s):
	res = []
	prevwhite = True
	for c in s:
		if c in ["#"]:
			continue
		if c in [' ','\t']:
			if not prevwhite:
				prevwhite = True
				res.append(' ')
		else:
			prevwhite = False
			res.append(c)
	return "".join(res)

# takes a string as input, and calculates if it could possibly contain a table.
# if yes, returns a list of strings which are the rows of the table
def possibletable(x):
	x = replace_whitespace(x)
	divide_lines = x.split('\n')
	max_features = None
	max_streak = 0
	num_spaces = [line.count(' ') for line in divide_lines]
	cur_streak = 0
	cur_streak_start = -1
	cur_val = None
	for (i,space_count) in enumerate(num_spaces):
		if space_count == cur_val and space_count != 0:
			cur_streak += 1
		elif cur_streak > max_streak:
			max_streak = cur_streak
			max_features = (cur_streak_start,i,cur_val)
		if space_count != cur_val:
			cur_val = space_count
			cur_streak_start = i
			cur_streak = 0
	if max_features is None:
		# print("max_features not found")
		return False
	(start,end,size) = max_features
	best_section =  divide_lines[start:end]
	# if countfile == 7:
	# 	print("-------------------------------------")
	# 	print('\n'.join(best_section))
	return best_section

def spaceseptotable(t):
	return [line.split(' ') for line in t]

def addheader(t):
	if any([isnonstring(s) for s in t[0]]):
		t = [(["c"+str(x) for x in range(len(t[0]))])] + t
	return t

def clean_table(t):
	t = addheader(t)
	res = []
	idxstolose = []
	for i in range(len(t[0])):
		if all([x[i]==t[1][i] for x in t[1:]]):
			idxstolose.append(i)
		if all([str(x[i])==str(j) for j,x in enumerate(t[1:])]):
			idxstolose.append(i)
		if all([str(x[i])==str(j+1) for j,x in enumerate(t[1:])]):
			idxstolose.append(i)
		if all([str(x[i])==str(j) for j,x in enumerate(t)]):
			idxstolose.append(i)
	for line in t:
		lineres = []
		for (i,x) in enumerate(line):
			if i not in idxstolose:
				lineres.append(x)
		res.append(lineres)
	res = addheader(res)
	return res

def likelytable(t):
	res = clean_table(spaceseptotable(t))
	if len(res)<=2 or len(res[0])<2:
		# print("best option is really bad:", length,",",size)
		return False
	return res

#determines (based on a guess) whether one input can create the other
def possibleinputoutput(inp,outp):
	flat1 = flatten(inp)
	flat2 = flatten(outp)
	t1vs = set(flat1)
	t2vs = set(flat2)

	countintersect = 0
	for x in t1vs:
		if x in t2vs:
			countintersect+=1

	if countintersect <= 1:
		return False

	t1numintersect = sum([1 if x in t2vs else 0 for x in flat1])
	t2numintersect = sum([1 if x in t1vs else 0 for x in flat2])

	if len(flat1) - t1numintersect < 3 and len(flat2) - t2numintersect < 3:
		return False

	return (inp,outp)

def findtable(post):
	possible_tables = [possibletable(v) for l,v in post]
	possible_tables = [x for x in possible_tables if x]
	likely_tables = [likelytable(t) for t in possible_tables]
	likely_tables = [x for x in likely_tables if x]
	for i,x in enumerate(likely_tables):
		for y in likely_tables[i+1:]:
			ts = possibleinputoutput(x,y)
			if ts:
				return ts
	return False

def csvfrompost(url,post):
	global countfile
	a = findtable(post)
	if not a:
		return False
	(t1,t2) = a
	subdir = 'newcsvs/e'+str(countfile)
	if not os.path.exists(subdir):
		os.mkdir(subdir)
	with open(subdir+'/input.csv','w',newline='\n') as csvfile:
		extractwriter = csv.writer(csvfile,delimiter=',')
		for line in t1:
			extractwriter.writerow(line)
	with open(subdir+'/output.csv','w',newline='\n') as csvfile:
		extractwriter = csv.writer(csvfile,delimiter=',')
		for line in t2:
			extractwriter.writerow(line)
	with open(subdir+'/url.txt','w') as f:
		f.write("https://stackoverflow.com/"+url)
	print("done")
	countfile += 1
	return True



with open("op_dataset.pkl",'rb') as f:
	raw = pickle.load(f)

flattened = flatten([raw[k] for k in list(raw.keys())])
cleaned = []
for post in flattened:
	metadata = post[0]
	question = post[1]
	answers = post[2]
	postarray = []
	postarray += question
	# for answerdata in answers:
	# 	answer = answerdata["ansr"]
	# 	postarray += answer
	cleaned.append((metadata["url"],postarray))
urldict = dict(cleaned)

if not os.path.exists('newcsvs'):
	os.mkdir('newcsvs')

for url,v in cleaned:
	csvfrompost(url,v)

# for url in ["https://stackoverflow.com"+cleaned[i][0] for i in range(8, 16)]:
# 	print(url)

# print(urldict["/questions/24459752/can-dplyr-package-be-used-for-conditional-mutating"][2][1])
# [possibletable(x[1]) for x in urldict["/questions/22959635/remove-duplicated-rows-using-dplyr"]]
# if possibleinputoutput(urldict["/questions/22959635/remove-duplicated-rows-using-dplyr"][1],urldict["/questions/22959635/remove-duplicated-rows-using-dplyr"][3]):
# 	print("hiiii")
# csvfrompost(urldict["/questions/22959635/remove-duplicated-rows-using-dplyr"])
# possibletable(urldict["/questions/24459752/can-dplyr-package-be-used-for-conditional-mutating"][2][1])

