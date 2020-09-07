from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import sys

today = datetime.today()
engine = create_engine('sqlite:///CDay.db?check_same_thread=False')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(DateTime, default=today)
    completed = Column(String, default='False')

    def __repr__(self):
        return self.task


Base.metadata.create_all(engine)


def add_task():
    while 1:
        try:
            task_input = input("\nEnter task\n>")
            dead_line = input("Enter deadline\n>")
            today = datetime.today()
            if task_input == ' ' or datetime.strptime(dead_line, '%d-%m-%Y %H:%M') <= today:
                print("\nSchedule appropriately!")
                continue
            new_row = Table(task=task_input, deadline=datetime.strptime(dead_line, '%d-%m-%Y %H:%M'), completed='False')
        except:
            print("\nSchedule appropriately!")
            continue
        session.add(new_row)
        session.commit()
        print("The task has been added successfully!\n")
        break


def get_tasks(task_date=datetime.today(), inp=True, all_t=False, missed_task=False, delete_t=False, extend_sched=False,
              completed=False, mark_comp=False, resched=False):
    today = datetime.today()
    if missed_task or resched:
        row = session.query(Table).filter(Table.deadline < today, Table.completed == 'False')\
            .order_by(Table.deadline).all()
    elif extend_sched:
        row = session.query(Table).filter(Table.deadline >= today, Table.completed == 'False').\
            order_by(Table.deadline).all()
    elif completed:
        row = session.query(Table).filter(Table.completed != 'False').order_by(Table.deadline).all()
    elif all_t:
        row = session.query(Table).order_by(Table.deadline).all()
    else:
        row = session.query(Table).filter(Table.completed == 'False').order_by(Table.deadline).all()
    if all_t:
        print("\nAll tasks:")
    elif missed_task or resched:
        print("\nMissed tasks:")
    elif completed:
        print("\nCompleted tasks:")
    elif inp and not delete_t and not extend_sched and not mark_comp:
        print(f"\nToday - {today.strftime('%A')} {today.day} {today.strftime('%B')}:")
    printed = 1
    i_d = 0
    if not all_t and not missed_task and not delete_t and not extend_sched and not completed \
            and not mark_comp and not resched:
        for task in row:
            if task.deadline.day == task_date.day and task.deadline.month == task_date.month:
                print(f'{i_d +1 }. "{task.task}" '
                      f"at {task.deadline.strftime('%H')}:{task.deadline.strftime('%M')}, "
                      f"Status - {'Completed!' if task.completed == 'True' else 'Not Completed Yet!'}")
                i_d += 1
                printed = 0
    else:
        if row and (extend_sched or mark_comp or delete_t):
            print("\nTasks:")
        for task in row:
            print(f'{i_d + 1}. "{task.task}"'
                  f' scheduled on {today.strftime("%A")} {task.deadline.day} {task.deadline.strftime("%b")}'
                  f' {task.deadline.strftime("%Y")} {task.deadline.strftime("%H")}:{task.deadline.strftime("%M")}, '
                  f'Status - {"Completed!" if task.completed == "True" else "Not Completed Yet!"}')
            printed = 0
            i_d += 1
        if not printed and not all_t and not completed and not missed_task:
            print("0. Back")
    if printed and not missed_task and not completed and not mark_comp and not extend_sched and not resched \
            and not all_t:
        print("Nothing to do!")
    elif printed and all_t:
        print("Nothing is scheduled!")
    elif printed and (missed_task or resched):
        print("Nothing is missed!")
    elif printed and extend_sched:
        print("\nNothing to extend!")
    elif printed and mark_comp:
        print("\nNothing to complete!")
    elif printed and completed:
        print("Nothing is completed!")
    print()


def weeks_plan():
    print()
    today = datetime.today()
    for i in range(7):
        todays = datetime(today.year, today.month, today.day + i)
        print(f'{todays.strftime("%A")} {todays.day}'
              f' {todays.strftime("%B")}:')
        get_tasks(task_date=datetime(today.year, today.month, today.day + i), inp=False)


def all_task():
    get_tasks(all_t=True)


def missed_task():
    get_tasks(missed_task=True)


def delete_task():
    rows = session.query(Table).filter(Table.completed == 'False').order_by(Table.deadline).all()
    if not rows:
        print("\nNothing to delete!\n")
        return
    get_tasks(delete_t=True)
    print("Choose from the above tasks:")
    task_del = int(input(">"))
    if task_del == 0:
        print()
        return
    specific_row = rows[task_del - 1]
    session.delete(specific_row)
    session.commit()
    print("The task has been deleted successfully!\n")


def delete_all():
    session.query(Table).delete()
    session.commit()


def change_deadline(rows, c):
    if rows:
        print("Choose from the above tasks:")
        while 1:
            try:
                re_option = int(input('>'))
                if re_option == 0:
                    print()
                    return
                task_input = rows[re_option - 1].task
                actual_deadline = rows[re_option - 1].deadline
                specific_row = rows[re_option - 1]
                session.delete(specific_row)
                break
            except:
                print("\nTry again! Choose the correct option!\n")
        session.commit()
        while 1:
            try:
                new_deadline = actual_deadline if c == 'True' else input("Enter the new deadline for the task!\n>")
                today = datetime.today()
                if c == 'False' and (datetime.strptime(new_deadline, '%d-%m-%Y %H:%M') <= today
                                     or datetime.strptime(new_deadline, '%d-%m-%Y %H:%M') == actual_deadline):
                    print("\nSchedule appropriately!\n")
                    continue
                new_row = Table(task=task_input, deadline=new_deadline if c == 'True'
                          else datetime.strptime(new_deadline, '%d-%m-%Y %H:%M'), completed=c)
            except:
                print("\nSchedule appropriately!\n")
                continue
            session.add(new_row)
            session.commit()
            if c == 'True':
                print("Successfully marked as completed!\n")
            else:
                print("The task has been updated successfully!\n")
            break


def reschedule():
    today = datetime.today()
    get_tasks(resched=True)
    rows = session.query(Table).filter(Table.deadline < today, Table.completed == 'False')\
        .order_by(Table.deadline).all()
    change_deadline(rows, 'False')


def extend_deadline():
    today = datetime.today()
    get_tasks(extend_sched=True)
    rows = session.query(Table).filter(Table.deadline >= today, Table.completed == 'False').\
        order_by(Table.deadline).all()
    change_deadline(rows, 'False')


def mark_completed_tasks():
    get_tasks(mark_comp=True)
    rows = session.query(Table).filter(Table.completed == 'False').order_by(Table.deadline).all()
    change_deadline(rows, 'True')


def completed():
    get_tasks(completed=True)


def menu():
    while 1:
        option = input("1) Today's tasks\n2) This week's tasks\n3) All tasks\n4) Missed tasks\n5) Add task\n"
                       "6) Delete task\n7) Re_schedule missed task\n8) Extend Deadline\n9) Mark task as completed\n"
                       "10) Completed tasks\n0) Go to main menu\n>")
        if option == '1':
            get_tasks()
        elif option == '2':
            weeks_plan()
        elif option == '3':
            all_task()
        elif option == '4':
            missed_task()
        elif option == '5':
            add_task()
        elif option == '6':
            delete_task()
        elif option == '7':
            reschedule()
        elif option == '8':
            extend_deadline()
        elif option == '9':
            mark_completed_tasks()
        elif option == '10':
            completed()
        elif option == '0':
            print()
            main()
        else:
            print("\nNo such option. Please try again!\n")


def main():
    while 1:
        opt = input("Greetings from CDay, your friendly task manager!\n1). Create a fresh lineup of tasks?\n"
                "2). Continue with your tasks?\n0). See you later?\n>")
        if opt == '1':
            delete_all()
            print()
            menu()
        elif opt == '2':
            print()
            menu()
        elif opt == '0':
            print("\nSee you soon!")
            sys.exit(0)
        else:
            print("\nNo such option. Please try again!\n")


if __name__ == '__main__':
    main()
