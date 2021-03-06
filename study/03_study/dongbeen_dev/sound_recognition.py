import speech_recognition as sr
import sys #-- 텍스트 저장시 사용


while 1:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say Something")
        speech = r.listen(source)

    #sys.stdout = open('audio_output.txt', 'w') #-- 텍스트 저장시 사용

    try:
        audio = r.recognize_google(speech, language="ko-KR")
        print("Your speech thinks like\n " + audio)
        if audio == "시작":
            print("Hello")
        elif audio == "종료":
            print("end")
        else:
            print("nothing")
    except sr.UnknownValueError:
        print("Your speech can not understand")
    except sr.RequestError as e:
        print("Request Error!; {0}".format(e))

#sys.stdout.close() #-- 텍스트 저장시 사용