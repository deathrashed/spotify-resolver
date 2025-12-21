#!/usr/bin/osascript
-- Spotify Album Resolver - Album Selector
--
-- Searches Spotify and lets you select from results.
-- Clean output with album selection dialog.
--
-- Version: 1.0.1

-- Configuration
-- Auto-detect project root (this script is in scripts/, so go up one level)
set scriptPath to POSIX path of (path to me)
set AppleScript's text item delimiters to "/"
set pathParts to text items of scriptPath
set pathParts to items 1 thru -2 of pathParts -- Remove filename
set projectRoot to (pathParts as string) & "/.."
set projectRoot to do shell script "cd " & quoted form of projectRoot & " && pwd"
set pythonSearchScript to projectRoot & "/src/spotify-album-search.py"
set AppleScript's text item delimiters to ""

-- Show input dialog
set dialogResult to display dialog "Search Spotify:" & return & return & "Examples:" & return & "• Taphos" & return & "• Trauma Shot" & return & "• Pink Floyd Dark Side" default answer "" buttons {"Cancel", "Search"} default button "Search" with icon note with title "Spotify Album Resolver"

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
	-- Run the search script to get results (suppress stderr warnings)
	set searchCommand to "python3 " & quoted form of pythonSearchScript & " " & quoted form of searchQuery & " --list-only --limit 20 2>/dev/null"
	set searchResults to do shell script searchCommand

	-- Check if we got results
	if searchResults contains "No albums found" or searchResults is "" then
		display dialog "No albums found for: " & searchQuery & return & return & "Try:" & return & "• Checking spelling" & return & "• Using partial names" buttons {"OK"} default button "OK" with icon caution with title "No Results"
		return
	end if

	-- Parse results into lists
	set albumChoices to {}
	set albumURLs to {}

	-- Split by double newline to get each album block
	set AppleScript's text item delimiters to return & return
	set albumBlocks to text items of searchResults

	-- Parse each album block
	repeat with albumBlock in albumBlocks
		if albumBlock is not "" then
			-- Split block into lines
			set AppleScript's text item delimiters to return
			set blockLines to text items of albumBlock

			if (count of blockLines) >= 2 then
				set albumLine to item 1 of blockLines
				set urlLine to item 2 of blockLines

				-- Clean URL
				set urlLine to my trim(urlLine)

				-- Parse album line: "1. Album Name — Artist(s)"
				if albumLine contains "—" then
					set AppleScript's text item delimiters to " — "
					set albumParts to text items of albumLine

					if (count of albumParts) >= 2 then
						-- Get album name (remove number)
						set albumWithNum to item 1 of albumParts
						set AppleScript's text item delimiters to ". "
						set numParts to text items of albumWithNum
						if (count of numParts) > 1 then
							set albumName to item 2 of numParts
						else
							set albumName to albumWithNum
						end if

						-- Get artist(s)
						set artistNames to item 2 of albumParts

						-- Create display string
						set displayString to albumName & " — " & artistNames

						-- Add to lists
						set end of albumChoices to displayString
						set end of albumURLs to urlLine
					end if
				end if
			end if
		end if
	end repeat

	-- Reset delimiters
	set AppleScript's text item delimiters to ""

	-- Check if we parsed any results
	if (count of albumChoices) is 0 then
		display dialog "Could not parse search results." buttons {"OK"} default button "OK" with icon stop with title "Error"
		return
	end if

	-- Add "ALL" option
	set end of albumChoices to "ALL albums (copy all URLs)"

	-- Show count and let user choose
	set resultCount to count of albumChoices
	set choiceDialog to choose from list albumChoices with prompt "Found " & (resultCount - 1) & " album(s). Select one:" with title "Spotify Album Resolver" OK button name "Copy Link" cancel button name "Cancel"

	if choiceDialog is false then
		-- User cancelled
		return
	end if

	-- Get the selected item
	set selectedAlbum to item 1 of choiceDialog

	-- Handle "ALL" selection
	if selectedAlbum is "ALL albums (copy all URLs)" then
		-- Copy all URLs (one per line)
		set allURLs to ""
		repeat with i from 1 to (count of albumURLs)
			set allURLs to allURLs & item i of albumURLs
			if i < (count of albumURLs) then
				set allURLs to allURLs & return
			end if
		end repeat
		set the clipboard to allURLs
		display dialog "Copied " & (count of albumURLs) & " album URLs to clipboard!" buttons {"OK"} default button "OK" with icon note with title "Success"
		return
	end if

	-- Find the index of the selected album
	set selectedIndex to 0
	repeat with i from 1 to (count of albumChoices) - 1
		if item i of albumChoices is selectedAlbum then
			set selectedIndex to i
			exit repeat
		end if
	end repeat

	if selectedIndex is 0 then
		display dialog "Error finding selected album." buttons {"OK"} default button "OK" with icon stop with title "Error"
		return
	end if

	-- Get the corresponding URL
	set selectedURL to item selectedIndex of albumURLs

	-- Copy to clipboard
	set the clipboard to selectedURL

	-- Show success with clean info
	display dialog "Album Link Copied!" & return & return & selectedAlbum & return & return & selectedURL buttons {"OK"} default button "OK" with icon note with title "Success"

on error errMsg number errNum
	-- Handle errors
	if errNum is -128 then
		-- User cancelled
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
