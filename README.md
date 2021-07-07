## Table of contents
* [Purpose](#Purpose)
* [Commands](#Commands)
* [Technologies](#Technologies)
* [Genres](#Genres)
* [Setup](#Setup)
## Purpose
Anime_Expert_Bot is a twitter bot created to tweet anime and manga suggestions to users. Users will need to mention @AnimeExpertBot bot in a tweet followed some request arguments. The bot will parse the mention and respond with the title, plot, and cover photo of an appropriate anime/manga

## Technologies
* Python version: 3.8.5
* Python modules
    * Pillow
    * Tweepy
* [Jikan Unoffical MyAnimeList API](https://jikan.docs.apiary.io/#)

## Commands

manga like <media_name>
Argument | Required | Description | Value | Position
:------------ | :------------ | :------------ | :------------ | :------------
manga | N | Makes it so the suggestion returned will be for manga rather than anime | 'manga' | First
like | Y | This request will be for media similar to the media_name argument | 'like' | If argument 'manga' is used: Second, else: First
media_name | Y | Name of media to find similar titles to | Any anime/manga name. Ex: 'Attack on titan' | Last

current <genre> manga
Argument | Required | Description | Value | Position
:------------ | :------------ | :------------ | :------------ | :------------
current | N | Makes it so the suggestion returned will be currently airing/publishing | 'current' | Any
genre | Y | 1 to 4 genre names for the suggestion to match | [Any genre](#Genres) | Any
manga | N | Makes it so the suggestion returned will befor manga rather than anime | 'manga' | Any

## Genres
### Anime
* action
* adventure
* cars
* comedy
* dementia
* demons	
* mystery
* drama
* ecchi	
* fantasy	
* game	
* hentai	
* historical
* horror	
* kids	
* magic	
* martial-arts
* mecha	
* music	
* parody	
* samurai	
* romance	
* school	
* sci-fi	 
* shoujo	
* shoujo-ai
* shounen	
* shounen-ai
* space
* sports	
* super-power
* vampire	
* yaoi	
* yuri	
* harem	
* slice-of-life
* supernatural
* military
* police		
* psychological
* thriller
* seinen	
* josei

### Manga
* action
* adventure
* cars
* comedy
* dementia
* demons	
* mystery
* drama
* ecchi	
* fantasy	
* game	
* hentai	
* historical
* horror	
* kids	
* magic	
* martial-arts
* mecha	
* music	
* parody	
* samurai	
* romance	
* school	
* sci-fi	 
* shoujo	
* shoujo-ai
* shounen	
* shounen-ai
* space
* sports	
* super-power
* vampire	
* yaoi	
* yuri	
* harem	
* slice-of-life
* supernatural
* military
* police		
* psychological
* seinen
* josei	
* doujinshi
* gender-bender
* thriller

## Setup
Install the [python modules](#Technologies) using pip
Within the text_files folder create a file called 'credentials.json' and copy the contents below into the file
```
{
        "API_KEY": "",
        "API_SECRET": "",
        "ACCESS_KEY": "",
        "ACCESS_SECRET": "",
        "CLIENT_ID": ""
}
```
The value for each key can be found in your twitter developer account
