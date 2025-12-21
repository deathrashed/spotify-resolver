#!/usr/bin/osascript
-- Spotify Artist Album Selector
--
-- Interactive: Search artist ? Pick artist ? Browse albums ? Pick album ? Copy
-- Clean dialog-based interface
--
-- Version: 1.0.0

-- Configuration
set scriptPath to POSIX path of (path to me)
set AppleScript's text item delimiters to "/"
set pathParts to text items of scriptPath
set pathParts to items 1 thru -2 of pathParts
set projectRoot to (pathParts as string) & "/.."
set projectRoot to do shell script "cd " & quoted form of projectRoot & " && pwd"
set AppleScript's text item delimiters to ""

-- Helper function to call Python script
on getPythonResult(command)
	try
		return do shell script command
	on error errMsg number errNum
		if errNum is 1 then
			display dialog "Error running Python script:" & return & errMsg buttons {"OK"} default button "OK" with icon stop with title "Error"
		end if
		error errMsg number errNum
	end try
end getPythonResult

-- Step 1: Get artist search query
set dialogResult to display dialog "Search for Artist:" & return & return & "Examples:" & return & "¥ Pink Floyd" & return & "¥ The Beatles" & return & "¥ Radiohead" default answer "" buttons {"Cancel", "Search"} default button "Search" with icon note with title "Spotify Artist Search"

if button returned of dialogResult is "Cancel" then
	return
end if

set searchQuery to text returned of dialogResult

if searchQuery is "" then
	display dialog "Please enter an artist name." buttons {"OK"} default button "OK" with icon stop with title "Error"
	return
end if

try
	-- Step 2: Search for artists using Python helper
	set searchCommand to "cd " & quoted form of projectRoot & " && python3 -c \"
import sys
sys.path.insert(0, 'src')
from spotify_resolver_utils import *
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from spotify_resolver_utils import *
import requests

# Define functions inline to avoid import issues
SPOTIFY_SEARCH_URL = 'https://api.spotify.com/v1/search'

def search_artists(query, session, token, limit=20):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'artist', 'limit': limit}
    response = session.get(SPOTIFY_SEARCH_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get('artists', {}).get('items', [])

def get_artist_albums(artist_id, session, token, limit=50):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    params = {'include_groups': 'album,single,compilation', 'limit': limit, 'market': 'US'}
    response = session.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get('items', [])

config = load_config()
session = create_session(config)
token = get_spotify_token(session, config.get('client_id'), config.get('client_secret'))

if not token:
    sys.exit(1)

artists = search_artists('" & searchQuery & "', session, token, 20)

for i, artist in enumerate(artists, 1):
    name = artist.get('name', '?')
    followers = artist.get('followers', {}).get('total', 0)
    genres = ', '.join(artist.get('genres', [])[:2])
    if genres:
        print(f'{i}. {name} ({followers:,} followers, {genres})')
    elif followers > 0:
        print(f'{i}. {name} ({followers:,} followers)')
    else:
        print(f'{i}. {name}')
    print(f'   ID: {artist.get(\"id\", \"?\")}')
    print()
\" 2>&1"

	set artistOutput to getPythonResult(searchCommand)

	-- Parse artist results
	set AppleScript's text item delimiters to return
	set outputLines to text items of artistOutput
	set AppleScript's text item delimiters to ""

	set artistChoices to {}
	set artistIDs to {}
	set i to 1

	repeat while i <= (count of outputLines)
		set currentLine to item i of outputLines
		-- Check if this line looks like an artist entry (starts with number)
		if currentLine contains "." and not currentLine contains "ID:" then
			-- Parse artist line: "1. Artist Name (followers, genres)"
			set AppleScript's text item delimiters to ". "
			set numParts to text items of currentLine
			set AppleScript's text item delimiters to ""

			if (count of numParts) > 1 then
				set artistName to item 2 of numParts
				-- Get artist ID from next line
				set artistID to ""
				if i < (count of outputLines) then
					set nextLine to item (i + 1) of outputLines
					set nextLine to my trim(nextLine)
					if nextLine starts with "   ID: " then
						set AppleScript's text item delimiters to "   ID: "
						set idParts to text items of nextLine
						set AppleScript's text item delimiters to ""
						if (count of idParts) > 1 then
							set artistID to item 2 of idParts
							set artistID to my trim(artistID)
							set i to i + 1 -- Skip the ID line
						end if
					end if
				end if

				if artistID is not "" then
					set end of artistChoices to artistName
					set end of artistIDs to artistID
				end if
			end if
		end if
		set i to i + 1
	end repeat

	set AppleScript's text item delimiters to ""

	if (count of artistChoices) is 0 then
		display dialog "No artists found for: " & searchQuery buttons {"OK"} default button "OK" with icon caution with title "No Results"
		return
	end if

	-- Step 3: Let user pick an artist
	set choiceDialog to choose from list artistChoices with prompt "Found " & (count of artistChoices) & " artist(s). Select one:" with title "Spotify Artist Search" OK button name "Select" cancel button name "Cancel"

	if choiceDialog is false then
		return
	end if

	set selectedArtistName to item 1 of choiceDialog
	set selectedArtistIndex to 0
	repeat with i from 1 to (count of artistChoices)
		if item i of artistChoices is selectedArtistName then
			set selectedArtistIndex to i
			exit repeat
		end if
	end repeat

	if selectedArtistIndex is 0 or selectedArtistIndex > (count of artistIDs) then
		display dialog "Error finding selected artist." buttons {"OK"} default button "OK" with icon stop with title "Error"
		return
	end if

	set selectedArtistID to item selectedArtistIndex of artistIDs

	-- Step 4: Get albums by selected artist
	set albumsCommand to "cd " & quoted form of projectRoot & " && python3 <<'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from spotify_resolver_utils import load_config, create_session, get_spotify_token
import requests

def get_artist_albums(artist_id, session, token, limit=50):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    params = {'include_groups': 'album,single,compilation', 'limit': limit, 'market': 'US'}
    response = session.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get('items', [])

config = load_config()
session = create_session(config)
token = get_spotify_token(session, config.get('client_id'), config.get('client_secret'))

if not token:
    sys.exit(1)

albums = get_artist_albums('" & selectedArtistID & "', session, token, 50)

# Deduplicate by ID
seen = set()
unique_albums = []
for album in albums:
    album_id = album.get('id')
    if album_id and album_id not in seen:
        seen.add(album_id)
        unique_albums.append(album)

# Sort by release date
unique_albums.sort(key=lambda x: x.get('release_date', ''), reverse=True)

for i, album in enumerate(unique_albums[:50], 1):
    name = album.get('name', '?')
    release_date = album.get('release_date', '')
    year = release_date[:4] if release_date else '?'
    url = album.get('external_urls', {}).get('spotify', '')
    print(f'{i}. {name} ({year})')
    print(f'   {url}')
    print()
PYTHON_SCRIPT
"

	set albumsOutput to getPythonResult(albumsCommand)

	-- Parse album results
	set AppleScript's text item delimiters to return
	set albumLines to text items of albumsOutput
	set AppleScript's text item delimiters to ""

	set albumChoices to {}
	set albumURLs to {}
	set j to 1

	repeat while j <= (count of albumLines)
		set currentLine to item j of albumLines
		-- Check if this line looks like an album entry (starts with number)
		if currentLine contains "." and not currentLine contains "http" then
			-- Parse album line: "1. Album Name (year)"
			set AppleScript's text item delimiters to ". "
			set numParts to text items of currentLine
			set AppleScript's text item delimiters to ""

			if (count of numParts) > 1 then
				set albumName to item 2 of numParts

				-- Get URL from next line
				set albumURL to ""
				if j < (count of albumLines) then
					set nextLine to item (j + 1) of albumLines
					set nextLine to my trim(nextLine)
					if nextLine starts with "http" then
						set albumURL to nextLine
						set j to j + 1 -- Skip the URL line
					end if
				end if

				if albumURL is not "" then
					set end of albumChoices to albumName
					set end of albumURLs to albumURL
				end if
			end if
		end if
		set j to j + 1
	end repeat

	set AppleScript's text item delimiters to ""

	if (count of albumChoices) is 0 then
		display dialog "No albums found for: " & selectedArtistName buttons {"OK"} default button "OK" with icon caution with title "No Albums"
		return
	end if

	-- Add "ALL" option
	set end of albumChoices to "ALL albums (copy all URLs)"

	-- Step 5: Let user pick an album
	set resultCount to count of albumChoices
	set albumDialog to choose from list albumChoices with prompt "Found " & (resultCount - 1) & " album(s) by " & selectedArtistName & ". Select one:" with title "Spotify Album Selection" OK button name "Copy Link" cancel button name "Cancel"

	if albumDialog is false then
		return
	end if

	set selectedAlbum to item 1 of albumDialog

	-- Step 6: Handle selection
	if selectedAlbum is "ALL albums (copy all URLs)" then
		-- Copy all URLs
		set allURLs to ""
		repeat with k from 1 to (count of albumURLs)
			set allURLs to allURLs & item k of albumURLs
			if k < (count of albumURLs) then
				set allURLs to allURLs & return
			end if
		end repeat
		set the clipboard to allURLs
		display dialog "Copied " & (count of albumURLs) & " album URLs to clipboard!" buttons {"OK"} default button "OK" with icon note with title "Success"
	else
		-- Find selected album index
		set selectedAlbumIndex to 0
		repeat with k from 1 to (count of albumChoices)
			if item k of albumChoices is selectedAlbum then
				set selectedAlbumIndex to k
				exit repeat
			end if
		end repeat

		if selectedAlbumIndex > 0 and selectedAlbumIndex <= (count of albumURLs) then
			set selectedURL to item selectedAlbumIndex of albumURLs
			set the clipboard to selectedURL
			display dialog "Album Link Copied!" & return & return & selectedAlbum & return & return & selectedURL buttons {"OK"} default button "OK" with icon note with title "Success"
		else
			display dialog "Error finding selected album." buttons {"OK"} default button "OK" with icon stop with title "Error"
		end if
	end if

on error errMsg number errNum
	if errNum is -128 then
		return
	else
		display dialog "Error: " & errMsg & return & return & "Error number: " & errNum buttons {"OK"} default button "OK" with icon stop with title "Error"
	end if
end try

-- Helper function to trim whitespace
on trim(str)
	set whiteSpace to {space, tab, return, linefeed}

	-- Trim leading
	repeat while (count of str) > 0
		if whiteSpace contains first character of str then
			set str to text 2 thru -1 of str
		else
			exit repeat
		end if
	end repeat

	-- Trim trailing
	repeat while (count of str) > 0
		if whiteSpace contains last character of str then
			set str to text 1 thru -2 of str
		else
			exit repeat
		end if
	end repeat

	return str
end trim
