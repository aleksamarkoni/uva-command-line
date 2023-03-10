import pickle
import time

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.live import Live
from rich.table import Table
import datetime
import timeago

import uva.localdb as localdb
import uva.helpers as helpers

BASE_URL = 'https://onlinejudge.org'
PDF_FILE_URL = BASE_URL + '/external'

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
UHUNT_SUBS_USER_API_URL = UHUNT_BASE_API_URL + '/subs-user'
UHUNT_SUBS_USER_LATEST_API_URL = UHUNT_BASE_API_URL + '/subs-user-last'

NOT_AUTHORIEZED_ERROR_STRING = 'You are not authorised to view this resource'
SUBMISSION_SUCESS_MESSAGE = 'mosmsg=Submission+received+with+ID+'

NOT_LOGGED_IN_MESSAGE = "It's seems that you are not logged in, please login first."


def login(username, password):
    console = Console(log_time=False, log_path=False)
    with console.status("[blue]Logging into uva") as status:
        console.log("Fetching the login form")
        session = requests.Session()
        r = session.get(BASE_URL)
        console.log("Filling out the form")
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

        console.log("Submitting the form")
        # TODO add error checks on this call
        response = session.post(BASE_URL, params=LOGIN_PARAMS, headers=headers, data=form_data)

        res = response.content.decode("utf-8")

        if NOT_AUTHORIEZED_ERROR_STRING in res:
            console.log('You are not authorize')
            return
        elif 'My Account' in res and 'Logout' in res:
            console.log('You are logged in')
        else:
            console.log('There was an error')
            return

        console.log("Saving login token to the local db")
        localdb.save_cookies(pickle.dumps(session.cookies))

        console.log("Getting uva hunt username")
        # TODO add error checking on this call
        p = requests.get(UHUNT_UNAME2UID_API_URL + '/' + username)

        console.log("Saving uva hunt username to local db")
        localdb.save_login_data(username, p.content.decode("utf-8"))
        console.log("[bold green]All done")


def get_latest_subs(count):
    console = Console(log_time=False, log_path=False)
    console.log("[blue]Logging into uva")
    cookie = localdb.read_cookies()
    if cookie is None:
        console.log(NOT_LOGGED_IN_MESSAGE)
        return
    console.log('[blue]Getting latest subs')
    uhunt_uid = localdb.read_uhunt_uid()
    url = f'{UHUNT_SUBS_USER_LATEST_API_URL}/{uhunt_uid}/{count}'
    submissions = requests.get(url)
    data = submissions.json()
    console.log(f"[blue]Submissions for user {data['name']}")
    if len(data["subs"]) != 0:
        table = Table(
            "Submission ID", "Problem ID", "Verdict ID", "Runtime", "Submission Time", "Language", "Rank"
        )

        for sub in reversed(data["subs"]):
            table.add_row(*helpers.generate_submission_table_row(sub))

        console.log(table)
        console.log('[blue]All done')
    else:
        console.log("[blue]No submissions for the current user")


def logout():
    console = Console(log_time=False, log_path=False)
    with console.status("[blue]Logging out from uva") as status:
        localdb.purge()
        console.log("[bold green]All done")


def submit(problem_id, filepath, language):
    console = Console(log_time=False, log_path=False)
    console.status("[blue]Submitting your solution")
    cookie = localdb.read_cookies()
    if cookie is None:
        console.log(NOT_LOGGED_IN_MESSAGE)
        return
    session = requests.session()
    session.cookies.update(pickle.loads(cookie))

    files = {
        'localid': (None, problem_id),
        'language': (None, str(language)),
        'codeupl': (filepath, open(filepath, 'rb')),
    }
    console.log("Uploading solution to Uva")
    response = session.post(BASE_URL, params=SUBMIT_PARAMS, files=files)
    res = response.content.decode("utf-8")

    if NOT_AUTHORIEZED_ERROR_STRING in res:
        console.log(NOT_AUTHORIEZED_ERROR_STRING)
    elif SUBMISSION_SUCESS_MESSAGE in res:
        index = res.find(SUBMISSION_SUCESS_MESSAGE)
        end = res.find('"', index)
        submission_id = res[index + len(SUBMISSION_SUCESS_MESSAGE):end]
        console.log(f"Submission with submission id {submission_id} submitted")
        wait_for_submission_results(submission_id, console)
    else:
        console.log('There was an error')


def wait_for_submission_results(submission_id, console=Console(log_time=False, log_path=False)):
    console.log("[bold green]Waiting for results, to exit ctrl + z")
    uhunt_uid = localdb.read_uhunt_uid()
    sub_id = str(int(submission_id) - 1)

    with Live(console=console, auto_refresh=False) as live:
        while True:
            res = requests.get(f"{UHUNT_SUBS_USER_API_URL}/{uhunt_uid}/{sub_id}")

            table = Table(
                "Submission ID", "Problem ID", "Verdict ID", "Runtime", "Submission Time", "Language", "Rank"
            )

            verdict = None
            # TODO this is not good, for some reason uhunt time is ahead for 15 mins.
            if len(res.json()["subs"]) != 0:
                s = res.json()["subs"][0]

                row_data = helpers.generate_submission_table_row(s)
                verdict = s[2]
                table.add_row(*row_data)
            else:
                table.add_row('?', '?', '?', '?', '?', '?', '?')

            live.update(table, refresh=True)

            if verdict is not None and verdict not in [0, 20]:
                break

            time.sleep(3)
    console.log('[bold green]All done')


def get_pdf_file(problem_id):
    url = f"{PDF_FILE_URL}/{problem_id[0:3]}/{problem_id}.pdf"
    res = requests.get(url)
    with open(f'{problem_id}.pdf', 'wb') as f:
        f.write(res.content)
