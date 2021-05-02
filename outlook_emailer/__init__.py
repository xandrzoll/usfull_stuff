import win32com.client as win
import re


class Emailer():
    
    def __init__(self, outlook_box):
        self.message_handlers = []
        self.check_folder = ''
        
        self._outlook = win.Dispatch('Outlook.Application').GetNamespace("MAPI")
#        accounts = win.Dispatch("Outlook.Application").Session.Accounts
        
#        account = accounts[0]
        self._inbox = self._outlook.Folders(outlook_box)
        
        self.folders = self._inbox.Folders
        
    
    def get_message_handlers(self):
        return self.message_handlers
    
    
    def message_handler(self, sender='', title='', body=''):
        def decorator(handler):
            handler_dict = {
                    'func': handler, 
                    'sender': sender, 
                    'title': title,
                    'body': body,
                    }
            self.message_handlers.append(handler_dict)
            
            return handler
        
        return decorator
    
    
    def check_emails(self, check_folder):
        
        for folder in self.folders:
            if folder.Name == check_folder:
                self.check_folder = folder
                break
				
        messages = self.check_folder.Items
        
        for message in messages:
            for handler in self.message_handlers:
                if not re.search(handler['sender'], message.SentOnBehalfOfName):
                    continue
                if not re.search(handler['title'], message.subject):
                    continue
                if not re.search(handler['body'], message.Body):
                    continue
                handler['func'](message)
                message.UnRead = False
                break
                    

if __name__ == '__main__':
    _outlook_box = r'vsp-equip@omega.sbrf.ru'
    _outlook_check_folder = r'Входящие'
    
    email = Emailer(_outlook_box)
    
    
    @email.message_handler(body='BODY')
    def test(message):
        print('-' * 20)
        print('Нужное сообщение')
        print(message.subject)
#        print(message.Body)


    @email.message_handler()
    def test2(message):
        print('-' * 20)
        print('А этот хендлер сработает для любого сообщения')
        print(message.subject)


    
    email.check_emails(_outlook_check_folder)
    
    
    
    
    
    
    
    
    
    