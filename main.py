import requests
import operator
from bs4 import BeautifulSoup
from pip._vendor.distlib.compat import raw_input

d = dict()

def get_best(url):
    url = 'http://www.infoarena.ro' + url
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "lxml")
    name = soup.find('span', {'class': 'username'}).find('a')['href'][35:]
    tests = soup.find_all('td', {'class': 'number'})
    max_ms = -1
    for test in tests:
        test = test.string
        if test.endswith('ms'):
            time = int(test.strip('ms'))
            max_ms = max(max_ms, time)
    if name not in d or max_ms < d[name][0]:
        d[name] = (max_ms, url)
    print(max_ms, name, url)

def monitor_spider(pb_name, fw):
    def_url = 'http://www.infoarena.ro/monitor?task=' + pb_name + '&display_entries=250&first_entry='
    first_entry = 0
    max_entries = -1
    accepted_entries = 0
    while True:
        url = def_url + str(first_entry)
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "lxml")
        if max_entries == -1:
            pages = soup.find('span', {'class': 'count'})
            if pages is None:
                print("There is no problem with that name. Please try again.")
                return
            max_entries = 0
            for c in pages.string:
                if c.isdigit():
                    max_entries = max_entries * 10 + int(c)
        if first_entry > max_entries:
            break
        submissions = soup.find_all('a', text='Evaluare completa: 100 puncte')
        for submission in submissions:
            accepted_entries += 1
            get_best(submission.get('href'))
        first_entry += 250

    fw.write('Problem: http://www.infoarena.ro/problema/{}\n'.format(pb_name))
    fw.write('Total submissions: {}\n'.format(max_entries))
    fw.write('Accepted submissions: {}\n'.format(accepted_entries))
    fw.write('Success rate: {0:.2f}%\n\n'.format((accepted_entries / max_entries) * 100))

def optimum():
    pb_name = input("Enter the problem's name: ")
    fw = open(pb_name + '.txt', 'w')
    monitor_spider(pb_name, fw)
    fw.write('Time Leaderboard\n')
    fw.write('-' * 16 + '\n')
    count = 0
    for (name, (time, url)) in sorted(d.items(), key=operator.itemgetter(1)):
        count += 1
        if not time or not url:
            print("Bad: {}".format(url))
            continue
        s = repr(count).ljust(5) + name.ljust(35) + (repr(time) + 'ms').ljust(10) + repr(url).strip('\'').ljust(45) + '\n'
        fw.write(s)
    fw.close()

optimum()
