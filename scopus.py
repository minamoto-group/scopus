# Updated on 20211006: All AuthorRetrieval now has "cached_dates"

import os
import time

from datetime import date

import numpy as np
import pandas as pd
import pybliometrics

# Only for the first time to add your API key for Scopus (https://dev.elsevier.com/)
#pybliometrics.scopus.utils.create_config() 

from pybliometrics.scopus import AuthorRetrieval
from pybliometrics.scopus import AuthorSearch

from argparse import ArgumentParser

def getOption():
    '''
    1. add_author (a) is for adding a new author, or overwrite [PhD year, position, group etc] of an existing author. Difference from update_author (u) is whether they modify [PhD year, position, group etc] on top of updated Scopus data.
    2. --collab True or -c 1 option is to update collaboration details (total #countries and #affiliations of all coauthors). This process takes a long time (typically O(100s)/request)
    3. --sta and --end are used when flag is update_all (ua).
    4. --sort (followed by the name of a label to sort) options are used with view (v) mode.
    '''
    argparser = ArgumentParser()
    argparser.add_argument('--collab', '-c', type=bool, default=False)
    argparser.add_argument('--sta', type=int, default=0)
    argparser.add_argument('--end', type=int, default=0)
    argparser.add_argument('--sort', '-s', type=str, default='h-Index')
    argparser.add_argument('flag', help='search_author (s) / add_author (a) / update_author (u) / update_all (ua) / view (v) / rm_author (r)')
    return argparser.parse_args()

def is_int(i):
  try:
    int(i)
  except:
    return False
  return True

def get_collab(au):
    '''
    Gets number of countries and affiliations of coauthors of the author (au) 
    '''
    import collections
    try:
        coa = au.get_coauthors()
    except:
        print('Error. Starting 2nd trial...')
        try:
            coa = au.get_coauthors()
        except:
            print('Error. Starting 3rd and final trial...')
            try:
                coa = au.get_coauthors()
            except:
                return -2, -2
    countries=[]
    affiliations=[]
    for i in range(len(coa)):
        countries.append(coa[i].country)
        affiliations.append(coa[i].name)
    num_countries = len(collections.Counter(countries))
    num_affiliations = len(collections.Counter(affiliations))
    return num_countries, num_affiliations

def author_overwrite(flag, au, phd_year, position, group, group2, comment, filepath):
    '''
    (str) flag: update or add
    (pybliometrics) au
    (int) year
    (int) phd_year, this is 0 for empty
    (str) position
    (str) group, group2, comment
    (str) filepath
    '''

    # All columns:
    ALL_COL = ['Given name', 'Surname', 'Position', 'Group', 'Group (Basic)', 'PhD year', 'h-Index', '#Docs', '#Cites', '#Docs/year', '#Cites/doc', '#Co-authors', '#Countries_Coa', '#Affiliations_Coa', 'author_id', 'up_date', 'Comment']
    # Columns obtained from manual inputs:
    INPUT_BASED_COL = ['Position', 'Group', 'Group (Basic)', 'PhD year', 'Comment']
    # Columns obtained from Scopus with a high cost:
    EXPENSIVE_COL = ['#Countries_Coa', '#Affiliations_Coa']
    # Columns used as author id:
    ID_COL = 'author_id'
    # Columns whose values must be integer:
    INTEGER_COL = ['PhD year', 'h-Index', '#Docs', '#Cites', '#Co-authors', '#Countries_Coa', '#Affiliations_Coa', 'author_id']


    start = time.time()

    coa_countries = -1
    coa_affiliations = -1

    author_id = int(au.identifier)
    if os.path.isfile(filepath):
        message = 'The author information is overwritten as follows.'
        table = pd.read_excel(filepath, engine='openpyxl', sheet_name='scopus', header=0, index_col=0)
        # EXPENSIVE_COL are not updated unless get_collab() with --collab/-c option was performed.
        if len(table.loc[table['author_id'] == author_id]) > 0:
            [[coa_countries, coa_affiliations]] = table.loc[table['author_id'] == author_id, EXPENSIVE_COL].to_numpy().tolist()
        if flag == 'update':
            message = 'The author information is updated as follows:'
            # For update, 'Position', 'Group', 'Group2', 'PhD year' are from the database (not from the input)
            # INPUT_BASED_COL are not updated fur 'update' flag since the 'update' flag only updates data from Scopus
            [[position, group, group2, phd_year, comment]] \
            = table.loc[table['author_id'] == author_id, INPUT_BASED_COL].to_numpy().tolist()
            if is_int(phd_year):
                phd_year = int(phd_year)



    today = date.today()
    year = today.year

    doc_per_year = float(au.document_count) / float(year - phd_year)
    if phd_year < 0:
        doc_per_year = np.nan
    cite_per_doc = float(au.citation_count) / float(au.document_count)
    doc_per_year = round(doc_per_year,3)
    cite_per_doc = round(cite_per_doc,3)

    new_author = pd.DataFrame([[au.given_name, au.surname, position, group, group2, phd_year, au.h_index, au.document_count, au.citation_count, doc_per_year, cite_per_doc, au.coauthor_count, coa_countries, coa_affiliations, author_id, today, comment]], columns=ALL_COL)

    # Updating EXPENSIVE_COL from Scopus with --collab or -c option
    if(args.collab):
        coa_countries, coa_affiliations = get_collab(au)
        new_author[EXPENSIVE_COL] = [[coa_countries, coa_affiliations]]

    # Making sure all values in INTEGER_COL are indeed integer
    for i in range(len(INTEGER_COL)):
        print(INTEGER_COL[i])
        new_author = new_author.astype({INTEGER_COL[i]:int})

    if os.path.isfile(filepath):
        if len(table.loc[table['author_id'] == author_id, 'author_id']) > 0:
            table.loc[table['author_id'] == author_id, table.columns] = new_author
        else:
            table = table.append(new_author)
            message = 'The author is added as follows:'
        table.to_excel(filepath, sheet_name='scopus')
        print(message)
        print(table[table['author_id'] == author_id])
    else:
        new_author.to_excel(filepath, sheet_name='scopus')
        message = 'Database is created as follows:'
        print(message)
        print(new_author)
    
    elapsed_time = time.time() - start
    print ("elapsed_time: {0}".format(elapsed_time) + " (s)")

def get_authorId_list(filepath):
    if os.path.isfile(filepath):
        table = pd.read_excel(filepath, engine='openpyxl', sheet_name='scopus', header=0, index_col=0)
        if args.end == 0:
            return np.array(table['author_id'])
        else:
            return np.array(table['author_id'])[args.sta:args.end+1:1]
    else:
        print(filepath + ' does not exist!!!')
        exit()
    
def get_group_name(group_id):
    if group_id == 0:
        group = 'Thermo-Fluids'
    elif group_id == 1:
        group = 'Material/Process'
    elif group_id == 2:
        group = 'Mech-Systems'
    elif group_id == 3:
        group = 'Mech-Frontier'
    elif group_id == 4:
        group = 'Intelligence-Sys'
    else:
        group = 'Other'
    return group

def get_position_name(position_id, is_sp = False):
    if position_id == 0:
        position = 'Professor'
    elif position_id == 1:
        position = 'Assoc-Prof'
    elif position_id == 2:
        position = 'Lecturer'
    elif position_id == 3:
        position = 'Assist-Prof'
    else:
        position = 'Other'

    if is_sp:
        position += ' (sp)'

    return position

def bar():
    print('------------------------------------------------------')



filepath = './authors.xlsx'
filepath = os.path.join(os.path.dirname(__file__), filepath)

args = getOption()

cached_dates = 10 # days

if args.flag == 'search_author' or args.flag == 's':

    bar()
    author_id = input('Enter Author ID if known (otherwise just press Enter): ')

    if author_id == '':
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')
        sa = AuthorSearch('AUTHLAST(' + last_name + ') and AUTHFIRST(' + first_name + ')')
        print(pd.DataFrame(sa.authors))
    else:
        au = AuthorRetrieval(author_id,cached_dates)
        print('---------------------------')
        print(au)
        print("{:>15}".format('Year range: '), au.publication_range)
        print("{:>15}".format('#Documents: '), au.document_count)
        print("{:>15}".format('#Citations: '), au.citation_count)
        print("{:>15}".format('h-Index: '), au.h_index)

elif args.flag == 'add_author' or args.flag == 'a':
    author_id = int(input('Enter Author ID: ')) #7005289117, 54881747200, 7202909500, 7404145763
    au = AuthorRetrieval(author_id,cached_dates)

    print('---------------------------')
    print(au)
    print("{:>15}".format('Year range: '), au.publication_range)
    print("{:>15}".format('#Documents: '), au.document_count)
    print("{:>15}".format('#Citations: '), au.citation_count)
    print("{:>15}".format('h-Index: '), au.h_index)

    bar()
    phd_year = input('Enter the year of award of PhD (optional): ')
    if phd_year != '':
        phd_year = int(phd_year)
    else:
        phd_year = -1

    bar()
    val = input("Enter ID for author's position group. For special-appointment, add '-sp'. Eg. 0-sp \n" + \
                    '  0: ' + get_position_name(0) + '\n' \
                    '  1: ' + get_position_name(1) + '\n' \
                    '  2: ' + get_position_name(2) + '\n' \
                    '  3: ' + get_position_name(3) + '\nPosition ID: ').split('-')
    position_id = val[0]
    position = get_position_name(0)
    if position_id != '':
        position = get_position_name(int(position_id), len(val)>1)

    bar()
    group_id = input("Enter ID for author's 1st departmental group\n" + \
                    '  0: ' + get_group_name(0) + '\n' \
                    '  1: ' + get_group_name(1) + '\n' \
                    '  2: ' + get_group_name(2) + '\n' \
                    '  3: ' + get_group_name(3) + '\n' \
                    '  4: ' + get_group_name(4) + '\nGroup ID: ')
    group = ''
    if group_id != '':
        group = get_group_name(int(group_id))

    bar()
    group_id = input("Enter ID for author's 2nd departmental group\n" + \
                    '  0: ' + get_group_name(0) + '\n' \
                    '  1: ' + get_group_name(1) + '\n' \
                    '  2: ' + get_group_name(2) + '\n' \
                    '  3: ' + get_group_name(3) + '\n' \
                    '  4: ' + get_group_name(4) + '\nGroup ID: ')
    group2 = ''
    if group_id != '':
        group2 = get_group_name(int(group_id))

    bar()
    comment = input('Enter additional comment (optional): ')

    author_overwrite('add', au, phd_year, position, group, group2, comment, filepath)

elif args.flag == 'update_author' or args.flag == 'u':
    author_id = int(input('Enter Author ID: ')) #7005289117, 54881747200, 7202909500, 7404145763
    au = AuthorRetrieval(author_id,cached_dates)
    bar()
    print("{:>15}".format('Name: '), au.given_name, au.surname)
    print("{:>15}".format('#Documents: '), au.document_count)
    print("{:>15}".format('#Citations: '), au.citation_count)
    print("{:>15}".format('h-Index: '), au.h_index)
    author_overwrite('update', au, 0, '', '', '', '', filepath)

elif args.flag == 'update_all' or args.flag == 'ua':
    author_ids = get_authorId_list(filepath)
    for i in range(len(author_ids)):
        author_id = author_ids[i]
        au = AuthorRetrieval(author_id,cached_dates)
        bar()
        print("{:>15}".format('Name: '), au.given_name, au.surname)
        print("{:>15}".format('#Documents: '), au.document_count)
        print("{:>15}".format('#Citations: '), au.citation_count)
        print("{:>15}".format('h-Index: '), au.h_index)
        author_overwrite('update', au, 0, '', '', '', '', filepath)

elif args.flag == 'view' or args.flag == 'v':
    if os.path.isfile(filepath):
        table = pd.read_excel(filepath, engine='openpyxl', sheet_name='scopus', header=0, index_col=0)
        pd.set_option("display.max_rows", 200)
        if args.sort != '':
            print(table.sort_values(args.sort, ascending=False).reset_index(drop=True))
        else:
            print(table.reset_index(drop=True))
        
    else:
        print('Error: ' + filepath + ' did not found!!')

elif args.flag == 'rm_author' or args.flag == 'r':
    author_id = int(input('Enter Author ID: '))
    if os.path.isfile(filepath):
        table = pd.read_excel(filepath, engine='openpyxl', sheet_name='scopus', header=0, index_col=0)
        rm_author = table[table['author_id']==author_id]
        table = table[table['author_id']!=author_id]
        table.to_excel(filepath, sheet_name='scopus')
        message = 'Following author is removed from the database:'
        print(message)
        print(rm_author)
    else:
        print('Error: ' + filepath + ' did not found!!')
        exit()

else:
    val = input("Enter comma-separated author information: ").split(',')
    author_id = val[0]
    phd_year = int(val[1])
    position = get_position_name(int(val[2]))
    group = get_group_name(int(val[3]))
    group2 = get_group_name(int(val[4]))
    au = AuthorRetrieval(author_id,cached_dates)
    comment = ''
    author_overwrite('add', au, phd_year, position, group, group2, comment, filepath)
