#!/usr/bin/env python
# -*- coding: utf-8 -*-

u'''
Mecabを使った単語分割,及びTF-IDF値計算
'''
import os
import sys
import MeCab
import collections
import csv
from math import log10

INPUT_DOC_DIR = './docs/'
OUTPUT_VEC = './vecs/wg_doc2vec.vec'

class GetVec():
    def __init__(self, doc_dir, vec_dir):
        self.doc_dir = doc_dir
        self.vec_dir = vec_dir

        self.corpus = list(self.get_all_files(self.doc_dir))
        self.corpus.sort()
        self.sentences = list(self.corpus_to_sentences(self.corpus))
        #sentences = list(self.corpus_to_sentences(self.corpus))

        #出現単語リスト（辞書）作成
        self.uniq_words = list(self.make_dictionary(self.sentences))
        #self.uniq_words = list(self.make_dictionary(sentences))

        #各文章での出現回数表作成
        #self.count_table = self.make_appearance_table(sentences, self.uniq_words)
        self.count_table = self.make_appearance_table(self.sentences, self.uniq_words)
        #count_table = self.make_appearance_table(self.sentences, self.uniq_words)

        #各文章での単語のTF値取得
        self.TF_Value = self.calc_TF(self.sentences, self.uniq_words, self.count_table)
        #self.TF_Value = self.calc_TF(sentences, self.uniq_words, self.count_table)
        #TF_Value = self.calc_TF(self.sentences, self.uniq_words, count_table)
        #self.TF_Value = self.calc_TF(self.sentences, self.uniq_words, count_table)

        #各文章での単語のIDF値取得
        self.IDF_Value = self.calc_IDF(self.sentences,self.uniq_words)
        #self.IDF_Value = self.calc_IDF(sentences,self.uniq_words)

        #各文章での単語のTFIDF値計算
        self.TFIDF_Value = self.calc_TFIDF(self.TF_Value,self.IDF_Value)

        #L2正規化
        self.L2_normalize = self.calc_L2(self.TFIDF_Value)


    def get_TF(self):
        return self.TF_Value

    def get_IDF(self):
        return self.IDF_Value

    def get_TFIDF(self):
        return self.TFIDF_Value

    def get_VEC(self):
        return self.L2_normalize

    #def getSentences(self):
    #    return self.sentences

    u'''文章ファイル読み込み'''
    def get_all_files(self,directory):

        for root, dirs, files in os.walk(directory):
            for file in files:
                yield os.path.join(root, file)

    u'''ファイルから文章を取得'''
    def read_document(self,path):
        with open(path, 'r', encoding='utf8', errors='ignore') as f:
            return f.read()

    u'''不要部分削除'''
    def trim_doc(self, doc):
        lines = doc.splitlines()
        valid_lines = []
        is_valid = False
        horizontal_rule_cnt = 0
        break_cnt = 0
        for line in lines:
            if horizontal_rule_cnt < 2 and '-----' in line:
                horizontal_rule_cnt += 1
                is_valid = horizontal_rule_cnt == 2
                continue
            if not(is_valid):
                continue
            if line == '':
                break_cnt += 1
                is_valid = break_cnt != 3
                continue
            break_cnt = 0
            valid_lines.append(line)
        return ''.join(valid_lines)


    u'''単語に分解'''
    def split_into_words(self, doc, name=''):
        mecab = MeCab.Tagger("-Ochasen")
        valid_doc = self.trim_doc(doc)
        lines = mecab.parse(doc).splitlines()
        words = []

        for iCnt in range(0, len(lines)):
            chunks = lines[iCnt].split('\t')
            if iCnt < len(lines)-1:
                chunks_after = lines[iCnt+1].split('\t')
                if len(chunks_after) <=3:
                    chunks_after = ['','','','','','']
            else:
                chunks_after = ['','','','','','']

            if len(chunks) <= 3:
                continue

            if chunks[3].startswith('動詞-自立'): 
                words.append(chunks[2])
            elif chunks[3].startswith('形容詞'):
                words.append(chunks[2])
            elif chunks[3].startswith('名詞-一般') and chunks_after[3].startswith('助動詞'):
                words.append(chunks[0]+chunks_after[2])
 
        return words

    u'''全単語リストを作成'''
    def make_dictionary(self, sentences):
        all_words = []
        for sublist in sentences:
            for item in sublist:
                all_words.append(item)
        all_words = set(all_words)
        all_words = sorted(all_words)    
        return all_words

    u'''出現回数表作成'''
    def make_appearance_table(self, sentences,uniq_words):
        count_table = []
        for iCnt in range(0, len(sentences)):
            count_table.append([])
            for target_word in uniq_words:
                count_table[iCnt].append(sentences[iCnt].count(target_word))
            iCnt = iCnt + 1
        return count_table
   
    u'''TF値計算'''
    def calc_TF(self, sentences,uniq_words,count_table):
        #def calc_TF(self, sentences,uniq_words):
        TF_Value = []
        #count_table = count_table
        for iCnt in range(0, len(sentences)):
            TF_Value.append([])
            iCnt2 = 0
            for target_word in uniq_words:
                TF_Value[iCnt].append(count_table[iCnt][iCnt2]/sum(count_table[iCnt]))
                iCnt2 = iCnt2 + 1
            iCnt = iCnt + 1
        return TF_Value      

    u'''IDF値計算'''
    def calc_IDF(self, sentences,uniq_words):
        IDF_Value = []
        for iCnt in range(0,len(uniq_words)):
            target_count = 0
            for iCnt2 in range(0,len(sentences)):
                if sentences[iCnt2].count(uniq_words[iCnt]) > 0:
                    target_count+=1
        
            IDF_Value.append(log10(len(sentences)/target_count)+1)
        return IDF_Value

    u'''TF-IDF値計算'''
    def calc_TFIDF(self, TF_Value,IDF_Value):
        TFIDF_Value = []
        for iCnt in range(0,len(TF_Value)):
            TFIDF_Value.append([])
            for iCnt2 in range(0,len(TF_Value[0])):
                 TFIDF_Value[iCnt].append(TF_Value[iCnt][iCnt2]*IDF_Value[iCnt2])
        return TFIDF_Value

    u'''L2正規化（TF-IDF値)'''
    def calc_L2(self, TFIDF_Value):
        L2_normalize = []
        max_TFIDF = max(max(TFIDF_Value))
        for iCnt in range(0,len(TFIDF_Value)):
            L2_normalize.append([])
            for iCnt2 in range(0,len(TFIDF_Value[0])):
                 L2_normalize[iCnt].append(TFIDF_Value[iCnt][iCnt2]/max_TFIDF)
        return L2_normalize

    u'''ファイルから単語のリストを取得'''
    def corpus_to_sentences(self, corpus):
        docs = [self.read_document(x) for x in corpus]
        for idx, (doc, name) in enumerate(zip(docs, corpus)):
            yield self.split_into_words(doc, name)

    def output_vecs(self, title_vec, target_vec):
        f = open(OUTPUT_VEC, 'w') # 書き込みモードで開く
        writer = csv.writer(f, lineterminator='\n') # 書き込みファイルの設定
    
        writer.writerow(title_vec) 
        writer.writerows(target_vec)
        f.close() # ファイルを閉じる



if __name__ == '__main__':

    wg_doc2vec = GetVec('./docs/', './vecs/wg_doc2vec.vec')

    print(wg_doc2vec.get_VEC())

    #print('文章群数:' + str(len(wg_doc2vec.sentences)))
    #print('文章群数:' + str(len(wg_doc2vec.getSentences())))
    #print('総単語数:' + str(len(uniq_words)))
    #output_vecs(uniq_words,L2_normalize)
