import spacy
import csv
import collections
import tqdm

nlp = spacy.load("en_core_web_lg")

def parse(file, output_format='devset_spacy'):
    all_uuas = []
    matches = collections.defaultdict(lambda: [0, 0])

    writer_100 = csv.DictWriter(open(f"{output_format}_100.csv", "w"), fieldnames=['Sentence ID', 'Original Sentence', 'New Sentence'])
    writer_100.writeheader()

    writer_95 = csv.DictWriter(open(f"{output_format}_95.csv", "w"), fieldnames=['Sentence ID', 'Original Sentence', 'New Sentence'])
    writer_95.writeheader()

    writer_l90 = csv.DictWriter(open(f"{output_format}_l90.csv", "w"), fieldnames=['Sentence ID', 'Original Sentence', 'New Sentence'])
    writer_l90.writeheader()

    with open(file) as csvfile:
        reader = list(csv.DictReader(csvfile))
        for row in tqdm.tqdm(reader):
            orig = row['Original Sentence']
            new = row['New Sentence']
            
            doc1 = nlp(orig)
            doc2 = nlp(new)


            a = [i.head.i for i in doc1[:-1]]
            b = [i.head.i for i in doc2[:-1]]
            if len(a) != len(b):
                continue

            
            uuas = sum(1 for i in range(len(a)) if a[i] == b[i]) / len(a)

            for idx, (i, j) in enumerate(zip(doc1[:-1], doc2[:-1])):
                if a[idx] == b[idx] and i.dep_ == j.dep_:
                    matches[i.dep_][0] += 1
                matches[i.dep_][1] += 1

            if uuas == 1:
                writer_100.writerow(row)
            elif 0.9 <= uuas and uuas < 1:
                writer_95.writerow(row)
            if uuas < 0.9:
                writer_l90.writerow(row)

            all_uuas.append(uuas)
