#!/usr/bin/env python
# coding: utf-8

# # INFO 2950 Discussion Week 3
# 
# For our group time on Friday we will be going through a tutorial on web scraping together.
# 
# **Make sure to complete and save this notebook before next Friday's section!** We will use the completed version for an activity on pushing to GitHub next week.
# 
# 
# 

# ## What is web scraping?
# 
# Web scraping is the process of creating structured data frames readable by computers from less-structured web pages that are intended to be read by humans.
# 
# ## Do you need to scrape?
# 
# Scraping is difficult, error-prone, and may get you in legal or ethical trouble. Always check if the information you are seeking already exists in a nicer format. Many companies also have APIs or other infrastructure dedicated to serving automated requests.
# 
# ## Ethics of scraping
# 
# Scraping is the aspect of data science most likely to get you into trouble. Legally, there are two main concerns: copyright violation if you are making copies of content that is protected by copyright, and terms-of-service violation. Many sites will also attempt to block scrapers. Acting to avoid these blocks may constitute hacking.
# 
# In addition to legal problems, there are ethical problems.
# 
# * Respect other people's hard work. Collecting information for a cool website is difficult and takes a long time and careful preparation. Is it fair to take all that work and use it for your purposes?
# * Respect other people's businesses. People feed their families by collecting and sharing information, for example through ad revenue. They may be unhappy if they think you are trying to steal their work and prevent them from monetizing it. Websites also sometimes pay for bandwidth and cloud services, and you don't want to take up all their resources for purposes that provide no revenue.
# * Respect other people's audiences. Don't [DDOS](https://en.wikipedia.org/wiki/Denial-of-service_attack) a website! Keep requests spaced to about 2/second at most. Web hits don't take a lot of resources, but it's easy to flood a site with requests, locking others out.
# 
# ## Process
# 
# Find a page that contains the info you want. Some older pages are static, but most of what you will see today are views of databases. For example, Amazon has a database of products, Letterboxd has a database of movies, and Netflix has a database of shows. Each page either lists entities in the database or gives information about specific entities.
# 
# You would prefer to get access directly to the database, and in some cases you can. But for whatever reason sometimes the web page is all you can get. This process can be difficult because web pages are optimized for people to look at, not for computers to operate on. But it is simpler because in this case a computer has to generate a page *from* a database record and a web browser has to know how to display the elements on the page so that humans can read them. These constraints mean that there are regularities in how specific pieces of information are shown in  HTML, and if you can figure them out, you can reverse the page generation process and get back to something that looks more like a database.
# 
# How do you know which pages to get? Often an index or search result page leads to individual pages with more detailed information.
# 
# 
# ### Web scraping in Python
# 
# The [`requests`](https://requests.readthedocs.io/en/latest/) library allows you to download files from the web. It is much easier to use than `urllib`. You can use the `requests` library to get information from web pages so that you can save them to files or analyze their data in python.
# 
# After using `requests` to access web data, you'll use [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to parse that information, organized in HTML. `BeautifulSoup` makes querying a tree of tags and their attributes much easier than trying to parse HTML from scratch. You'll need to spend some time looking at the target web page and finding the combination of tag names and classes you're interested in, but `BeautifulSoup` can help access that information once you know what you need.
# 
# 
# 
# ## Installation
# As usual, to use these new modules you'll need to first **install `BeautifulSoup` and `requests` to your virtual environment for this class**. Only once you've completed that process can successfully you run the next cell of code to load in `requests`, `BeautifulSoup`, and other modules.
# 
# 
# 
# 

# In[2]:


import requests
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import time



# ## In-session Example: Cornell University Website
# 
# The TA will show you [this page about Cornell University](https://www.cornell.edu/about/). This webpage has information about Cornell, including general statistics about number of students, different campus locations, and many links to other Cornell pages.
# 
# ## Viewing HTML
# Take a look at the HTML of the page. You can view this in a couple of different ways:
# 
# *   Right click > "View Page Source"
# *   Right click > "Inspect"
# 
# **What differences do you notice between the two HTML views?**
# 
# 

# Today, our goal is to collect and organize various stats about Cornell.
# 
# We need to put together clues from the structure of the page and the appearance of elements on the page. Appearance is usually determined by the CSS `style` property. Figuring out how to automatically find values from HTML will involve looking at HTML source, ^F searching for values that you want, and figuring out how to identify styles or containing elements. Modern web pages are long and have lots of complicated elements, many of which do not appear as visible content. Starting from the top of the document and reading through is not recommended.
# 
# You will scrape information from cached copies of "About Cornell" pages. These are locally hosted so we don't have hundreds of students hitting Cornell's website at the same time. They probably wouldn't notice, but it's more responsible to keep it local.
# 

# In[18]:


cornell_url = "https://koenecke.infosci.cornell.edu/files/info2950/About%20Cornell%20University.html"


# The following code does a `GET` request to the web host for the specified filename. HTTP is the protocol used to make web requests. It has a series of "status codes" that tell you the result of request. 200 is success. Others you have probably seen: 404 is "page not found", 403 is "you do not have access". Codes starting with 3-- are often redirects. 500 means there is a bug in the server-side code.

# In[19]:


cornell_result = requests.get(cornell_url)
if cornell_result.status_code != 200:
  print("something went wrong:", cornell_result.status_code, cornell_result.reason)


# You're never going to get the analysis of a web page right the first time, so it's good to save a local copy of the HTML source so we don't need to hit the server again.

# In[20]:


with open("cornell_about.html", "w", encoding="utf-8") as writer:
  writer.write(cornell_result.text)


# Here we're immediately reading the file again, but you could split these into two separate notebooks, one for downloading, one for analysis.

# In[21]:


with open("cornell_about.html", "r") as reader:
  html_source = reader.read()


# There are a lot of things that can go wrong when you are accessing web documents. Get in the habit of constantly adding confidence checks to make sure the state of variables is what you expect it to be.

# In[15]:


# Make sure this worked
html_source[:20]


# Here's where we turn the HTML text from a single long string into a searchable tree of tags. `BeautifulSoup` can support different ways of parsing (including XML). Here we'll use an HTML parser.

# In[16]:


page = BeautifulSoup(html_source, "html.parser")


# Now that we have a structured document we can ask for specific tags. See the Beautiful Soup documentation linked at the top for more details.

# In[17]:


page.title


# If you want just the text between the HTML tags, you can use `.text`.

# In[18]:


page.title.text


# We can also find all of the instances of a given tag. Since this "About Cornell" page seems like more of a landing page, pointing to other resources, we want to use the links on this page to get us to that other linked information. What happens if we ask for all the `a` tags, which [defines a hyperlink](https://www.w3schools.com/tags/tag_a.asp)?

# In[19]:


links = page.find_all("a")
print("there are", len(links), "links on the page")
links[:20]


# Whoa, that's too much! And most of these links seem to be navigation links in header menus.
# 
# Let's be more specific. Viewing the source, we can search for an interesting string (like "Facts about Cornell") and look at the HTML around it.
# 
# Inspecting the HTML we find that `a` tags can be associated with a number of class styles. The class style for "Facts about Cornell" is `link-caret`. Here's how to find all of the `a` tags with this style:

# In[20]:


link_carets = page.find_all("a", {"class":"link-caret"})
print(link_carets)


# Once we find a tag, we can also access attributes of the tag, like the URL target of a link (`href`) or the text contained within the tag (`.text`).

# In[21]:


for link in link_carets:
  print(link.text, link["href"])


# ## Organizing structured data
# Now, we want to collect different stats and facts about Cornell, so the table on the right side with "Quick Facts" seems like a great place to start. **Our goal is to recreate the "Quick Facts" table as a pandas dataframe.**
# 
# Remember, instead of reading the HTML from start to bottom, use ^F to search for the text "Undergraduate Students" (for example).
# 
# While there are different ways of collecting this tag, you really want to keep the name of the fact and its value together. For this reason, let's collect the list element as a singular unit (with tag `li` and the `stat` class style).

# In[22]:


cornell_stats = page.find_all("li", {"class": "stat"})
print(len(cornell_stats))


# Now that we have a list of every `li` (list item) with the `stat` class, we can extract the values of the list. Let's start with the first item in this new list:

# In[23]:


print(cornell_stats[0].find("div", {"class": "stat-label"}).text)
print(cornell_stats[0].find("div", {"class": "stat-value"}).text)


# What's with all that whitespace? You can strip the extra whitespace with `.strip()`.

# In[24]:


print(cornell_stats[0].find("div", {"class": "stat-label"}).text.strip())
print(cornell_stats[0].find("div", {"class": "stat-value"}).text.strip())


# Much better! Now, we can use a loop to extract the label and value from each list item.

# In[25]:


for html_stat in cornell_stats:
  print(html_stat.find("div", {"class": "stat-label"}).text.strip())
  print(html_stat.find("div", {"class": "stat-value"}).text.strip())


# In reality, you probably don't just want to print these items. You want to store them! Let's use **list comprehension** to create two lists, `labels_l` and `value_l`.

# In[27]:


label_l = [stat.find("div", {"class": "stat-label"}).text.strip() for stat in cornell_stats]
value_l = [stat.find("div", {"class": "stat-value"}).text.strip() for stat in cornell_stats]


# Now, we can store this as a dataframe.

# In[28]:


data = {'Label':label_l, 'Stat':value_l}
cornell_df = pd.DataFrame(data)


# In[29]:


cornell_df


# **Is there any other data cleaning you'd do to this dataframe if you wanted to use it for data science?**

# ## Collecting text
# Often, when you're scraping a website you aren't just collecting headers and tables. You're also collecting text! Now, you're going to collect the text below "Our Profile." Use ^F to find the first sentence in the HTML.
# 
# You should find that the text is in a `p` tag below a `div` tag. **What class would you use to extract this `div` tag?**

# In[ ]:


about_profile = page.find("div", {"class":""}) # THIS CELL WILL NOT EXECUTE UNTIL YOU FILL IN THE CLASS
print(about_profile)


# Before moving on, **do you notice anything odd about the above HTML?**

# Now, if we want to extract the natural text from the `about_profile` variable, we can use the `p` tag.

# In[ ]:


print(about_profile.find('p').text)


# ---
# # Problem 2: Recreating the timeline as a table
# 
# Earlier, you found links to fact pages about Cornell (stored in `link_carets`). One of those links was to a Cornell Timeline (https://www.cornell.edu/about/timeline/). Take some time to inspect the HTML of the page, and then load the cached version with the link below, create a `BeautifulSoup` object, and find some information about Cornell.
# 
# Notice the table of data **Cornell Through the Years** with information about Cornell's history. It looks like each event includes three types of information:
# 
# 1.   Event year
# 2.   Event title
# 3.   Event summary
# 
# Use `BeautifulSoup` and `requests` to scrape this data and format it as a data frame with one column for the year, another for the title, and a third for the summary.

# 1. Use the requests library to `get` the website's HTML. Check the status code.

# In[5]:


timeline_url = "https://koenecke.infosci.cornell.edu/files/info2950/About%20Cornell%20University%20Timeline.html"


# In[7]:


# your code here
timeline_result = requests.get(timeline_url)
if timeline_result.status_code != 200:
  print("something went wrong:", cornell_result.status_code, cornell_result.reason)


# 2. Convert what you retrieved with the `requests` library to a text string.
# 
# 
# 

# In[8]:


# your code here
timeline_source = timeline_result.text


# 3. Parse the text as HTML with BeautifulSoup.

# In[9]:


# your code here
page = BeautifulSoup(timeline_source, "html.parser")


# 4. Identify the HTML tag and class above the year, title, and summary text. Find all occurences of this tag and save it to a list.

# In[12]:


# your code here
timeline = page.find_all("div", {"class": "item-content"})
print(len(timeline_events))


# 5. Access the year, title, and summary text at the 10th index position. Print these.

# In[13]:


# your code here
print(timeline[9].find('div', {'class':'item-year'}).text)
print(timeline[9].find('div', {'class':'item-title'}).text)
print(timeline[9].find('div', {'class':'item-desc'}).text)


# 6. Collect all years, titles, and summaries in the list of timeline events. Add each of these to a list (`year_l`, `title_l`, and `summary_l`).

# In[14]:


# your code here
# your code here
year = []
title= []
summary = []

for event in timeline:
    year.append(event.find('div', {'class':'item-year'}).text)
    title.append(event.find('div', {'class':'item-title'}).text)
    summary.append(event.find('div', {'class':'item-desc'}).text)

print(year)
print(title)
print(summary)


# 7. Convert these lists into data frame columns and display the data frame.
# 
# *Note: you might notice a couple of cells in the first and last row have missing information. This is an issue with the cached version of the webpage. You do not need to fix this.*

# In[16]:


# your code here
data= {'Year': year, 'Title': title, 'Summary': summary}
pd.DataFrame(data)


# ---

# ## Problem 3
# 
# Select a page from the web that contains some table element. Extract the table's information and put it into a pandas data frame. Make sure to display the table when you are finished.
# 
# As a suggestion, you may use the [Wikipedia page for Cornell University](https://en.wikipedia.org/wiki/Cornell_University). The table on the right side of the page is a good option for scraping and displaying.
# 
# Remember to use the following steps, as you did above:
# 1. Use the requests library to `get` the website's HTML. Check the status code.
# 2. Convert what you retrieved with the `requests` library to a text string.
# 3. Parse the text as HTML with BeautifulSoup.
# 4. Manually search the HTML (with ^F) for the text strings you want to collect. Identify the tags and classes associated with that text.
# 5. Use combinations of `find` and `find_all` to retrieve the text you are interested in.
# 6. Convert the text to a data frame. Display this.
# 
# 

# In[18]:


wiki_url = "https://koenecke.infosci.cornell.edu/files/info2950/Cornell%20University%20-%20Wikipedia.html" # optional cached version


# In[19]:


# your code here, add as many cells as you need
wiki_result = requests.get(wiki_url)
if wiki_result.status_code != 200:
  print("something went wrong:", wiki_result.status_code, wiki_result.reason)


# In[20]:


wiki_source = wiki_result.text
print(wiki_source[:20])


# In[22]:


wiki = BeautifulSoup(wiki_source, "html.parser")


# In[ ]:





# ## Submission
# **Make sure to complete and save this notebook before next Friday's section.** We will practice pushing and pulling code from GitHub and we will ask you to push a completed version of this notebook to that repository.
