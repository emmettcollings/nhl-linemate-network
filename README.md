# NHL Linemates Network

This project was originally created for the course CPSC 572/672: Fundamentals of Social Network Analysis and Data Mining taught at the University of Calgary in Fall 2022.

## Course Version of Repo

The repo is currently undergoing some renovations to clean up extraneous files/panicked spaghetti.
The version of the repo that was used to write our submitted paper is tagged as `archive/course-submission`.
The old version is provided in case marking must use that version, as well as to preserve course-specific materials such as the group project and other course deliverables.
The results however haven't changed and we recommend using the current version for an easier time browsing.

## About

For a basic rundown on what hockey is and how it might relate to what we are trying to answer see https://thehockeywriters.com/hockey-101-beginners-guide-ice-hockey/.

This project aims to investigate the effects that NHL players have on their linemates.
It's a known phenomenon that some players perform better with specific players over others.
Famous examples include Alex Ovechkin and Nicklas Backstrom, Brent Seabrook and Duncan Keith, and the Sedin twins to name a few.
What makes these players work together so well?
What player traits tend to synergize with each other?
Can we quantify what makes an effective duo?
Conversely, can we predict whether a potential pair of players will be a good match for each other?
These are a few of the questions we aim to analyze using network techniques.

### Network

The network's nodes are individual players.
A pair of directed edges are present between players if they have spent significant time playing at even strength with each other.
The magnitude of these edges is equivalent to the difference between the destination player's [Corsi For %](<https://en.wikipedia.org/wiki/Corsi_(statistic)>) when playing with the source player and their Corsi For % in all other play.

Data was sourced from [moneypuck.com](https://moneypuck.com/data.htm).

## Repository Overview

A [conda](https://www.anaconda.com/) environment file `conda_env.yml` is provided.
It's recommended to create a new environment with this file to easily load all dependencies.
Data processing is done via the python files in `src/scripts`, outputting all processed data to the folder `data/interim`.
Network analysis can be found in `src/notebooks`.
Any data outputs from these can be found in `data/final`.
Additionally, the networks are exported as `.gexf` files that can be read with network visualization software such as [Gephi](https://gephi.org/).
Gephi files with completed visualizations can be found at `reports/gephi`.
Finally, a paper discussing some results of the project can be found in `reports/paper`.
