#!/usr/bin/osascript
-- Spotify Album Resolver - Quick AppleScript Interface
--
-- Fast single-result resolver with clean output
-- For multiple results, use spotify-album-selector.applescript
--
-- Version: 1.0.0

-- Configuration
-- Auto-detect project root (this script is in scripts/, so go up one level)
set scriptPath to POSIX path of (path to me)
set AppleScript's text item delimiters to "/"
set pathParts to text items of scriptPath
set pathParts to items 1 thru -2 of pathParts -- Remove filename
set projectRoot to (pathParts as string) & "/.."
set projectRoot to do shell script "cd " & quoted form of projectRoot & " && pwd"
set pythonScript to projectRoot & "/src/spotify-album-resolver.py"
set pythonSearchScript to projectRoot & "/src/spotify-album-search.py"
set AppleScript's text item delimiters to ""

-- Show input dialog
set dialogResult to display dialog "Search Spotify:" & return & return & "Examples:" & return & "• Taphos" & return & "• Metallica Master" & return & "• Pink Floyd Dark Side" default answer "" buttons {"Cancel", "Search"} default button "Search" with icon note with title "Spotify Album Resolver"

if button returned of dialogResult is "Cancel" then
	return
end if

set searchQuery to text returned of dialogResult

-- Validate input
if searchQuery is "" then
	display dialog "Please enter a search query." buttons {"OK"} default button "OK" with icon stop with title "Error"
	return
end if

try
	-- Run search to get first result (suppress stderr warnings)
	set searchCommand to "python3 " & quoted form of pythonSearchScript & " " & quoted form of searchQuery & " 2>/dev/null | head -n 1"
	set firstResult to do shell script searchCommand

	-- Check if we got results
	if firstResult contains "No albums found" or firstResult is "" then
		display dialog "No albums found for: " & searchQuery & return & return & "Try:" & return & "• Checking spelling" & return & "• Using partial names" buttons {"OK"} default button "OK" with icon caution with title "No Results"
		return
	end if

	-- Parse the result (format: "1. Album Name — Artist(s)" followed by URL on next line)
	-- Split by newline to get album info and URL separately
	set AppleScript's text item delimiters to return
	set lines to text items of firstResult

	if (count of lines) < 2 then
		display dialog "Error parsing result." buttons {"OK"} default button "OK" with icon stop with title "Error"
		return
	end if

	set albumLine to item 1 of lines
	set albumURL to item 2 of lines

	-- Clean URL (remove leading spaces)
	set albumURL to my trim(albumURL)

	-- Parse album line: "1. Album Name — Artist(s)"
	set AppleScript's text item delimiters to " — "
	set albumParts to text items of albumLine

	if (count of albumParts) < 2 then
		display dialog "Error parsing album info." buttons {"OK"} default button "OK" with icon stop with title "Error"
		return
	end if

	-- Extract album name (remove number prefix)
	set albumWithNumber to item 1 of albumParts
	set AppleScript's text item delimiters to ". "
	set numberParts to text items of albumWithNumber
	if (count of numberParts) > 1 then
		set albumName to item 2 of numberParts
	else
		set albumName to albumWithNumber
	end if

	-- Extract artist(s)
	set artistName to item 2 of albumParts

	-- Reset delimiters
	set AppleScript's text item delimiters to ""

	-- Copy to clipboard
	set the clipboard to albumURL

	-- Show clean success message
	display dialog "Album Link Copied!" & return & return & albumName & return & artistName & return & return & albumURL buttons {"OK"} default button "OK" with icon note with title "Success"

on error errMsg number errNum
	if errNum is -128 then
		-- User cancelled
		return
	else
		display dialog "Error: " & errMsg buttons {"OK"} default button "OK" with icon stop with title "Error"
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
