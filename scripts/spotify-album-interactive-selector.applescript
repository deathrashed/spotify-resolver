#!/usr/bin/osascript
-- Spotify Album Interactive Selector
--
-- Interactive: Search albums ? Pick album(s) ? Copy
-- Supports picking one album or all albums
--
-- Version: 1.0.0

-- Configuration
set scriptPath to POSIX path of (path to me)
set AppleScript's text item delimiters to "/"
set pathParts to text items of scriptPath
set pathParts to items 1 thru -2 of pathParts
set projectRoot to (pathParts as string) & "/.."
set projectRoot to do shell script "cd " & quoted form of projectRoot & " && pwd"
set pythonScript to projectRoot & "/src/spotify-album-search.py"
set AppleScript's text item delimiters to ""

-- Step 1: Get album search query
set dialogResult to display dialog "Search for Albums:" & return & return & "Examples:" & return & "¥ Pink Floyd Dark Side" & return & "¥ The Beatles Abbey Road" & return & "¥ Metallica Master" default answer "" buttons {"Cancel", "Search"} default button "Search" with icon note with title "Spotify Album Search"

if button returned of dialogResult is "Cancel" then
	return
end if

set searchQuery to text returned of dialogResult

if searchQuery is "" then
	display dialog "Please enter a search query." buttons {"OK"} default button "OK" with icon stop with title "Error"
	return
end if

try
	-- Step 2: Use the basic spotify-album-search.py with --list-only for reliable output
	set searchCommand to "python3 " & quoted form of pythonScript & " " & quoted form of searchQuery & " --list-only 2>&1"
	set searchOutput to do shell script searchCommand

	-- Parse results (format: "1. Album Name Ñ Artists\n   URL\n")
	set AppleScript's text item delimiters to return
	set outputLines to text items of searchOutput
	set AppleScript's text item delimiters to ""

	set albumChoices to {}
	set albumURLs to {}
	set i to 1

	repeat while i <= (count of outputLines)
		set currentLine to item i of outputLines
		-- Check if this line looks like an album entry (starts with number)
		if currentLine contains "." and currentLine contains " Ñ " then
			-- Parse album line: "1. Album Name Ñ Artists"
			set AppleScript's text item delimiters to " Ñ "
			set albumParts to text items of currentLine
			set AppleScript's text item delimiters to ""

			if (count of albumParts) >= 2 then
				-- Get album name (remove number)
				set albumWithNum to item 1 of albumParts
				set AppleScript's text item delimiters to ". "
				set numParts to text items of albumWithNum
				set AppleScript's text item delimiters to ""

				if (count of numParts) > 1 then
					set albumName to item 2 of numParts
				else
					set albumName to albumWithNum
				end if

				-- Get artist(s)
				set artistNames to item 2 of albumParts

				-- Create display string
				set displayString to albumName & " Ñ " & artistNames

				-- Get URL from next line (should be indented)
				set urlLine to ""
				if i < (count of outputLines) then
					set nextLine to item (i + 1) of outputLines
					set nextLine to my trim(nextLine)
					if nextLine starts with "http" then
						set urlLine to nextLine
						set i to i + 1 -- Skip the URL line
					end if
				end if

				if urlLine is not "" then
					-- Add to lists
					set end of albumChoices to displayString
					set end of albumURLs to urlLine
				end if
			end if
		end if
		set i to i + 1
	end repeat

	set AppleScript's text item delimiters to ""

	if (count of albumChoices) is 0 then
		display dialog "No albums found for: " & searchQuery buttons {"OK"} default button "OK" with icon caution with title "No Results"
		return
	end if

	-- Add "ALL" option
	set end of albumChoices to "ALL albums (copy all URLs)"

	-- Step 3: Let user pick an album
	set resultCount to count of albumChoices
	set choiceDialog to choose from list albumChoices with prompt "Found " & (resultCount - 1) & " album(s). Select one:" with title "Spotify Album Search" OK button name "Copy Link" cancel button name "Cancel"

	if choiceDialog is false then
		return
	end if

	set selectedAlbum to item 1 of choiceDialog

	-- Step 4: Handle selection
	if selectedAlbum is "ALL albums (copy all URLs)" then
		-- Copy all URLs
		set allURLs to ""
		repeat with i from 1 to (count of albumURLs)
			set allURLs to allURLs & item i of albumURLs
			if i < (count of albumURLs) then
				set allURLs to allURLs & return
			end if
		end repeat
		set the clipboard to allURLs
		display dialog "Copied " & (count of albumURLs) & " album URLs to clipboard!" buttons {"OK"} default button "OK" with icon note with title "Success"
	else
		-- Find selected album index
		set selectedIndex to 0
		repeat with i from 1 to (count of albumChoices)
			if item i of albumChoices is selectedAlbum then
				set selectedIndex to i
				exit repeat
			end if
		end repeat

		if selectedIndex > 0 and selectedIndex <= (count of albumURLs) then
			set selectedURL to item selectedIndex of albumURLs
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
