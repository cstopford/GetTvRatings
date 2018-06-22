import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from bs4 import BeautifulSoup

imdbID = 'tt0060028' # ST:TOS

#imdbID = 'tt0944947' # Game of Thrones

# Find number of seasons:
seasonUrl = 'https://www.imdb.com/title/' + imdbID

seasonResponse = urllib.request.urlopen(seasonUrl)
seasonData = seasonResponse.read()      # a `bytes` object
seasonText = seasonData.decode('utf-8') # convert to text

ssoup = BeautifulSoup(seasonText, 'html.parser') # feed to BeautifulSoup

ssection = ssoup.find('div', attrs={'class':'seasons-and-year-nav'}) # Look for the dropdown list of seasons
nseasonsStr = ssection.text.replace('Seasons','').replace('Years','') # Trim text to just the first season number
nseasonsStr = nseasonsStr.lstrip()
nseasonsStr = nseasonsStr[:nseasonsStr.find('\xa0')]

# Find series title
stitle = ssoup.find('title').text.replace(' - IMDb','')
print(stitle)


# Get ratings:
ratings = []  
votes = []
seasonNumber = []

for i in range(1, int(nseasonsStr)+1):

    print('  Season: ' + str(i))
    url = 'http://www.imdb.com/title/' + imdbID + '/episodes?season=' + str(i)
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8')

    soup = BeautifulSoup(text, 'html.parser')
    sections = soup.find_all('div', attrs={'class':'ipl-rating-star'})

    for section in sections:
        if len(section) == 7:
            valString = section.text.lstrip()
            ratings.append(float(valString[:valString.find('\n')]))
            vote = valString[valString.find('(') + 1 : valString.find(')')].replace(',','')
            votes.append(float(vote))
            seasonNumber.append(i)
        
# Plot output using matplotlib
x = list(range(0,len(ratings)))
f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.scatter(x, ratings)
ax1.set_title(stitle)
ax1.set_ylim(0, 10)
ax1.grid()
ax1.set_ylabel('Rating')

ax2.scatter(x, votes)
ax2.set_ylim(0, max(votes)*1.2)
ax2.grid()
ax2.set_xlabel('Episode #')
ax2.set_ylabel('# views')
plt.savefig(imdbID + '.png')
plt.show()

# Plot using something else...
import dash
import dash_core_components as dcc
import dash_html_components as html
app = dash.Dash()
app.layout = html.Div(children=[
    html.H1(children='TV Ratings'),

    html.Div(children='''
        Get TV Ratings: see how a show fares over time
    '''),

    dcc.Graph(
        id='ratings-graph',
        figure={
            'data': [
                {'x': x, 'y': ratings, 'type': 'scatter', 'name': 'Ratings', 'mode': 'markers'},
                {'x': x, 'y': votes, 'type': 'scatter', 'name': 'Votes', 'mode': 'line', 'yaxis': 'y2'},
            ],
            'layout': {
                'title': 'TV Data Visualisation',
                'yaxis1': {'title': 'Ratings', 'range': [0, 10]},
                'yaxis2': {'title': '# votes', 'overlaying': 'y', 'side': 'right'}
            }
        }
    )

])

if __name__ == '__main__':
    app.run_server(debug=False)