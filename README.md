# Listjack - Clickjack testing automation

Listjack is a script to automate the process of checking a list of targets for clickjacking.

## How it works

The scripts does the following

- Creates a hidden browser using Selenium and Xvfb (X virtual framebuffer)
- Creates an html file with an iframe tag containing a target from the input list
- Serves the html file locally with SocketServer
- Takes a screenshot of the html page with Selenium
  - screenshots are stored in the /img_epoch/ directory
  - screenshots have their corresponding URL associated to them with Linux extended file attributes. You can retrieve the URL of any image with the following command: getfattr -n 'user.url' /path/to/file.ext
- Compares the screenshot against a baseline image (blank iframe template) using [fuzzy hashing](http://ssdeep.sourceforge.net/)

## Usage

First, run the setup script

```
sudo setup.sh
```

The command syntax is

```
sudo ./listjack.py <inputfile>
```

where the input file is a newline delimited list of targets. Example: 

```
http://site.com
https://example.com
```

## Output

Example output

```
+-------+----------+-------------------------+
| File  | Likeness | url                     |
+-------+----------+-------------------------+
| 3.png | 100      | https://www.site.com    |
+-------+----------+-------------------------+
| 1.png | 0        | https://1.2.3.4/        |
+-------+----------+-------------------------+
| 2.png | 0        | https://example.org     |
+-------+----------+-------------------------+

```

**What it means**

- File = local file name as found in the /img_epoch/ directory
- Likeness = fuzzy hash comparison value on a scale from 0 (dissimilar) to 100 (similar)
  - a value of 100 means the attempt to clickjack was unsuccessful (probably due to something like X-FRAME-OPTIONS). If you suspect that the target(s) is using a frame buster, consider adding the "sandbox" attribute to the iframe template and re-running the script.
  - a value closer to 0 means the attempt was *likely* successful, though you should still manually check the results
- URL = entry from target list

## Changelog

- 7/23/2017 - script now restarts xvfb & webdriver every 5 requests due to memory issues in xvfb; added URL in screenshots; additional minor changes
- 7/17/2017 - moved progress bar from processing to requesting; no longer processes blank lines in the input file; changed local server port from 8080 to 8081 since 8080 is more commonly used by Burp
- 7/4/2017 - initial commit

## Notes

**Testing**: This was tested on Ubuntu 17.04 

**Suggestions**: If you have any feature suggestions, please open an issue
