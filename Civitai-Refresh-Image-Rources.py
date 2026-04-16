# Civitai-Refresh-Image-Resources.py
# 2026-04-16 v0.2-beta by tomtombombadil using Gemini Pro
# This code is designed to automate refreshing the detected resources on CivitAI.com (and .red) for your user's posted images.
# Often times, CivitAI's post images code fails to detect an image's resouces upon first load. Other times, somehow, CivitAI
# 'forgets' these resouces. This is unfortunate because that means your image is no longer tied to the models/LORAs/embeddings
# that were used to create it, and more importantly, your images will not appear on those resource pages for others to see.
# This code automates the process of refreshing those resource detections, re-linking your images to those resources and
# restoring your images visibility to more users of the site.
#
from playwright.sync_api import sync_playwright
import time
import datetime
import os
import json

# =========================================================
# SELECTORS AND CONSTANTS
# =========================================================
IMAGE_CARD_CONTAINER_SELECTOR = "div.rounded-lg.p-3:has(h3:has-text('Resources'))"
WARNING_TEXT = "Some resources detected in this image could not be matched to models on Civitai"
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

def process_civitai_profile():
    print("\n--- Civitai Resource Auto-Refresher ---")
    
    config = load_config()
    use_saved = False
    
    if config:
        print("\n--- Saved Settings Found ---")
        print(f" Domain:   {config.get('base_domain')}")
        print(f" Username: {config.get('username')}")
        print(f" Resolution: {config.get('res_label', 'Custom')}")
        
        choice = input("\nUse these saved settings? (y/n): ").lower().strip()
        if choice == 'y':
            use_saved = True

    if not use_saved:
        print("\nWhich domain are you targeting?")
        print("1. civitai.com (Standard)")
        print("2. civitai.red (Adult/NSFW)")
        domain_choice = input("Enter choice (1 or 2) [Default 1]: ").strip()
        base_domain = "civitai.red" if domain_choice == "2" else "civitai.com"

        username = input("\nEnter your Civitai username: ").strip()
        if not username: return

        print("\nSelect Browser Window Size:")
        print("1. Default (1280x720)")
        print("2. 1080p (1920x1080)")
        print("3. Maximized (Full Screen)")
        print("4. Custom Dimensions")
        size_choice = input("Enter choice (1-4) [Default 1]: ").strip()

        viewport_settings = {"width": 1280, "height": 720}
        browser_args = ["--disable-blink-features=AutomationControlled"]
        res_label = "Default"

        if size_choice == "2":
            viewport_settings = {"width": 1920, "height": 1080}
            res_label = "1080p"
        elif size_choice == "3":
            viewport_settings = None  
            browser_args.append("--start-maximized")
            res_label = "Maximized"
        elif size_choice == "4":
            try:
                w = int(input("   Enter width (e.g., 1600): "))
                h = int(input("   Enter height (e.g., 900): "))
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

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"CivitaiRefreshLog_{timestamp}.txt"
    
    def write_log(message):
        print(message)
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")

    write_log(f"\n--- Starting Civitai Refresh Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    post_urls = []

    # Start Playwright Phase
    stats = {
        "total_posts_checked": 0,
        "posts_needing_refresh": 0,
        "posts_not_needing_refresh": 0,
        "total_images_refreshed": 0,
        "total_images_skipped": 0
    }

    with sync_playwright() as p:
        user_data_dir = "./civitai_session" 
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
        input("\nPress Enter in this PowerShell window once you are logged in...")

        # Step 2: Navigate to user's Posts tab and inject harvester
        posts_page_url = f"https://{base_domain}/user/{username}/posts"
        write_log(f"\nNavigating to {posts_page_url} for extraction...")
        page.goto(posts_page_url)
        page.wait_for_load_state("domcontentloaded")

        write_log("Injecting background DOM harvester...")
        
        # Javascript payload that runs continuously in the browser background
        harvester_js = r"""
            // Create a floating UI counter
            const counter = document.createElement('div');
            counter.style.cssText = 'position:fixed;top:20px;right:20px;background:#e50914;color:white;padding:12px 20px;z-index:999999;font-weight:bold;font-size:18px;border-radius:8px;box-shadow: 0 4px 6px rgba(0,0,0,0.3);font-family:sans-serif;pointer-events:none;';
            counter.id = 'civitai-harvester-count';
            counter.innerText = 'Posts Found: 0';
            document.body.appendChild(counter);

            // Set up the background collection bucket
            window.civitaiPostIds = new Set();
            
            // Scan the screen every 500ms for post links
            setInterval(() => {
                document.querySelectorAll('a[href*="/posts/"]').forEach(a => {
                    const match = a.href.match(/\/posts\/(\d+)/);
                    if (match) {
                        window.civitaiPostIds.add(match[1]);
                    }
                });
                // Update the floating counter
                document.getElementById('civitai-harvester-count').innerText = 'Posts Found: ' + window.civitaiPostIds.size;
            }, 500);
        """
        page.evaluate(harvester_js)

        print("================================================================")
        print(f"                !!!!! ACTION REQUIRED !!!!!")
        print("Click on the Chromium browser window again. Make sure it is on")
        print("your user's Posts page:")
        print("     https://{base_domain}/user/{username}/posts")
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
        input("scrolling to the bottom of your posts page...")

        # Step 3: Retrieve the harvested IDs
        write_log("\nRetrieving harvested Post IDs from the browser...")
        harvested_ids = page.evaluate("Array.from(window.civitaiPostIds)")
        
        for pid in harvested_ids:
            post_urls.append(f"https://{base_domain}/posts/{pid}/edit")
            
        total_posts_found = len(post_urls)
        write_log(f"\n--- HARVEST COMPLETE ---")
        write_log(f"Total Posts Found: {total_posts_found}")

        if not post_urls:
            write_log("\nERROR: No posts were captured. Exiting.")
            return

        # Step 4: The Refresh Loop
        write_log("\nStarting the conditional refresh loop...")
        for url in post_urls:
            stats["total_posts_checked"] += 1
            write_log(f"\nChecking Post {stats['total_posts_checked']} of {total_posts_found}: {url}")
            post_needed_refresh = False
            
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)
                
                all_image_cards = page.locator(IMAGE_CARD_CONTAINER_SELECTOR)
                card_count = all_image_cards.count()
                
                if card_count > 0:
                    write_log(f" -> Found {card_count} total images in this post.")
                    img_refreshed = 0
                    for i in range(card_count):
                        current_card = all_image_cards.nth(i)
                        
                        if current_card.get_by_text(WARNING_TEXT).is_visible():
                            write_log(f"    -> Image {i+1}: Missing resources detected. Refreshing.")
                            post_needed_refresh = True
                            img_refreshed += 1
                            stats["total_images_refreshed"] += 1
                            
                            current_card.locator("button:has(svg.tabler-icon-refresh)").click()
                            page.wait_for_timeout(2500)
                        else:
                            stats["total_images_skipped"] += 1
                            
                    if post_needed_refresh:
                        stats["posts_needing_refresh"] += 1
                        write_log(f" -> Post complete. Refreshed resources for {img_refreshed} images.")
                    else:
                        stats["posts_not_needing_refresh"] += 1
                        write_log(" -> Post complete. All images already had resources. None required refreshing.")

                else:
                    write_log(" -> No image cards found on this page using the selector.")
                    stats["posts_not_needing_refresh"] += 1
                    
            except Exception as e:
                write_log(f" -> Error processing post: {e}")
                
            time.sleep(4)
            
        write_log("\n" + "="*50)
        write_log("RUN COMPLETE - FINAL SUMMARY")
        write_log("="*50)
        write_log(f"Total Posts Checked:           {stats['total_posts_checked']}")
        write_log(f"Posts Needing Refresh:         {stats['posts_needing_refresh']}")
        write_log(f"Posts NOT Needing Refresh:     {stats['posts_not_needing_refresh']}")
        write_log(f"Total Images Refreshed:        {stats['total_images_refreshed']}")
        write_log(f"Total Images Skipped (OK):     {stats['total_images_skipped']}")
        write_log("="*50)
        write_log(f"A copy of this output has been saved to: {log_filename}")
        
        input("\nScript finished! Press Enter in this PowerShell window to close the browser...")

if __name__ == "__main__":
    process_civitai_profile()
