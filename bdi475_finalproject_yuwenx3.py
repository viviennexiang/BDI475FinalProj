
# coding: utf-8

# # Michelin Guide Restaurant Exploratory Data Analysis
# 
# Author: Yuwen Xiang

# The data is from https://www.kaggle.com/datasets/ngshiheng/michelin-guide-restaurants-2021
# 
# Micheline guide is published by Michelin group. It contains selected restaurants around the world for tourists. The standard of Michelin Guide is very high. It divides selected restaurants into 3 level of stars. 
# The 3 levels are described as:
# - ⭐️: "A very good restaurant in its category" 
# - ⭐️⭐️: "Excellent cooking, worth a detour"
# - ⭐️⭐️⭐️: "Exceptional cuisine, worth a special journey"
# 
# In addition, there is an award called *Bib Gourmand*. Restaurants with this award have high quality food and affordable price.
# 
# Gaining a Michelin star can be a lifelong dream for chefs.If the restaurant has a Michelin star, tourists will flock to the restaurant. Meanwhile, losing a star could be a nightmare for chefs.
# 
# The dataset contains 6353 observations of restaurant in Michelin Guide 2021. I like to travel, when I plan for a trip to a new country, I usually make reservations to local Michelin restaurant in advance. So, for my final project of BDI 475, I found that making an exploratory data analysis of Michelin guide will be useful for me and someone enjoy traveling. Though COVID has not ended yet, it is great to know those restaurants in advance in case of a trip without plan!

# ### Potential Questions
# - What are the average prices of Michelin restaurants in different cities?
# - What are the average prices of different cuisines?
# - Which type of cuisines accounts for the most in the Michelin Guide? And which cuisine has the most 3 Star Micheline restaurants?
# - Which city has the most Michelin restaurants? And which city has the most 3 Star Micheline restaurants?
# - What cuisine and city are recommended for a tight budget? What cuisine and city are recommended for an adequate budget?
# - What is the breakdown of Michelin restaurants in different cities?

# ## Exploratory Data Analysis

# ### Clean the data

# First, let's load packages needed and the dataset.

# In[78]:


import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.express as px


# In[77]:


df = pd.read_csv('https://raw.githubusercontent.com/viviennexiang/BDI475FinalProj/main/michelin_my_maps.csv')


# Now, let's have a look of the dataset's basic information.

# In[79]:


# Display the number of rows and columns

nrow = df.shape[0]
ncol = df.shape[1]
print(f'Michelin data contains {nrow} rows and {ncol} columns.')


# In[80]:


# Display all the columns

pd.set_option('display.max_columns', 50)
display(df)


# In[81]:


# Check the data types of each column and non-missing rows

df.info()


# A data cleaning will be conducted. The insterested columns with non-missing rows will be kept.

# In[82]:


# Clean the data, keep rows with non-missing Name, Address, Location, MinPrice, MaxPrice, Currency, Cuisine, Longtitude, Latitude, and Award.
michelin = df.loc[:, ["Name", "Address", "Location", "MinPrice", "MaxPrice", "Currency", "Cuisine", "Longitude", "Latitude","Award"]]
michelin = michelin.dropna()
michelin = michelin.reset_index(drop=True)
michelin.head(5)


# The next step is to convert currencies. To give a intuitive comparison, all prices will be converted to USD.

# In[83]:


michelin2 = michelin.copy()


# In[84]:


michelin2['Rate'] = 0
michelin2['cminprice'] = 0
michelin2['cmaxprice'] = 0


# In[85]:


get_ipython().run_cell_magic('capture', '--no-stderr', '!pip install requests')


# In[86]:


st = ','.join(set(list((michelin['Currency']))))


# In[87]:


pd.options.mode.chained_assignment = None
import requests

api = "p9CdBS0XFeoB0CR3iEm9ErnxPndZjtdE"

params = {'access_key': api, 'currencies': st, 'format': 1}

url = "https://v6.exchangerate-api.com/v6/{0}/latest/USD".format(api)
url = "https://v6.exchangerate-api.com/v6/a3b189d15daf0fe8105487e6/latest/USD"

response = requests.get(url)

r = requests.get('http://apilayer.net/api/live', params = params)

data = response.json()['conversion_rates']

unique_currency = list(set(list(michelin['Currency'])))

for currency in unique_currency:
    michelin2['Rate'][michelin2['Currency'] == currency] = data[currency]


# In[88]:


pd.options.mode.chained_assignment = None
for i in range(michelin2.shape[0]):
        michelin2['cminprice'][i] = float("".join(michelin2['MinPrice'][i].split(',')))/michelin2['Rate'][i]
        michelin2['cmaxprice'][i] = float("".join(michelin2['MaxPrice'][i].split(',')))/michelin2['Rate'][i]


# In[89]:


michelin = michelin2.loc[:,['Name', 'Address', 'Location','Cuisine', 'Longitude', 'Latitude', 'Award','cminprice', 'cmaxprice']]
michelin.rename(columns={"cminprice": "MinPrice", "cmaxprice": "MaxPrice"}, inplace=True)


# In[90]:


michelin.to_csv("michelin_cleaned.csv")


# ### Explore the price differences between cuisines and cities.

# First, let's have a look to the distribution of minimum price and maximum price.

# In[91]:


fig = px.box(michelin,
             x='MinPrice',
             orientation='h',
             title='Range of MinPrice')
fig.show()


# The lowest minimum price is about \\$0.5 while the highest is \\$600. There are many outliers, which makes sense, the minimum price of some 3-Star Michelins can be extremely high.

# In[92]:


fig = px.box(michelin,
             x='MaxPrice',
             orientation='h',
             title='Range of MaxPrice')
fig.show()


# The lowest maximum price is about \\$0.5, which is same as the minimum price, a possible interpretation maybe it is a stand that only sell one streetfood. The highest maximum price is about \\$1320.7. There are many outliers, too. 

# Let's check the top 10 cuisines. There are 1045 Michelin restaurants are in Mordern Cuisine. Creative Cuisine is the second highest, 438 Michelin restaurants are in Creative cuisine. As expected, the number of Michelin restaurants making Japanese cuisine is as high as 272.

# In[93]:


by_cuisine = michelin.groupby('Cuisine', as_index=False).agg({'Name': 'count'})
by_cuisine.rename(columns={'Name': 'Count'}, inplace=True)
by_cuisine.sort_values('Count', ascending=False, inplace=True)
by_cuisine.head(10)


# In[72]:


fig = px.bar(by_cuisine[0:10], 
             x="Cuisine", 
             y="Count", 
             title="Top 10 cuisines with the highest number of Michelin restaurants",
             color="Cuisine", 
             width=800,height=500)
fig.show()


# Then, let's check top 10 cities with Michelin restaurants. If you are a gourmet, the cities below are the recommend place for you to travel. 

# In[94]:


by_city = michelin.groupby('Location', as_index=False).agg({'Name': 'count'})
by_city.rename(columns={'Name': 'Count'}, inplace=True)
by_city.sort_values('Count', ascending=False, inplace=True)
by_city.head(10)


# In[73]:


fig = px.bar(by_city[0:10], 
             x="Location", 
             y="Count", 
             title="Top 10 cities with the highest number of Michelin restaurants",
             color="Location", 
             width=800,
             height=500)
fig.show()


# Next, let's explore the maximum price and minimum price differences between cuisines and cities.

# In[95]:


max_by_cuisine = michelin.groupby('Cuisine', as_index=False).agg({'Name': 'count','MaxPrice': ['min', 'max', 'mean']})
max_by_cuisine.rename(columns={'count': 'Number','min': 'Minimum', 'max': 'Maximum', 'mean': 'Average'}, inplace=True)
max_by_cuisine.sort_values(('MaxPrice', 'Average'), ascending=False, inplace=True)
max_by_cuisine.head(10)


# Sorted by average maximum price, cuisines above are the top 10 expensive. The average maximum prices are all over $250. If you plan to visit restaurants with these cuisines, maybe you need to increase your budget. 

# In[96]:


min_by_cuisine = michelin.groupby('Cuisine', as_index=False).agg({'Name': 'count','MinPrice': ['min', 'max', 'mean']})
min_by_cuisine.rename(columns={'count': 'Number','min': 'Minimum', 'max': 'Maximum', 'mean': 'Average'}, inplace=True)
min_by_cuisine.sort_values(('MinPrice', 'Average'), ascending=True, inplace=True)
min_by_cuisine.head(10)


# Sorted by average minimum price, cuisines above are the top 10 affordable. Most of them have an average minimum price less than 10 dollars. If you have a tight budget, try them!

# Below is the top 10 cities with the highest average maximum price. If you plan to visit here, remember to prepare enough money.

# In[97]:


max_by_city = michelin.groupby('Location', as_index=False).agg({'Name': 'count','MaxPrice': ['min', 'max', 'mean']})
max_by_city.rename(columns={'count': 'Number','min': 'Minimum', 'max': 'Maximum', 'mean': 'Average'}, inplace=True)
max_by_city.sort_values(('MaxPrice', 'Average'), ascending=False, inplace=True)
max_by_city.head(10)


# So, what cities have the top 10 lowest average minimum price? It seems like Chiang Mai is a good place to visit for the number of Micheline restaurants it has and their prices.

# In[98]:


min_by_city = michelin.groupby('Location', as_index=False).agg({'Name': 'count','MinPrice': ['min', 'max', 'mean']})
min_by_city.rename(columns={'count': 'Number','min': 'Minimum', 'max': 'Maximum', 'mean': 'Average'}, inplace=True)
min_by_city.sort_values(('MinPrice', 'Average'), ascending=True, inplace=True)
min_by_city.head(10)


# As mentioned in data description. Stars are important for chefs. Let's check the 3-star Michelin restaurants cuisine break down.

# In[99]:


threestar = michelin[michelin['Award'] == '3 MICHELIN Stars']
fig = px.pie(
    threestar,
    names='Cuisine',
    title='Three star Michelin restaurant cuisine breakdown',
    width=800,
    height=700
)

fig.show()


# Detailed Top 10 cuisines with the most 3-star Michelin restaurants is shown below.

# In[100]:


by_cuisine_star = threestar.groupby(['Cuisine'], as_index=False).agg({'Name': 'count'})
by_cuisine_star.rename(columns={'Name':'Count'}, inplace = True)
by_cuisine_star.sort_values('Count', ascending=False, inplace=True)

fig = px.bar(
    by_cuisine_star[0:10],
    x = 'Cuisine',
    y = 'Count',
    title = 'Top 10 cuisines with the most 3-star Michelin Restaurants',
    color="Cuisine", 
    width=800,
    height=500
)

fig.show()


# Creative cuisine and Japanese cuisine account for high proportion in both overall Michelin restaurants and 3-Star Micheline restaurants. Though the number of Michelin restaurant in Modern style is the highest, about two times higher than Creative cuisine restaurants, there are not many 3-Star Modern restaurants.

# Similar to cuisines, we are also interested in  3-star Michelin restaurants city break down. Because cities with 1 three-star Michelin restaurant account for the most, which makes the plot messy, only cities with more than 2 three-star Michelin restaurants will be shown.

# In[101]:


threestar2 = threestar.groupby(['Location'], as_index=False).agg({'Name': 'count'})
threestar2 = threestar2[threestar2['Name']>=2]
st2 = ','.join(set(list((threestar2['Location']))))
unique_city = list(set(list(threestar2['Location'])))

threestar3 = threestar[(threestar['Location'].isin(unique_city))]


# In[102]:


fig = px.pie(
    threestar3,
    names='Location',
    title='Three star Michelin restaurant city breakdown(>=2 three-star Michelins)',
    width=800,
    height=700
)

fig.show()


# The top 10 cities with the most 3-star Michelin restaurants:

# In[103]:


by_city_star = threestar.groupby(['Location'], as_index=False).agg({'Name': 'count'})
by_city_star.rename(columns={'Name':'Count'}, inplace = True)
by_city_star.sort_values('Count', ascending=False, inplace=True)

fig = px.bar(
    by_city_star[1:10],
    x = 'Location',
    y = 'Count',
    title = 'Top 10 cities with the most 3-star Michelin Restaurants',
    color="Location", 
    width=800,
    height=500
)

fig.show()


# Tokyo is the city with both highest amount of Michelin restaurants and 3-Star Michelin restaurants, making it worth visiting. Paris comes second, though it doesn't have as many Michelin restaurants as Tokyo does, the quality of its Michelin restaurants are relatively high. Hong Kong is similar to Paris,if you are considering for visiting Hong Kong, please don't be hesitate!

# However, consider price and difficulties in reservation, 3-Star Michelins are not the main goal for most tourists. An Award break down of Cities with more than 2 3-Star Michelins will be conducted for travelers who are insterested in Michelins in levels other than 3-star.

# In[104]:


top_cities = michelin[(michelin['Location'].isin(unique_city))]
by_city_award = top_cities.groupby(['Location', 'Award'], as_index=False).agg({
        'Name': 'count'
    }).rename(columns={
        'Name': 'num_listings'
    })


# In[105]:


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

fig = px.treemap(
    by_city_award,
    path=['Location', 'Award'],
    title='Top cities breakdown',
    values='num_listings',
    height=700
)

fig.show()


# Most of the top cities have similar trends, Bib gourmand is in the lead. In cities like Paris, London, Shanghai, and Beijing, 1-star Michelin accounts for the most. Cities above are definitely worth visiting, where you can enjoy both affordable Michelin Restaurant and expensive delicacies.

# ### Summary
# - Tokyo is the city with both the most Michelin restaurants and 3-Star Michelin restaurants, offering tourists various choices of high quality foods. Moreover, Kyoto and Osaka, which located in Japan as well, are worth visiting, too. 
# - Michelin restaurants are mostly located in East Asia, Europe, and the United States.
# - If you have a tight budget, Chiang Mai will be recommended. It has 23 Michelin restaurants and the average minimum expense is as low as 12 dollars.
# - Among all cuisines, Modern cuisine has the most Michelin restaurants while creative cuisine has the most 3-star Michelin restaurants. Crab Specialities is the most expensive cuisine and Street food is the most affordable.

# In[ ]:




