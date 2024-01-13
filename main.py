import hashlib
import math
import random
import sys
import time
from multiprocessing import Pool

taille, alphabet = 4, "abcdefghijklmnopqrstuvwxyz"
gTable = {}
gTableKeys = []
storedI2C = {}
def N():
	return len(alphabet) ** taille
storedN = N()
lenAlphabet = len(alphabet)
lenTableKeys = 0
def updateGlobals():
	global storedN, lenAlphabet, gTableKeys, lenTableKeys, gTable
	storedN = N()
	lenAlphabet = len(alphabet)
	gTableKeys = list(gTable.keys())
	lenTableKeys = len(gTableKeys)

def hashW(word):
	return hashlib.sha1(word.encode()).digest()

def i2c(integer):
	if integer in storedI2C:
		return storedI2C[integer]
	res = ""
	for _ in range(taille):
		integer, c = divmod(integer, lenAlphabet)
		res = alphabet[c] + res
	storedI2C[integer] = res
	return res

def c2i(word):
	res = 0
	for c in word:
		res = res * lenAlphabet + alphabet.index(c)
	return res

def h2i(y, t):
	return (t + int.from_bytes(y[:8], "little")) % storedN

def i2i(x, t):
	return h2i(hashW(i2c(x)), t)

def nouvelle_chaine(args):
	tmp = args[0]
	for x in range(1, args[1]):
		tmp = i2i(tmp, x)
	return args[0], tmp

def index_aleatoire(_v):
	return random.randint(0, storedN-1)

def recherche(idx):
	# with a dichotomic search find the range of indexes that have the same value as idx
	deb, fin = 0, lenTableKeys-1
	while deb <= fin:
		mil = (deb + fin) // 2
		if gTable[gTableKeys[mil]] < idx:
			deb = mil + 1
		elif gTable[gTableKeys[mil]] > idx:
			fin = mil - 1
		else:
			# found the first index
			deb = fin = mil
			while deb > 0 and gTable[gTableKeys[deb-1]] == idx:
				deb -= 1
			while fin < lenTableKeys-1 and gTable[gTableKeys[fin+1]] == idx:
				fin += 1
			return deb, fin
	return -1, -1

def check_candidate(h, t, idx):
	for x in range(1, t):
		idx = i2i(idx, x)
	clair = i2c(idx)
	h2 = hashW(clair)
	return h2 == h, clair

def inversion(largeur, h):
	for t in range(largeur-1, 0, -1):
		idx = h2i(h, t)
		for x in range(t + 1, largeur):
			idx = i2i(idx, x)
		res = recherche(idx)
		print(f"t={t} idx={idx} res={res}")
		if res[0] != -1:
			for x in range(res[0], res[1] + 1):
				ok, clair = check_candidate(h, t, gTableKeys[x])
				if ok:
					return clair
	return None

def getAllIndexes(hauteur, largeur, get_index):
	tmp = []
	for x in range(hauteur):
		tmp.append([get_index(x), largeur])
	return tmp

def initPoolCreateTable(t, a, n):
	global taille, alphabet, storedN, lenAlphabet
	taille, alphabet, storedN, lenAlphabet = t, a, n, len(a)

def creer_table(largeur, hauteur, get_index):
	global gTable
	with Pool(initializer=initPoolCreateTable, initargs=(taille, alphabet, storedN)) as pool:
		result = pool.map(nouvelle_chaine, getAllIndexes(hauteur, largeur, get_index))
	# Return the table sorted by values
	gTable = dict(sorted(result, key=lambda x: x[1]))
	updateGlobals()

def creer_tableIter(largeur, hauteur, get_index):
	global gTable, gTableKeys
	res = []
	for x in range(hauteur):
		idx = get_index(x)
		res.append(nouvelle_chaine([idx, largeur]))
	# Return the table sorted by values
	gTable = dict(sorted(res, key=lambda val: val[1]))
	updateGlobals()

def save_table(largeur, filename):
	with open(filename, "w") as f:
		f.write(f"{alphabet} {taille} {lenTableKeys} {largeur}\n")
		for k, x in gTable.items():
			f.write(f"{k} {x}\n")

def load_table(filename):
	global taille, alphabet, gTable, gTableKeys
	with open(filename, "r") as f:
		alphabet, taille, hauteur, largeur = f.readline().split()
		taille, hauteur, largeur = int(taille), int(hauteur), int(largeur)
		table = {}
		for _ in range(hauteur):
			k, x = f.readline().split()
			table[int(k)] = int(x)
		gTable = table
		updateGlobals()
		return hauteur, largeur

def info(args):
	filename = args[0]
	height, width = load_table(filename)
	print("hash function: sha1")
	print(f"alphabet: {alphabet}")
	print(f"alphabet length: {len(alphabet)}")
	print(f"size: {taille}")
	print(f"nb clear text: {N()}")
	print(f"height: {height}")
	print(f"width: {width}")
	print("content:")
	for k, x in enumerate(gTable.items()):
		if k < 10:
			print(f"{k:0>8}: {x[0]} --> {x[1]}")
		elif k == 10:
			print("...")
		elif k > height - 10:
			print(f"{k:0>8}: {x[0]} --> {x[1]}")

def create(args):
	height, width, saveName, randomIndex = int(args[0]), int(args[1]), args[2], "y" in args[3]
	start = time.time()
	creer_table(width, height, index_aleatoire if randomIndex else lambda x: x + 1)
	end = time.time()
	print(f"elapsed time: {end - start:.2f}s")
	save_table(width, saveName)
	info([saveName])

def crack(args):
	h = int.from_bytes(bytes.fromhex(args[0]), "little").to_bytes(20, "little")
	height, width = load_table(args[1])
	start = time.time()
	clair = inversion(width, h)
	end = time.time()
	print(f"elapsed time: {end - start:.2f}s")
	if clair is None:
		print("not found")
	else:
		print(clair)

def bruteforce_hash(h):
	for idx in range(N()):
		clair = i2c(idx)
		h2 = hashW(clair)
		if h2 == h:
			return clair
	return None

def bruteforce(args):
	h = int.from_bytes(bytes.fromhex(args[0]), "little").to_bytes(20, "little")
	start = time.time()
	clair = bruteforce_hash(h)
	end = time.time()
	print(f"elapsed time: {end - start:.2f}s")
	if clair is None:
		print("not found")
	else:
		print(clair)

def stats(args):
	print(f"height: {args[0]}")
	print(f"width: {args[1]}")
	print(f"size: {taille}")
	m = int(args[0])
	x = 1.0
	for _ in range(int(args[1])):
		x = x * (1 - m / storedN)
		m = storedN * (1 - math.exp(-m / storedN))
	couverture = 100 * (1 - x)
	print(f"estimated byte size: {taille * int(args[0])}")
	print(f"estimated coverage: {couverture:.2f}%")
	print(f"estimated time of creation: {0.0000007*args[0]*args[1]:.2f}s")
	print(f"estimated bruteforce cracking time: 0..{0.00000161934105 * N():.2f}s")

def helpMenu():
	print("""usage: python main.py <CMD> [OPTIONS] [ARGS]

Available commands:
  create <height> <width> <FILENAME>
            create the corresponding rainbow tables
  info <FILENAME> [LIMIT]
            display some information about the table from given file
  crack <H> <FILENAMES> ...
            crack the given hash with the rainbow tables
  test ...
        	development tests (run "./rbt test list" for available tests)
  stats <height> <width>
			display some statistics about the estimated table
  bruteforce <H>
			bruteforce the given hash
  help
			display this message

Available options:
  --alphabet=<s>          allowed characters for clear text
  -A<N> / --abc<N>      choose standard alphabet:
         N=26               abcdefghijklmnopqrstuvwxyz (default)
         N=26A              ABCDEFGHIJKLMNOPQRSTUVWXYZ
         N=36               abcdefghijklmnopqrstuvwxyz0123456789
         N=40               abcdefghijklmnopqrstuvwxyz0123456789,;:$.
         N=52               ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
         N=62               0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
         N=66               0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz,;:$.
  -s <n> / --size <n>     exact size of clear text (default: 5)
  -help / -h              this message
	""")

def test(args):
	global gTable
	if len(args) == 0:
		print("usage: python main.py test <CMD> [OPTIONS] [ARGS]")
		exit(1)

	testCmd = args[0]
	if testCmd == "list":
		print("""Available tests:
    test list                           this list
    test config                         show configuration
    test hash <s1> <s2> ...             compute hash of strings s1, s2, ...
    test i2c <i1> <i2> ...              compute i2c(i1), i2c(i2), ...
    test c2i <c1> <c2> ...              compute c2i(c1), c2i(c2), ...
    test h2i <s> <t>                    compute h2i(H(s), t, n)
    test i2i <i1> <t1> ...              compute i2i(i1, t1), i2i(i2, t2), ...
    test full_chain <width> <i1> ...    compute (full) chains starting at i1, i2, ...
    test search <FILENAME> <i>          search the first and last occurences of i in table
		""")
	elif testCmd == "config":
		print(f"alphabet = \"{alphabet}\"\ntaille = {taille}\nN = {N()}")
	elif testCmd == "hash":
		[print(f"hash({s}) = {hashW(s).hex()}") for s in args[1:]]
	elif testCmd == "i2c":
		[print(f"i2c({c}) = {i2c(int(c))}") for c in args[1:]]
	elif testCmd == "c2i":
		[print(f"c2i({c}) = {c2i(c)}") for c in args[1:]]
	elif testCmd == "h2i":
		if len(args) < 3:
			print("usage: python main.py test h2i <s> <t>")
			exit(1)
		s, t = args[1], int(args[2])
		print(f"hash({s}) = {hashW(s).hex()}")
		print(f"h2i(hash({s}), {t}) = {h2i(hashW(s), t)}")
	elif testCmd == "i2i":
		print(args)
		[print(f"i2i({x}, {t}) = {i2i(int(x), int(t))}") for x, t in zip(args[1::2], args[2::2])]
	elif testCmd == "full_chain":
		if len(args) < 2:
			print("usage: python main.py test full_chain <width> <i1> <i2> ...")
			exit(1)
		width = int(args[1])
		for x in args[2:]:
			res = nouvelle_chaine([int(x), width])
			print(f"full_chain({x}, {width}) = {res[0]} .. {res[0]}")
			gTable.clear()
	elif testCmd == "search":
		if len(args) < 3:
			print("usage: python main.py test search <FILENAME> <i>")
			exit(1)
		filename, x = args[1], int(args[2])
		load_table(filename)
		print(f"search({filename}, {x}) = {recherche(x)}")


if __name__ == '__main__':
	if len(sys.argv) == 1:
		helpMenu()
		exit(0)

	unusedArgs = []

	for i, v in enumerate(sys.argv[2:]):
		if v == "-h" or v == "--help":
			helpMenu()
			exit(0)
		elif "-A" in v or "--abc" in v:
			alphabet = "abcdefghijklmnopqrstuvwxyz"
			if "26A" in v:
				alphabet = alphabet.upper()
			if "36" in v:
				alphabet += "0123456789"
			if "40" in v:
				alphabet += "0123456789,;:$."
			if "52" in v:
				alphabet += alphabet.upper()
			if "62" in v:
				alphabet = "0123456789"+alphabet.upper()+alphabet
			if "66" in v:
				alphabet = "0123456789"+alphabet.upper()+alphabet+",;:$."
		elif "-s=" in v:
			taille = int(v[3:])
		elif "--size=" in v:
			taille = int(v[7:])
		elif "--alphabet=" in v:
			alphabet = v[11:]
		else:
			unusedArgs.append(v)
	updateGlobals()

	cmd = sys.argv[1]
	if cmd == "create":
		create(unusedArgs)
	elif cmd == "info":
		info(unusedArgs)
	elif cmd == "crack":
		crack(unusedArgs)
	elif cmd == "test":
		test(unusedArgs)
	elif cmd == "stats":
		stats(unusedArgs)
	elif cmd == "bruteforce":
		bruteforce(unusedArgs)
	elif cmd == "help":
		helpMenu()
	else:
		print(f"Unknown command: {cmd}")
		helpMenu()
		exit(1)