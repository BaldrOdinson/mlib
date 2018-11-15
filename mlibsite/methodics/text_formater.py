import os

def text_format_for_html(text):
    '''
    Разбиваем полученный из базы текст по строкам, чтобы затем вывести в форме в отдельных <p>
    Иммитация переносов строк, которые иначе проебываются, а <pre> не поддерживает bootstrap styling
    '''
    with open('text_tmp.txt', 'w') as file:
        file.write(text)
    html_text_list=[]
    with open('text_tmp.txt', 'r') as file:
        for line in file.readlines():
            if line != '\n':
                html_text_list.append(line)
    os.remove('text_tmp.txt')
    # print(html_text_list)
    return html_text_list


if __name__ == '__main__':
    text='one\ntwo\nthree'
    text_format_for_html(text)
