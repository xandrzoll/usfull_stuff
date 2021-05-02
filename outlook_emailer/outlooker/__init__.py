from win32com.client import Dispatch
import re
import time


class Outlooker():
    def __init__(self, outlook_box, set_account=True):
        self.message_handlers = []
        self.check_folder = ''
        self._outlook = Dispatch('Outlook.Application').GetNamespace("MAPI")
        self._inbox = self._outlook.Folders(outlook_box)
        self.folders = self._inbox.Folders
        if set_account:
            self._outlook_sender = Dispatch('Outlook.Application')
            self.accounts = self._outlook_sender.Session.Accounts
            self.current_acc = self._set_current_account(outlook_box)


    def __del__(self):
        self._inbox = None
        self.folders = None
        self._outlook.Quit()

    def _set_current_account(self, acc):
        current_acc = None
        for account in self.accounts:
            if account.DisplayName == acc:
                current_acc = account
                break
        if not current_acc:
            current_acc = self.accounts[0]
        return current_acc

    def get_message_handlers(self):
        return self.message_handlers

    def message_handler(self, **kwargs):
        def decorator(handler):
            handler_dict = dict()
            for kwarg in kwargs:
                handler_dict[kwarg] = kwargs[kwarg]

            handler_dict['func'] = handler
            self.message_handlers.append(handler_dict)

            return handler

        return decorator

    def check_emails(self, check_folder, unread_only=False):
        for folder in self.folders:
            if folder.Name == check_folder:
                self.check_folder = folder
                break
        messages = self.check_folder.Items

        for message in messages:
            try:
                if not message.UnRead and unread_only:
                    continue
                message_params = {
                    'sender': message.SentOnBehalfOfName,
                    'title': message.subject,
                    'body': message.Body,
                    'email': message.SenderEmailAddress,
                }
                print(time.strftime('%Y-%m-%d %H:%M'), '-', message_params['sender'], ':', message_params['title'])
                is_handler_find = False
                for handler in self.message_handlers:
                    for mp in message_params:
                        handler_cond = handler.get(mp)
                        if handler_cond:
                            if re.search(handler_cond, message_params[mp]):
                                is_handler_find = True
                            else:
                                is_handler_find = False

                    if is_handler_find:
                        handler['func'](message)
                        break
                if unread_only:
                    message.unRead = False
            except Exception:
                continue

    def run(self, check_folder, wait=1):
        try:
            while True:
                self.check_emails(check_folder, unread_only=True)
                time.sleep(wait)
        except KeyboardInterrupt:
            print('Stopped.')
        finally:
            self._outlook.Quit()

    def send_message(self, to='', title='', body='', HTMLBody='', attach=''):
        try:
            msg = self._outlook_sender.CreateItem(0)
            msg.To = to
            msg.Subject = title
            if HTMLBody:
                msg.HTMLBody = HTMLBody
            else:
                msg.body = body
            if attach:
                msg.Attachments.Add(Source=attach)

            msg._oleobj_.Invoke(*(64209, 0, 8, 0, self.current_acc))
            msg.Send()
        except Exception as err:
            print(err)
            return False

        return True
