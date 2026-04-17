# Civitai-Refresh-Image-Resources.py
# 2026-04-16 v1.0 by tomtombombadil using Gemini Pro and Claude Opus v4.6 Extended
# This code is designed to automate refreshing the detected resources on CivitAI.com (and .red) for your user's posted images.
# Often times, CivitAI's post images code fails to detect an image's resources upon first load. Other times, somehow, CivitAI
# 'forgets' these resources. This is unfortunate because that means your image is no longer tied to the models/LORAs/embeddings
# that were used to create it, and more importantly, your images will not appear on those resource pages for others to see.
# This code automates the process of refreshing those resource detections, re-linking your images to those resources and
# restoring your images' visibility to more users of the site.
#
from playwright.sync_api import sync_playwright
import time
import datetime
import os
import json

# msvcrt provides non-blocking keypress detection on Windows.
# If unavailable (Linux/Mac), the Q-to-quit feature is simply disabled.
try:
    import msvcrt
    QUIT_KEY_AVAILABLE = True
except ImportError:
    QUIT_KEY_AVAILABLE = False

# =========================================================
# SELECTORS AND CONSTANTS
# =========================================================
IMAGE_CARD_CONTAINER_SELECTOR = "div.rounded-lg.p-3:has(h3:has-text('Resources'))"
WARNING_TEXT = "Some resources detected in this image could not be matched to models on Civitai"
CONFIG_FILE = "crir_config.json"
SAVED_POSTS_FILE = "crir_saved_posts.json"
PROCESSED_POSTS_FILE = "crir_processed_posts.txt"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

def append_to_processed_file(url):
    """Safely appends a successfully processed URL to the tracking file."""
    try:
        with open(PROCESSED_POSTS_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
    except Exception:
        pass

def check_for_quit_key():
    """Check if Q has been pressed (non-blocking). Drains the input buffer
    and returns True if Q was found among the buffered keypresses.
    Call this after any long operation to catch a Q pressed during it."""
    if not QUIT_KEY_AVAILABLE:
        return False
    found_quit = False
    while msvcrt.kbhit():
        key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        if key == 'q':
            found_quit = True
    return found_quit

def wait_with_quit_check(seconds):
    """Wait for the specified duration, checking for Q keypress every 0.5s.
    Returns True if Q was pressed, False otherwise. Any non-Q keypresses
    are consumed and discarded."""
    if not QUIT_KEY_AVAILABLE:
        time.sleep(seconds)
        return False
    
    intervals = int(seconds / 0.5)
    for _ in range(intervals):
        time.sleep(0.5)
        if check_for_quit_key():
            return True
    return False

def process_civitai_profile():
    print("\n--- Civitai Resource Auto-Refresher ---")
    
    config = load_config()
    use_saved = False
    
    if config:
        print("\n--- Settings From Last Time Found ---")
        print(f" Domain:   {config.get('base_domain')}")
        print(f" Username: {config.get('username')}")
        print(f" Resolution: {config.get('res_label', 'Custom')}")
        
        choice = input("\nUse these saved settings? (y/n): ").lower().strip()
        if choice == 'y':
            use_saved = True

    if not use_saved:
        print("\nWhich CivitAI site are you using?")
        print("1. civitai.com (Standard)")
        print("2. civitai.red (Adult/NSFW Content)")
        domain_choice = input("Enter choice (1 or 2) [Default 1]: ").strip()
        base_domain = "civitai.red" if domain_choice == "2" else "civitai.com"

        username = input("\nEnter your Civitai username: ").strip()
        if not username: return

        print("\nSelect Browser Window Size:")
        print("1. 720p (1280x720) (Default)")
        print("2. 1080p (1920x1080)")
        print("3. Maximized (Full Screen)")
        print("4. Enter your own size")
        size_choice = input("Enter choice (1-4) [Default 1]: ").strip()

        viewport_settings = {"width": 1280, "height": 720}
        browser_args = ["--disable-blink-features=AutomationControlled"]
        res_label = "Default"

        if size_choice == "2":
            viewport_settings = {"width": 1910, "height": 960}
            res_label = "1080p"
        elif size_choice == "3":
            viewport_settings = None  
            browser_args.append("--start-maximized")
            res_label = "Maximized"
        elif size_choice == "4":
            try:
                w = int(input("   Enter browser viewport width (e.g., 1600): "))
                h = int(input("   Enter browser viewport height (e.g., 900): "))
                viewport_settings = {"width": w, "height": h}
                res_label = f"Custom ({w}x{h})"
            except ValueError:
                print("   Invalid input. Defaulting to 1280x720.")
        
        config = {
            "base_domain": base_domain,
            "username": username,
            "viewport_settings": viewport_settings,
            "browser_args": browser_args,
            "res_label": res_label
        }
        save_config(config)
    else:
        base_domain = config['base_domain']
        username = config['username']
        viewport_settings = config['viewport_settings']
        browser_args = config['browser_args']

    # Prompt for saved post list if it exists
    use_saved_urls = False
    saved_post_urls = []
    
    if os.path.exists(SAVED_POSTS_FILE):
        try:
            with open(SAVED_POSTS_FILE, "r") as f:
                saved_data = json.load(f)
                if "urls" in saved_data and "timestamp" in saved_data:
                    print("\n--- Saved Posts List Found ---")
                    print(f" Saved on: {saved_data['timestamp']}")
                    print(f" Posts:    {len(saved_data['urls'])}")
                    print("\nUse this saved Post List instead of scrolling & scraping")
                    choice = input("your Posts page on the CivitAI site again? (y/n): ").lower().strip()
                    if choice == 'y':
                        use_saved_urls = True
                        saved_post_urls = saved_data['urls']
        except Exception:
            pass 

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"crir_{timestamp}.log"
    
    def write_log(message):
        print(message)
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")

    write_log(f"\n--- Starting Civitai Image Refresh at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    post_urls = []

    # Start Playwright Phase
    stats = {
        "total_posts_checked": 0,
        "posts_needing_refresh": 0,
        "posts_not_needing_refresh": 0,
        "error_posts": 0,
        "total_images_refreshed": 0,
        "total_images_skipped": 0,
        "total_images_checked": 0
    }

    with sync_playwright() as p:
        user_data_dir = "./crir_session" 
        browser = p.chromium.launch_persistent_context(
            user_data_dir, headless=False, slow_mo=100, 
            viewport=viewport_settings, args=browser_args, 
            ignore_default_args=["--enable-automation"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Step 1: Authentication Check
        page.goto(f"https://{base_domain}")
        print("================================================================")
        print(f"                !!!!! ACTION REQUIRED !!!!!")
        print("In the new Chromium window that just opened, login to your")
        print("CivitAI account. If you have already logged in during previous")
        print("uses of this program, it may have cached your login.")
        print("     Just make sure you're logged in before continuing!")
        print("================================================================")
        input("\nPress Enter in this PowerShell window once you are logged in.")

        if not use_saved_urls:
            # Step 2: Navigate to user's Posts tab and inject harvester
            posts_page_url = f"https://{base_domain}/user/{username}/posts"
            write_log(f"\nNavigating to {posts_page_url} for extraction...")
            page.goto(posts_page_url)
            page.wait_for_load_state("domcontentloaded")

            write_log("Injecting background DOM harvester...")
            
            harvester_js = r"""
                const counter = document.createElement('div');
                counter.style.cssText = 'position:fixed;top:20px;right:20px;background:#e50914;color:white;padding:12px 20px;z-index:999999;font-weight:bold;font-size:18px;border-radius:8px;box-shadow: 0 4px 6px rgba(0,0,0,0.3);font-family:sans-serif;pointer-events:none;';
                counter.id = 'civitai-harvester-count';
                counter.innerText = 'Posts Found: 0';
                document.body.appendChild(counter);

                window.civitaiPostIds = new Set();
                
                setInterval(() => {
                    document.querySelectorAll('a[href*="/posts/"]').forEach(a => {
                        const match = a.href.match(/\/posts\/(\d+)/);
                        if (match) {
                            window.civitaiPostIds.add(match[1]);
                        }
                    });
                    document.getElementById('civitai-harvester-count').innerText = 'Posts Found: ' + window.civitaiPostIds.size;
                }, 500);
            """
            page.evaluate(harvester_js)

            print("================================================================")
            print(f"                !!!!! ACTION REQUIRED !!!!!")
            print("Click on the Chromium browser window again. Make sure it is on")
            print("your user's Posts page:")
            print(f"     https://{base_domain}/user/{username}/posts")
            print("Take note of the number of posts you have on CivitAI. That number")
            print("is shown at the top of the page, next to the Posts tab.")
            print("Carefully scroll down through your posts. As you scroll, you will")
            print("see a post counter in RED in the upper right corner, counting up.")
            print("Make sure to allow the page time to load all the post's images.")
            print("Once you get to the bottom of your Posts page, the number should")
            print("match the number of posts you noted at the top of the page.")
            print("Do NOT scroll back up to check the number.")
            print("================================================================")
            print("\nPress Enter in this PowerShell window when you have finished")
            input("scrolling to the bottom of your posts page.")

            # Step 3: Retrieve the harvested IDs
            write_log("\nRetrieving harvested Post IDs from the browser...")
            harvested_ids = page.evaluate("Array.from(window.civitaiPostIds)")
            
            for pid in harvested_ids:
                post_urls.append(f"https://{base_domain}/posts/{pid}/edit")
                
            write_log(f"\n--- CivitAI POST ID HARVEST COMPLETE ---")
            write_log(f"Total Posts Found: {len(post_urls)}")

            if not post_urls:
                write_log("\nERROR: No posts were captured. Exiting.")
                return
                
            try:
                with open(SAVED_POSTS_FILE, "w") as f:
                    json.dump({
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                        "urls": post_urls
                    }, f, indent=4)
                write_log("Saved newly harvested posts to local file for future use.")
            except Exception as e:
                write_log(f"Warning: Could not save posts to file: {e}")

        else:
            post_urls = saved_post_urls
            write_log(f"\n--- USING SAVED HARVEST ---")
            write_log(f"Loaded {len(post_urls)} posts from {SAVED_POSTS_FILE}")


        # =====================================================================
        # Step 3.5: Processed History Check
        # =====================================================================
        if os.path.exists(PROCESSED_POSTS_FILE):
            try:
                with open(PROCESSED_POSTS_FILE, "r", encoding="utf-8") as f:
                    processed_urls = set(line.strip() for line in f if line.strip())
                
                if processed_urls:
                    print("\n================================================================")
                    print(f" Found {len(processed_urls)} posts that were successfully processed")
                    print(" during previous runs.")
                    print("================================================================")
                    skip_choice = input("Would you like to SKIP these posts for this run? (y/n) [Default y]: ").strip().lower()
                    
                    if skip_choice != 'n':
                        # Filter out the already processed URLs
                        post_urls = [url for url in post_urls if url not in processed_urls]
                        write_log(f"\n{len(processed_urls)} previously processed posts will not be processed this run.")
                    else:
                        write_log("\nUser elected to re-process all posts. Clearing history.")
                        # Wipe the history file clean
                        open(PROCESSED_POSTS_FILE, 'w').close()
            except Exception as e:
                write_log(f"\nWarning: Could not read processed posts file: {e}")

        total_posts_found = len(post_urls)
        if total_posts_found == 0:
            write_log("\nAll posts have already been successfully processed. Nothing to do!")
            input("\nProcess Complete! Press Enter to close this window.")
            return

        write_log(f"Remaining posts to check this run: {total_posts_found}")

        # =====================================================================
        # CORE CHECKING FUNCTION
        # =====================================================================
        def check_post_url(url, current_num, total_num, is_retry=False):
            prefix = "Retrying" if is_retry else "Checking"
            write_log(f"\n{prefix} Post {current_num} of {total_num}: {url}")
            
            try:
                page.goto(url, timeout=45000)
                
                cards_loaded = True
                try:
                    page.wait_for_selector(IMAGE_CARD_CONTAINER_SELECTOR, state="attached", timeout=25000)
                except Exception:
                    cards_loaded = False
                
                page.wait_for_timeout(1000)
                
                all_image_cards = page.locator(IMAGE_CARD_CONTAINER_SELECTOR)
                card_count = all_image_cards.count()
                
                if not cards_loaded and card_count == 0:
                    write_log("  Timeout: Image cards failed to load from CivitAI. Adding this Post to retry list.")
                    return False
                
                if card_count > 0:
                    write_log(f"  Found {card_count} total images in this post.")
                    img_refreshed = 0
                    post_needed_refresh = False
                    
                    for i in range(card_count):
                        current_card = all_image_cards.nth(i)
                        
                        if current_card.get_by_text(WARNING_TEXT).is_visible():
                            write_log(f"     Image {i+1:02d}: No resources detected => REFRESHING")
                            post_needed_refresh = True
                            img_refreshed += 1
                            stats["total_images_refreshed"] += 1
                            
                            current_card.locator("button:has(svg.tabler-icon-refresh)").click()
                            page.wait_for_timeout(2500)
                        else:
                            write_log(f"     Image {i+1:02d}: No refresh required.")
                            stats["total_images_skipped"] += 1
                            
                    if post_needed_refresh:
                        stats["posts_needing_refresh"] += 1
                        write_log(f"  Post complete. {img_refreshed} images refreshed.")
                    else:
                        stats["posts_not_needing_refresh"] += 1
                        write_log("  Post complete. No images requiring refresh detected.")
                else:
                    if is_retry:
                        write_log("  ERROR: No image cards found on this page (retry failed). Marking as error post.")
                        stats["error_posts"] += 1
                    else:
                        write_log("  ERROR: No image cards found on this page! Adding to retry list.")
                    return False
                    
                return True
                
            except Exception as e:
                write_log(f"  ERROR: Can't process post (Timeout/Crash): {e}")
                return False

        # =====================================================================
        # Step 4: The Refresh Loop
        # =====================================================================
        failed_posts = []
        user_quit = False
        
        write_log("\nStarting the conditional refresh loop...")
        if QUIT_KEY_AVAILABLE:
            print("(Press Q at any time to quit after the current post finishes processing.)")
        for idx, url in enumerate(post_urls, 1):
            stats["total_posts_checked"] += 1
            success = check_post_url(url, idx, total_posts_found)
            
            if success:
                append_to_processed_file(url)
            else:
                failed_posts.append(url)
            
            # Check if Q was pressed during post processing
            if check_for_quit_key():
                write_log(f"\n--- User requested quit after post {idx} of {total_posts_found} ---")
                user_quit = True
                break
                
            if idx < total_posts_found:
                print("\n >>>>> Press Q to quit after this post is processed <<<<<")
                if wait_with_quit_check(1):
                    write_log(f"\n--- User requested quit after post {idx} of {total_posts_found} ---")
                    user_quit = True
                    break
            
        # =====================================================================
        # Step 5: Retry Phase for Failed URLs
        # =====================================================================
        if failed_posts and not user_quit:
            print("\n================================================================")
            print(f" {len(failed_posts)} posts failed to load due to timeouts or site errors.")
            print("================================================================")
            write_log(f"\n--- {len(failed_posts)} POSTS FAILED TO LOAD ---")
            
            retry_choice = input("Would you like to retry these failed posts now? (y/n): ").strip().lower()
            if retry_choice == 'y':
                write_log("\n--- RETRYING FAILED POSTS ---")
                still_failed = []
                retry_total = len(failed_posts)
                
                for idx, url in enumerate(failed_posts, 1):
                    success = check_post_url(url, idx, retry_total, is_retry=True)
                    if success:
                        append_to_processed_file(url)
                    else:
                        still_failed.append(url)
                    
                    # Check if Q was pressed during post processing
                    if check_for_quit_key():
                        write_log(f"\n--- User requested quit during retry, after post {idx} of {retry_total} ---")
                        user_quit = True
                        break
                    
                    if idx < retry_total:
                        print("\nPress Q to quit after this post is processed.\n")
                        if wait_with_quit_check(4):
                            write_log(f"\n--- User requested quit during retry, after post {idx} of {retry_total} ---")
                            user_quit = True
                            break
                
                # If user quit mid-retry, preserve the un-attempted posts so they
                # appear in the failed posts file and summary counts rather than
                # silently vanishing.
                if user_quit:
                    still_failed.extend(failed_posts[idx:])
                
                failed_posts = still_failed 

            if failed_posts:
                fail_filename = f"crir_failed_posts_{timestamp}.txt"
                try:
                    with open(fail_filename, "w", encoding="utf-8") as f:
                        for url in failed_posts:
                            f.write(url + "\n")
                    write_log(f"\nSaved {len(failed_posts)} permanently failed posts to {fail_filename} for manual investigation.")
                except Exception as e:
                    write_log(f"ERROR: Could not save failed posts to file: {e}")
            else:
                write_log("\nAll retried posts processed successfully!")
            
        stats["total_images_checked"] = stats["total_images_skipped"] + stats["total_images_refreshed"]
        write_log("\n" + "="*50)
        if user_quit:
            write_log("RUN STOPPED BY USER - PARTIAL SUMMARY")
        else:
            write_log("RUN COMPLETE - FINAL SUMMARY")
        write_log("="*50)
        write_log(f"Posts NOT Needing Refresh:     {stats['posts_not_needing_refresh']}")
        write_log(f"Posts Needing Refresh:         {stats['posts_needing_refresh']}")
        write_log(f"Posts Permanently Failed:      {len(failed_posts)}")
        write_log(f"  (Error Posts - No Cards):    {stats['error_posts']}")
        write_log("======================================")
        write_log(f"Total Posts Checked:           {stats['total_posts_checked']}")

        write_log(f"\nTotal Images Skipped -") 
        write_log(f"  (Didn't need refreshing):    {stats['total_images_skipped']}")
        write_log(f"Total Images Refreshed:        {stats['total_images_refreshed']}")
        write_log("======================================")
        write_log(f"Total Images Checked:          {stats['total_images_checked']}")

        write_log("="*50)
        write_log(f"A copy of this output has been saved to: {log_filename}")
        
        input("\nScript finished! Press Enter in this PowerShell window to close the browser...")

if __name__ == "__main__":
    process_civitai_profile()
