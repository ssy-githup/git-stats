# encoding: utf8
import os
import json
import time,datetime
import requests
#import smtplib
import sys, getopt
import csv
import codecs
import pymysql
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email_name_dict import email_name

project_result = {}
#防重处理
all_commits={}

# 参数
params = {
    "mysql": {
        "host": '192.168.87.208',
        "port": 3306,
        "user": 'root',
        "password": '43RmMZzX7yZkpFe',
        "db": 'test_mysql',
        "table": 'commit_stats' 
    },
    "token": '', # token信息
    "base_url": 'http://gitlab2.bitautotech.com/api/v4', #gitlab api访问url前缀， eg. https://gitlab.com/api/v4
    "since_date": '', #统计开始日期， eg. 2019-09-05 00:00:00
    "until_date": '' # 统计终止日期, eg. 2019-09-12 00:00:00
}

def get_data(url):
    headers = {
        "PRIVATE-TOKEN": params['token']
    }

    rs = []

    try:
        r = requests.get(url, headers=headers)

    except Exception as e:
        print(e)

    else:
        rs = r.json()

    return rs


#http://git.opsnow.tech/api/v4/groups/47/issues\?state\=opened
# /projects/:id/issues
def get_issue_by_projectid(project_id):
    url = "%s/projects/%s/issues?per_page=2000" % (params['base_url'], project_id)
    return get_data(url)

# /projects/:id/repository/commits?ref_name=master&since=&until=
def get_commits(project_id, project_name, branch_name, group_name):

    result = []

    page = 1

    commits = get_commits_page(project_id, project_name, branch_name, group_name, page)

    while len(commits) > 0:
        result.extend(commits)
        page = page + 1
        commits = get_commits_page(project_id, project_name, branch_name, group_name, page)

    return result

def get_commits_page(project_id, project_name, branch_name, group_name, page):
    url = "%s/projects/%s/repository/commits?page=%s&per_page=100&ref_name=%s&since=%s&until=%s&with_stats=yes" % (params['base_url'], project_id, page, branch_name, params['since_date'], params['until_date'])
    print(url)
    rs = get_data(url)

    commit_details = []

    for commit in rs:
        commit_id = commit['id']
        if commit_id in all_commits:
            continue
        all_commits[commit_id] = commit
        stats = commit['stats']

        author_name = commit['author_name']
        commiter_email = commit['committer_email']
        if commiter_email in email_name:
            author_name = email_name[commiter_email]
        commit_details.append({
                'commit_id': commit_id,
                'name': commit['committer_name'], 
                'email': commit['committer_email'], 
                'author_name': author_name,
                'group': group_name,
                'project':project_name, 
                'branch': branch_name, 
                'additions': stats['additions'], 
                'deletions': stats['deletions'], 
                'total': stats['total'],
                'commit_count': 1
                })
    return commit_details

# /projects/:id/repository/branches/
def get_branches(project_id):

    page = 1

    result = []

    branches = get_branches_page(project_id, page)

    while len(branches) > 0:
        result.extend(branches)
        page = page + 1
        branches = get_branches_page(project_id, page)

    return result

def get_branches_page(project_id, page):
    url = "%s/projects/%s/repository/branches?page=%s&per_page=100" % (params['base_url'], project_id, page)
    
    rs = get_data(url)

    result = []
    for branch in rs:
        if isinstance(branch,dict):
            branch_name = branch['name']
            result.append(branch_name)

    return result

# /projects
def get_projects():
    url = "%s/projects?per_page=2000" % params['base_url']
    rs = get_data(url)

    projects = []

    namespaces = {}

    count = 0
    for project in rs:
        p = {
            "id": project['id'],
            "name": project['name'],
            "path_with_namespace": project['path_with_namespace'],
            "ssh_url_to_repo": project['ssh_url_to_repo'],
            "http_url_to_repo": project['http_url_to_repo'],
            "namespace": project['namespace']['full_path'],
            "branches": []
        }
        # if p['namespace'].startswith('PD/Private2.0') or p['namespace'].startswith('oc-si') or p['namespace'].startswith('PD/Private'):
            # projects.append(p)
        projects.append(p)
        namespaces[p['namespace']] = {}

    return projects

def write_csv_obj(filename, headers, data_rows):
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(data_rows)

def write_csv_dict(filename, headers, data_dict):
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()

        for k, v in data_dict.items():
            f_csv.writerow(v)
    

def getStas():
    print('starting get git stas .....')
    projects = get_projects()

    # project_headers = ["id",
    #         "name",
    #         "path_with_namespace",
    #         "ssh_url_to_repo",
    #         "http_url_to_repo",
    #         "namespace",
    #         "branches"]
    # write_csv_obj('./projects.csv', project_headers, projects)

    print('1. 获取项目结束， 共有项目数量：', len(projects))

    commits = []

    for p in projects:
        project_id = p['id']
        project_name = p['name']
        branches = get_branches(project_id)
        p['branches'] = branches
        print('2. 获取项目', project_name, '分支结束', '分支数量：', len(branches))
        for b in branches:
            branch_commits = get_commits(project_id, project_name, b, p['namespace'])
            print('3. 获取项目', p['namespace'], '/', project_name, ' 分支：', b, '所有提交结束, len:', len(branch_commits))
            commits += branch_commits
            print('total commits len:', len(commits))

    print('commits len:', len(commits))

    commit_details_headers = ['commit_id','name', 'email', 'author_name','group','project', 'branch', 'additions', 'deletions', 'total','commit_count']
    # 保存提交日志明细到commit_details.csv文件
    print("---- get commits ---------------------------------------------------")
    # print(commits)
    # write_csv_obj('./commit_details.csv', commit_details_headers, commits)

    author_stats = {}

    print('4. 获取所有提交结束，开始进行统计')
    for commit in commits:
        author_name = commit['email']
        if author_name in author_stats:
            author_commit = author_stats[author_name]
            author_commit['additions'] += commit['additions']
            author_commit['deletions'] += commit['deletions']
            author_commit['total'] += commit['total']
            author_commit['commit_count'] += 1
        else:
            author_stats[author_name] = {
                'name': commit['name'], 
                'email': commit['email'], 
                'author_name': commit['author_name'],
                'group': commit['group'],
                'project':commit['project'],
                'additions': commit['additions'],
                'deletions': commit['deletions'],
                'total': commit['total'],
                'commit_count': commit['commit_count']
            }
            # if email_name.get(commit['email']):
            #     author_stats[author_name]['name'] = email_name[commit['email']]
    

    commit_stats_headers = ["group", "project", "email", "name", 'author_name', "additions", "deletions", "total", "commit_count"]
    write_to_mysql(commit_stats_headers, author_stats)
    #write_csv_dict('./commit_stats.csv', commit_stats_headers, author_stats)
    # write_csv_file(author_stats)


def insertDB(cur,sql,args):
    try:
        cur.execute(sql,args)
    except Exception as e:
        print(e)


def write_to_mysql(headers, data_dict):
    print(headers)
    conn = get_mysqlconn()
    cur = conn.cursor()
    
    sqltemplate = 'insert into ' + params['mysql']['table'] + ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    for item in data_dict.values():
        itemDic:dict = item
        values = []
        for ki in range(len(headers)):
            values.append(itemDic[headers[ki]])
        #values.extend(v.values())
        values.append(params['since_date'])
        values.append(params['until_date'])
        insertDB(cur,sqltemplate,values)
        print('写入SQL Item:')
        print(values)

    conn.commit()
    cur.close()
    conn.close()
    print('git commits write to mysql complated!')

def get_mysqlconn():
    db = pymysql.connect(host=params['mysql']['host'],port=params['mysql']['port'],
                        user=params['mysql']['user'],password=params['mysql']['password'],
                        db=params['mysql']['db'],charset="utf8"   )
    return db




def usage():
    msg = "Usage: %s -t <token> -s <since_date> -u <until_date> -a <api_url> [-h] or %s --token <token> --sincedate <since_date> --untildate <until_date> --apiurl <api_url> [--help]" % (sys.argv[0], sys.argv[0])
    print(msg)

# 处理参数
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ht:s:u:a:", ["help", "token=", "sincedate=", "untildate=", "apiurl="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    has_token = 0 # 是否传了token参数
    has_since_date = 0 # 开始时间
    has_until_date = 0 # 结束时间
    for opt, arg in opts:
        if opt in ('h', 'help'):
            usage()
            sys.exit()
        elif opt in ("-t", "--token"):
            params['token'] = arg
            has_token = 1
        elif opt in ("-s", "--sincedate"):
            params['since_date'] = arg
            has_since_date = 1
        elif opt in ("a", "--apiurl"):
            params['base_url'] = arg
        elif opt in ("-u", "--untildate"):
            params['until_date'] = arg
            has_until_date = 1

    if has_token == 0: #or has_since_date == 0 or has_until_date == 0:
        usage()
        sys.exit()


    if params['since_date'] == '' and params['until_date'] =='':
        params['since_date'],params['until_date'] = getStatsTime()

    print(params)
    getStas()
    print('complated & exit')
   
def getYesterday(): 
    yesterday = datetime.date.today() + datetime.timedelta(-1)
    return yesterday

def getStatsTime():
    strDate = getYesterday().strftime("%Y-%m-%d")
    return strDate +' 00:00:00' , strDate + ' 23:59:59'


if __name__ == "__main__":
    main(sys.argv[1:])
