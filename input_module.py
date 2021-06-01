"""input module"""


def raw_input(scheme):
    """
    The user have to use specific set of commands to be able to interact with program.
    These commands includes 'add', 'del' for elements and '-->', '-!>' for connection.

    For adding a new element user should use command as follows:
        add *element* *id(name)* *cor1* *cor2*, where 'cor1' and 'cor2' are x and y coordinates accordingly.
    Examples:
        add and en 20 20
        add or inp 3 4
    For deleting existing element user should use command as follows:
        del *id(name)*
    Examples:
        del en
        del inp
    For adding new connection between elements user should use next command:
        *element1* *id1(name)* --> *element2* *id2(name)*
    Example:
        and en --> or inp
    For deleting existing connection between elements user should use next command:
        *element1* *id1(name)* -!> *element2* *id2(name)*
    Example:
        and en -!> or inp
    """
    commands = ''
    command = input("Enter the command: ")
    while command != 'q':
        commands += command + '\n'
        command = input("Enter the command: ")

    for line in commands.split('\n'):
        line = line.strip().split()
        if line[0] == 'add':
            scheme.add_element(line[1], line[2], (int(line[3], int(line[4]))))
        elif line[0] == 'del':
            scheme.delete_element(line[1])
        elif '-->' in line:
            scheme.add_connection(line[1], line[0], line[4], line[3])
        elif '-!>' in line:
            scheme.delete_connection(line[1], line[0], line[4], line[3])


def input_from_file(path, scheme):
    """
    In the file *path* user should write commands as in raw_input, each command from a new line.
    """
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip().split()
            if line[0] == 'add':
                scheme.add_element(line[1], line[2], (int(line[3], int(line[4]))))
            elif line[0] == 'del':
                scheme.delete_element(line[1])
            elif '-->' in line:
                scheme.add_connection(line[1], line[0], line[4], line[3])
            elif '-!>' in line:
                scheme.delete_connection(line[1], line[0], line[4], line[3])
            else:
                continue
