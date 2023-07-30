# -*- coding: utf-8 -*-

import json
import sys
import pynlpir
import numpy as np
from gensim.models import Word2Vec
from keras.models import load_model
from keras.preprocessing import sequence

w2vmodel = Word2Vec.load('scripts/Word2Vec.model')
ecnnpm2model = load_model('scripts/ECNNpm2.model')
ecnnp3model = load_model('scripts/ECNNp3.model')
ecnnm4model = load_model('scripts/ECNNm4.model')

def get_words(string):
	ret=[]
	pynlpir.open()
	segments = pynlpir.segment(string)
	for segment in segments:
		if(segment[0]=='！' or segment[0]=='？'or segment[1]!="punctuation mark"):
			if(segment[1]!="numeral" and segment[1]!="None" and segment[0]!=" "):
				ret.append(segment[0])
	pynlpir.close()
	return ret

def get_vector(maxlen,lists):
	x=[]
	for i in range(len(lists)):
		try:
			feature = w2vmodel[lists[i]]
		except:
			pass
		else:
			x.extend(feature.reshape(1, feature.size))
	x = np.array(x)
	x = x.reshape(1, x.size)
	x = sequence.pad_sequences(x, maxlen = maxlen, dtype = 'float32')
	return np.array(x)
	
def chg(vec,x,y):
	ret=[]
	for i in range(y):
		tmp=0
		for j in range(x):
			tmp+=vec[i*x+j]
		ret.append(tmp/x)
	return np.array(ret)
	
def get_sim(vec_a,vec_b):
	dot=vec_a.dot(vec_b)
	len_a=vec_a.dot(vec_a)
	len_b=vec_b.dot(vec_b)
	return dot/((len_a*len_b)**0.5)
	
if __name__=='__main__':
	num = int(sys.argv[1])
	input = json.loads(sys.argv[2])
	ret={}
	for i in range(num+1):
		words = get_words(input.get("id"+str(i)).get("text"))
		vector = get_vector(70*50,words)
		tmp_json={}
		if i==0 :
			base=chg(vector[0],70,50)
			tmp_json[0]=str(1.0)
		else:
			tmp_json[0]=str(get_sim(base,chg(vector[0],70,50)))
		vector = vector.reshape(vector.shape[0], 70, 50)
		label = ecnnpm2model.predict(vector)[0]
		result = np.array([0, 0, 0, 0, 0, 0, 0], dtype = 'float32')
		if label[0] >= 0.5:
			tmp = ecnnp3model.predict(vector)[0]
			result[0] = tmp[0]
			result[1] = tmp[1]
			result[6] = tmp[2]
		if label[1] >= 0.5:
			tmp = ecnnm4model.predict(vector)[0]
			result[2] = tmp[0]
			result[3] = tmp[1]
			result[4] = tmp[2]
			result[5] = tmp[3]
		for j in range(len(result)):
			tmp_json[j+1]=str(result[j])
		ret[i]=tmp_json
	print(json.dumps(ret))
