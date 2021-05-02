from outlooker import Outlooker


_outlook_box = r'xandr.rudkovsky@outlook.com'
email = Outlooker(_outlook_box)


# @email.message_handler(sender='Александр Рудковский', title='SQL')
# def run_sql(message):
#     print(message.Body)
#     is_send = email.send_message(
#         to=message.SenderEmailAddress,
#         title='sql',
#         body='Hello. Your data in the attach.',
#         attach=r'D:\projects\TGBot_Klepa_Two\utils\balance.csv'
#     )
#     if is_send:
#         print('Message was send')
#
#
# @email.message_handler(sender='Александр Рудковский', title='get file')
# def run_sql(message):
#     path_to_file = message.Body
#     path_to_file = r'{}'.format(path_to_file)
#     is_send = email.send_message(
#         to=message.SenderEmailAddress,
#         title=message.Subject,
#         body='Hello. Your file in the attach, ' + message.SentOnBehalfOfName,
#         attach=path_to_file
#     )
#     if is_send:
#         print('Message was send')


@email.message_handler(sender='Александр Рудковский')
def run_sql(message):
    message.ReplyAll()
    message.HTMLBody = '<br>Test<br><hr>' + message.HTMLBody
    # message.To = 'xandr.rudkovsky@outlook.com'
    message.Send()

email.run('Inbox')
