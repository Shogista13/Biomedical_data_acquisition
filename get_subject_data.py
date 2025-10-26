import pandas as pd
from tkinter import *
import pygame
import os

class Form:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.path = "Data_project/subject"+str(len(os.listdir("Data_project")))
        self.root = Tk()
        self.root.title("Subject data")
        self.root.geometry("400x100")
        self.root.config(bg="grey")
        self.gender = StringVar(self.root, "0")

        self.entry = Entry(self.root,width=25)
        Label(self.root, text="Age", bg="grey").grid(row=1, column=0)
        self.entry.grid(row=1, column=1, ipadx=100)

        Label(self.root, text="Gender", bg="grey").grid(row=2, column=0)
        sexes = {"Female":"F",
                 "Male":"M"}
        for i,(text, value) in enumerate(sexes.items()):
            Radiobutton(self.root,text = text,variable = self.gender,
                value = value,background = "light blue",indicator = 0,
        width=20).grid(row=2+i,column=1,ipadx=100)
        Button(self.root, text="Submit", fg="black", bg="red", command=self.save_data).grid(row=4, column=1)
        self.root.mainloop()

    def save_data(self):
        subject_data = {"Age":[self.entry.get()],
                "Gender":[self.gender.get()],
                "Screen width":[self.width],
                "Screen height":[self.height]
        }
        df = pd.DataFrame(subject_data)
        os.makedirs(self.path)
        pd.DataFrame.to_csv(df, self.path+"/subject_data")
        os.makedirs(self.path+"/unprocessed")
        os.makedirs(self.path+"/processed")
        self.root.destroy()