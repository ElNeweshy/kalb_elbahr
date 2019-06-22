# -*- coding: utf-8 -*-

import os
import re
import pandas as pd


class WhatsAppFile:
    def __init__(self, file_name):
        self.file_name = file_name.split('.')[0]
        self.df = pd.DataFrame(columns=['date', 'time', 'sender', 'message', 'media', 'mentioned', 'no_words',
                                   'emotion_count', 'url_messages', 'file_attached_message'])
        self.extract_data_from_lines()

    def get_text_files_lines(self):
        text_file_lines = open('{}.txt'.format(self.file_name), encoding='utf-8').readlines()
        return text_file_lines

    def extract_data_from_lines(self):
        # df = pd.DataFrame(columns=['date', 'time', 'sender', 'message', 'media', 'mentioned', 'no_words',
        #                            'emotion_count', 'url_messages', 'file_attached_message'])

        sender = None
        for line in self.get_text_files_lines():
            needed_line = True

            # Try to detect the message where the sender has a name
            main_line = re.findall(r'\d{2}\/\d{2}\/\d{4}, \d{1,2}\:\d{2} \w{2} - [\w ]+:', line)
            if len(main_line) != 1:
                # Try to detect the message where the sender is a phone number
                main_line = re.findall(r'\d{2}\/\d{2}\/\d{4}, \d{1,2}\:\d{2} \w{2} - +[\d+ ]+:', line)

            # Capture
            # 1- adding line and there must not have "added" word as well to be a correct adding line
            # 2- Change icon line
            # 3- Change subject line
            adding_step = re.findall(r'\d{2}\/\d{2}\/\d{4}, \d{1,2}\:\d{2} \w{2} - [\w ]+', line)
            if len(adding_step) == 1 and 'added' in line:
                needed_line = False
            if 'changed the subject from' in line:
                needed_line = False
            if "changed this group's icon" in line:
                needed_line = False

            # Capture message lines
            if len(main_line) == 1:
                date = re.findall(r'\d{2}\/\d{2}\/\d{4}', line)[0]
                time = re.findall(r'\d{1,2}\:\d{2} \w{2}', line)[0]
                sender = re.findall(r'- [\w+ ]+', line)[0]
                sender = sender[2:]
                message = line.replace('{}, {} - {}: '.format(date, time, sender), '')

            elif sender != None and needed_line == True:
                message = line

            else:
                continue

            # Final processing on message data
            # Check media
            message = message.replace('\n', '')
            if message == '<Media omitted>':
                message = ''
                media = True
            else:
                media = None
            # Check mentioned people
            mentioned = re.findall('\@[\d+]+', message)
            for mention in mentioned:
                message = message.replace('{}'.format(mention), '')

            # Emotions count
            #TODO: Not working on all cases
            emotion_count = message.count('💃')
            message = message.replace('💃', '')

            # Attached files
            file_attached_message = None
            if '(file attached)' in message:
                file_attached_message, message = message, ''

            # URL capture
            url_messages = None
            # url_regex = r"(([\w]+:)?//)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,63}(:[\d]+)?(/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?"
            url_regex = r"https?[\S]+"
            urls = re.findall(url_regex, message)
            # if len(urls) != 0:
            #     url_messages, message = message, ''
            for url in urls:
                message = message.replace(url, '')
            url_messages = urls


            # Count number of words in the message
            no_words = len(re.findall(r'\w+', message))

            dict = {'date': date, 'time': time, 'sender': sender, 'message': "'{}'".format(message), 'media': media, 'mentioned': mentioned, 'no_words': no_words, 'emotion_count': emotion_count, 'url_messages': url_messages, 'file_attached_message': file_attached_message}
            self.df = self.df.append(dict, ignore_index=True)

        return self.df

    def print_data_csv(self):
        df = self.extract_data_from_lines()
        df.to_csv('{}.csv'.format(self.file_name), sep=',', encoding='utf-8-sig')

    def get_creation_data(self):
        for line in self.get_text_files_lines():
            if 'created group' in line:
                first_group_name = re.findall(r'"\S+"', line)[0]
                first_group_name = first_group_name.replace('"', '')
                creator = re.findall(r"[\w+ ]+ created group", line)[0]
                creator = creator.replace(' created group', '')
                creation_date = re.findall(r'\d{2}\/\d{2}\/\d{4}', line)[0]
                break

        creation_data = {'creator': creator, 'creation_date': creation_date, 'first_group_name': first_group_name}
        return creation_data


def get_text_files():
    all_files = os.listdir()
    text_files = [item for item in all_files if item.endswith('txt')]
    return text_files


if __name__ == "__main__":
    text_files = get_text_files()

    whats_app_file = WhatsAppFile(text_files[0])

    whats_app_file.extract_data_from_lines()
    whats_app_file.get_creation_data()
    whats_app_file.print_data_csv()
