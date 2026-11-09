**Title:** [OC] Who's on the mountains? I linked 2,228 mountains named after people to their namesakes' birthplaces: 84% of the person-named peaks of Australia and New Zealand honour someone born on another continent

**Body:**

Everest, Kosciuszko, Cook, McKinley: lots of mountains carry a person's name. Using Wikidata I drew a line from every person-named mountain to the place its namesake was born.

- In Europe 98% of person-named peaks honour someone born in Europe. In Australia and New Zealand 84% honour someone born on another continent; in South America 71%; in North America 35%.
- 88% of New Zealand's person-named peaks honour people born abroad, mostly in Britain. The longest line: Mount Grey, NZ, to George Grey's birthplace in Lisbon, 19,505 km.
- Scientists are 29% of the people honoured, royals, rulers and politicians 19%. Only 5.1% are women.
- Recent renamings in the data: Denali, Black Elk Peak, Doso Doyabi, Mount Blue Sky, Kuwohi.

Interactive map (click a mountain to draw the line home): https://maps.tristanhotham.com/mountain-names/

**Source comment:**

Data: Wikidata (CC0) "named after" (P138) statements for mountains, summits, hills, volcanoes and ranges, with each person's birthplace (P19), sex and occupations, queried through QLever; 1,635 people with a mapped birthplace. I removed 49 links that were wrong, out of date or to a saint honoured by a church rather than in memory, and left 59 country-level birthplaces off the map. Countries and continents are modern, from Natural Earth. Wikidata is not a complete list of mountains. Tools: Python (pandas, geopandas, matplotlib), MapLibre. Paper, data and code: https://github.com/Tristan-Hotham/mountain-names
