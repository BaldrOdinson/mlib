from mlibsite.models import Comments, User

def count_comments(item_id, item_type):
    quant_of_comments = Comments.query.filter(Comments.item_type==item_type, Comments.item_id==item_id, Comments.disabled==False).count()
    return quant_of_comments


def select_comments(item_id, item_type, page):
    """
    Выбираем из базы комментарии для нужной прокоментированной сущности, формируем словарь
    с помощью доп.функций
    """
    print(f'Пришли в select_comments, item_id: {item_id} item_type: {item_type}')
    # берем базовые комментарии, сначалп свежие
    # Pagination
    per_page=10
    paginate_base_comments = Comments.query.filter(Comments.item_type==item_type, Comments.item_id==item_id, Comments.parrent_comment==0, Comments.disabled==False).order_by(Comments.create_date.desc()).paginate(page=page, per_page=per_page)
    base_comments = Comments.query.filter(Comments.item_type==item_type, Comments.item_id==item_id, Comments.parrent_comment==0, Comments.disabled==False).order_by(Comments.create_date.desc())[page*per_page-per_page:page*per_page]
    # base_comments = Comments.query.filter(Comments.item_type==item_type, Comments.item_id==item_id, Comments.parrent_comment==0, Comments.disabled==False).order_by(Comments.create_date.desc()).all()
    sub_comments = Comments.query.filter(Comments.item_type==item_type, Comments.item_id==item_id, Comments.parrent_comment!=0, Comments.disabled==False).order_by(Comments.create_date).all()
    print(f'Выборка comments из базы: base: {base_comments} sub: {sub_comments}')
    comments_dict = create_comments_dict(base_comments, sub_comments)
    whole_comments = Comments.query.filter(Comments.item_type==item_type, Comments.item_id==item_id).all()
    # Формируем словать с авторами комментариев
    authors_dict = {}
    for comment in whole_comments:
        author_id = comment.author_id
        author = User.query.filter_by(id=author_id).first()
        if author not in authors_dict:
            authors_dict[author_id] = author
    print(f'FINAL Categories dict: {comments_dict}\nАвторы комментариев: {authors_dict}')
    return comments_dict, authors_dict, paginate_base_comments


def create_comments_dict(base_comments, sub_comments):
    '''
    Строим словарь с комментариями, где подкомменты вложены в родительские комменты
    '''
    # определяем финальный словарь с деревом комментариев
    comments_dict = {}
    # Формируем базовый список со всеми полученными из БД комментариями, его будем постепенно уменьшать, удаляя обработанные комментарии
    curr_base_comments_list = list(base_comments)
    curr_sub_comments_list = list(sub_comments)
    # Начинаем с комментария у которой родительский комментарий 0
    base_comment_parrent = 0

    # base category
    def add_comm_in_dict(base_comment):
        """
        Формируем словарь для корневого комментария
        """
        comm_list = curr_base_comments_list.copy()
        curr_comm_list = []
        for comment in comm_list:
            print(f'ОБРАБАТЫВАЕМ {comment} в корне')
            # если родительский комментарий (parrent_comm) выбранного комментария совпадает с рутовым комментарием
            if comment.parrent_comment == base_comment:
                # делаем копию списка, которую затем пошлем в sub-функцию для заполнения
                sub_curr_comm_list = curr_comm_list.copy()
                # добавляем в словарь коммент
                comments_dict[comment] = sub_curr_comm_list
                # удаляем из общего списка комментариев обработанный коммент
                curr_base_comments_list.pop(curr_base_comments_list.index(comment))
                # Формируем список со словарями подкомментов для проверки на содержание собственных подкомментов
                sub_comment_add(comment, sub_curr_comm_list)


    # sub comment
    # Новый корневой комментарий base_comment
    def sub_comment_add(base_comment, sub_curr_comm_list):
        # Берем список с оставшимися комментариями
        comm_list = curr_sub_comments_list.copy()
        # список комментариев у которых базовый является родительским
        curr_comm_list = []
        sub_comm_dict = {}
        for comment in comm_list:
            # print(f'ОБРАБАТЫВАЕМ {comment} с сабе, полученный sub_curr_comm_list: {sub_curr_comm_list}')
            # если родительский коммент равен базовому
            if comment.parrent_comment == base_comment.id:
                # делаем копию списка, которую затем пошлем в sub-функцию для заполнения
                new_curr_comm_list = curr_comm_list.copy()
                # добавляем его в словарь с пустым списком подкомментариев
                sub_comm_dict[comment] = new_curr_comm_list
                # print(f'    добавляем sub_comm_dict: {sub_comm_dict} в локальный список')
                # Добавляем этот словарь в общий список подходящих комментариев, только если он пустой, иначе он сам заполнится по рекурсии
                # print(f'sub_curr_comm_list перед добавление в него словаря: {sub_curr_comm_list}')
                if not sub_curr_comm_list:
                    sub_curr_comm_list.append(sub_comm_dict)
                # print(f'локальный sub_curr_comm_list: {sub_curr_comm_list}')
                # удаляем из общего списка комментариев обработанный коммент
                curr_sub_comments_list.pop(curr_sub_comments_list.index(comment))
                # print(f'базовый comments_comm_list: {curr_comments_list}')
                # print(f'Финальный comments_dict: {comments_dict}')
                # Recursion, запускаем поиск подкомментариев у текущего комментари
                sub_comment_add(comment, new_curr_comm_list)


    # RUN
    add_comm_in_dict(base_comment_parrent)
    # print(f'FINAL Categories dict: {comments_dict}')
    return comments_dict


if __name__ == '__main__':
    select_comments(22, 1)
