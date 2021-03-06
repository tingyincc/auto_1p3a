import requests
import re
import json
import shutil
import os
from io import BytesIO
from PIL import Image
from predict import image_test_color_seg

# for collecting images
save_captcha = True


class AutoPunch:
    def __init__(self, username, pwd):
        self.username = username
        self.pwd = pwd
        self.main_url = 'https://www.1point3acres.com/bbs'
        self.question_url = 'https://www.1point3acres.com/bbs/plugin.php?id=ahome_dayquestion:pop'
        self.login_url = 'https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        self.punch_url = 'https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1'
        self.verify_url = 'https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=update&idhash=SA00&inajax=1&ajaxtarget=seccode_SA00'
        self.verify_url_check = 'https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=update&idhash=S00&inajax=1&ajaxtarget=seccode_S00'  # 0711 new
        self.session = requests.Session()
        self.headers = {
            'origin': 'https://www.1point3acres.com',
            # server doesn't check referer right now
            'referer': 'https://www.1point3acres.com/bbs/id=ahome_dayquestion:pop',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }

    def login(self):
        res = self.session.post(self.login_url,
                                headers=self.headers,
                                data={
                                    'username': self.username,
                                    'password': self.pwd,
                                    'quickforward': 'yes',
                                    'handlekey': 'ls'
                                })

        return res

    def get_punch_formhash(self):
        res = self.session.get(self.main_url, headers=self.headers)
        # print(res.text)
        result = re.search('formhash=(.{8})', res.text)
        if result:
            return result.group(1)
        else:
            print("No formhash for daily punch.")
            return

    def punch(self, formhash, code):
        if(code == None):
            res = self.session.post(self.punch_url,
                                    headers=self.headers,
                                    data={
                                        'formhash': formhash,
                                        'qdxq': 'kx',
                                        'qdmode': 2,
                                        'todaysay': 'check in',
                                        'fastreply': 0
                                    })
        else:
            res = self.session.post(self.punch_url,
                                    headers=self.headers,
                                    data={
                                        'formhash': formhash,
                                        'qdxq': 'kx',
                                        'qdmode': 2,
                                        'todaysay': 'check in',
                                        'fastreply': 0,
                                        'sechash': 'S00',
                                        'seccodeverify': code
                                    })
        return res

    def get_question_response(self):
        return self.session.get(self.question_url, headers=self.headers)

    def get_question_formhash(self, res):
        formhash = re.search('name="formhash" value="(.{8})"', res.text)
        if formhash:
            return formhash.group(1)
        else:
            print("No formhash for question, may already answered")
            return

    def get_question(self, res):
        question = re.search('【题目】</b>&nbsp;(.*)</font>', res.text)
        if question:
            return question.group(1).strip()
        else:
            return

    def get_answer(self, question):
        # 检查题库
        print(f"开始检索题库, 题目: {question}")
        answer = ""
        with open("question_list.json", encoding="utf-8") as f:
            q_dict = json.load(f)
        try:
            answer = q_dict[question]
        except KeyError:
            print("No matched question in database")
            fd = open("unanswered_question.txt", "a+", encoding="utf-8")
            print(fd.read())
            if question not in fd.read():
                fd.write(question+'\n')
            return

        if type(answer) is list:
            answer_set = set(answer)
        else:
            answer_set = set([answer])

        options_list = ['']*4
        for i in range(4):
            result = re.search('name="answer" value="' +
                               str(i+1)+'">&nbsp;&nbsp;(.*?)</div>', res.text)
            if(result):
                options_list[i] = result.group(1)
            else:
                result = re.search(
                    'name="answer" value="'+str(i+1)+'" >&nbsp;&nbsp;(.*?)</div>', res.text)
                options_list[i] = result.group(1)

        for index, potential_ans in enumerate(options_list):
            if potential_ans in answer_set:
                answer = potential_ans
                break

        return index+1

    def crack_verify(self, option):

        if(option == 1):
            res = self.session.get(
                self.verify_url_check, stream=True, headers=self.headers)
        else:
            res = self.session.get(
                self.verify_url, stream=True, headers=self.headers)
        try:
            result = re.search('src="(.*)" class="vm"', res.text)
        except:
            return None
        res = self.session.get("https://www.1point3acres.com/bbs/" +
                               result.group(1), stream=True, headers=self.headers)
        # with open("img.jpg", 'wb') as fp:
        #    fp.write(res.content)

        # Credict:Hanyang-Li/BotFarmer-1point3acres
        verify_gif = Image.open(BytesIO(res.content))
        durations = []
        try:
            while True:
                durations.append(verify_gif.info['duration'])
                verify_gif.seek(verify_gif.tell() + 1)
        except EOFError:
            pass
        verify_gif.seek(durations.index(max(durations)))
        verify_image = Image.new('RGB', verify_gif.size)
        verify_image.paste(verify_gif)
        verify_image.save(str(option)+"_img.png")

        captcha_text = image_test_color_seg(str(option)+"_img.png")
        print("Result of Cracking: ", captcha_text)
        return captcha_text

    def answer(self, formhash, code, answer):
        res = self.session.post(self.question_url,
                                headers=self.headers,
                                # cookies= cookieJar,
                                data={
                                    'formhash': formhash,
                                    'answer': answer,
                                    'sechash': 'SA00',
                                    'seccodeverify': code,
                                    'submit': 'true'
                                })

        return res


if __name__ == '__main__':
    retry_sign = 10
    retry_answer = 10
    with open('username.json') as json_file:
        account = json.load(json_file)
        # Sign and punch
        ap = AutoPunch(account['id'], account['password'])
        ap.login()

        while(retry_sign > 0):
            login_formhash = ap.get_punch_formhash()
            if(login_formhash):
                # need code from May 30, maybe server detected auto check in
                code = ap.crack_verify(1)
                res = ap.punch(login_formhash, code)
                if("您今日已经签到，请明天再来！" in res.text):
                    print(account['id'] + ' check in succeed.')
                    break
                with open("punch_res.txt", 'w+', encoding="utf-8") as f:
                    f.write(res.text)
                retry_sign -= 1
                print("Retry check in: ", retry_sign)

        # Answer question
        while(retry_answer > 0):
            res = ap.get_question_response()
            formhash = ap.get_question_formhash(res)
            question = ap.get_question(res)

            if(question):
                answer_index = ap.get_answer(question)
            else:
                print("No question")
                break

            if(formhash and question and answer_index):
                code = ap.crack_verify(2)
                res = ap.answer(formhash, code, answer_index)
                if("恭喜你，回答正确！奖励1大米" in res.text):
                    print("Answering Succeed.")
                    # save correct verify image
                    directory = "./verify_images/"
                    if save_captcha:
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        os.rename("2_img.png", directory + code + ".png")
                    break
                else:
                    print("Answering failed.")

            retry_answer -= 1
            print("Retry answering: ", retry_answer)
