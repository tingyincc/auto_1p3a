# auto_1p3a

## Description
The python scrpits which can automatically get rewards from **daily check in** and **daily question answering** using request and deep learning CNN model for captcha cracking.

## Dependency
|  Package| Version |
|--|--|
| requests| 2.23.0 |
| numpy | 1.18.1 |
| matplotlib | 3.1.3 |
|tensorflow|2.0.0|
|opencv|3.4.2|

## Usage

 1. Add your user name and password into *username.json*
 2. `python auto_1p3a.py`

	

## Shedule it with conda environment
In Windows, you should put a bat file under C:\ProgramData\Anaconda3\envs\[your env name] which has content like this:

	call C:\ProgramData\Anaconda3\Scripts\activate.bat C:\ProgramData\Anaconda3\envs\[your env name]
    D:
    cd [Your auto_1p3a directory path]
    python auto_1p3a.py

Chang these paths based on your environment. 
Then create a windows scheduled task using this bat file.

## Credits and notes

 - The json file of questions comes from:
   [https://github.com/eagleoflqj/p1a3_script](https://github.com/eagleoflqj/p1a3_script)
 - The check in python code comes from:
   [https://clarka.github.io/1p3c-auto-punch-in/](https://clarka.github.io/1p3c-auto-punch-in/)
 It said that the password in json should be encrypted, but I use the unencrypted one and still works.
 - You can use pytesseract instead of tensorflow (deep learning) for captcha: [https://github.com/xjm-Toys/1Point3AcresAuto](https://github.com/xjm-Toys/1Point3AcresAuto)   
   
 - I tried some projects using selenium but failed to find the elements and idk why :(
 - Still need more error handling and code cleaning.