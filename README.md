# Civitai-Refresh-Image-Resources

This python program will cycle through your CivitAI posts and images, refreshing the Resource detection on images without resources listed. This corrects a problem CivitAI has had for a while now. In the past, and ocassionaly now, CivitAI's post-an-image process fails to detect or write the resources detected to the CivitAI database. Also, sometimes it 'forgets' the resources tied to an image. This breaks the connection between your images and the resources (checkpoints/LORAs/embeddings) that were used to create the image. More importantly (to me at least), it means your image/post will no longer appear on that resource's page, which is where most users find images - or at least MANY users find images that way. So this will increase engagement with your images and make them more visible to the community at large.

The purpose of this program is to fix that problem. It goes into each of your posts, and clicks the Refresh button for each image that needs it.

## Features

- **Supports both CivitAI domains** — works with civitai.com (standard) and civitai.red (adult/NSFW content).
- **Interactive setup** — no need to edit the code. The script asks for your username, preferred domain, and desired browser window size right in the terminal.
- **Smart detection** — doesn't blindly click every button. It reads each image card and only triggers a refresh on images displaying the "resources could not be matched" warning, saving time and reducing server load.
- **Persistent login** — saves your browser session data locally in a `crir_session` folder. You only have to log in to CivitAI once; future runs reuse the cached session.
- **Persistent settings** — saves your configuration (username, domain, browser size) to `crir_config.json` so you don't re-enter them every time.
- **Post list caching** — after you scroll through your posts page once, the harvested post URLs are saved to `crir_saved_posts.json`. Future runs can reuse this list instead of requiring you to scroll again.
- **Progress tracking and resume** — each successfully processed post is recorded in `crir_processed_posts.txt`. On the next run, you can skip already-processed posts and pick up where you left off.
- **Automatic retry** — posts that fail to load (CivitAI timeouts, server errors) are collected and retried at the end of the run. Posts that fail twice are saved to a `crir_failed_posts` file for manual investigation.
- **Error post tracking** — posts that load but contain zero image cards (an anomalous server response) are tracked separately as error posts in the summary.
- **Graceful quit** — press Q at any time during processing. The script finishes the current post, saves all progress, writes the summary to the log, and exits cleanly. You can resume on the next run.
- **Detailed logging** — every run generates a timestamped `.log` file with per-image detail and a final summary showing posts checked, images refreshed, images skipped, error posts, and permanently failed posts.
- **Anti-detection** — disables Chromium's automation flags to reduce the chance of being flagged by CivitAI's bot detection.

## Requirements

- **Windows** (the graceful Q-to-quit feature uses `msvcrt`, which is Windows-only; the rest of the script would work on other platforms but has only been tested on Windows)
- **Python 3.10+** (you likely already have this if you run any local AI image generator)
- **Playwright** for Python (browser automation)

## Installation

1. **Get the code.** Clone this repo, or just download `Civitai-Refresh-Image-Resources.py` and `requirements.txt` into a new folder.

2. **Create a Python virtual environment.** This keeps the dependencies isolated from your other Python projects (like your AI image generator).
   ```
   python -m venv .venv
   ```

3. **Activate the virtual environment.** You'll need to do this every time you open a new PowerShell window to run the program.
   ```
   .venv\Scripts\Activate.ps1
   ```

4. **Install the dependencies.** Only do this once for your intial install.
   ```
   python -m pip install -r requirements.txt
   ```
   Or if you prefer, just install Playwright directly:
   ```
   pip install playwright
   ```

5. **Install the Chromium browser for Playwright.** Only do this once for your initial install.
   ```
   playwright install chromium
   ```

That's it. You're ready to go.

## Usage

1. Open PowerShell and navigate to the folder where you placed the program.

2. Activate your virtual environment:
   ```
   .\.venv\Scripts\Activate.ps1
   ```

3. Run the program:
   ```
   python Civitai-Refresh-Image-Resources.py
   ```

4. **First-time you run the program:** The program will ask you:
   - Which domain — civitai.com or civitai.red
   - Your CivitAI username
   - What browser window size you want (default is 720p, or enter a custom size)
   - These settings are saved for future runs, so you don't have to re-enter this information every time.

5. **Login:** A Chromium browser window will open. Log in to your CivitAI account. If you've logged in during a previous run, your session may still be cached and you'll already be logged in. Once you're logged in, click back on the PowerShell window and press Enter to continue.

6. **Harvest your posts:** The program will navigate to your Posts page. (Instructions will appear in the Powershell console, but they're shown here too.)
   - Note the number of posts shown next to the Posts tab at the top of your Posts page. That's how many Posts you have on CivitAI.
   - Slowly scroll to the bottom of the page. A red counter in the upper-right corner shows how many posts have been detected.
   - Allow time for thumbnails to load as you scroll.
   - Once you get to the bottom of your Posts page, the red counter number should match your Posts number from the top of the page.
   - **Do NOT scroll back up** — this can cause posts to be missed.
   - Click the PowerShell window and press Enter.
   - On future runs, the program will offer to reuse the saved post list so you can skip this step.

7. **Let it run.** The program will cycle through your posts and click Refresh on images that need it.
   - Be patient — each post takes time to load and process. (about 1 minute for a Post with 20 images to refresh)
   - Do NOT click or scroll in the Chromium window.
   - Do NOT minimize the Chromium window.
   - You can use other applications normally; just leave PowerShell and Chromium running behind your other windows.
   - **Press Q at any time** to quit gracefully. The program will finish processing the rest of the images on that Post page, then quit. Your progress is saved so you can resume later.

8. **Review the results.** When the run completes (or you quit with Q), a summary is displayed showing how many posts were checked, images refreshed, images skipped, and any errors. A detailed log file is saved in the same folder as the program and shows the same summary that was shown in the console (Powershell).

## Files Created

The program creates several files in its working directory. All filenames begin with `crir_` (short for Civitai-Refresh-Image-Resources) so they're easy to identify:

| File | Purpose |
|------|---------|
| `crir_config.json` | Your saved settings (username, domain, browser size) |
| `crir_saved_posts.json` | Cached list of post URLs from the harvesting step |
| `crir_processed_posts.txt` | Running list of successfully processed post URLs (for resume) |
| `crir_YYYYMMDD_HHMMSS.log` | Detailed log for each run |
| `crir_failed_posts_YYYYMMDD_HHMMSS.txt` | URLs of posts that failed even after retry (if any) |
| `crir_session/` | Browser session data (keeps you logged in between runs) |

## Tips

- **First run:** Expect it to take a while if you have hundreds of posts. The program processes every post to establish a baseline. Future runs will be much faster since you can skip already-processed posts.
- **If you add new posts**, you'll want to re-harvest your post list (answer "n" when asked to use the saved list) so the new posts are included. But also respond with a Y when asked if you want to skip posts that have already been processed. No need to check them again, you just want to process your new Posts.
- **To start completely fresh**, delete the `crir_processed_posts.txt` file, or choose N when asked if you want to skip previously processed Posts.

## Notes

I am *not* a programmer. 

I built this with the help of Google Gemini Pro (initial code generation) and Claude Opus 4.6 Extended (bug fixes, code review, and feature development). The code is 99% AI created and 1% my tweaks.

I cannot provide technical support for this code. This code is meant to be run on Windows. I don't know if it will work on Linux or Mac OS. Feel free to fork it and make it great on other platforms!

I tested this on my own CivitAI account with several hundred posts and thousands of images. It found that **more than 52% of my images** had NO resource links and this program successfully refreshed them. Your mileage may vary — I only have one account to test with. That is a small sample size.

I hope you find this useful. I found CivitAI's lack of a bulk resource-refresh feature to be frustrating, so this is my workaround. The goal is simple: repair the broken links between your images and the resources used to create them, so your work gets the visibility it deserves.

## License

GNU General Public License v3.0
