# The Other Side

_The Other Side_ (to be renamed) analyzes the political psychologies of the Democratic and Republican parties since 1960 (the year of the first general presidential debate).

Debate transcripts can be found at [The American Presidency Project](http://www.presidency.ucsb.edu/debates.php).

# Timeline

- [x] *Scraping:* cleaning transcripts from the web and storing them in formatted CSV's
- [ ] *Analysis:* engine to get a targeted word frequency for any transcript
- [ ] *1<sup>st</sup> Aggregator:* combining word frequencies for each debate to a Democrat and Republican key
- [ ] *2<sup>nd</sup> Aggregator:* combining debate scores for each year (separate primary & general)

# Literature

## On Measuring Text
- [_Measuring Moral Culture_](https://kenan.ethics.duke.edu/wp-content/uploads/2014/03/Vaisey-and-Miles-Measuring-Moral-Culture-12-16-13.pdf)
- [_Liberals and Conservatives Rely on Different Sets of Moral Foundations_](http://www-bcf.usc.edu/~jessegra/papers/GrahamHaidtNosek.2009.Moral%20foundations%20of%20liberals%20and%20conservatives.JPSP.pdf) Study 4, page 1038-1040
- [_Measuring Moral Rhetoric in Text_](https://www.researchgate.net/publication/258698999_Measuring_Moral_Rhetoric_in_Text) (1-13)

## On Ideology and Sentiment
- [_Moral Foundations and Heterogeneity in Ideological Preferences_](http://www.jstor.org/stable/23481157)
- [_Morality Between the Lines: Detecting Moral Sentiment In Text_](http://morteza-dehghani.net/wp-content/uploads/morality-lines-detecting.pdf)

# Methodology

## Scraping Transcripts

| - | Presidential | Vice Presidential | Primary |
| --- | --- | --- | --- |
| 2016 | participants | participants | participants |
| 2012 | _The President.<br>...Romney._ | __...BIDEN:<br>...RYAN:__ | participants |
| 2008 | __OBAMA:__<br>`(?i)`__MCCAIN:__ | __BIDEN:<br>PALIN:__ | participants |
| 2004 | _...Bush.<br/>Kerry._ | CHENEY:<br>EDWARDS: | __DEAN:<br>LIEBERMAN:__<br>... |
| 2000 | BUSH:<br>GORE: | CHENEY:<br>LIEBERMAN: | participants |
| 1996 | _The President.<br>...Dole._ | KEMP:<br>GORE: | - |
| 1992 | Governor Clinton.<br>President Bush. | GORE:<br>...QUAYLE: | - |
| 1988 | DUKAKIS:<br>BUSH: | QUAYLE:<br>BENTSEN: | - |
| 1984 | The President.<br>Mr. Mondale. | FERRARO:<br>BUSH: | - |
| 1980 | THE PRESIDENT.<br>GOVERNOR REAGAN. | - | - |
| 1976 | THE PRESIDENT.<br>MR. CARTER. | DOLE:<br>MONDALE: | - |
| 1960 | MR. NIXON:<br>MR. KENNEDY: | - | - |

# Data

## Moral Foundations Dictionary
- [Moral Foundations LIWC Dictionary](http://www.moralfoundations.org/sites/default/files/files/downloads/moral%20foundations%20dictionary.dic): a list of 324 of base foundation words

The header section of the file is contained within two percent signs, each on their own line. The lines in between them each contain the hash index of the foundation followed by a tab and the foundation name.
```
%
01    FOUNDATION1_VIRTUE
02    FOUNDATION1_VICE
03    FOUNDATION1_VIRTUE
...
%
```

In the lines underneath, one keyword and its foundation index lie on each line. Some keywords may refer to multiple foundations.
```
...
%
keyword1    01
keyword2    01 02
keyword3    02
...
```

# Discussion
- For future research, [_Measuring Moral Rhetoric In Text_](https://www.researchgate.net/publication/258698999_Measuring_Moral_Rhetoric_in_Text) made a text analysis method that could focus on a specific topic instead of a whole body of text.
