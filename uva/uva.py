import pickle
import requests
from bs4 import BeautifulSoup

import localdb

BASE_URL = 'https://onlinejudge.org/index.php'

LOGIN_PARAMS = {
    'option': 'com_comprofiler',
    'task': 'login',
}

SUBMIT_PARAMS = {
    'option': 'com_onlinejudge',
    'Itemid': 8,
    'page': 'save_submission'
}

UHUNT_BASE_API_URL = 'https://uhunt.onlinejudge.org/api'
UHUNT_UNAME2UID_API_URL = UHUNT_BASE_API_URL + '/uname2uid'
UHUNT_SUBS_USER_LATEST_API_URL = UHUNT_BASE_API_URL + '/subs-user-last'

NOT_AUTHORIEZED_ERROR_STRING = 'You are not authorised to view this resource'
SUBMISSION_SUCESS_MESSAGE = 'mosmsg=Submission+received+with+ID+'


def login(username, password):
    session = requests.Session()
    r = session.get(BASE_URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    form = soup.find('form', id='mod_loginform')
    inputs = form.find_all('input', type='hidden')

    form_data = {
        'username': username,
        'passwd': password,
        'remember': 'yes'
    }
    for tag in inputs:
        form_data[tag['name']] = tag['value']

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # TODO add error checks on this call
    response = session.post(BASE_URL, params=LOGIN_PARAMS, headers=headers, data=form_data)

    res = response.content.decode("utf-8")

    if NOT_AUTHORIEZED_ERROR_STRING in res:
        print('You are not authorize')
    elif 'My Account' in res and 'Logout' in res:
        print('You are logged in')
    else:
        print('There was an error')

    localdb.save_cookies(pickle.dumps(session.cookies))

    # TODO add error checking on this call
    p = requests.get(UHUNT_UNAME2UID_API_URL + '/' + username)

    localdb.save_login_data(username, p.content.decode("utf-8"))


def get_latest_subs(count):
    uhunt_uid = localdb.read_uhunt_uid()
    url = f'{UHUNT_SUBS_USER_LATEST_API_URL}/{uhunt_uid}/{count}'
    # TODO add error checks for this call
    submissions = requests.get(url)
    return submissions.content.decode("utf-8")


def logout():
    localdb.purge()


def submit(problem_id, filepath, language):
    cookies = localdb.read_cookies()
    session = requests.session()
    session.cookies.update(pickle.loads(cookies))

    files = {
        'localid': (None, problem_id),
        'language': (None, language),
        'codeupl': (filepath, open(filepath, 'rb')),
    }

    response = session.post(BASE_URL, params=SUBMIT_PARAMS, files=files)
    res = response.content.decode("utf-8")

    if NOT_AUTHORIEZED_ERROR_STRING in res:
        print('You are not authorize')
    elif SUBMISSION_SUCESS_MESSAGE in res:
        index = res.find(SUBMISSION_SUCESS_MESSAGE)
        end = res.find('"', index)
        submission_id = res[index + len(SUBMISSION_SUCESS_MESSAGE):end]
        print(submission_id)
        #TODO call this endpoint to fetch the submission status and see if everything is good
        #https://uhunt.onlinejudge.org/api/subs-user/88772/28133692

    else:
        print('There was an error')
