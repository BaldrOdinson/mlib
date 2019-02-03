from mlibsite.models import UserRole

def get_roles(item_id, item_type):
    '''
    Смотрим роли пользователей по проекту
    '''
    roles_dict = {}
    item_admins = UserRole.query.filter(UserRole.item_type==2, UserRole.item_id==item_id, UserRole.role_type==1).all()
    item_moders = UserRole.query.filter(UserRole.item_type==2, UserRole.item_id==item_id, UserRole.role_type==2).all()
    item_readers = UserRole.query.filter(UserRole.item_type==2, UserRole.item_id==item_id, UserRole.role_type==3).all()
    roles_dict['admins'] = list(project.user_id for project in item_admins)
    roles_dict['moders'] = list(project.user_id for project in item_moders)
    roles_dict['readers'] = list(project.user_id for project in item_readers)
    # print(f'Roles dict: {roles_dict}')
    return roles_dict

def user_role(roles_dict, user_id):
    '''
    определяем роль пользователя
    '''
    user_role = ''
    print(f'roles dict: {roles_dict}\nuser id: {user_id}')
    if user_id in roles_dict['admins']:
        user_role = 'admin'
    elif user_id in roles_dict['moders']:
        user_role = 'moder'
    elif user_id in roles_dict['readers']:
        user_role = 'reader'
    print(f'user role: {user_role}')
    return user_role
