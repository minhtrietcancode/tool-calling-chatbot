import os

def rename_images(directory):
    for class_name in ["cat", "dog"]:
        path = os.path.join(directory, class_name)
        if not os.path.exists(path):
            print(f"Directory {path} does not exist. Skipping.")
            continue

        print(f"Renaming images in {path}...")
        images = [f for f in os.listdir(path) if f.startswith("google_") and not f.endswith("google_done")]
        images.sort() # Ensure consistent ordering

        for i, filename in enumerate(images):
            # Extract file extension
            _, ext = os.path.splitext(filename)
            new_name = f"{class_name}_{i+1:04d}{ext}"
            old_path = os.path.join(path, filename)
            new_path = os.path.join(path, new_name)

            try:
                os.rename(old_path, new_path)
                print(f"Renamed {filename} to {new_name}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    download_dir = "download"
    rename_images(download_dir)
