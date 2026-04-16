# Civitai-Refresh-Image-Resources

This python program will cycle through your CivitAI posts and images, refreshing the Resource detection on images without resources listed. This corrects a problem CivitAI has had for a while now. In the past, and ocassionaly now, CivitAI's post-an-image process fails to detect or write the resources detected to the CivitAI database. Also, sometimes it 'forgets' the resources tied to an image. This breaks the connection between your images and the resources (checkpoints/LORAs/embeddings) that were used to create the image. More importantly (to me at least), it means your image/post will no longer appear on that resource's page, which is where most users find images - or at least MANY users find images that way. So this will increase engagement with your images and make them more visible to the community at large.

## Features
-	Interactive Setup: No need to edit the code. The script asks for your username, preferred domain (.com or .red), and desired window size right in the terminal.
-	Smart Detection: It doesn't blindly click every button. It reads the page and only triggers a refresh on images displaying the "resources could not be matched" warning, saving time and reducing server load.
-	Detailed Logging: Automatically generates a timestamped .txt log file in your folder, detailing exactly how many posts were checked, which images were refreshed, and which were skipped.
-	Persistent Login: Saves your session data locally. You only have to log in to Civitai once.
-	Persistent Settings: Saves the program settings (your API key, username, browser size), so next time you use the program you don't have to enter them again.

## Requirements
- Python 3.10+ (You likely already have this, since every local AI image generator I know of requires Python)
- See `requirements.txt`

## Installation
1. Clone the repo (Or just download the .py file and the requirements.txt files, put them in a folder to be used just for this program, then open Powershell and change to that new folder)
2. Create a venv for this repo: `python -m venv .venv`
   - This is so what happens in this Python instance doesn't imapact anything else you're doing in Python on your machine, like AI image generation
4. Activate your venv: `.venv\Scripts\Activate.ps1`
   - Do this before you run the program any time you open a new Powershell window to use this program
5. Install dependencies: `python -m pip install -r requirements.txt` alternatively just install Playwright `pip install playwright`
6. Install Chromium browser for Playwright: `playwright install chromium`

## !!! PRIOR TO USAGE !!!
You will need to go to your CivitAI user profile Manage Account page (https://civitai.com/user/account or https://civitai.red/user/account) and get an API key.
1. On the Manage Account page, scroll down almost to the bottom, and under the 'Add API Keys' section you will find a button to 'Add API Key'. Click it.
2. It will ask you what you want to name the API key. Name it Civitai-Refresh-Image-Resources so you know what you use this key for, then click Save.
3. As soon as you click Save, it will show you the API key. Copy and Paste it into a text editor and save it. Save it to the folder where you keep this program. You will need to cpoy/paste this API key into the console the first time you run this program.
4. Once you have saved your API key, continue with the Usage section.

## Usage
1. Open a Powershell window, change to the folder you placed this repository.
2. Make sure to activate your python virtual environment: `.\.venv\Scripts\Activate.ps1`
3. Start the repository's python program: `python Civitai-Refresh-Image-Resources.py`
4. Answer which domain you need to use - civitai.com or civitai.red
5. Answer what size window you want the Chromium browser (default is 1280x720), yes, you can enter your own custom size.
6. Once the Chromium browswer opens, log in to your CivitAI account.
7. Once you're logged in, click the Powershell window again and hit enter to continue the program.
8. The program will prompt you to click the Chromium window again and navigate to your user profile's Posts page.
9. Once on your Posts page, note the number of posts you have next to the Posts tab at the top.
10. Slowly scroll to the bottom of the page, allowing the browser and CivitAI to populate the posts/thumbnails.
    - As you scroll, there will be a number in a RED box in the upper right. This is the number of posts the program has detected. It will increase as you scroll down.
    - Once you're at the bottom of the Posts page, the number in the RED box should match the total number of posts you have.
    - Do NOT scroll back to the top of the page to check! That's why I told you to remember it at the top! :)
12. Once you've scrolled down and the post count is complete, click on the Powershell window again and hit Enter.
13. Let the program do it's work. It will cycle through your posts and click Refresh on the Resources where needed.
   - Be patient.
   - Do NOT scroll in the Chromium window or click on anything.
   - Do NOT minimize the Chromium window!
   - You can use other applications normally, just leave the Powershell and Chromium window operating in the background.
   - It will check each image in each post for lack of resources, clicking Refresh for any that need it.
   - When it is done it will write a summary to the LOG file in that same folder as the program. This will tell you how many posts it worked on, how many images, etc.
14. You can stop the program early by closing the Powershell window, but this will truncate your log and not give you the summary information at the end. You can safely start the program again later, but it will process your posts in order again. Fortunately, it will only click the Refresh Resources button on images that need it (not the ones it has already done in previous runs). So at least it doesn't re-do all that work.

# NOTES

I am *NOT* a programmer!

I wrote this using Google Gemini to generate the code. It is 99% Gemini and 1% my tweaks.

I cannot support this code in any way.

I tested this code on my own CivitAI account. It worked for me quite well. I can't guarantee it will work for you. I only have one account to test it on. That's not a big sample size.

I hope you find this useful. That's why I shared it. I found CivitAI's lack of a resource refresh on a grand scale to be frustrating, so this is my fix/work-around.

Why is this useful?

A while back - maybe spring or summer of 2025 - maybe as late as fall of 2025 - CivitAI's automatic resource detection upon-upload of an image was broken, and thousands of images were uploaded without resources in their data. Also, I have noticed that images I posted a while ago that had resources now don't. Somehow CivitAI 'forgot' them. What does that mean when an image doesn't have resources? It means those images won't appear on the checkpoint, LORA, or embeddings pages. In general that means no one will ever see those images. (The only way to find them, short of going to the user's profile page, would be to search by tag or keyword, and most users don't do that.)

The real purpose of this script is to repair that broken link between your images and the resources used to create them, so your images appear on those resource pages. That way others can see them, like/comment/share/remix and do all those wonderful things that CivitAI lets you do with images - improving your work's visbility and 'driving engagement' (as the kids these days say).

## License
GNU General Public License v3.0
