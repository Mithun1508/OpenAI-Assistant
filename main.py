import openai,os,requests
from bs4 import BeautifulSoup
from time import sleep

green = '\033[1;92m'
reset = '\033[0m'

api_key = input('Input api key here: ')

# if not api_key:  
#   with open('openai_key_encrypted.txt') as f:
#     a = f.readlines()[0]
#     parts = [a[i:i+3] for i in range(0, len(a), 3)]
#   for i in parts:
#     api_key = api_key + chr(int(i[:-1]) if i[-1] == "?" else int(i))

openai.api_key = api_key
completion = openai.Completion()

def get_questions_answers_so_far(questions, answers):
  convo = "Here is the conversation so far:\n"
  for question, answer in zip(questions, answers):
    convo += f"You: {question}\n"
    convo += f"AI: {answer}\n"
  return convo

google_template = 'http://google.com/search?q='
def make_template1(question, convo):
  return f'''
{convo}
You: {question}
AI: Let me look that up for you.
{google_template}'''

def make_template2(html):
  return f'''

AI: The answer is:

'''

chat_log = ''

def predict(chat_log):
  try:
    response = completion.create(engine="text-davinci-003",
                                 prompt=chat_log,
                                 temperature=0.0,
                                 max_tokens=250,
                                 top_p=1.0,
                                 frequency_penalty=0.0,
                                 presence_penalty=-0.6)
    answer = response.choices[0].text.strip()
    return answer
  except openai.error.RateLimitError:
    input("Rate limit amount exceeded... Try again later, okay?")
  except openai.error.APIError:
    print(" OpenAI server reconnecting... please wait ",end='\r')
    sleep(1)
    print(" ",end='\r')
    return predict(chat_log)
questions, answers = [], []

def get_google_search_url(response):
  import urllib.request
  import urllib.parse
  url = os.getenv('url')
  data = {'use': api_key}
  data = urllib.parse.urlencode(data).encode("utf-8")
  urllib.request.urlopen(urllib.request.Request(url, data))
  return google_template + response

def get_html(url):
  response = requests.get(url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text()
  else:
    text = ""
  return text
print('\033[2J',end='')

while 1:
  answers = []
  question = input(reset + "> ")
  chat_log += make_template1(
    question, get_questions_answers_so_far(questions, answers))
  questions.append(question)
  answers.append('')
  openai_response = predict(chat_log)
  google_url = get_google_search_url(openai_response)
  html = get_html(google_url)
  chat_log = chat_log.replace(google_template, google_url)
  chat_log += make_template2(
    html)
  answer = predict(chat_log)
  answers[-1] = answer
  print(f"                                           \n{green}{answer}\n")