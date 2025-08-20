import os
from collections import defaultdict
import re
import pickle
import csv
import random
import tqdm
from llr import llr_2x2

def parse(text):
    tokens = []
    pattern = re.compile(r"<L (.*?)>")
    matches = pattern.findall(text)

    for match in matches:
        parts = match.split()
        if len(parts) >= 4:
            word = parts[3]
            category = parts[0]
            cat2 = parts[1]
            tokens.append((word, category, cat2))
    
    return tokens

def parse_ccgbank(ccg_directory='ccgbank', min_sentence_length=5, max_sentence_length=30, tags_out='tags', words_out='words', sents_out='all_sents', outfile='devset.csv'):
    files = []
    for d, s, f in os.walk(ccg_directory):
        for file in f:
            if file.endswith("auto"):
                files.append(f"{d}/{file}")

    tags = defaultdict(list)
    words = defaultdict(lambda: defaultdict(int))

    all_sents = []
    for file in tqdm.tqdm(files):
        with open(file) as f:
            for line in f.readlines():
                sentence = parse(line)
                for word, c1, c2 in sentence:
                    if word not in tags[(c1, c2)]:
                        tags[(c1, c2)].append(word) # sets aren't hashable
                    words[word] = defaultdict(int)
                    for word2, c12, c22 in sentence:
                        if word != word2:
                            words[word][word2] += 1
                            words[word2][word] += 1

                if len(sentence) >= min_sentence_length and len(sentence) <= max_sentence_length:
                    all_sents.append(sentence)

    sents = []
    for idx, sent in enumerate(all_sents):
        sents.append([idx, ' '.join(i[0] for i in sent)])

    pickle.dump(dict(tags), open(tags_out, "wb"))
    pickle.dump(dict(words), open(words_out, "wb"))
    pickle.dump(all_sents, open(sents_out, "wb"))

    with open(outfile, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Sentence ID', 'Original Sentence', 'New Sentence'])
        writer.writeheader()

        for x in tqdm.tqdm(sents):
            sent_id, sent = x
            writer.writerow({'Sentence ID': sent_id, 'Original Sentence': sent})

class Replacer:
    def __init__(self, tags='tags', words='words', sents='all_sents'):
        self.tags = pickle.load(open(tags, "rb"))
        self.words = pickle.load(open(words, "rb"))
        self.sents = pickle.load(open(sents, "rb"))

        self.k22a = 0
        for k, v in self.words.items():
            self.k22a += sum(v.values())
        self.k22a //= 2

    def frequency(self, word):
        return sum(self.words[word].values())


    def get_llr(self, w1, w2):
        k11 = self.words[w1][w2]
        k12 = sum(self.words[w1].values()) - k11
        k21 = sum(self.words[w2].values()) - k11
        k22 = self.k22a - k12 - k21 - k11
        return llr_2x2(k11, k12, k21, k22)    

    def get_sentence_llr(self, sent):
        total = 0
        for token1 in sent:
            for token2 in sent:
                total += self.get_llr(token1, token2)
        return total

    def can_replace(self, word, c1, c2):
        if word in ["n't", "'s", "'m", "to", "%"]:
            return False
        if c1 in [r'(S[dcl]\NP)/(S[b]\NP)', 'NP[nb]/N', r'(NP\NP)/NP', 'conj', ',', '.',  r'(S[b]\NP)/(S[adj]\NP)', r'(S[dcl]\NP)/(S[ng]\NP)', r'(NP\NP)/(NP\NP)', r'(S[dcl]\NP)/(S[pss]\NP)']:
            return False
        if c2 in ['$', 'DT', 'IN', 'CC', 'PRP', 'CD', 'MD', 'NNP']:
            return False
        return True

    def get_replacements(self, sent_id):
        sent = self.sents[sent_id]
        repl = []
        for word, c1, c2 in sent:
            if not self.can_replace(word, c1, c2):
                continue
            else:
                w = None
                while not w:
                    w = random.choice(self.tags[(c1, c2)])
                repl.append(w)
        return repl

    def do_replacements(self, sent_id, repls):
        sent = self.sents[sent_id]
        new_sent = []
        i = 0
        for word, c1, c2 in sent:
            if not self.can_replace(word, c1, c2):
                new_sent.append(word)
            else:
                new_sent.append(repls[i])
                i += 1
        return new_sent

    def find_sent(self, sent): # dirty way to rematch sentences since IDs can switch
        k = sent.split()
        for i, j in enumerate(self.sents):
            if ' '.join(k) == ' '.join(w[0] for w in j):
                return i
            
    def replace(self, file, outfile='devset.csv'):
        rows = []
        with open(file) as devset:
            reader = list(csv.DictReader(devset))
            for row in tqdm.tqdm(reader):
                sent_id = self.find_sent(row["Original Sentence"])
                if sent_id is None:
                    continue
                orig = row["Original Sentence"]

                replacement_candidates = [self.get_replacements(sent_id) for _ in range(10)]
                best_candidate = max(replacement_candidates, key=self.get_sentence_llr)
                new_sentence = ' '.join(self.do_replacements(sent_id, best_candidate))
                rows.append({"Sentence ID": sent_id, "Original Sentence": orig, "New Sentence": new_sentence})

        with open(outfile, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['Sentence ID', 'Original Sentence', 'New Sentence'])
            writer.writeheader()

            for row in tqdm.tqdm(rows):
                writer.writerow(row)