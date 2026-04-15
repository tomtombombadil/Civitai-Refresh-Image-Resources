# Civitai-Refresh-Image-Resources

This python program will cycle through your CivitAI posts and images, refreshing the Resource detection on images without resources listed. This corrects a problem CivitAI had for a while back in 2025.

## Features
-	Interactive Setup: No need to edit the code. The script asks for your username, preferred domain (.com or .red), and desired window size right in the terminal.
-	Smart Detection: It doesn't blindly click every button. It reads the page and only triggers a refresh on images displaying the "resources could not be matched" warning, saving time and reducing server load.
-	Detailed Logging: Automatically generates a timestamped .txt log file in your folder, detailing exactly how many posts were checked, which images were refreshed, and which were skipped.
-	Persistent Login: Saves your session data locally. You only have to log in to Civitai once.
-	Infinite Scroll Handling: Automatically pages through massive galleries by simulating natural keyboard scrolling.

## Requirements
- Python 3.10+ (You likely already have this, since every local AI image generator I know of requires Python)
- See `requirements.txt`

## Installation
1. Clone the repo (Or just download the .py file and the requirements.txt files, put them in a folder to be used just for this program, then open Powershell and change to that new folder)
2. Create a venv for this repo: `python -m venv .venv` (This is so what happens in this Python instance doesn't imapact anything else you're doing in Python on your machine, like AI image generation)
3. Activate your venv: `.venv\Scripts\Activate.ps1` (Do this before you run the program any time you open a new Powershell window to use this program)
4. Install dependencies: `python -m pip install -r requirements.txt` alternatively just install Playwright `pip install playwright`
5. Install Chromium browswer for Playwright: `playwright install chromium`

## Usage
1. Open a Powershell window, change to the folder you placed this repository.
2. Make sure to activate your python virtual environment: `.\.venv\Scripts\Activate.ps1`
3. Start the repository's python program: `python Civitai-Refresh-Image-Resources.py`
4. Answer which domain you need to use - civitai.com or civitai.red
5. Answer what size window you want the Chromium browser (default is 1280x720), yes, you can enter your own custom size.
6. Once the Chromium browswer opens, log in to your CivitAI account and navigate to your Profile's Posts page. Let the page finish loading - CivitAI can be slow sometimes.
7. Once the Posts page is loaded, click the Powershell window to activate it and hit enter to let it know you're ready for it to proceed.
8. Let the program do it's work.
   - Be patient.
   - Do NOT scroll in the Chromium window or click on anything.
   - Do NOT minimize the Chromium window!
   - You can use other applications normally, just leave the Powershell and Chromium window operating in the background.
   - The program will scroll down your Posts page, taking its time to allow CivitAI's site to keep up.
   - Then once it gets to the bottom of your Posts page, it will scrape the info for each post, and begin to iterate through each post, editing the post.
   - It will check the each image in that post for lack of resources. If it finds any lacking, it will click the Refresh button in the Resources card, thus populating that images resources.
   - It will carry on down through the images in that post. When it's done with that post, it will go to the next post. And so on until it has processed all your posts and images.
   - When it is done it will write a summary to the LOG file in that same folder as the program. This will tell you how many posts it worked on, how many images, etc. This is so you can verify that it did everything against the numbers shown on CivitAI in your profile for your number of posts and number of images. The totals should match.
9. You can stop the program early by closing the Powershell window, but this will truncate your log and not give you the summary information at the end. You can safely start the program again later, but it will process your posts in order again. Fortunately, it will only click the Refresh Resources button on images that need it (not the ones it has already done in previous runs). So at least it doesn't re-do all that work.

# NOTES

I am *NOT* a programmer!

I wrote this using Google Gemini to generate the code. It is 99% Gemini and 1% my tweaks.

I cannot support this code in any way.

I tested this code on my own CivitAI account. It worked for me quite well. I can't guarantee it will work for you. I only have one account to test it on. That's not a big sample size.

I hope you find this useful. That's why I shared it. I found CivitAI's lack of a resource refresh on a grand scale to be frustrating, so this is my fix/work-around.

Why is this useful?

A while back - maybe spring or summer of 2025 - maybe as late as fall of 2025 - CivitAI's automatic resource detection upon-upload of an image was broken, and thousands of images were uploaded without resources in their data. What does that mean? It means those images won't appear on the checkpoint, LORA, or embeddings pages, which, in general means no one will ever see those images. (The only way to find them, short of going to the user's profile page, would be to search by tag or keyword, and most users don't do that.

The real purpose of this script is to repair that broken link between your images and the resources used to create them, so your images appear on those resource pages. That way others can see them, like/comment/share/remix and do all those wonderful things that CivitAI lets you do with images - improving your work's visbility and 'driving engagement' (as the kids these days say).

SIDENOTE: I notice when using this program that MANY of my images - even ones outside the timeframe listed above were missing resources! This fixed it. Yes, it's likely too-little too-late to actually 'drive engagement' on those images, but at least they're properly linked now and will show up on those resource pages the way they're supposed to.

## License
GNU General Public License v3.0
