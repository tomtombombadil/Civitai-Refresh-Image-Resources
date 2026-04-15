from playwright.sync_api import sync_playwright
import time
import re
import datetime
import os

# =========================================================
# SELECTORS AND CONSTANTS
# =========================================================
IMAGE_CARD_CONTAINER_SELECTOR = "div.rounded-lg.p-3:has(h3:has-text('Resources'))"
WARNING_TEXT = "Some resources detected in this image could not be matched to models on Civitai"

def process_civitai_profile():
    print("\n--- Civitai Resource Auto-Refresher Setup ---")
    
    # 1. Domain Selection
    print("\nWhich domain are you targeting?")
    print("1. civitai.com (Standard)")
    print("2. civitai.red (Adult/NSFW)")
    domain_choice = input("Enter choice (1 or 2) [Default 1]: ").strip()
    base_domain = "civitai.red" if domain_choice == "2" else "civitai.com"

    # 2. Username Input
    username = input("\nEnter your Civitai username: ").strip()
    if not username:
        print("Username cannot be blank. Exiting.")
        return
    target_url = f"https://{base_domain}/user/{username}/posts"

    # 3. Window Size Selection
    print("\nWhile Playwright is processing your posts and images, a special Chromium")
    print("browswer window will open, displaying the CivitAI site and your posts,")
    print("as it scrapes and processes the images and resource settings:")
    print("YOU MUST LEAVE THIS WINDOW OPEN AND NOT MINIMIZED!")
    print("You can drag it out of the way, or put it behind other windows and continue")
    print("using your computer normally. Just don't minimize the Chromium window,")
    print("close it, or otherwise click/scroll in the Chromium window.")
    print("\nWith that in mind, how big would you like the browser window to be?")
    print("(The display portion of the window can't be resized.)")
    print("1. 720p (1280x720) - default")
    print("2. 1080p (1920x1080)")
    print("3. Maximized (Full Screen)")
    print("4. Custom Dimensions")
    size_choice = input("Enter choice (1-4) [Default 1]: ").strip()

    viewport_settings = {"width": 1280, "height": 720}
    browser_args = ["--disable-blink-features=AutomationControlled"]

    if size_choice == "2":
        viewport_settings = {"width": 1920, "height": 1080}
    elif size_choice == "3":
        viewport_settings = None  # None allows the maximized flag to take over
        browser_args.append("--start-maximized")
    elif size_choice == "4":
        try:
            w = int(input("   Enter width (e.g., 1600): "))
            h = int(input("   Enter height (e.g., 900): "))
            viewport_settings = {"width": w, "height": h}
        except ValueError:
            print("   Invalid input. Defaulting to 1280x720.")

    # 4. Initialize Logging
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"CivitaiRefreshLog_{timestamp}.txt"
    
    def write_log(message):
        # Print to console and append to log file simultaneously
        print(message)
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")

    write_log(f"--- Starting Civitai Refresh Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    write_log(f"Targeting: {target_url}\n")

    # Tracking Variables
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
            user_data_dir, 
            headless=False, 
            slow_mo=100,
            viewport=viewport_settings,  
            args=browser_args,
            ignore_default_args=["--enable-automation"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("\nLaunching browser...")
        page.goto(target_url)
        
        print("=======================================================")
        print("ACTION REQUIRED:")
        print(f"1. Log in to {base_domain} if you aren't already.")
        print(f"2. Navigate to your User Profile and your Posts page: {target_url}")
        print("3. Wait for the initial page of posts to fully load.")
        print("=======================================================")
        
        input("\nWhen the first page of posts is fully loaded, press Enter in this PowerShell window to begin scraping...")
        
        write_log("Taking over the browser to scroll and collect posts...")
        post_urls = set()
        last_count = 0
        
        # 1. Scraping Phase: Collect Post Edit URLs
        for scroll_attempt in range(150):
            links = []
            
            for retry in range(3):
                try:
                    links = page.locator("a[href*='/posts/']").evaluate_all("elements => elements.map(e => e.href)")
                    break 
                except Exception:
                    page.wait_for_timeout(1000) 
            
            for link in links:
                match = re.search(r'/posts/(\d+)', link)
                if match:
                    post_id = match.group(1)
                    post_urls.add(f"https://{base_domain}/posts/{post_id}/edit")
            
            page.keyboard.press("End")
            page.wait_for_timeout(10000) 
            
            current_count = len(post_urls)
            if current_count == last_count:
                page.keyboard.press("End")
                page.wait_for_timeout(10000)
                
                for retry in range(3):
                    try:
                        links = page.locator("a[href*='/posts/']").evaluate_all("elements => elements.map(e => e.href)")
                        break
                    except Exception:
                        page.wait_for_timeout(1000)
                        
                for link in links:
                    match = re.search(r'/posts/(\d+)', link)
                    if match:
                        post_id = match.group(1)
                        post_urls.add(f"https://{base_domain}/posts/{post_id}/edit")
                        
                if len(post_urls) == last_count:
                    break 
                    
            last_count = len(post_urls)
            
        write_log(f"Finished scrolling. Collected {len(post_urls)} unique posts.\n")
        
        if len(post_urls) == 0:
            write_log("No posts found! Ensure you were on the 'Posts' tab.")
            input("\nScript paused. Press Enter in this PowerShell window to close the browser...")
            return

        # 2. Clicking Phase: Start the targeted refresh loop
        write_log("Starting the conditional refresh loop...")
        
        for url in list(post_urls):
            write_log(f"\nChecking Post: {url}")
            stats["total_posts_checked"] += 1
            post_needed_refresh = False
            
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)
            except Exception as load_err:
                write_log(f" -> Could not load page. Skipping. Error: {load_err}")
                continue
            
            try:
                all_image_cards = page.locator(IMAGE_CARD_CONTAINER_SELECTOR)
                card_count = all_image_cards.count()
                
                if card_count > 0:
                    write_log(f" -> Found {card_count} total images in this post.")
                    images_refreshed_this_post = 0
                    
                    for i in range(card_count):
                        current_card = all_image_cards.nth(i)
                        
                        if current_card.get_by_text(WARNING_TEXT).is_visible():
                            write_log(f"    -> Image {i+1}: Missing resources detected. Clicking refresh.")
                            post_needed_refresh = True
                            images_refreshed_this_post += 1
                            stats["total_images_refreshed"] += 1
                            
                            current_card.locator("button:has(svg.tabler-icon-refresh)").click()
                            page.wait_for_timeout(2500)
                        else:
                            stats["total_images_skipped"] += 1
                            
                    if post_needed_refresh:
                        stats["posts_needing_refresh"] += 1
                        write_log(f" -> Post complete. Refreshed {images_refreshed_this_post} missing images.")
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
