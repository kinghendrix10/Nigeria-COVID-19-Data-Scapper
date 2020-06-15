#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import requests
import bs4
import re
import pandas as pd


# In[2]:


# NCDC website for web scraping
web_page = 'https://covid19.ncdc.gov.ng/'

# make request for data from website
res = requests.get(web_page)

# store the retrieved content
html_page = res.content

# create a BeautifulSoup object
soup = bs4.BeautifulSoup(html_page, "html.parser")

# store scraped table contents in a variable
table = soup.find_all(class_="pcoded-content")


# In[3]:


# store contents from various div classes
confirmed_states = soup.find(class_="card-title")

table_header = soup.find_all('thead')

table_body = soup.find('tbody')


# In[4]:


#clean contents from div classes
str_cells = str(table_header)
cleantext = bs4.BeautifulSoup(str_cells, "lxml").get_text()

list_rows = []
for tr in table_body:
    cells = table_body.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, ' ', str_cells))
    list_rows.append(clean2)


# In[5]:


#store cleaned contents in dataframe
df = pd.DataFrame(list_rows)


# In[6]:


#isolate desired data row
df = df.loc[:0, :]


# In[7]:


#remove html tags
df = df.replace(r'\n', ' ', regex=True)
df = df.replace(r'\t', '', regex=True)
df = df.replace(r'\s\s\s', '', regex=True)


# In[8]:


#split the contents into seperate columns and store in new dataframe
df1 = df[0].str.split(',', expand=True)


# In[9]:


df1


# In[10]:


#strip leading and trailing square brackets
df1.loc[0, 0] = df1.loc[0, 0].strip('[')
df1.loc[0, 184] = df1.loc[0, 184].strip(']')


# In[11]:


#split contents into seperate dataframes
df2 = df1[[0, 1, 2, 3, 4, 5, 6, 7]]
df3 = df1[[8, 9, 10, 11, 12, 13]]
df4 = df1[[14, 15, 16, 17, 18, 19]]


# In[12]:


#merge multiline columns data
df2.loc[:, 1] = df2.loc[:, 1].astype(str) + df2.loc[:, 2].astype(str)
df2.loc[:, 3] = df2.loc[:, 3].astype(str) + df2.loc[:, 4].astype(str)
df2.loc[:, 5] = df2.loc[:, 5].astype(str) + df2.loc[:, 6].astype(str)
df3.loc[:, 9] = df3.loc[:, 9].astype(str) + df3.loc[:, 10].astype(str)
df4.loc[:, 15] = df4.loc[:, 15].astype(str) + df4.loc[:, 16].astype(str)


# In[13]:


#drop duplicate columns after merger
df2 = df2.drop(columns=2, axis=1)
df2 = df2.drop(columns=4, axis=1)
df2 = df2.drop(columns=6, axis=1)

df3 = df3.drop(columns=10, axis=1)

df4 = df4.drop(columns=16, axis=1)


# In[14]:


#reset column headers for concatenation
df3.columns = df2.columns
df4.columns = df2.columns

#merger dataframes as rows
data_table = pd.concat([df2, df3, df4], axis=0, ignore_index=True)

#split and remerge data as new rows
for i in range(20, 184, 5):
    table = df1[[i, 1 + i, 2 + i, 3 + i, 4 + i]]
    table.columns = df2.columns
    data_table = pd.concat([data_table, table], axis=0, ignore_index=True)


# In[15]:


#rename column headers
data_table.columns = [
    'States Affected', 'No. of Cases (Lab Confirmed)',
    'No. of Cases (on admission)', 'No. Discharged', 'No. of Deaths'
]


# In[16]:


#view table to confirm data
data_table


# In[17]:


#strip leading and traiing spaces from 'States Affected' columns
data_table['States Affected'] = data_table['States Affected'].str.strip()


# In[18]:


#save table
data_table.to_csv('NCDC 15-6-2020.csv', index=False)
print("Your table was successfully saved!")


# In[19]:


#create date column
data_table['Date'] = '15/6/2020'


# In[20]:


#drop unneeded column
data_table = data_table.drop('No. of Cases (on admission)', axis=1)


# In[21]:


#Reorder and rename column headers
data_table = data_table[[
    'Date', 'States Affected', 'No. of Cases (Lab Confirmed)',
    'No. Discharged', 'No. of Deaths'
]]

data_table.columns = [
    'Date', 'States Affected', 'Total No of Cases', 'Total No Discharged',
    'Total No of Deaths'
]


# In[22]:


#Load total data
total_data = pd.read_csv('Nigeria COVID 19 Data.csv')


# In[23]:


#Update total data with scrapped data
total_data = pd.concat([total_data, data_table], axis=0, ignore_index=True)


# In[24]:


#view total data table to confirm results
total_data


# In[25]:


#save total data
total_data.to_csv('Nigeria COVID 19 Data.csv', index=False)
print("Your table was successfully saved!")

