import os
import re
import pandas as pd


class WhatsAppFile:
    def __init__(self, file_name):
        self.file_name = file_name

    def get_text_files_lines(self):
        text_file_lines = open(self.file_name, encoding='utf-8').readlines()
        return text_file_lines

    @property
    def extract_data_from_lines(self):
        df = pd.DataFrame(columns=['date', 'time', 'sender', 'message', 'media'])

        sender = None
        for line in self.get_text_files_lines():
            needed_line = True
            media = False

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

            if len(main_line) == 1:
                date = re.findall(r'\d{2}\/\d{2}\/\d{4}', line)[0]
                time = re.findall(r'\d{1,2}\:\d{2} \w{2}', line)[0]
                sender = re.findall(r'- [\w+ ]+', line)[0]
                sender = sender[2:]
                message = line.replace('{}, {} - {}: '.format(date, time, sender), '')
                message = message.replace('\n', '')
                # print(message)
                # message = message[1:-1]
                # print(date, time, sender, message)
            elif sender != None and needed_line == True:
                message = line
                message = message.replace('\n', '')

            else:
                continue

            dict = {'date': date, 'time': time, 'sender': sender, 'message': message, 'media': media}
            df = df.append(dict, ignore_index=True)

        # print(df)
        return df

    def print_data_csv(self):
        df = self.extract_data_from_lines()
        df.to_csv('{}.csv'.format(self.file_name), sep=',', encoding='utf-8')

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
