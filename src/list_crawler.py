
def create_directory(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def does_file_exist(path):
    return os.path.isfile(path)

def write_to_file(path,data):
   with open(path, 'a') as file:
        file.write(data + '\n')

def create_new_file(path):
    f = open(path,'w')
    f.write("")
    f.close()

def get_details(directory, url):
    driver.get(url)
    title = driver.find_element_by_class_name('post-title')
    print('\nTitle \n')
    write_to_file(directory + '/articles.txt', "\n Title: \n")
    print(str(title.text))
    write_to_file(directory + '/articles.txt', title.text)
    try:
        paragraphs = driver.find_element_by_class_name('tz-paragraph')
        print('\nParagraphs \n')
        write_to_file(directory + '/articles.txt', "\n Paragraphs: \n")
        print(str(paragraphs.text))
        write_to_file(directory + '/articles.txt', paragraphs.text)
    except NoSuchElementException:
        print('\nParagraphs \n')
        write_to_file(directory + '/articles.txt', "\n Paragraphs: \n")
        print('Empty')
        write_to_file(directory + '/articles.txt', '\n Empty \n')
    try:
        comments = driver.find_elements_by_class_name('reply-detail')
        print('\nComments \n')
        write_to_file(directory + '/articles.txt', "\n Comments: \n")
        for comment in comments:
            print(str(comment.text) + '\n')
            write_to_file(directory + '/articles.txt', comment.text)
    except NoSuchElementException:
        print('\nComments \n')
        write_to_file(directory + '/articles.txt', "\n Comments: \n")
        print('Empty')
        write_to_file(directory + '/articles.txt', "\n Empty \n")
    try:
        subcomments = driver.find_elements_by_class_name('reply-sub-front')
        print('\nSubComments \n')
        write_to_file(directory + '/articles.txt', "\n SubComments: \n")
        for subcomment in set(subcomments):
            print(str(subcomment.text) + '\n')
            write_to_file(directory + '/articles.txt', subcomment.text)
    except NoSuchElementException:
        print('\nSubComments \n')
        write_to_file(directory + '/articles.txt', "\n SubComments: \n")
        print('Empty')
        write_to_file(directory + '/articles.txt', "\n Empty \n")
    driver.close()
    

def main_scraper(url,directory):
    driver.get(url)
    continue_link = driver.find_element_by_tag_name('a')
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in set(elems):
        if 'thread' and '6830271' in str(elem.get_attribute("href")):
            print("url: " + elem.get_attribute("href"))
            elem_formatted = "url: " + elem.get_attribute("href")
            if does_file_exist(directory + "/articles.txt") is False:
                create_new_file(directory + "/articles.txt")
            write_to_file(directory + '/articles.txt', elem_formatted)
            get_details(directory, elem.get_attribute("href"))
        elif 'thread' and '6830286' in str(elem.get_attribute("href")):
            print("url: " + elem.get_attribute("href"))
            elem_formatted = "url: " + elem.get_attribute("href")
            if does_file_exist(directory + "/articles.txt") is False:
                create_new_file(directory + "/articles.txt")
            write_to_file(directory + '/articles.txt', elem_formatted)
            get_details(directory, elem.get_attribute("href"))
        else:
            continue



main_scraper('http://club.autohome.com.cn/bbs/forum-c-5769-1.html#pvareaid=3454448','ModelYAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6404-1.html#pvareaid=2108152','LYRIQAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6035-1.html#pvareaid=2108152','ID-6XAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6029-1.html#pvareaid=3454448','MustangMach-EAutoHomeBlog')
