import pickle
import requests

if __name__ == '__main__':

    session = requests.session()

    payload = {
        'username': 'aleksamarkoni',
        'passwd': 'nikokaoona'
    }

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB;q=0.6,sr;q=0.5",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    session.post('https://onlinejudge.org/index.php?option=com_comprofiler&task=login', headers=headers, data=payload)

    with open('somefile.txt', 'wb') as f:
        pickle.dump(session.cookies, f)

        #"body": "op2=login&lang=english&force_session=1&return=B%3AaHR0cDovL29ubGluZWp1ZGdlLm9yZy9pbmRleC5waHA%2Fb3B0aW9uPWNvbV9sb2dpbiZhbXA7SXRlbWlkPTU%3D&message=0&loginfrom=loginmodule&cbsecuritym3=cbm_6a2c8d6b_5850cb94_dc5e55affe8ebaf534b597e0fe5a889c&j934fbf38ee3cab473f6cd4a8b59b2a3e=1&Submit=Login",

    session1 = requests.session()
    # with open('somefile.txt', 'rb') as f:
    #     session1.cookies.update(pickle.load(f))

    p = session1.get('https://uhunt.onlinejudge.org/api/uname2uid/aleksamarkoni')
    print(p.status_code)
    print(p.content)
    print(p)

    g = session1.get('https://uhunt.onlinejudge.org/api/subs-user-last/88772/10')
    print(g.status_code)
    print(g.content)
