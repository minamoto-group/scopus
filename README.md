# What scopus.py does

I developed this script, scopus.py, to update scopus scores of my 100+ colleagues in the department regularly. The script has several functionalities which include 

1. searching authors by name or author ID
2. adding author(s) information to the list (see below)
3. updating authors' information in the list
4. view the list
5. remove the author(s) from the list

# The list
The list in which authors' scopus scores are contained is located (once it is created at the first run) in the same directory as the script and its name is "authors.xlsx" (hard coded). An example "authors.xlsx" is included in the repository with only my Scopus entry in it. Once you add author(s) to the list, authors.xlsx would contain the following items:

**Item names
1. Given name
2. Surname
3. Position\* (0: Professor; 1: Associate Professor; 2: Lecturer; 3: Assistant Professor; 4: Other)
4. Group\* (0: Thermo-fluids; 1: Material/Process; 2: Mech-Systems; 3: Mech-Frontier; 4: Intelligence-Sys; 5:Other)
5. Group\* (Basic) (0: Thermo-fluids; 1: Material/Process; 2: Mech-Systems; 3: Mech-Frontier; 4: Intelligence-Sys; 5:Other)
6. PhD year\*
7. h-Index
8. #Docs
9. #Cites
10. #Docs/year
11. #Cites/doc
12. #Co-authors
13. #Countries_Coa
14. #Affiliations_Coa
15. author_id\*
16. up_date
17. Comment\*

You may want to enter the author's information for the optional items denoted with "\*" for the first time of adding the author. Values for other items are automatically obtained and computed from Scopus.

The items "Group" and "Group (basic)" are largely related to my affiliation so users should remove or modify for their purpose.

# API key and environment
You can only use this script in the network which are under contract with Scopus. As far as I know, most research universities have eligible subscription for this. In this case, you can run this script in the university network.

Before run the script, you need to obtain API key from https://dev.elsevier.com/. The key is for free. Once you get an API key, run
```
$ python3
Python 3.6.9 (default, Jan 26 2021, 15:33:00)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pybliometrics
>>> pybliometrics.scopus.utils.create_config()
```
and enter your API key to configure. This is required for the first time.

# General usage

Here is how I was usually using this script.

## 1. Search an author
Let say you want to find my scopus scopus score. Perhaps, you do not know my author ID. So you can enter my first and last names, and now you see authors with the matched name. Based on their affiliations, you can see that the first row is me, and my author ID is: 54881747200.
```
$python3 scopus.py s
------------------------------------------------------
Enter Author ID if known (otherwise just press Enter):
Enter first name: Yuki
Enter last name: Minamoto
                  eid   surname initials givenname  ... affiliation_id    city country                            areas
0  9-s2.0-54881747200  Minamoto       Y.      Yuki  ...       60031126   Tokyo   Japan  ENER (58); ENGI (37); CENG (36)
1  9-s2.0-57201667965  Minamoto       Y.      Yuki  ...       60000264  Nagoya   Japan     EART (4); ENVI (2); ENER (1)
[2 rows x 10 columns]
```

## 2. Add an author
One you find an author ID of interest, you can add the author to the list (authors.xlsx). To do so,
```
$ python3 scopus.py a
Enter Author ID: 54881747200
```
You may manually enter values for the optional items with '\*' as mentioned above. 

## 3. Update an author's information
To update the information of an author with the author ID, do something like:
```
$ python3 scopus.py u
Enter Author ID: 54881747200
```
Here, you cannot update the optional items with "\*". To update them, you need to detele the author from the list and then add the author with updated values for the optional items.

## 4. Update for all authors
You can update for all the authors in the list by doing something like:
```
$ python3 scopus.py ua
```

## 5. View the list
You can view the current list by doing:
```
$ python3 scopus.py v
```
You can also sort the displayed list. For example, to sort the list by #citations per document (see item names above):
```
python3 scopus.py v -s '#Cites/doc'
```

## 6. Remove an author from the list
You can also remove an author from the list by doing:
```
$ python3 scopus.py r
Enter Author ID: 54881747200
```

## 7. Collaboration-related info

By adding "-c 1" option when adding and updating, you can add "#collaborated authors" and "#countries of the collaborators". However, this takes longer time to retrieve the information from Scopus.




