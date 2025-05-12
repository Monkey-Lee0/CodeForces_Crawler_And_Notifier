import plotly.graph_objects as go
import webbrowser
from dominate import document
from dominate.tags import *
from dominate.util import raw
import schedule
import tkinter as tk
import pygame
import requests
import json
import time
from datetime import datetime
import colorful

from colorful import ColorfulSubmission


class User:
    def __init__(self, userID, statusSet=None, Rating=0):
        if statusSet is None:
            statusSet = []
        self.userID = userID
        self.statusSet = statusSet
        self.Rating = Rating

    @staticmethod
    def calc_problemID(problem):
        if "contestId" in problem:
            return str(problem["contestId"]) + str(problem["index"])
        elif "problemsetName" in problem:
            return str(problem["problemsetName"]) + str(problem["index"])
        else:
            return str(problem["index"])

    def show_user(self,doc):
        colorfulStr=colorful.ColorfulUser(self.userID,self.Rating)
        with doc:
            with p(style="font-size:25px"):
                with a(href="https://codeforces.com/profile/"+self.userID):
                    for item in colorfulStr.List:
                        span(item[0],style=f'color:{item[1]};float:left;')
                span(raw('&nbsp;'),str(self.Rating))

    def show_ratio(self,doc):
        AC,CE,RE,WA,TLE,MLE,ILE,OTHER=0,0,0,0,0,0,0,0
        for item in self.statusSet:
            match item["verdict"]:
                case "OK":
                    AC += 1
                case "COMPILATION_ERROR":
                    CE += 1
                case "RUNTIME_ERROR":
                    RE += 1
                case "WRONG_ANSWER":
                    WA += 1
                case "TIME_LIMIT_EXCEEDED":
                    TLE += 1
                case "MEMORY_LIMIT_EXCEEDED":
                    MLE += 1
                case "IDLENESS_LIMIT_EXCEEDED":
                    ILE += 1
                case _:
                    OTHER += 1
        with doc:
            with div():
                span("AC="+str(AC))
                span("CE="+str(CE))
                span("RE="+str(RE))
                span("WA="+str(WA))
                span("TLE="+str(TLE))
                span("MLE="+str(MLE))
                span("ILE="+str(ILE))
                span("OTHER="+str(OTHER))
                span("ratio="+str(AC/(AC+CE+RE+WA+TLE+MLE+ILE+OTHER)))

    def show_MaxDirt(self,doc):
        D={}
        Pro,Max=[],0
        for item in self.statusSet:
            Name=self.calc_problemID(item["problem"])
            if Name not in D:
                D[Name]=0
            if item["verdict"] == "OK":
                D[Name]=0
            else:
                D[Name]+=1
        for pro,num in D.items():
            if num>Max:
                Max=num
                Pro=[pro]
            elif num==Max:
                Pro.append(pro)
        text="Max Dirt Problems: "
        for item in Pro:
            text+=str(item)+' '
        with doc:
            p("Max Dirt Time:"+str(Max))
            p(text)

    def show_AC(self,doc):
        with doc:
            h4("Recent AC")
        count=10
        S=[]
        for r in self.statusSet:
            if count==0:
                break
            if r["verdict"]!="OK":
                continue
            problem=r["problem"]
            problemID=self.calc_problemID(problem)
            problemName=problem["name"]
            if "rating" in problem:
                problemRating=problem["rating"]
            else:
                problemRating=""
            if problemID in S:
                continue
            S.append(problemID)
            with doc:
                with div():
                    span(problemID)
                    span(problemName)
                    span(problemRating)
            count-=1

    def show_problem_difficulty(self,doc):
        difficulty=[]
        count=[]
        total=0
        for dif in range(800,3600,100):
            difficulty.append(dif)
            count.append(0)
        S=[]
        for item in self.statusSet:
            problem=item["problem"]
            Name=self.calc_problemID(problem)
            if Name in S:
                continue
            if item["verdict"]!="OK":
                continue
            if "rating" not in problem:
                continue
            count[problem["rating"]//100-8]+=1
            total+=problem["rating"]

        colors=['#BCBDBE','#BCBDBE','#BCBDBE','#BCBDBE','#6FEB71','#6FEB71','#6FCCAF','#6FCCAF',
                '#9D9EEC','#9D9EEC','#9D9EEC','#EA80EC','#EA80EC','#EABD81','#EABD81','#EAAE53',
                '#EA7071','#EA7071','#EA3334','#EA3334','#EA3334','#EA3334','#9D0506','#9D0506',
                '#9D0506','#9D0506','#9D0506','#9D0506']
        hover_text=[]
        for cnt in count:
            hover_text.append("Problems Solved: "+str(cnt))
        data = [go.Bar(x=difficulty, y=count,
                       hovertemplate="Problems Solved: %{y}",
                       name="",
                       marker=dict(color=colors))]
        fig = go.Figure(data=data)
        fig.update_layout(title='Count of difficulties',
                          xaxis_title="Difficulty",
                          yaxis_title="Count",
                          xaxis=dict(
                              dtick=1,
                              tickmode='array',
                              tickvals=difficulty,
                              ticktext=[str(d) for d in difficulty]
                         )
                         )
        with doc:
            raw(fig.to_html())
            with p():
                span("average rating: ")
                S=sum(count)
                if S:
                    span(str(total/S))
                else:
                    span("NaN")

    def show_problem_tag(self,doc):
        tag={}
        S=[]
        for item in self.statusSet:
            problem=item["problem"]
            Name=self.calc_problemID(problem)
            if Name in S:
                continue
            if item["verdict"]!="OK":
                continue
            if "tags" not in problem:
                continue
            List=problem["tags"]
            for T in List:
                if T not in tag:
                    tag[T]=0
                tag[T]+=1
        tag=dict(sorted(tag.items(), key=lambda tmp: tmp[1], reverse=True))
        TAG=[]
        count=[]
        for [x,y] in tag.items():
            TAG.append(x)
            count.append(y)
        data=[go.Pie(labels=TAG,values=count)]
        fig=go.Figure(data=data)
        fig.update_traces(hoverinfo='label+value',
                          textinfo='value'
        )
        fig.update_layout(
            width=1200,
            height=600
        )
        with doc:
            raw(fig.to_html())

    def show_report(self,OPEN=False):
        def put_div():
            with doc:
                hr()
        doc = document(title="CodeForces Report of " + self.userID)
        self.show_user(doc)
        self.show_ratio(doc)
        put_div()
        self.show_MaxDirt(doc)
        put_div()
        self.show_AC(doc)
        put_div()
        self.show_problem_difficulty(doc)
        put_div()
        self.show_problem_tag(doc)
        put_div()

        t = time.time() - 60 * 60 * 24 * 30
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        with doc:
            p("generate time:" + time_string)

        html_content = doc.render()
        with open(f"report_{self.userID}.html", "w", encoding="utf-8") as file:
            file.write(html_content)

        if OPEN:
            webbrowser.open(f"report_{self.userID}.html")

    def get_rating(self):
        l=json.loads(requests.get("https://codeforces.com/api/user.rating?handle="+str(self.userID)).text)
        if l["status"] != "OK":
            print("FAIL")
            return
        r=l["result"]
        if len(r) == 0:
            self.Rating = 0
        else:
            self.Rating = r[-1]["newRating"]

    def get_status(self):
        print(f'Crawling {self.userID}')
        l=json.loads(requests.get("https://codeforces.com/api/user.status?handle=" + str(self.userID)).text)
        if l["status"] != "OK":
            print("FAIL")
            return None
        r = l["result"]
        diff = []
        pt = 0
        for submission in r:
            if pt >= len(self.statusSet) or self.statusSet[pt]['id'] != submission['id']: # it is a new submission
                diff.append([self.userID,self.Rating,submission])
            elif self.statusSet[pt]['verdict'] != submission['verdict']:
                diff.append([self.userID,self.Rating,submission])
                pt += 1
            else:
                pt += 1
        self.statusSet = r
        return diff


class UserList:
    def __init__(self,nameList):
        self.userList=[]
        for userName in nameList:
            self.userList.append(User(userName))

    def CrawlAll(self):
        diff=[]
        for user in self.userList:
            user.get_rating()
            diff += user.get_status()
        if len(diff):
            sorted_diff = sorted(diff, key=lambda x: x[2]['creationTimeSeconds'], reverse=True)
            report_diff(sorted_diff[:15])

    def ReportAll(self):
        self.CrawlAll()
        for user in self.userList:
            user.show_report()


def report_diff(packed_message):
    messages = colorful.Colorful()
    MaxUserNameLength, MaxProblemNameLength, MaxProblemIdLength = 0,0,0
    pygame.mixer.music.play()

    for message in packed_message:
        MaxUserNameLength = max(MaxUserNameLength, len(message[0]))
        MaxProblemNameLength = max(MaxProblemNameLength, len(message[2]['problem']['name']))
        MaxProblemIdLength = max(MaxProblemIdLength, len(User.calc_problemID(message[2]['problem'])))

    MaxUserNameLength = min(MaxUserNameLength, 25)
    MaxProblemNameLength = min(MaxProblemNameLength, 50)
    MaxProblemIdLength = min(MaxProblemIdLength, 10)

    for message in packed_message:
        messages += ColorfulSubmission(message[0],message[1],message[2],
                                       MaxUserNameLength, MaxProblemNameLength, MaxProblemIdLength)
        messages.append('\n')

    root = tk.Tk()

    text = tk.Text(root, wrap='word', font=('Courier New', 9), fg='#8DBDB1', bg='#1E1F22', borderwidth=0)
    text.pack(fill='both', expand=True, padx=10, pady=10)
    for item in messages:
        text.tag_config(item[1], foreground=item[1])
        text.insert(tk.END, item[0], item[1])
    text.update_idletasks()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = min(screen_width - 10, 600 + 9 * (MaxUserNameLength + MaxProblemIdLength + MaxProblemNameLength))
    window_height = min(screen_height - 50, max(len(packed_message)*20+10,50))

    x = screen_width - window_width - 10
    y = screen_height - window_height - 50
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg='#1E1F22')

    root.overrideredirect(True)
    root.focus_force()
    root.attributes('-topmost', True)

    def close_window(event):
        root.destroy()
    root.after(15000, root.destroy)
    root.bind('<Button-1>', close_window)
    root.mainloop()

def work():
    pygame.mixer.init()
    pygame.mixer.music.load("notification.wav")
    nameList = input().split()
    Group = UserList(nameList[:5])
    Group.ReportAll()

    schedule.every(1).minutes.do(Group.CrawlAll)

    while True:
        schedule.run_pending()
        time.sleep(10)

work()