import os


def get_cropped_docs(user_input):
    needed_images = []
    text_pages = os.listdir("text_pages") if os.path.exists("text_pages") else []
    # Basic run to check for existance
    for text_page in text_pages:
        if user_input.lower() in open("text_pages/" + text_page).read().lower():
            needed_images.append(text_page[:-3] + "png")
    return needed_images
