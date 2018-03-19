from pandas import DataFrame
import numpy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import mailbox

def getEmails(mboxPath):
	myMailBox = mailbox.mbox(mboxPath)

	for mail in myMailBox:
		subject = mail['subject']

		body = " "

		try:
			if mail.is_multipart:
				for part in mail.walk():
					contentType = part.get_content_type()
					contentDisposition = str(part.get('Content-Disposition'))
					if contentType == 'text/plain' and 'attachment' not in contentDisposition:
						body = part.get_payload(decode=True)
			else:
				body = mail.get_payload(decode=True)
		except:
			pass

		yield [subject,body]

def storeEmail(emailNo,subject,body,probabilityUseful,probabilityUseless,openedFile):
	openedFile.write("*****\n")

	openedFile.write("No: ")
	openedFile.write(emailNo)
	openedFile.write("\n")
	openedFile.write("PROBABILITY USEFUL: \n")
	openedFile.write(probabilityUseful)
	openedFile.write("\n")
	openedFile.write("PROBABILITY USELESS: \n")
	openedFile.write(probabilityUseless)
	openedFile.write("\n")
	openedFile.write("SUBJECT:\n")
	openedFile.write(subject)
	openedFile.write("\n")
	openedFile.write("BODY:\n")
	for line in (str(body)).split("\\r\\n"):
		openedFile.write(line)
		openedFile.write("\n")

	openedFile.write("*****")


def buildDataFrame(subject,body,classification):
 	rows = [{"mail":body, "class":classification}]
 	index = [subject]
 	data_frame = DataFrame(rows,index=index)
    
 	return data_frame

data = DataFrame({'text': [], 'class': []})

f = open("trainer2",'r')
trainer = f.read().split("*****")

for mail in trainer:
	subject = mail.split("subject:")[1].split("body:")[0][:-2]
	body = mail.split("body:")[1].split("classification:")[0][:-2]
	classification = mail.split("classification:")[1][2:-3]

	data = data.append(buildDataFrame(subject,body,classification))

f.close()

count_vectorizer = CountVectorizer()
counts = count_vectorizer.fit_transform(data["mail"].values)

classifier = MultinomialNB()
targets = data['class'].values
classifier.fit(counts, targets)

print("Classifier Trained!")

mboxPath = input("Enter mbox path: ")
fileName = input("Enter results file name: ")

myMailGenerator = getEmails(mboxPath)

results = open(fileName,"w")


i = 1
j = 1
for subject,body in myMailGenerator:
	try:
		print("Current Mail: {0} : {1}".format(i,subject))
		i += 1

		if(classifier.predict(count_vectorizer.transform([body])) == ['useful']):		
			probabilityUseful = str(classifier.predict_proba(count_vectorizer.transform([body]))[0][0])
			probabilityUseless = str(classifier.predict_proba(count_vectorizer.transform([body]))[0][1])
			storeEmail(str(j),subject,body,probabilityUseful,probabilityUseless,results)
			j += 1
		
			
	except Exception as e:
		print(str(e))
		pass


results.close()

