"""
Copyright 2018 YoongiKim

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import requests
import shutil
from collect_links import CollectLinks
from PIL import Image
import base64
from pathlib import Path
import random


class Sites:
    GOOGLE = 1
    GOOGLE_FULL = 3

    @staticmethod
    def get_text(code):
        if code == Sites.GOOGLE:
            return 'google'
        elif code == Sites.GOOGLE_FULL:
            return 'google'

    @staticmethod
    def get_face_url(code):
        if code == Sites.GOOGLE or Sites.GOOGLE_FULL:
            return "&tbs=itp:face"


class AutoCrawler:
    def __init__(self, skip_already_exist=True, download_path='download', full_resolution=False, 
                 face=False, no_gui=False, proxy_list=None):
        """
        :param skip_already_exist: Skips keyword already downloaded before.
        :param download_path: Download folder path
        :param full_resolution: Download full resolution image instead of thumbnails (slow)
        :param face: Face search mode
        :param no_gui: No GUI mode. Acceleration for full_resolution mode.
        :param proxy_list: The proxy list. Every thread will randomly choose one from the list.
        """
        self.skip = skip_already_exist
        self.download_path = download_path
        self.full_resolution = full_resolution
        self.face = face
        self.no_gui = no_gui
        self.proxy_list = proxy_list if proxy_list and len(proxy_list) > 0 else None

        os.makedirs('./{}'.format(self.download_path), exist_ok=True)

    @staticmethod
    def get_extension_from_link(link, default='jpg'):
        splits = str(link).split('.')
        if len(splits) == 0:
            return default
        ext = splits[-1].lower()
        if ext == 'jpg' or ext == 'jpeg':
            return 'jpg'
        elif ext == 'gif':
            return 'gif'
        elif ext == 'png':
            return 'png'
        else:
            return default

    @staticmethod
    def validate_image(path):   
        try:
            with Image.open(path) as img:
                # Get the format and convert to lowercase
                ext = img.format.lower()
                if ext == 'jpeg':
                    ext = 'jpg'
                return ext
        except Exception:
            return None  # returns None if not valid

    @staticmethod
    def make_dir(dirname):
        current_path = os.getcwd()
        path = os.path.join(current_path, dirname)
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def save_object_to_file(obj, file_path, is_base64=False):
        try:
            with open('{}'.format(file_path), 'wb') as file:
                if is_base64:
                    file.write(obj)
                else:
                    shutil.copyfileobj(obj.raw, file)
        except Exception as e:
            print('Save failed - {}'.format(e))

    @staticmethod
    def base64_to_object(src):
        header, encoded = str(src).split(',', 1)
        data = base64.decodebytes(bytes(encoded, encoding='utf-8'))
        return data

    def download_images(self, keyword, links, site_name, max_count=0):
        self.make_dir('{}/{}'.format(self.download_path, keyword.replace('"', '')))
        success_count = 0

        if max_count == 0:
            max_count = len(links)

        for index, link in enumerate(links):
            if success_count >= max_count:
                break

            try:
                print('Downloading {} from {}: {} / {}'.format(keyword, site_name, success_count + 1, max_count))

                if str(link).startswith('data:image/jpeg;base64'):
                    response = self.base64_to_object(link)
                    ext = 'jpg'
                    is_base64 = True
                elif str(link).startswith('data:image/png;base64'):
                    response = self.base64_to_object(link)
                    ext = 'png'
                    is_base64 = True
                else:
                    response = requests.get(link, stream=True, timeout=10)
                    ext = self.get_extension_from_link(link)
                    is_base64 = False

                no_ext_path = '{}/{}/{}_{}'.format(self.download_path.replace('"', ''), keyword, keyword, str(index).zfill(4))
                path = no_ext_path + '.' + ext
                self.save_object_to_file(response, path, is_base64=is_base64)

                success_count += 1
                del response

                ext2 = self.validate_image(path)
                if ext2 is None:
                    print('Unreadable file - {}'.format(link))
                    os.remove(path)
                    success_count -= 1
                else:
                    if ext != ext2:
                        path2 = no_ext_path + '.' + ext2
                        os.rename(path, path2)
                        print('Renamed extension {} -> {}'.format(ext, ext2))

            except KeyboardInterrupt:
                break
            except Exception as e:
                print('Download failed - ', e)
                continue

    def download_keyword_images(self, keyword, num_images):
        """
        Download images for a specific keyword with specified count.
        
        :param keyword: Search term (string)
        :param num_images: Number of images to download (integer)
        :return: Success status (boolean)
        """
        print(f'Starting download for keyword: "{keyword}" with {num_images} images')
        
        # Create directory for the keyword
        keyword_safe = keyword.replace('"', '')
        keyword_dir = f'{self.download_path}/{keyword_safe}'
        self.make_dir(keyword_dir)
        
        # Check if already completed and skip option is enabled
        google_done_file = os.path.join(os.getcwd(), keyword_dir, 'google_done')
        if os.path.exists(google_done_file) and self.skip:
            print(f'Skipping already completed keyword: {keyword}')
            return True
        
        # Determine site code based on full_resolution setting
        site_code = Sites.GOOGLE_FULL if self.full_resolution else Sites.GOOGLE
        site_name = Sites.get_text(site_code)
        add_url = Sites.get_face_url(site_code) if self.face else ""
        
        try:
            # Initialize Chrome driver with proxy if available
            proxy = None
            if self.proxy_list:
                proxy = random.choice(self.proxy_list)
            
            collect = CollectLinks(no_gui=self.no_gui, proxy=proxy)
            
        except Exception as e:
            print(f'Error occurred while initializing chromedriver - {e}')
            return False
        
        try:
            print(f'Collecting links for "{keyword}" from {site_name}')
            
            # Collect links based on site code
            if site_code == Sites.GOOGLE:
                links = collect.google(keyword, add_url)
            elif site_code == Sites.GOOGLE_FULL:
                links = collect.google_full(keyword, add_url, num_images)
            else:
                print('Invalid Site Code')
                return False
            
            if not links:
                print(f'No links collected for keyword: {keyword}')
                return False
            
            print(f'Collected {len(links)} links. Downloading images...')
            
            # Download images with the specified limit
            self.download_images(keyword, links, site_name, max_count=num_images)
            
            # Create completion marker file
            Path(f'{keyword_dir}/google_done').touch()
            
            print(f'Successfully completed download for "{keyword}": {num_images} images')
            return True
            
        except Exception as e:
            print(f'Exception occurred during download for "{keyword}": {e}')
            return False
        
        finally:
            # Ensure browser is closed
            try:
                collect.browser.quit()
            except:
                pass


if __name__ == '__main__':
    # Test the new download_keyword_images method
    
    print("Testing download_keyword_images method...")
    print("=" * 50)
    
    # Create AutoCrawler instance with test settings
    crawler = AutoCrawler(
        skip_already_exist=False,  # Set to False to always download
        download_path='test_downloads',  # Use separate folder for testing
        full_resolution=False,  # Use thumbnail mode for faster testing
        face=False,
        no_gui=True,  # Headless mode for faster execution
        proxy_list=None
    )
    
    # Test cases
    test_cases = [
        ("ronaldo", 5),
        ("messi", 10),
        ("neymar", 3)
    ]
    
    print(f"Running {len(test_cases)} test cases:")
    print("-" * 30)
    
    results = []
    
    for keyword, num_images in test_cases:
        print(f"\n🔍 Testing: '{keyword}' with {num_images} images")
        print("-" * 40)
        
        try:
            success = crawler.download_keyword_images(keyword, num_images)
            
            if success:
                print(f"✅ SUCCESS: Downloaded images for '{keyword}'")
                results.append((keyword, num_images, "SUCCESS"))
            else:
                print(f"❌ FAILED: Could not download images for '{keyword}'")
                results.append((keyword, num_images, "FAILED"))
                
        except Exception as e:
            print(f"💥 ERROR: Exception occurred for '{keyword}': {e}")
            results.append((keyword, num_images, f"ERROR: {e}"))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("=" * 50)
    
    success_count = 0
    for keyword, num_images, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_icon} {keyword} ({num_images} images): {status}")
        if status == "SUCCESS":
            success_count += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    if success_count == len(results):
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {len(results) - success_count} test(s) failed")
    
    print("\nCheck the 'test_downloads' folder to see downloaded images.")
    print("Each keyword will have its own subfolder.")