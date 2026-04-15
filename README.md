# Civitai-Refresh-Image-Resources
This Python script will automate cycling through your posts and images and refresh the resource detection for images that are missing resources. It uses Playwright to simulate YOU going through your own posts and clicking the Resource Refresh button yourself. The script works slowly (CivitAI's site can be very slow to load posts and images) to account for the site slowness and to keep it friendly towards the CivitAI servers.

First things first: I am NOT a programmer. Google's Gemini helped me write this. It is 99% Gemini code and 1% me tweaking it. That means I can't support it, nor really help you if you have issues. This code is presented because I found it useful and I hope you do too.

What it does:
This python program will go through your posts on CivitAI's site, check each post, and each image in each post to see if this message is present in the Resources section of the image data: "Some resources detected in this image could not be matched to models on Civitai". If it finds that message, it will click the Refresh button for the Resources for that image. Generally speaking, CivitAI's latest code will find the right resource data in the metadata of your image and properly populate the Resources section of that image's data.

Why is this useful?
A while back - maybe spring or summer of 2025 - CivitAI's automatic resource detection upon-upload of an image was broken, and thousands of images were uploaded without resources in their data. What does that mean? It means those images won't appear on the checkpoint, LORA, or embeddings pages, which, in general means no one will ever see those images. (The only way to find them, short of going to the user's profile page, would be to search by tag or keyword, and most users don't do that.

So the real purpose of this script is to repair that broken link between your images and the resources used to create them, so your images appear on those resource pages. That way others can see them, like/comment/share/remix and do all those wonderful things that CivitAI lets you do with images - improving your work's visbility and 'driving engagement' (as the kids these days say).

Requirements:
This is a python program. You need to have Python installed. Since you generate AI images and post them on CivitAI, you almost certainly already have python installed. Open a Powershell window and enter this command to check:
  python --version
If you get something similar to this: "Python 3.10.6" back, congrats, you have python installed.

Before you can run this script, you also need to create a working directory/folder for it and a Python VENV for it to work with. We create a VENV (virtual environment) so that what we do with Python here doesn't interfere with any other python-based environments that you may have setup (such as Automatic1111, Forge, ReForge, ComfyUI, etc.).

Create a folder to work in. Download the python program from this repository and place it in that folder. Then open Powershell and change to that folder. Use this command to create the VENV:
  python -m venv .venv

Every time you want to use this python program, you need to Activate the venv first, using this command from the Powershell window in that folder:
  .\.venv\Scripts\Activate.ps1
The Powershell prompt will show this: "(.venv)" at the beginning, indicating you're not working inside the virtual environment.

Next install playwright with this command:
  pip install playwright
That will take a few seconds, then install the Chromium browser for Playwright with this command:
  playwright install chromium
That will take a few seconds more.

Now you're ready to run the script using this command:
  python Civitai-Refresh-Image-Resources.py

It will tell you some things, ask you some things, and then proceed to open the Chromium browswer and pause the program while you login to CivitAi and go to your Profile's Posts page. Once you're there and the slow CivitAI servers have loaded the first screen of your posts, click on the Powershell window again to activate it and hit enter to let the program know it can get started.

Playwright will control the Chromium browser window, behaving like a human being clicking through the CivitAI site. You're free to watch it process, but LEAVE THE CHROMIUM WINDOW OPEN - DO NOT MINIMIZE IT! You can still use your computer. Just leave the Chromium window alone. Drag it out of the way or Alt-Tab to bring another application to the front and do whatever you need to do. Just don't minimize the Chromium window, and don't click or scroll in the Chromium window.

In the Powershell window, it will be scrolling information on the screen as it works. This information is also getting logged. The log file can be found in the same folder as the python program.

The whole process is SLOW because it needs to leave time for the CivitAI site to respond, and we also don't want to be a jerk and hammer the CivitAI servers. So just let it run. It will have a summary at the end of the log when it is done.
