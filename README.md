# ulauncher-zeal

A [Ulauncher](https://ulauncher.io/) extension to query the [Zeal](https://zealdocs.org/) offline documentation browser.

## Features

- Show installed Zeal docsets with their icons
- Fuzzy filtering of docsets
- Open the Zeal app with the specified docset and search query

*Note: the extension cannot show actual search results because as of this writing, Zeal doesn't have an actual search API. The only way to interact with Zeal is to pass the docset name and the query on the command line.*

## Requirements

- Install [Zeal](https://zealdocs.org/)

## Installation

Open Ulauncher preferences window -> Extensions -> "Add extension" and paste the following url:

```
https://github.com/pbkhrv/ulauncher-zeal
```

## Configuration

- `Zeal docsets path`: path to where your installation of Zeal stores the downloaded docsets. The default works on Ubuntu with Zeal installed thru apt, but your mileage may vary. Check *Zeal -> Preferences -> General -> Docset storage*.

## Usage

Open Ulauncher and type in "zl " to start the extension. If everything is configured correctly, you'll see the list of your downloaded Zeal docsets:

![All docsets](images/screenshots/all-docsets.png)

The first argument is the docset keyword. It filters the list of docsets down to whatever matches the keyword:

![Keyword](images/screenshots/keyword-py.png)

The second argument is the search query that'll be passed to Zeal:

![Query](images/screenshots/query.png)

Press Enter to open Zeal with that keyword and query:

![Zeal window](images/screenshots/zeal-window.png)

## Inspiration and thanks

I loved Alfred on MacOS, and now I love Ulauncher on Linux. The Python API is a joy to work with.

Thanks to [Dash for MacOS](https://kapeli.com/dash) and the [Zeal project](https://github.com/zealdocs/zeal/) for making awesome offline documentation easily available.