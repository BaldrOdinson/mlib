from mlibsite.models import Courses, Lessons, Term, Projects, Students, StudentsGroup, Learning_groups

def student_projects_info_dict(student_id):
    '''
    Вынимаем из базы всю известную о участнике информацию,
    контактные данные, в каких активностях замечен,
    группа, курс, период, проект
    '''
    student = Students.query.get_or_404(student_id)
    # Выясняем группы данного студента
    learning_groups = Learning_groups.query.filter_by(student_id=student.id).all()
    students_groups_id = []
    students_group = []
    students_courses = []
    students_terms = []
    students_projects = []
    for group in learning_groups:
        students_groups_id.append(group.group_id)
        curr_group = StudentsGroup.query.filter_by(id = group.group_id).all()
        for c_group in curr_group:
            students_group.append(c_group)
        # Выясняем курсы данного студента
        curr_students_courses = Courses.query.filter_by(students_group_id = group.group_id).all()
        for curr_course in curr_students_courses:
            students_courses.append(curr_course)
    # Список периодов
    for course in students_courses:
        curr_students_terms = Term.query.filter_by(id=course.term_id).first()
        students_terms.append(curr_students_terms)
    # Список проектов
    for term in students_terms:
        curr_students_projects = Projects.query.filter_by(id=term.project_id).first()
        students_projects.append(curr_students_projects)
    student_proj_info_dict = {}
    student_proj_info_dict['students_group'] = students_group
    student_proj_info_dict['students_courses'] = students_courses
    student_proj_info_dict['students_terms'] = students_terms
    student_proj_info_dict['students_projects'] = students_projects
    # print(f'students_group[0].name: {students_group[0].description}\n\
    #         students_courses[0].name: {students_courses[0].name}\n\
    #         students_terms[0].name: {students_terms[0].name}\n\
    #         students_projects[0].name: {students_projects[0].name}')
    return student_proj_info_dict
