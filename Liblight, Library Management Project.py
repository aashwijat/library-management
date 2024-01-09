from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter.simpledialog import askstring
#from PIL import ImageTk,Image
import datetime as dt
import threading
import random

#connecting mysql database
import mysql.connector
global connect
def connect():
    global db,cur,db1,cur1
    db = mysql.connector.connect(host='localhost', user='root', password='root1', database='liblight') 
    cur = db.cursor()
    db1 = mysql.connector.connect(host='localhost', user='root', password='root1', database='liblight')
    cur1= db1.cursor()
connect()
##cur1 = db.cursor()

##the lists for qcs
qcs=[[101,"Query","How to understand membership benefits",""],[102,'Complaint','Borrow function not working',""],[101,"Complaint","Books not reaching on time",""]]
sug=[[101,"UI should be more user friendly"],[102,"Add Review system"]]
aqac=[[102,'Query','How to search for books','Simply click on the search button in user functions and type in what criteria you want to search for'],[101,'Query','how to upgrade membership?','you can upgrade membership by borrowing more books, reading them faster and being more active on the app.'],
      [101,"Complaint","Tables not displayed properly","We will try to fix that as soon as possible"]] 

cur.execute("SELECT*FROM books")
booklog=cur.fetchall()
global userlog
cur.execute("SELECT*FROM user")
userlog= cur.fetchall()

def main():
    connect()
    root= Tk()
    root.title('Library')
    root.geometry('800x600')

    '''background_image =Image.open("lib4.jpg")
    img = ImageTk.PhotoImage(background_image)
    Canvas1 = Canvas(root)      
    Canvas1.config(bg="#12a4d9")
    Canvas1.create_image(600,400,image = img)
    Canvas1.pack(expand=True,fill=BOTH,anchor='ne')'''

    Canvas1 = Canvas(root)
    Canvas1.config(bg="#12a4d9")
    Canvas1.pack(expand=True,fill=BOTH)

    headingFrame1 = Frame(root,bg="#FFBB00",bd=5)
    headingFrame1.place(relx=0.25,rely=0.1,relwidth=0.5,relheight=0.13)

    headingLabel = Label(headingFrame1, text="LIBLIGHT LOGIN", bg='black', fg='white', font=('Courier',15))
    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

    labelFrame = Frame(root,bg='black')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.35)

    #Login details
    co=Label(labelFrame,text='Select Profile: ', bg='black', fg='white',font=('',14))
    co.place(relx=0.05,rely=0.2, relheight=0.1)
    spbu=Combobox(labelFrame,values=('Admin','User'))
    spbu.place(relx=0.3,rely=0.2, relwidth=0.62, relheight=0.1)
    
    co1=Label(labelFrame,text='Username :', bg='black', fg='white',font=('',14))
    co1.place(relx=0.05,rely=0.365, relheight=0.1)
    unbu=Entry(labelFrame)
    unbu.place(relx=0.3,rely=0.365, relwidth=0.62, relheight=0.1)
    
    co2=Label(labelFrame,text='Password :', bg='black', fg='white',font=('',14))
    co2.place(relx=0.05,rely=0.53, relheight=0.1)
    psbu=Entry(labelFrame,show='*')
    psbu.place(relx=0.3,rely=0.53, relwidth=0.62, relheight=0.1)

    #updating fines
    global dailfines
    def dailfines():
        global connect, fup
        connect()
        tdate=dt.date.today()
        cur1.execute('SELECT bk_id,title,fine,borrowed_by,issued_on,due_on,returned_on,sl_no FROM borrowed_books WHERE (%s > due_on) AND (status IN (%s,%s) AND status!=%s)',(tdate,'Pending','-','Paid'))
        finst=cur1.fetchall()
        fdic={}
        for us in userlog:
            fdic[us[1]]=0
        for fr in finst:
            f=list(fr)
            if f[6]== None:
                f[6]= tdate
            dn=(f[6]-f[5]).days
            if dn>0:
                for j in userlog:
                    if j[1]==f[3]:
                        if j[8]=="silver":
                            f[2]=(dn*5.0)-15.0
                        elif j[8]=="gold":
                            f[2]=(dn*5.0)-25.0
                        else:
                            f[2]=dn*5.0
                        
                cur1.execute('UPDATE borrowed_books SET fine= %s, status=%s WHERE borrowed_by= %s AND sl_no= %s',(f[2],'Pending',f[3],f[7]))
                db1.commit()
                #print(f)
                x=fdic[f[3]]
                fdic[f[3]]= float(x) + f[2]
        print('\n',fdic)
        for u in fdic:
            connect()
            cur1.execute('UPDATE user SET fines= %s, due_amount= %s WHERE username= %s',(fdic[u],fdic[u],u))
            db1.commit()
    dailfines()
    
    #After logging in
    global login
    def login():

    
        #USER FUNCTIONS
        if spbu.get().lower()=='user':

            #Username 
            global userlog,unpsli,cusid #global pname

            unpsli={}
            for p in userlog:
                unpsli[p[1]]= p[5]

            #cur.execute('SELECT name FROM user WHERE username= %s AND password = %s', (unbu.get(), psbu.get(),))
            #pname = cur.fetchone()
                  
            if unbu.get() in unpsli and psbu.get()== unpsli[unbu.get()]: #if str(pname) != None: 
                global ub,memcheck,bbk
                ub=unbu.get()#Username

                cur.execute('SELECT user_id FROM user WHERE username= %s AND password = %s', (unbu.get(), psbu.get(),))
                cusid=cur.fetchone()[0]

                def memcheck():
                    cur.execute("SELECT current_reader FROM books")
                    bobrno= cur.fetchall()

                    cur.execute("SELECT membership FROM user WHERE username=%s", (ub,))
                    usmems= cur.fetchone()[0]

                    borcount=0
                    for i in bobrno:
                        if i[0]==ub:
                            borcount+=1
                    return usmems,borcount

                def bbk(b):
                    global memcheck,ub
                    bormem=memcheck()
                                    
                    cur.execute("SELECT status,title,author FROM books WHERE b_id=%s", (b,))
                    rec=cur.fetchone()
                    stat=rec[0]
                    print(stat)

                    cur.execute("SELECT * from borrowed_books where borrowed_by=%s",(ub,))
                    bbde=cur.fetchall();coul=[];bbdic={}
                    ttd=dt.date.today().month
                    tty=dt.date.today().year
                    for bo in bbde:
                        btd=bo[5].month
                        bty=bo[5].year
                        if btd==ttd and tty==bty:
                            coul.append(bo[1])
                    for i in coul:
                        coun=coul.count(i)
                        bbdic[i]=coun
                    print(bbde)
                    print(coul)
                    print(bbdic)
                    
                    usmem= bormem[0]; borcoun=bormem[1]
                    #print(stat,bobrno,usmems,borcount)
                    print(usmem=='bronze' and borcoun==2)
                    print(usmem=='silver' and borcoun==3)
                    print(usmem=='gold' and borcoun==4)
                                    
                    if stat!="Issued" :
                        if (usmem=='bronze' and borcoun==2) or (usmem=='silver' and borcoun==3) or (usmem=='gold' and borcoun==4):
                            messagebox.showinfo('Borrow Book','Sorry! You cannot borrow more books\nYou are exceeding your borrow limit\nbased on your membership')
                                            
                        else:
                                            
                            date=dt.datetime.now()
                            doidt=date.strftime('%Y-%m-%d')
                            td=dt.date.today()
                            if usmem=='bronze':
                                rd=td+dt.timedelta(days=7)
                            elif usmem=='silver':
                                rd=td+dt.timedelta(days=10)
                            elif usmem=='gold':
                                rd=td+dt.timedelta(days=12)
                            dordt=rd.strftime('%d-%m-%Y')
                            print(doidt,dordt)
                            statusup="Issued"; bkeid=int(b)
                            cur.execute("UPDATE books SET status= %s,current_reader= %s,issued_on=%s WHERE b_id= %s",(statusup,ub,doidt,bkeid))
                            db.commit()
                            cur.execute("INSERT INTO borrowed_books(bk_id,title,author,borrowed_by,issued_on,due_on) values (%s,%s,%s,%s,%s,%s)",(bkeid,rec[1],rec[2],ub,doidt,rd))
                            db.commit()
                            messagebox.showinfo('Borrow Book','You have Borrowed the book!\nPlease return the book on or before\n%s'%(dordt,))

                    else:
                        messagebox.showinfo('Borrow Book','Sorry! This book has already been borrowed')

                global rbk
                def rbk(bn,brd):
                    global st,ub,userlog
                    cur.execute("SELECT b_id, title, author, genre, status, current_reader, issued_on FROM books WHERE b_id=%s", (bn,))
                    st= cur.fetchone()
                    date=dt.datetime.now()
                    doidt=date.strftime('%Y-%m-%d')
                    print(st)
                    
                    if st[4]!="Available" and st[5]==ub:
                        statusup="Available"; curuse=''
                        cur.execute("UPDATE books SET status= %s,current_reader= %s,issued_on=%s WHERE b_id= %s",(statusup,curuse,0000-00-00,st[0]))
                        db.commit()
                        cur.execute("UPDATE borrowed_books SET returned_on= %s WHERE bk_id= %s and issued_on=%s and borrowed_by=%s",(doidt,st[0],brd,ub))
                        db.commit()
                        connect()
                        dailfines()
                        cur.execute('SELECT fine FROM borrowed_books WHERE bk_id= %s and borrowed_by=%s and issued_on=%s',(st[0],ub,brd))
                        fine=cur.fetchone()[0]
                        if fine>0.0:
                            messagebox.showinfo('Return Book','Book Returned! You have returned the book past due date.\nPlease pay a fine of Rs %s'%(fine,))
                        else:
                            messagebox.showinfo('Return Book','Book Returned!')
                    else:
                        messagebox.showinfo('Return Book','Sorry! This book cannot be returned.\n You have not borrowed the book or It is Available')
                       
                
                root.withdraw()

                #User window
                rootu = Tk()
                rootu.title("Library")
                rootu.minsize(width=400,height=400)
                rootu.geometry("1000x650")

                Canvas1 = Canvas(rootu)
                Canvas1.config(bg="#12a4d9")
                Canvas1.pack(expand=True,fill=BOTH)

                headingFrame1 = Frame(rootu,bg="#FFBB00",bd=5)
                headingFrame1.place(relx=0.3,rely=0.08,relwidth=0.4,relheight=0.13)
                headingLabel = Label(headingFrame1, text="HOME PAGE", bg='black', fg='white', font=('Courier',17, ))
                headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                labelFrame = Frame(rootu,bg='black')
                labelFrame.place(relx=0.08,rely=0.26,relwidth=0.82,relheight=0.6)

                lb2 = Label(labelFrame,text="Hello user! Welcome to LibLight Library. \n What would you like to use today?: ", bg="#FFBB00", fg='black', font=('Courier',13))
                lb2.place(relx=0.001,rely=0.001,relwidth=1,relheight=0.14)

                #HOMEPAGE Functions
                
                #Profile Window
                def prof():
                    global userlog,ub,cusid
                    pro=Tk()
                    pro.title("Your Account")
                    pro.geometry('600x500')

                    Canvas1 = Canvas(pro)
                    Canvas1.config(bg="#12a4d9")
                    Canvas1.pack(expand=True,fill=BOTH)
                    
                    headingFrame1 = Frame(pro,bg="#FFBB00",bd=5)
                    headingFrame1.place(relx=0.25,rely=0.1,relwidth=0.5,relheight=0.13)

                    headingLabel = Label(headingFrame1, text="PROFILE", bg='black', fg='white', font=('Courier',15))
                    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                    labelFrame = Frame(pro,bg='black')
                    labelFrame.place(relx=0.1,rely=0.36,relwidth=0.8,relheight=0.4)
                    
                    #User Details
                    global ps,nm,db,em,mbn,Ud,dob,j
                    #cur.execute("SELECT  username, name, email_id, mobile_no, dob, password FROM user WHERE username=%s", (unbu.get(),))
                    cur.execute("SELECT  username, name, email_id, mobile_no, dob, password FROM user WHERE user_id=%s", (cusid,))
                    j = cur.fetchone()
##                    ps=userlog[ub]['password']
                    nm=j[1]
                    dob=j[4]
                    em=j[2]
                    mbn=j[3]
                    ps= j[5]
                    ub= j[0]
##                    global passwd, name, email, dob, mobileno, userid
                    

                    #Edit profile
                    def edi():
                        
                        global userlog,ub, dobed,cusid

                        pro.withdraw()
                    
    
                        proed=Tk()
                        proed.title("Edit Profile")
                        proed.geometry('1000x650')

                        Canvas1 = Canvas(proed) 
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(proed,bg='#FFBB00',bd=5)
                        headingFrame1.place(relx=0.25,rely=0.07,relwidth=0.5,relheight=0.13)

                        headingLabel = Label(headingFrame1, text="EDIT PROFILE", bg='black', fg='white', font = ('Courier',18))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(proed,bg='black')
                        labelFrame.place(relx=0.1,rely=0.3,relwidth=0.8,relheight=0.6)
                        Label(labelFrame, text='Edit Details', bg='#FFBB00', fg='black', font = ('Courier',18), padx=500).place(relx=0,rely=0,)
                            
                        #User id 
                        lb1 = Label(labelFrame,text="Username", bg='black', fg='white',font=('Courier',15))
                        lb1.place(relx=0.05,rely=0.13, relheight=0.07)
                        usnm = Entry(labelFrame,bg='grey98')
                        usnm.place(relx=0.05,rely=0.20, relwidth=0.35, relheight=0.07)
                        usnm.insert(0,ub)
                        
                        #Password
                        lb2 = Label(labelFrame,text="Password", bg='black', fg='white',font=('Courier',15))
                        lb2.place(relx=0.05,rely=0.33, relheight=0.07)
                        '''psed = Button(labelFrame,text='Change Password',bg='grey98')
                        psed.place(relx=0.05,rely=0.40, relwidth=0.35, relheight=0.07)
                        psed.insert(0,ps)'''
                        
                        #User name
                        lb3 = Label(labelFrame,text="Name", bg='black', fg='white',font=('Courier',15))
                        lb3.place(relx=0.05,rely=0.53, relheight=0.07)
                        funm = Entry(labelFrame,bg='grey98')
                        funm.place(relx=0.05,rely=0.60, relwidth=0.35, relheight=0.07)
                        funm.insert(0,nm)
                        
                        #Date of birth
                        lb4 = Label(labelFrame,text="Date of Birth ", bg='black', fg='white',font=('Courier',15))
                        lb4.place(relx=0.05,rely=0.73, relheight=0.07)
                        dobed = Entry(labelFrame,bg='grey98')
                        dobed.place(relx=0.05,rely=0.80, relwidth=0.35, relheight=0.07)
                        dobed.insert(0,dob)
                        
                        #Email id
                        lb5 = Label(labelFrame,text="Email ID", bg='black', fg='white',font=('Courier',15))
                        lb5.place(relx=0.55,rely=0.13, relheight=0.07)
                        emide = Entry(labelFrame,bg='grey98')
                        emide.place(relx=0.55,rely=0.20, relwidth=0.35, relheight=0.07)
                        emide.insert(0,em)
                        
                        #Mobile number
                        lb6 = Label(labelFrame,text="Mobile number ", bg='black', fg='white',font=('Courier',15))
                        lb6.place(relx=0.55,rely=0.33, relheight=0.07)
                        mbnme = Entry(labelFrame,bg='grey98')
                        mbnme.place(relx=0.55,rely=0.40, relwidth=0.35, relheight=0.07)
                        mbnme.insert(0,mbn)

                        def chpw():

                            proed.withdraw()
                            
                            rootf=Tk()
                            rootf.title('User Password')
                            rootf.geometry('600x400')
                                
                            Canvasf = Canvas(rootf) 
                            Canvasf.config(bg="#12a4d9")
                            Canvasf.pack(expand=True,fill=BOTH)

                            headingFrame1f = Frame(rootf,bg="#FFBB00",bd=5)
                            headingFrame1f.place(relx=0.1,rely=0.07,relwidth=0.8,relheight=0.13)

                            headingLabelf = Label(headingFrame1f, text=" CHANGE PASSWORD .", bg='black', fg='white', font = ('Courier',15))
                            headingLabelf.place(relx=0,rely=0, relwidth=1, relheight=1)
                            Label(rootf,bg='lightblue',padx=1200,pady=0.5).place(relx=0,rely=0.24)

                            global ue1,cue1,ue2,cue2
                                
                            labelFramef = Frame(rootf,bg='black')
                            labelFramef.place(relx=0.1,rely=0.33,relwidth=0.8,relheight=0.6)
                                
                            ue1=Label(labelFramef,text='Current Password:',font=('',15),bg='black',fg='white')
                            ue1.place(relx=0.1,rely=0.14, relheight=0.07)
                                
                            cue1=Entry(labelFramef)
                            cue1.place(relx=0.49,rely=0.14, relwidth=0.35, relheight=0.07)
                                
                            ue2=Label(labelFramef,text='New Password:',font=('',15),bg='black',fg='white')
                            ue2.place(relx=0.1,rely=0.33, relheight=0.07)
                                
                            cue2=Entry(labelFramef)
                            cue2.place(relx=0.49,rely=0.33, relwidth=0.35, relheight=0.07)

                            ue3=Label(labelFramef,text='Confirm Password:',font=('',15),bg='black',fg='white')
                            ue3.place(relx=0.1,rely=0.52, relheight=0.07)
                                
                            cue3=Entry(labelFramef)
                            cue3.place(relx=0.49,rely=0.52, relwidth=0.35, relheight=0.07)

                            global psd,usi
                            cur.execute("SELECT  username, name, email_id, mobile_no, dob, password FROM user WHERE user_id=%s", (cusid,))
                            usi = cur.fetchone()
                            psd=usi[5]

                            def doncp():
                                global ub,psd,cusid
                                if (len(cue1.get())==0) or (len(cue2.get())==0) or (len(cue3.get())==0):
                                    messagebox.showerror('Password Entry','All Entries are Mandatory!\nFill in All the Details')
                                    
                                elif cue1.get()!= psd:
                                    messagebox.showerror('Wrong Password','Oh no! You have entered\nIncorrect Password !')
                                    
                                elif cue3.get()!=cue2.get():
                                    messagebox.showerror('New Password','Passwords Do Not Match!')
                                    
                                elif cue3.get()==cue2.get():
                                    #update password
                                    cur.execute("UPDATE user SET password= %s WHERE user_id= %s", (cue3.get(),cusid))
                                    db.commit()
                                    
                                #Condition if both given pswd and in database are same, if updated
                                cur.execute("SELECT password FROM user WHERE user_id=%s", (cusid,))
                                nchps = cur.fetchone()
                                if (cue1.get()== psd) and (nchps[0]==cue3.get()) and (nchps[0]==cue2.get()): #if(ab in U and U[ab]==cue3.get()) and (cue2.get()==Ud[ab]['Password']):
                                    messagebox.showinfo('New Password','New Password Created')
                                    rootf.destroy()
                                    proed.deiconify()

                            npsbu=Button(labelFramef,text="Done",bg='lightgrey',font=('Times',14),command=doncp)
                            npsbu.place(relx=0.36,rely=0.72, relwidth=0.28,relheight=0.15)
                            rootf.mainloop()

                        psed = Button(labelFrame,text='Change Password',bg='grey98',command=chpw)
                        psed.place(relx=0.05,rely=0.40, relwidth=0.35, relheight=0.07)

                        def save():
                            #Entry Error Message
                            global userlog,dbg,dobed,cusid
                            dbg= dobed.get()
                            cur.execute("SELECT username FROM user")
                            userlo = cur.fetchall()
                            global tm
                            tm='y'
                            while tm=='y':  #for i in range(4):
                                if '-' not in dbg:
                                    messagebox.showerror('Date of Birth','Write in correct format\nyyyy-mm-dd')
                                    tm='n'
                                    break
##                                else:
##                                    tm=0

                                print('after dob',tm)
                                    
                                if '.com' not in emide.get() or '@' not in emide.get():
                                    messagebox.showerror('Email Id','Write in correct format\nabc@xyz.com')
                                    tm='n'
                                    break
##                                else:
##                                    tm=0

                                print('after email',tm)

                                def uche():
                                    global tm
                                    for c in userlo:
                                        if usnm.get()== c[0] and usnm.get()!=ub:
                                            messagebox.showerror('Username','Username already exists\nTry Again')
                                            tm='h'
                                            print('after us',tm)
                                            break
    ##                                  break
    ##                                else:
    ##                                    tm=0
    ##                                    break


                                def mche():
                                    global tm
                                    for k in mbnme.get():
                                        if k.isdigit()== False:
                                            messagebox.showerror('Mobile Number','Invalid Entry\nTry Again')
                                            tm='h'
                                            break
##                                        break

                                
                                global dobli
                                dobli=dbg.split('-')
                                if len(dobli[0])!=4:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    tm='n'
                                    break
                                elif int(dobli[1])>12:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    tm='n'
                                    break
                                elif int(dobli[2])>31:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    tm='n'
                                    break

                                def bche():
                                    global tm,dobli
                                    for k in dobli:
                                        if k.isdigit()== False:
                                            messagebox.showerror('Date of Birth','Date of Birth is NOT in Digits')
                                            tm='h'
                                            break
                                        
                                bche()        
                                uche()
                                mche()
                                break
                            
                            if tm=='y':
                                tm=0
##                            
##                                    '''else:
##                                        tm=0
##                                        break'''

                            print(tm)
                                
                            while tm==0: #if '-'in dbg and k in ['1','2','3','4','5','6','7','8','9','0',' '] and ('.com' in emide.get() and '@' in emide.get()):

                                
                                #Saving
                                global l1,l2,l3,l4,l5,l6
                                
##                                udadd = ("ALTER TABLE user SET user_id, username, 
##                                udadd={'Password':psed.get(),'Name':funm.get(),'DOB':dbg,'DOJ':doj,'Email_Id':emide.get(),'MobNum':int(mbnme.get())}
##                                del userlog[ub]
##                                delete = "DELETE FROM user WHERE username =%s", (unbu.get(),)
##                                cur.execute(delete)
##                                db.commit()
##                                userlog.setdefault(usnm.get(),udadd)
                                
                                global nusn,nnm,ndj,nem,nmbn,ndb
                                
##                                cur.execute("SELECT username,email_id, mobile_no, dob FROM user WHERE username=%s", (unbu.get(),))
##                                f = cur.fetchone()
##                                nnm=f[0]['Name']
##                                ndj=userlog[nusn]['DOJ']
                                
##                                cur.execute("SELECT user_id, name,email_id, mobile_no, dob, username FROM user WHERE username=%s", (unbu.get(),))
##                                ez = cur.fetchone()

                                nnm=funm.get()
                                nem=emide.get()
                                nmbn=mbnme.get()
                                ndb=dobed.get()
                                nusn=usnm.get()
                                
                                #Updating Profile Page
##                                update = "UPDATE user SET email_id= {} WHERE username = {}.format(nem,unbu)"
##                                cur.execute(update)
##                                db.commit()
                                
                                #userid= int(unbu.get())
                                
##                                upd = "UPDATE user SET email_id= %s, mobile_no= %s, dob= %s, username= %s, name= %s WHERE user_id= %s", (nem,nmbn,ndb,nusn,nnm,ez[0])
##                                try:
##                                    cur.execute(upd)
##                                    db.commit()
##                                except:
##                                    db.rollback()

                                global cusid

                                cur.execute("UPDATE user SET email_id= %s, mobile_no= %s, dob= %s, username= %s, name= %s WHERE user_id= %s", (nem,nmbn,dt.datetime.strptime(ndb,'%Y-%m-%d').date(),nusn,nnm,cusid))
                                db.commit()

                                #cur.execute("UPDATE user SET user_id_name= %s,username= %s,email_id= %s,mobile_no= %s,dob= %s WHERE user_id= %s",(nusn,nnm,nem,nmbn,ndb,ez[0]))
                                #db.commit()
                  
                                #Delete Previous
                                '''lb1.destroy()
                                lb2.destroy()
                                lb3.destroy()
                                lb4.destroy()
                                lb5.destroy()'''
                                #Message of Update
                                cur.execute("SELECT user_id, name,email_id, mobile_no, dob, username FROM user WHERE user_id=%s", (cusid,))
                                ez1 = cur.fetchone()
                                
                                if ez1[5]==nusn and ez1[1]==nnm and ez1[2]==nem and ez1[3]==nmbn and ez1[4]==dt.datetime.strptime(ndb,'%Y-%m-%d').date():
                                    messagebox.showinfo('Edited Profile','Changes Saved')
                                    proed.destroy()
                                    pro.destroy()
                                    prof()
                                else:
                                    messagebox.showinfo('Edited Profile','Sorry! Changes Not Saved')
                                    
                                #Updated/Edited Details
                                '''Label(pro,text=nusn,font=('Times',42)).place(x=680,y=100)
                                Label(pro,text=nnm,font=('Roman',20)).place(x=980,y=250)
                                Label(pro,text=ndj,font=('Roman',20)).place(x=980,y=330)
                                Label(pro,text=nem,font=('Roman',20)).place(x=980,y=410)
                                Label(pro,text=nmbn,font=('Roman',20)).place(x=980,y=490)
                                Label(pro,text=ndb,font=('Roman',20)).place(x=980,y=570)'''

                                break

                        saveb = Button(labelFrame,text="SAVE ",bg='#f7f1e3', fg='black',command=save)
                        saveb.place(relx=0.75,rely=0.8,relwidth=0.18, relheight=0.08)
                        
                    #Log Out
                    def logout():
                        pro.destroy()
                        rootu.destroy()
                        root.destroy()
                        main()

                    #Membership
                    def Membership():
                        
                        global ub,memcheck
                        
                        pro.withdraw()

                        mesp=memcheck()
                        if mesp[0]=='bronze':
                            blim=2
                            btie=' 7 days '
                            finew=" Not applicable "
                            col='LightSalmon3'
                        elif mesp[0]=='silver':
                            blim=3
                            btie=' 7+3 days '
                            finew=" Rs. 15 per book"
                            col='silver'
                        elif mesp[0]=='gold':
                            blim=4
                            btie=' 7+5 days '
                            finew=" Rs. 25 per book"
                            col='gold'
                        else:
                            pass
                        
                        memb = Tk()
                        memb.title("Library")
                        memb.minsize(width=400,height=400)
                        memb.geometry("1000x650")

                        Canvas1 = Canvas(memb)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(memb,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.3,rely=0.08,relwidth=0.4,relheight=0.13)
                        headingLabel = Label(headingFrame1, text="MEMBERSHIP", bg='black', fg='white', font=('Courier',17))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(memb,bg='black')
                        labelFrame.place(relx=0.08,rely=0.26,relwidth=0.82,relheight=0.58)

                        lb2 = Label(labelFrame,text="Welcome to MEMBERSHIP! These are the tiered benefits you get with your account. ", bg="#FFBB00", fg='black', font=('Courier',13))
                        lb2.place(relx=0.001,rely=0.001,relwidth=1,relheight=0.14)

                        #username
                        lb1 = Label(labelFrame,text="Username: ", bg='black', fg='white',font=('Courier',14))
                        lb1.place(relx=0.07,rely=0.2, relheight=0.08)
                        '''uname = Entry(labelFrame,bg='grey98',)
                        uname.place(relx=0.07,rely=0.3, relwidth=0.35, relheight=0.08)
                        uname.configure(state="disabled")'''
                        uname = Label(labelFrame,bg='grey98',text=ub,font=('',13))
                        uname.place(relx=0.07,rely=0.3, relwidth=0.35, relheight=0.08)

                        #Membership Tier
                        lb2 = Label(labelFrame,text="Membership Tier: ", bg='black', fg='white',font=('Courier',14))
                        lb2.place(relx=0.57,rely=0.2, relheight=0.08)
                        '''umt = Entry(labelFrame,bg='grey98')
                        umt.place(relx=0.57,rely=0.3, relwidth=0.35, relheight=0.08)
                        umt.configure(state="disabled")'''
                        umt = Label(labelFrame,bg=col,text=mesp[0],font=('',13))
                        umt.place(relx=0.57,rely=0.3, relwidth=0.35, relheight=0.08)

                        #Borrow Rate
                        lb3 = Label(labelFrame,text="Borrow Rate: ", bg='black', fg='white',font=('Courier',14))
                        lb3.place(relx=0.07,rely=0.45, relheight=0.08)
                        '''ubr = Entry(labelFrame,bg='grey98')
                        ubr.place(relx=0.07,rely=0.55, relwidth=0.35, relheight=0.08)
                        ubr.configure(state="disabled")'''
                        ubr = Label(labelFrame,bg='grey98',text=str(mesp[1])+' / '+str(blim)+" books",font=('',13))
                        ubr.place(relx=0.07,rely=0.55, relwidth=0.35, relheight=0.08)

                        #Borrow Time
                        lb4 = Label(labelFrame,text="Borrow Time: ", bg='black', fg='white',font=('Courier',14))
                        lb4.place(relx=0.57,rely=0.45, relheight=0.08)
                        '''ubt = Entry(labelFrame,bg='grey98')
                        ubt.place(relx=0.57,rely=0.55, relwidth=0.35, relheight=0.08)
                        ubt.configure(state="disabled")'''
                        ubt = Label(labelFrame,bg='grey98',text=btie,font=('',13))
                        ubt.place(relx=0.57,rely=0.55, relwidth=0.35, relheight=0.08)

                        #Fine waver
                        lb5 = Label(labelFrame,text="Fine waiver: ", bg='black', fg='white',font=('Courier',14))
                        lb5.place(relx=0.07,rely=0.7, relheight=0.08)
                        ufw = Label(labelFrame,bg='grey98',text=finew,font=('',13))
                        ufw.place(relx=0.07,rely=0.8, relwidth=0.35, relheight=0.08)                              

                        #other
                        lb6 = Label(labelFrame,text="Other Benefits: ", bg='black', fg='white',font=('Courier',14))
                        lb6.place(relx=0.57,rely=0.7, relheight=0.08)
                        uoth = Entry(labelFrame,bg='grey98')
                        uoth.place(relx=0.57,rely=0.8, relwidth=0.35, relheight=0.08)
                        uoth.insert(0," None Applicable")
                        uoth.configure(state="disabled")
                       

                        sBtn = Button(memb,text="RETURN TO PROFILE",bg='#f7f1e3', fg='black', font = ('Courier',14),command=lambda:[pro.destroy(),memb.destroy(),prof()])
                        sBtn.place(relx=0.35,rely=0.86, relwidth=0.3,relheight=0.09)

                    # User's name
                    lb1 = Label(labelFrame,text="NAME : ", bg='black', fg='white', font=('MS Sans Serif',13))
                    lb1.place(relx=0.07,rely=0.17, relheight=0.08)
                    
                    l1 = Label(labelFrame, text=nm, bg='black', fg='white', font=('Helvetica',13))#bg="white", fg="black")
                    l1.place(relx=0.55,rely=0.17, relheight=0.095)#, relwidth=0.62, relheight=0.08)
                    
                    # User Id          # Date of joining
                    lb2 = Label(labelFrame,text="USERNAME : ", bg='black', fg='white', font=('MS Sans Serif',13)) #text="Date of joining : ", bg='black', fg='white')
                    lb2.place(relx=0.07,rely=0.32, relheight=0.08)
                    
                    l2 = Label(labelFrame, text=ub, bg='black', fg='white', font=('Helvetica',13))#bg="white", fg="black" )   #l2 = Label(labelFrame, text=doj, bg="white", fg="black" )
                    l2.place(relx=0.55,rely=0.32, relheight=0.095)#, relwidth=0.62, relheight=0.08)
                    
                    # Email Id
                    lb3 = Label(labelFrame,text="EMAIL ID : ", bg='black', fg='white', font=('MS Sans Serif',13))
                    lb3.place(relx=0.07,rely=0.47, relheight=0.08)
                    
                    l3 = Label(labelFrame,text=em,bg='black', fg='white', font=('Helvetica',13))#bg="white", fg="black" )
                    l3.place(relx=0.55,rely=0.47, relheight=0.095)#, relwidth=0.62, relheight=0.08)

                    # Mobile no
                    lb4 = Label(labelFrame,text="MOBILE NUMBER : ", bg='black', fg='white', font=('MS Sans Serif',13))
                    lb4.place(relx=0.07,rely=0.62, relheight=0.08)
                    
                    l4 = Label(labelFrame, text=mbn, bg='black', fg='white', font=('Helvetica',13))#bg="white", fg="black")
                    l4.place(relx=0.55,rely=0.62, relheight=0.095)#, relwidth=0.62, relheight=0.08)
                    
                    # Date of birth
                    lb5 = Label(labelFrame,text="DATE OF BIRTH : ", bg='black', fg='white', font=('MS Sans Serif',13))
                    lb5.place(relx=0.07,rely=0.77, relheight=0.08)
                    
                    l5 = Label(labelFrame, text=dob , bg='black', fg='white', font=('Helvetica',13))#bg="white", fg="black")
                    l5.place(relx=0.55,rely=0.77, relheight=0.095)#, relwidth=0.62, relheight=0.08)
                    
                    #Side Buttons
                    editBtn = Button(pro,text="Edit profile",bg='#d1ccc0', fg='black',command=edi)
                    editBtn.place(relx=0.2,rely=0.86, relwidth=0.18,relheight=0.08)

                    membBtn = Button(pro,text="Membership",bg='#f7f1e3', fg='black',command=Membership)
                    membBtn.place(relx=0.4,rely=0.86, relwidth=0.18,relheight=0.08)

                    logBtn = Button(pro,text="LOGOUT",bg='#d1ccc0', fg='black', command=logout)
                    logBtn.place(relx=0.6,rely=0.86, relwidth=0.18,relheight=0.08)
                  
                    pro.mainloop()

                #Activity Window
                def activity():
                    global cur,ub
                    cur.execute("SELECT * from books")
                    blist=cur.fetchall()

                    ##cur.execute("SELECT * from books WHERE current_reader=%s",(uid,))
                    ##un=cur.fetchone()
                    global bl
                    bl=[]
                    for a in blist:
                        if a[6]==ub:
                            bl.append(a)
                            
                    ##BORROW
                    def borrow():

                        def borbk():
                            global v,ub,bn
                            
                            lb3 = Label(labelFrame,text="Book Details: ", bg='black', fg='white', font=('Courier',13))
                            lb3.place(relx=0.26,rely=0.22, relwidth=0.45, relheight=0.1)

                            '''tab=Label(labelFrame, text="%-5s%-36s%-20s%-12s"%('BID','Title','Author','Genre'),font = ('Courier',12),bg='black',fg='white')
                            tab.place(relx=0.06,rely=0.33)
                            line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                            line.place(relx=0.06,rely=0.38)'''
                            tab=Label(labelFrame, text="%-8s%-35s%-18s%-15s%-10s"%('BID','Title','Author','Genre','Status'),font = ('Courier',12),bg='black',fg='white')
                            tab.place(relx=0.032,rely=0.33)
                            line=Label(labelFrame, text = "------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                            line.place(relx=0.03,rely=0.38)

                            lb4 = Label(labelFrame,text="How would you like to proceed?", bg='white', fg='black', font=('Courier',13))
                            lb4.place(relx=0.25,rely=0.6, relwidth=0.45, relheight=0.1)
                        
                            cur.execute("SELECT*FROM books")
                            booklog=cur.fetchall()
                            disli=[]
                            for a in booklog:
                                if bn.get().lower() in a[1].lower():
                                    disli.append(a)
                                            
                            t=0
                            if len(disli)!=0: 
                                        
                                global i
                                t=t+1
                                                    
                                #Display Book Details
                                i=bn.get()
                                
                                labelFrame1=Frame(labelFrame,bg='black')
                                labelFrame1.place(relx=0.025,rely=0.45,relheight=0.27)

                                scrollb=Scrollbar(labelFrame1,orient=VERTICAL)

                                bslt=Listbox(labelFrame1,width=90,yscrollcommand=scrollb.set,bg='black',fg='white',font=('Courier',12))

                                scrollb.config(command=bslt.yview)
                                scrollb.pack(side=RIGHT,fill=Y)


                                for v in disli:
                                    #bslt.insert(END,"%-5s%-36s%-20s%-12s"%(str(v[0]),v[1],v[2],v[3]))
                                    bslt.insert(END,"%-5s%-35s%-19s%-19s%-15s"%(str(v[0]),v[1],v[2],v[3],v[5]))


                                bslt.pack()

                                def bord():
                                            global bbk
                                            val=bslt.get(ANCHOR)
                                            if val=='':
                                                messagebox.showerror('Selection','Please Select Book to Borrow.')
                                            else:
                                                l=val.split()[0];print(l)
                                                cur.execute("SELECT title,author FROM books WHERE b_id=%s", (l,))
                                                bdet= cur.fetchone()
                                                resp=messagebox.askyesno('Borrow Book','Do you want to Borrow this Book?\n\n  Book Name: %s\n  Author: %s'%(bdet[0],bdet[1]))
                                                if resp==1:
                                                    bbk(l)
                                                    bk.destroy()
                                                    activity()
                                                    
                                borBtn = Button(labelFrame,text="BORROW BOOK",bg='#d1ccc0', fg='black',font=('Courier',13),command= bord)
                                borBtn.place(relx=0.18,rely=0.78, relwidth=0.25,relheight=0.15)

                                bBtn = Button(labelFrame,text="BACK TO ACTIVITY",bg='#d1ccc0', fg='black',font=('Courier',13),command=lambda:[bk.destroy(),activity()])
                                bBtn.place(relx=0.52,rely=0.78, relwidth=0.25,relheight=0.15)

                            else:
                                messagebox.showerror('Borrow Book','Sorry! Book not Found')
                                bk.destroy()
                                borrow()

                            
                        
                        bk=Tk()
                        bk.title("Borrow Function")
                        bk.minsize(width=400,height=400)
                        bk.geometry("1100x650")
                        
                        Canvas1 = Canvas(bk)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(bk,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.3,rely=0.08,relwidth=0.4,relheight=0.13)
                        headingLabel = Label(headingFrame1, text="BORROW", bg='black', fg='white', font=('Courier',18))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(bk,bg='black')
                        labelFrame.place(relx=0.06,rely=0.28,relwidth=0.88,relheight=0.58)

                        lb2 = Label(labelFrame,text="Enter book name: ", bg="#FFBB00", fg='black', font=('Courier',13))
                        lb2.place(relx=0.08,rely=0.1, relwidth=0.3, relheight=0.1)
                        global bn
                        bn = Entry(labelFrame)
                        bn.place(relx=0.4,rely=0.1, relwidth=0.4, relheight=0.1)
                        ebtn = Button(labelFrame,text="ENTER",bg='#d1ccc0', fg='black',command=borbk)
                        ebtn.place(relx=0.82,rely=0.1, relwidth=0.1,relheight=0.1,)
                        

                    ##FINES DISPLAY
                    def fined():

                        global memcheck,ub
                        
                        fk=Tk()
                        fk.title("Pending Fines")
                        fk.minsize(width=400,height=400)
                        fk.geometry("605x400")
                        
                        Canvas1 = Canvas(fk)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(fk,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.25,rely=0.08,relwidth=0.5,relheight=0.13)
                        headingLabel = Label(headingFrame1, text="PENDING FINES", bg='black', fg='white', font=('Courier',18))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(fk,bg='black')
                        labelFrame.place(relx=0.09,rely=0.3,relwidth=0.82,relheight=0.58)
                        
                        td=dt.date.today()
                        cur1.execute("SELECT username from user where fines!=0")
                        uf=cur1.fetchall()
                        for i in uf:
                            m=memcheck()
                            if m[0]=="bronze":
                                rd=td+dt.timedelta(days=-7)
                            elif m[0]=="silver":
                                rd=td+dt.timedelta(days=-10)
                            elif m[0]=="gold":
                                rd=td+dt.timedelta(days=-12)
                            
                            cur1.execute("SELECT title FROM books WHERE current_reader=%s AND issued_on < %s",(ub,rd,))
                            fbks=cur1.fetchall()
                            cur1.execute('SELECT title FROM borrowed_books WHERE borrowed_by=%s AND fine != %s AND status=%s',(ub,0.0,'Pending'))
                            fbbks=cur1.fetchall()
                            for h in fbbks:
                                if h not in fbks:
                                    fbks.append(h)
                            fb=', '.join(str(b[0]) for b in fbks)
                            if ub in i:
                                cur1.execute("SELECT fines from user where username=%s",(ub,))
                                pf=cur1.fetchone()
                                lb2 = Text(labelFrame, bg="white", fg='black', font=('Courier',13))
                                lb2.place(relx=0.05,rely=0.08,relwidth=0.89,relheight=0.65)
                                lb2.insert('end'," You currently have a fine of Rs."+str(pf[0])+" from the books: \n  "+fb+".\n  Please pay this on your next visit after returning the fined books.")
                                lb2.configure(state="disabled")
                                break
                        else:
                            lb3= Text(labelFrame, bg="white", fg='black', font=('Courier',13))
                            lb3.place(relx=0.08,rely=0.08,relwidth=0.83,relheight=0.65)
                            lb3.insert('end'," You currently have no fines pending.\n Congratulate yourself on being a punctual user! :)")
                            lb3.configure(state="disabled")

                        bb=Button(labelFrame,text="BACK TO ACTIVITY",bg='grey', fg='black',font=('Courier',12),command=lambda:[fk.destroy(),activity()])
                        bb.place(relx=0.6,rely=0.8,relwidth=0.36, relheight=0.15) 
                        
                    
                    act=Tk()
                    act.title("Activity")
                    act.minsize(width=400,height=400)
                    act.geometry("1400x700")
                    
                    Canvas1 = Canvas(act)
                    Canvas1.config(bg="#12a4d9")
                    Canvas1.pack(expand=True,fill=BOTH)

                    headingFrame1 = Frame(act,bg="#FFBB00",bd=5)
                    headingFrame1.place(relx=0.3,rely=0.08,relwidth=0.4,relheight=0.13)
                    headingLabel = Label(headingFrame1, text="ACTIVITY", bg='black', fg='white', font=('Courier',18))
                    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                    labelFrame = Frame(act,bg='black')
                    labelFrame.place(relx=0.08,rely=0.28,relwidth=0.82,relheight=0.64)

                    lb2 = Label(labelFrame,text="Welcome to the ACTIVITY! \n These are the books currently in your possession: ", bg="#FFBB00", fg='black', font=('Courier',15))
                    lb2.place(relx=0.001,rely=0.001,relwidth=1,relheight=0.15)

                    tab=Label(labelFrame, text="%-5s%-29s%-15s%-15s%-15s%-14s%-15s"%('BID','Title','Author','Genre','Issued on','To Return','Days Delayed'),font = ('Courier',12),bg='black',fg='white')
                    tab.place(relx=0.03,rely=0.17)
                    line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                    line.place (relx=0.03,rely=0.24)
                    #y=0.3

                    labelFrame1=Frame(labelFrame,bg='black')
                    labelFrame1.place(relx=0.025,rely=0.31,relheight=0.26)
                                        
                    scrollb=Scrollbar(labelFrame1,orient=VERTICAL)

                    bslt=Listbox(labelFrame1,width=102,yscrollcommand=scrollb.set,bg='black',fg='white',font=('Courier',12))

                    scrollb.config(command=bslt.yview)
                    scrollb.pack(side=RIGHT,fill=Y)

                    
                    ##RETURN
                    
                    global memcheck
                    usmem=memcheck()[0]
                    td=dt.date.today()
                    for j in bl:
                        if usmem=='bronze':
                            rd=j[7]+dt.timedelta(days=7)
                        elif usmem=='silver':
                            rd=j[7]+dt.timedelta(days=10)
                        elif usmem=='gold':
                            rd=j[7]+dt.timedelta(days=12)
                        nd=(td-rd).days
                        bslt.insert(END,"%-5s%-27s%-17s%-16s%-15s%-15s%-15s"%(str(j[0]),j[1],j[2],j[3],j[7].strftime('%d-%m-%Y'),rd.strftime('%d-%m-%Y'),nd))

                    bslt.pack()

                    def rord():
                        global rbk
                        val=bslt.get(ANCHOR)
                        if val=='':
                            messagebox.showerror('Selection','Please Select Book to Return.')
                        else:
                            l=val.split()[0];print(l)
                            cur.execute("SELECT title,author,issued_on FROM books WHERE b_id=%s", (l,))
                            bdet= cur.fetchone()
                            resp=messagebox.askyesno('Return Book','Do you want to Return this Book?\n\n  Book Name: %s\n  Author: %s'%(bdet[0],bdet[1]))
                            if resp==1:
                                rbk(l,bdet[2])
                                act.destroy()
                                activity()

                    lb = Label(labelFrame,text="What would you like to do today?", bg='white', fg='black', font=('Courier',13))
                    lb.place(relx=0.2,rely=0.6, relwidth=0.6, relheight=0.08)
                    br=Button(labelFrame,text="BORROW",bg='light grey', fg='black',font=('Courier',12),command=lambda:[act.destroy(),borrow()])
                    br.place(relx=0.1,rely=0.715,relwidth=0.2, relheight=0.13)
                    rt =Button(labelFrame,text="RETURN",bg='light grey', fg='black',font=('Courier',12),command=lambda:rord())
                    rt.place(relx=0.32,rely=0.715,relwidth=0.2, relheight=0.13)
                    pf =Button(labelFrame,text=" VIEW PENDING FINES",bg='light grey', fg='black',font=('Courier',12),command=lambda:[act.destroy(),fined()])
                    pf.place(relx=0.54,rely=0.715,relwidth=0.36, relheight=0.13)
                    bb=Button(labelFrame,text="BACK TO HOME PAGE",bg='grey', fg='black',font=('Courier',12),command=lambda:[act.destroy()])
                    bb.place(relx=0.35,rely=0.88,relwidth=0.27, relheight=0.1)    


                #Discover tab
                def discover():
                    cur.execute("SELECT author, genre, title, b_id FROM books")
                    bl = cur.fetchall()

                    ##Search part
                    def search():
                        #Book List
                        cur.execute("SELECT * from books")
                        boklist=cur.fetchall()

                        def sval():
                            sv=sp.get()

                            def bknmf():

                                def sname():
                                    disli=[]
                                    for a in boklist:
                                        if sb.get().lower() in a[1].lower():
                                            disli.append(a)
                                            
                                    #cur.execute('SELECT b_id, title, author, genre, status FROM books WHERE title=%s', (bn.get(),))
                                    #v = cur.fetchone()
                                    t=0
                                    if len(disli)!=0: 
                                        #for v in disli: 1 tab
                                            #if v!= None: 2 tab
                                        global i
                                        #if bn.get() in v: same as global
                                        t=t+1
                                                    
                                        #Display Book Details
                                        i=sb.get()

                                        lb3 = Label(labelFrame,text="Book Details: ", bg='black', fg='white', font=('Courier',13))
                                        lb3.place(relx=0.26,rely=0.33, relwidth=0.45, relheight=0.1)

                                        labelFrame1=Frame(labelFrame,bg='black')
                                        labelFrame1.place(relx=0.05,rely=0.52,relheight=0.26)
                                        
                                        scrollb=Scrollbar(labelFrame1,orient=VERTICAL)

                                        bslt=Listbox(labelFrame1,width=78,yscrollcommand=scrollb.set,bg='black',fg='white',font=('Courier',12))

                                        scrollb.config(command=bslt.yview)
                                        scrollb.pack(side=RIGHT,fill=Y)

                                        tab=Label(labelFrame, text="%-5s%-38s%-18s%-10s"%('BID','Title','Author','Status'),font = ('Courier',12),bg='black',fg='white')
                                        tab.place(relx=0.06,rely=0.43)
                                        line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                        line.place (relx=0.06,rely=0.48)

                                        for v in disli:
                                            bslt.insert(END,"%-5s%-38s%-18s%-10s"%(str(v[0]),v[1],v[2],v[5]))

                                        bslt.pack()

                                        def bord():
                                            global bbk
                                            val=bslt.get(ANCHOR)
                                            if val=='':
                                                messagebox.showerror('Selection','Please Select Book to Borrow.')
                                            else:
                                                l=val.split()[0];print(l)
                                                cur.execute("SELECT title,author FROM books WHERE b_id=%s", (l,))
                                                bdet= cur.fetchone()
                                                resp=messagebox.askyesno('Borrow Book','Do you want to Borrow this Book?\n\n  Book Name: %s\n  Author: %s'%(bdet[0],bdet[1]))
                                                if resp==1:
                                                    bbk(l)
                                        #lb = Label(labelFrame,text="You have selected: "+val+". Would you like to : ", bg='black', fg='white', font=('Courier',13))
                                        lb = Label(labelFrame,text=" Would you like to : ", bg='black', fg='white', font=('Courier',13))
                                        lb.place(relx=0.09,rely=0.78, relwidth=0.8, relheight=0.08)
                                        br=Button(labelFrame,text="BORROW",bg='light grey', fg='black',font=('Courier',10),command=bord)
                                        br.place(relx=0.18,rely=0.86,relwidth=0.2, relheight=0.1)
                                        br=Button(labelFrame,text="RETURN TO DISCOVER",bg='light grey', fg='black',font=('Courier',10),command=lambda:[sea.destroy(),discover()])
                                        br.place(relx=0.48,rely=0.86,relwidth=0.32, relheight=0.1)

                                    else:
                                        messagebox.showerror('Search Error','Sorry! Book not found')

                                    
                                l1=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                l1.place (relx=0.06,rely=0.2)
                                lb4 = Label(labelFrame,text="Type in the bookname here :", bg='black', fg='white', font=('Courier',12))
                                lb4.place(relx=0.07,rely=0.24, relwidth=0.35, relheight=0.1)
                                
                                #text box for entering parameter
                                sb = Entry(labelFrame,font=('',10))
                                sb.place(relx=0.44,rely=0.26, relwidth=0.37, relheight=0.07)
                                sbtn = Button(labelFrame,text="SEARCH",bg='#f7f1e3', fg='black',font=('Courier',10),command=sname)
                                sbtn.place(relx=0.84,rely=0.26,relwidth=0.1, relheight=0.07)

                            def authf():

                                def sauth():
                                    disli=[]    
                                    for a in boklist:
                                        if sb.get().lower() in a[2].lower():
                                            disli.append(a)

                                    #cur.execute("SELECT b_id, title, author, genre, status FROM books WHERE author=%s",(ba.get(),))
                                    #bauth= cur.fetchone()
                                    #if (str(bauth)!="None"):
                                    t=0
                                    if len(disli)!=0: #if ba.get() in bauth:
                                        t=t+1       
                                            #Display Book Details
                                        i=sb.get()

                                        lb3 = Label(labelFrame,text="Book Details: ", bg='black', fg='white', font=('Courier',13))
                                        lb3.place(relx=0.26,rely=0.33, relwidth=0.45, relheight=0.1)

                                        labelFrame1=Frame(labelFrame,bg='black')
                                        labelFrame1.place(relx=0.05,rely=0.52,relheight=0.26)
                                        
                                        scrollb=Scrollbar(labelFrame1,orient=VERTICAL)

                                        bslt=Listbox(labelFrame1,width=78,yscrollcommand=scrollb.set,bg='black',fg='white',font=('Courier',12))

                                        scrollb.config(command=bslt.yview)
                                        scrollb.pack(side=RIGHT,fill=Y)

                                        tab=Label(labelFrame, text="%-5s%-33s%-15s%-15s%-10s"%('BID','Title','Author','Genre','Status'),font = ('Courier',12),bg='black',fg='white')
                                        tab.place(relx=0.06,rely=0.43)
                                        line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                        line.place (relx=0.06,rely=0.48)

                                        for bauth in disli:
                                            bslt.insert(END,"%-5s%-33s%-15s%-15s%-10s"%(str(bauth[0]),bauth[1],bauth[2],bauth[3],bauth[5]))

                                        bslt.pack()

                                        def bord():
                                            global bbk
                                            val=bslt.get(ANCHOR)
                                            if val=='':
                                                messagebox.showerror('Selection','Please Select Book to Borrow.')
                                            else:
                                                l=val.split()[0];print(l)
                                                cur.execute("SELECT title,author FROM books WHERE b_id=%s", (l,))
                                                bdet= cur.fetchone()
                                                resp=messagebox.askyesno('Borrow Book','Do you want to Borrow this Book?\n\n  Book Name: %s\n  Author: %s'%(bdet[0],bdet[1]))
                                                if resp==1:
                                                    bbk(l)
                                        
                                        lb = Label(labelFrame,text=" Would you like to : ", bg='black', fg='white', font=('Courier',13))
                                        lb.place(relx=0.09,rely=0.78, relwidth=0.8, relheight=0.08)
                                        br=Button(labelFrame,text="BORROW",bg='light grey', fg='black',font=('Courier',10),command=bord)
                                        br.place(relx=0.18,rely=0.86,relwidth=0.2, relheight=0.1)
                                        br=Button(labelFrame,text="RETURN TO DISCOVER",bg='light grey', fg='black',font=('Courier',10),command=lambda:[sea.destroy(),discover()])
                                        br.place(relx=0.48,rely=0.86,relwidth=0.32, relheight=0.1)

                                    else:
                                        messagebox.showerror('Search Error','Sorry! Books not found')
                                    
                                l1=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                l1.place (relx=0.06,rely=0.2)
                                lb4 = Label(labelFrame,text="Type in the author here :", bg='black', fg='white', font=('Courier',12))
                                lb4.place(relx=0.07,rely=0.24, relwidth=0.35, relheight=0.1)
                                
                                #text box for entering parameter
                                sb = Entry(labelFrame,bg='#f7f1e3', fg='black',font=('',10))
                                sb.place(relx=0.44,rely=0.26, relwidth=0.37, relheight=0.07)
                                sbtn = Button(labelFrame,text="SEARCH",bg='#f7f1e3', fg='black',font=('Courier',10),command=sauth)
                                sbtn.place(relx=0.84,rely=0.26,relwidth=0.1, relheight=0.07)

                            def genrf():

                                def sgen():
                                    disli=[]
                                    def sel(val):
                                        lb = Label(labelFrame,text="You have selected: "+val+". Would you like to : ", bg='black', fg='white', font=('Courier',13))
                                        lb.place(relx=0.08,rely=0.76, relwidth=0.8, relheight=0.08)
                                        br=Button(labelFrame,text="BORROW",bg='light grey', fg='black',font=('Courier',10),)
                                        br.place(relx=0.17,rely=0.84,relwidth=0.2, relheight=0.1)
                                        br=Button(labelFrame,text="RETURN TO DISCOVER",bg='light grey', fg='black',font=('Courier',10),command=lambda:[sea.destroy(),discover()])
                                        br.place(relx=0.47,rely=0.84,relwidth=0.32, relheight=0.1)
                                        
                                    for a in boklist:
                                        if sb.get().lower() in a[3].lower():
                                            disli.append(a)
                                    
                                    
                                    if len(disli)!=0:
                                        
                                        i=sb.get()
                                        lb3 = Label(labelFrame,text="Book Details: ", bg='black', fg='white', font=('Courier',13))
                                        lb3.place(relx=0.26,rely=0.33, relwidth=0.45, relheight=0.1)

                                        labelFrame1=Frame(labelFrame,bg='black')
                                        labelFrame1.place(relx=0.05,rely=0.52,relheight=0.26)
                                        
                                        scrollb=Scrollbar(labelFrame1,orient=VERTICAL)

                                        bslt=Listbox(labelFrame1,width=78,yscrollcommand=scrollb.set,bg='black',fg='white',font=('Courier',12))

                                        scrollb.config(command=bslt.yview)
                                        scrollb.pack(side=RIGHT,fill=Y)

                                        tab=Label(labelFrame, text="%-5s%-38s%-18s%-15s"%('BID','Title','Genre','Status'),font = ('Courier',12),bg='black',fg='white')
                                        tab.place(relx=0.06,rely=0.43)
                                        line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                        line.place (relx=0.06,rely=0.48)

                                        for row in disli:
                                            bslt.insert(END,"%-5s%-38s%-18s%-15s"%(str(row[0]),row[1],row[3],row[5]))

                                        bslt.pack()

                                        def bord():
                                            global bbk
                                            val=bslt.get(ANCHOR)
                                            if val=='':
                                                messagebox.showerror('Selection','Please Select Book to Borrow.')
                                            else:
                                                l=val.split()[0];print(l)
                                                cur.execute("SELECT title,author FROM books WHERE b_id=%s", (l,))
                                                bdet= cur.fetchone()
                                                resp=messagebox.askyesno('Borrow Book','Do you want to Borrow this Book?\n\n  Book Name: %s\n  Author: %s'%(bdet[0],bdet[1]))
                                                if resp==1:
                                                    bbk(l)
                                        
                                        lb = Label(labelFrame,text=" Would you like to : ", bg='black', fg='white', font=('Courier',13))
                                        lb.place(relx=0.09,rely=0.78, relwidth=0.8, relheight=0.08)
                                        br=Button(labelFrame,text="BORROW",bg='light grey', fg='black',font=('Courier',10),command=bord)
                                        br.place(relx=0.18,rely=0.86,relwidth=0.2, relheight=0.1)
                                        br=Button(labelFrame,text="RETURN TO DISCOVER",bg='light grey', fg='black',font=('Courier',10),command=lambda:[sea.destroy(),discover()])
                                        br.place(relx=0.48,rely=0.86,relwidth=0.32, relheight=0.1)

                                    else:
                                        messagebox.showerror('Search Error','Sorry! Books not found')
                                    
                                l1=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                l1.place (relx=0.06,rely=0.2)
                                lb4 = Label(labelFrame,text="Type in the genre here :", bg='black', fg='white', font=('Courier',12))
                                lb4.place(relx=0.07,rely=0.24, relwidth=0.35, relheight=0.1)
                                
                                #text box for entering parameter
                                sb = Entry(labelFrame,bg='#f7f1e3', fg='black',font=('',10))
                                sb.place(relx=0.44,rely=0.26, relwidth=0.37, relheight=0.07)
                                sbtn = Button(labelFrame,text="SEARCH",bg='#f7f1e3', fg='black',font=('Courier',10),command=sgen)
                                sbtn.place(relx=0.84,rely=0.26,relwidth=0.1, relheight=0.07)

                                    
                            if sv=="Book name":
                                    bknmf()
                            elif sv=="Author":
                                    authf()
                            elif sv=="Genre":
                                    genrf()
                            else:
                                messagebox.showinfo('Category','Please select Search By\nBook name or Author or Genre')
                            
                        sea=Tk()
                        sea.title('Search')
                        sea.geometry('1050x650')

                        Canvas1 = Canvas(sea)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(sea,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.3,rely=0.08,relwidth=0.4,relheight=0.11)

                        headingLabel = Label(headingFrame1, text="SEARCH", bg='black', fg='white', font=('Courier',17))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(sea,bg='black')
                        labelFrame.place(relx=0.08,rely=0.27,relwidth=0.83,relheight=0.65)

                        slb = Label(labelFrame,text="What would you like to search by:  ", bg="#FFBB00", fg='black', font=('Courier',13))
                        slb.place(relx=0.05,rely=0.08, relwidth=0.5, relheight=0.1)
                        sp =Combobox(labelFrame,values=('Book name','Author', 'Genre'),font=('',10))
                        sp.place(relx=0.58,rely=0.08, relwidth=0.22, relheight=0.1)
                        eb = Button(labelFrame,text="ENTER",bg='#f7f1e3', fg='black',font=('Courier',10),command=sval)
                        eb.place(relx=0.83,rely=0.08,relwidth=0.12, relheight=0.1)
                        
                    authl=[]
                    genl=[]
                    for i in bl:
                        if i[0] not in authl:
                            authl.append(i[0])
                        if i[1] not in genl:
                            genl.append(i[1])
                            
                    sroot=Tk()
                    sroot.title('Discover')
                    sroot.geometry('1000x650')

                    Canvas1 = Canvas(sroot) 
                    Canvas1.config(bg="#12a4d9")
                    Canvas1.pack(expand=True,fill=BOTH)

                    headingFrame1 = Frame(sroot,bg='#FFBB00',bd=5)
                    headingFrame1.place(relx=0.28,rely=0.05,relwidth=0.4,relheight=0.1)

                    headingLabel = Label(headingFrame1, text="DISCOVER AND SEARCH", bg='black', fg='white', font = ('Courier',17))
                    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                    labelFrame = Frame(sroot,bg='black')
                    labelFrame.place(relx=0.08,rely=0.2,relwidth=0.84,relheight=0.68)
                    Label(labelFrame, text='  Books you may want to try out:  ', bg='#FFBB00', fg='black', font = ('Courier',16), padx=200).place(relx=0,rely=0,)

                    labelFrame1= Frame(sroot,bg='black')
                    labelFrame1.place(relx=0.08,rely=0.25,relwidth=0.43,relheight=0.68)
                    Label(labelFrame1, text='  If you liked this author: ', bg='#FFBB00', fg='black', font = ('Courier',15), padx=40).place(relx=0,rely=0)
                    
                    labelFrame2= Frame(sroot,bg='black')
                    labelFrame2.place(relx=0.49,rely=0.25,relwidth=0.43,relheight=0.68)
                    Label(labelFrame2, text='   If you liked this genre: ', bg='#FFBB00', fg='black', font = ('Courier',15), padx=45).place(relx=0,rely=0)
                    
                    yva=0.1
                    yvg=0.1
                    for i in range(2):
                        rgl=[]
                        ral=[]
                            
                        ra=random.randint(0,len(authl)-1)
                        Label(labelFrame1, text=(authl[ra]), bg='#f7f1e3', fg='black', font = ('Courier',14), padx=40).place(relx=0.15,rely=yva)
                        yva=yva+0.08
                        Label(labelFrame1, text="Title",bg='black',fg='white',font = ('Courier',10), padx=45).place(relx=0.018,rely=yva)
                        yva=yva+0.04
                        Label(labelFrame1, text ="--------------------------",bg='black',fg='white',font = ('Courier',10), padx=45).place (relx=0.018,rely=yva)    
                        for j in bl:
                            if j[0]==authl[ra]:
                                ral.append([j[2],j[3]])
                        yva=yva+0.05
                        for j in ral:
                            Label(labelFrame1, text=(j[0]),bg='black',fg='white',font = ('Courier',12), padx=45).place(relx=0.016,rely=yva)
                            yva=yva+0.06
                        yva=yva+0.01

                        rg=random.randint(0,len(genl)-1)
                        Label(labelFrame2, text=(genl[rg]), bg='#f7f1e3', fg='black', font = ('Courier',14), padx=40).place(relx=0.13,rely=yvg)
                        yvg=yvg+0.08
                        Label(labelFrame2, text="Title",bg='black',fg='white',font = ('Courier',10), padx=45).place(relx=0.02,rely=yvg)
                        yvg=yvg+0.04
                        Label(labelFrame2, text ="--------------------------",bg='black',fg='white',font = ('Courier',10), padx=45).place (relx=0.02,rely=yvg)    
                        for j in bl:
                            if j[1]==genl[rg]:
                                rgl.append([j[2],j[3]])
                        yvg=yvg+0.06
                        for j in rgl:
                            Label(labelFrame2, text=(j[0]),bg='black',fg='white',font = ('Courier',12), padx=45).place(relx=0.02,rely=yvg)
                            yvg=yvg+0.06
                        yvg=yvg+0.01

                    bBtn = Button(sroot,text="BACK",bg='#f7f1e3', fg='black', font = ('Courier',14), command=sroot.destroy)
                    bBtn.place(relx=0.26,rely=0.81, relwidth=0.18,relheight=0.08)
                    
                    sBtn = Button(sroot,text="SEARCH",bg='#f7f1e3', fg='black', font = ('Courier',14), command=lambda :[sroot.destroy(),search()])
                    sBtn.place(relx=0.52,rely=0.81, relwidth=0.18,relheight=0.08)

                #Queries,Compliants and Suggestions user part
                def QCSu():
                    global userlog, booklog, qcs,sug,uid,cusid
                    #fetching userid
                    uid=cusid
                    def nqcs():
                        global userlog, booklog, qcs,bf,qcsv
                        def qcsl():
                            global qcsv, qcs, bf,v
                            v=qcsv.get()

                            def query():
                                global qe,bf,qcs,aqac

                                def ql():
                                    global qcs, qe, userlog, booklog,v,bf

                                    uq=str(qe.get(1.0,'end'))[:-1:]
                                    qcs.append([uid,v,str(uq),""])
                                    messagebox.showinfo('Success',"Your query has been entered. Please wait for a response! :)")
                                    bf.destroy()
                                    QCSu()
                                
                                lb3 = Label(labelFrame,text="Queries ", bg='black', fg='white', font=('Courier',16))
                                lb3.place(relx=0.3,rely=0.25, relwidth=0.45, relheight=0.1)
                                l1=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                l1.place (relx=0.06,rely=0.32)
                                lb4 = Label(labelFrame,text="What does your query relate to? :", bg='black', fg='white', font=('Courier',13))
                                lb4.place(relx=0.03,rely=0.38, relwidth=0.5, relheight=0.1)
                                qs =Combobox(labelFrame,values=('Borrow/Return', 'Membership', 'Fine/Damage', 'Other'),)
                                qs.place(relx=0.58,rely=0.38, relwidth=0.22, relheight=0.07)
                                lb5 = Label(labelFrame,text="Please type in your query :  ", bg='black', fg='white', font=('Courier',13))
                                lb5.place(relx=0.01,rely=0.48, relwidth=0.5, relheight=0.1)
                                #text box for entering query
                                qe = Text(labelFrame,bg='#f7f1e3', fg='black',font=('Courier',13))
                                qe.place(relx=0.05,rely=0.58, relwidth=0.9, relheight=0.25)
                                sb = Button(labelFrame,text="SUBMIT",bg='#f7f1e3', fg='black',font=('Courier',10), command=ql)
                                sb.place(relx=0.83,rely=0.85,relwidth=0.12, relheight=0.1,)
                                
                            def compl():
                                global ce, qcs, aqac

                                def cl():
                                    global qcs, ce, userlog, booklog,v,bf

                                    uc=str(ce.get(1.0,'end'))[:-1:]
                                    qcs.append([uid,v,str(uc),""])
                                    messagebox.showinfo('Success',"Your complaint has been entered. Please wait as we answer! :)")
                                    bf.destroy()
                                    QCSu()
                                
                                lb3 = Label(labelFrame,text="Complaints ", bg='black', fg='white', font=('Courier',16))
                                lb3.place(relx=0.3,rely=0.25, relwidth=0.45, relheight=0.1)
                                l1=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                l1.place (relx=0.06,rely=0.32)
                                lb4 = Label(labelFrame,text="What does your complaint relate to? :", bg='black', fg='white', font=('Courier',13))
                                lb4.place(relx=0.03,rely=0.38, relwidth=0.5, relheight=0.1)
                                qs =Combobox(labelFrame,values=('Borrow/Return', 'Membership', 'Fine/Damage', 'Other'),)
                                qs.place(relx=0.58,rely=0.38, relwidth=0.22, relheight=0.07)
                                lb5 = Label(labelFrame,text="Please type in your complaint :  ", bg='black', fg='white', font=('Courier',13))
                                lb5.place(relx=0.01,rely=0.48, relwidth=0.5, relheight=0.1)
                                #text box for entering complaint
                                ce = Text(labelFrame,bg='#f7f1e3', fg='black',font=('Courier',13))
                                ce.place(relx=0.05,rely=0.58, relwidth=0.9, relheight=0.25)
                                sb = Button(labelFrame,text="SUBMIT",bg='#f7f1e3', fg='black',font=('Courier',10), command=cl)
                                sb.place(relx=0.83,rely=0.85,relwidth=0.12, relheight=0.1)

                            if v=="Query":
                                query()
                            elif v=="Complaint":
                                compl()
                            else:
                                messagebox.showinfo('Category','Please select Complaint or Query')
                        
                        bf = Tk()
                        bf.title("Library")
                        bf.minsize(width=400,height=400)
                        bf.geometry("1000x650")

                        Canvas1 = Canvas(bf)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                        headingLabel = Label(headingFrame1, text="QUERIES AND COMPLAINTS", bg='black', fg='white', font=('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(bf,bg='black')
                        labelFrame.place(relx=0.08,rely=0.3,relwidth=0.84,relheight=0.6)

                        lb2 = Label(labelFrame,text="What would you like to register today? ", bg="#FFBB00", fg='black', font=('Courier',13))
                        lb2.place(relx=0.05,rely=0.1, relwidth=0.5, relheight=0.1)
                        qcsv =Combobox(labelFrame,values=('Query','Complaint'),font=('',10))
                        qcsv.place(relx=0.58,rely=0.1, relwidth=0.22, relheight=0.1)
                        eb = Button(labelFrame,text="ENTER",bg='#f7f1e3', fg='black',font=('Courier',10), command=qcsl)
                        eb.place(relx=0.83,rely=0.1,relwidth=0.12, relheight=0.1)

                    def pqcs():
                        global userlog, booklog, aqac, uid, cusid, qcs

                        def vans(iv):
                            a = Tk()
                            a.title("Library")
                            a.minsize(width=400,height=400)
                            a.geometry("600x400")

                            Canvas1 = Canvas(a)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)

                            qn=iv
                            ques=aqac[qn][2]
                            answ=aqac[qn][3]

                            headingFrame1 = Frame(a,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.08,rely=0.08,relwidth=0.3,relheight=0.12)
                            headingLabel1 = Label(headingFrame1, text="  Question:", bg='black', fg='white', font=('Courier',13),anchor='w')
                            headingLabel1.place(relx=0,rely=0, relwidth=1, relheight=1)
                            qbox = Text(a, bg='#f7f1e3', fg='black',font=('Courier',10))
                            qbox.place(relx=0.08,rely=0.22, relwidth=0.8, relheight=0.2)
                            qbox.insert('end',ques)
                            qbox.configure(state="disabled")

                            headingFrame2 = Frame(a,bg="#FFBB00",bd=5)
                            headingFrame2.place(relx=0.08,rely=0.48,relwidth=0.3,relheight=0.12)
                            headingLabel2= Label(headingFrame2, text="  Answer:", bg='black', fg='white', font=('Courier',13),anchor='w')
                            headingLabel2.place(relx=0,rely=0, relwidth=1, relheight=1)
                            abox = Text(a, bg='#f7f1e3', fg='black',font=('Courier',10))
                            abox.place(relx=0.08,rely=0.63, relwidth=0.8, relheight=0.2)
                            abox.insert('end',answ)
                            abox.configure(state="disabled")

                            b=Button(a,text="RETURN",bg='black', fg='white', font = ('Courier',12),command=lambda :[a.destroy(),pqcs()])
                            b.place(relx=0.66,rely=0.88, relwidth=0.3,relheight=0.1)

                        bf = Tk()
                        bf.title("Library")
                        bf.minsize(width=400,height=400)
                        bf.geometry("1000x650")

                        Canvas1 = Canvas(bf)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                        headingLabel = Label(headingFrame1, text="QUERIES AND COMPLAINTS", bg='black', fg='white', font=('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(bf,bg='black')
                        labelFrame.place(relx=0.08,rely=0.3,relwidth=0.84,relheight=0.55)

                        lb2 = Label(labelFrame,text="   Previously Entered Queries and Complaints   ", bg="#FFBB00", fg='black', font=('Courier',17))
                        lb2.place(relx=0,rely=0,relwidth=1)

                        tab=Label(labelFrame, text="%-10s%-15s%-30s%-15s"%('UID','Type','Brief','Status'),font = ('Courier',14),bg='black',fg='white')
                        tab.place(relx=0.05,rely=0.12)
                        line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                        line.place (relx=0.03,rely=0.18)
                        global y
                        y=0.24
                        for i in range(0,len(aqac)):
                            if aqac[i][0]==uid:
                                d=Label(labelFrame,text="%-10s%-15s%-30s"%(aqac[i][0],aqac[i][1],aqac[i][2]),font = ('Courier',11), bg='black', fg='white')
                                d.place(relx=0.05,rely=y)
                                b=Button(labelFrame,text="View Answer",bg='#f7f1e3', fg='black', font = ('Courier',11),command=lambda i=i :[bf.destroy(),vans(i)])
                                b.place(relx=0.72,rely=y, relwidth=0.2,relheight=0.05)
                                y += 0.06

                        for i in range(0,len(qcs)):
                            if qcs[i][0]==uid:
                                d=Label(labelFrame,text="%-10s%-15s%-40s%-25s"%(qcs[i][0],qcs[i][1],qcs[i][2],"  Unanswered"),font = ('Courier',11), bg='black', fg='white')
                                d.place(relx=0.05,rely=y)
                                y += 0.06

                        for i in range(0,len(sug)):
                             if sug[i][0]==uid:
                                d=Label(labelFrame,text="%-10s%-15s%-40s%-25s"%(sug[i][0],"Suggestions",sug[i][1],"  Seen"),font = ('Courier',11), bg='black', fg='white')
                                d.place(relx=0.05,rely=y)
                                y += 0.06

                        b=Button(bf,text="RETURN", bg='#f7f1e3', fg='black', font = ('Courier',12),command=lambda :[bf.destroy(),QCSu()])
                        b.place(relx=0.43,rely=0.88, relwidth=0.16,relheight=0.08)
                        

                    def sugst():
                        global qcs, se, userlog, booklog,sug

                        def sl():
                            global qcs, se, userlog, booklog,sug
                            us=str(se.get(1.0,'end'))[:-1:]
                            sug.append([uid,us])
                            messagebox.showinfo('Success',"Thank you for your suggestion. We will take your input into consideration while making this an easier experience :)")
                            bf.destroy()
                            QCSu()

                        bf = Tk()
                        bf.title("Library")
                        bf.minsize(width=400,height=400)
                        bf.geometry("1000x650")

                        Canvas1 = Canvas(bf)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                        headingLabel = Label(headingFrame1, text="SUGGESTIONS", bg='black', fg='white', font=('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelFrame = Frame(bf,bg='black')
                        labelFrame.place(relx=0.1,rely=0.35,relwidth=0.8,relheight=0.6)
                        yf=Label(labelFrame, text='You may enter your suggestions here  ', bg='#FFBB00', fg='black', font = ('Courier',17), padx=150)
                        yf.place(relx=0,rely=0)
                        
                        lb3 = Label(labelFrame,text="Your inputs make this a better experience for everyone ", bg='black', fg='white', font=('Courier',14))
                        lb3.place(relx=0.1,rely=0.15)
                        l1=Label(labelFrame, text = "---------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                        l1.place (relx=0.06,rely=0.23)
                        lb4 = Label(labelFrame,text="What does your suggestion relate to? :", bg='black', fg='white', font=('Courier',13))
                        lb4.place(relx=0.03,rely=0.3, relwidth=0.5, relheight=0.1)
                        qs =Combobox(labelFrame,values=('Borrow/Return', 'Membership', 'Fine/Damage', 'Other'),)
                        qs.place(relx=0.58,rely=0.3, relwidth=0.22, relheight=0.07)
                        lb5 = Label(labelFrame,text="Please type in your suggestion :  ", bg='black', fg='white', font=('Courier',13))
                        lb5.place(relx=0.01,rely=0.4, relwidth=0.5, relheight=0.1)
                        #text box for entering suggestion
                        se = Text(labelFrame,bg='#f7f1e3', fg='black',font=('Courier',13))
                        se.place(relx=0.05,rely=0.53, relwidth=0.9, relheight=0.25)
                        sb = Button(labelFrame,text="SUBMIT",bg='#f7f1e3', fg='black',font=('Courier',10), command=sl)
                        sb.place(relx=0.83,rely=0.85,relwidth=0.12, relheight=0.1)

                    qcsf = Tk()
                    qcsf.title("Library")
                    qcsf.minsize(width=400,height=400)
                    qcsf.geometry("1000x650")

                    Canvas1 = Canvas(qcsf)
                    Canvas1.config(bg="#12a4d9")
                    Canvas1.pack(expand=True,fill=BOTH)

                    headingFrame1 = Frame(qcsf,bg="#FFBB00",bd=5)
                    headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                    headingLabel = Label(headingFrame1, text="QUERIES, COMPLAINTS AND SUGGESTIONS", bg='black', fg='white', font=('Courier',15))
                    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                    btn1 = Button(qcsf,text="REGISTER NEW QUERY/COMPLAINT",bg='black', fg='white',font = ('Courier',14),command=lambda:[qcsf.destroy(), nqcs()])
                    btn1.place(relx=0.225,rely=0.36, relwidth=0.55,relheight=0.1)

                    btn2 = Button(qcsf,text="PREVIOUSLY REGISTERED QUERIES/COMPLAINTS",bg='black', fg='white',font = ('Courier',14), command=lambda:[qcsf.destroy(), pqcs()])
                    btn2.place(relx=0.225,rely=0.5, relwidth=0.55,relheight=0.1)

                    btn3 = Button(qcsf,text="SUGGESTIONS",bg='black', fg='white',font = ('Courier',14), command=lambda:[qcsf.destroy(), sugst()])
                    btn3.place(relx=0.27,rely=0.64, relwidth=0.45,relheight=0.1)

                    btn4 = Button(qcsf,text="RETURN TO HOME PAGE",bg='grey', fg='white',font = ('Courier',14), command=lambda:[qcsf.destroy()])
                    btn4.place(relx=0.31,rely=0.78, relwidth=0.36,relheight=0.08)

                    qcsf.mainloop() 

                #Widgets
                
                #Activity
                aBtn = Button(labelFrame,text="ACTIVITY",bg='white', fg='black', font = ('Courier',16),command=activity)
                aBtn.place(relx=0.07,rely=0.3, relwidth=0.38,relheight=0.18)
                
                #Discover
                dBtn = Button(labelFrame,text="DISCOVER",bg='white', fg='black', font = ('Courier',16),command=discover)
                dBtn.place(relx=0.55,rely=0.3, relwidth=0.38,relheight=0.18)
                
                #Queries and Complaints
                qcsBtn = Button(labelFrame,text="QUERIES & COMPLAINTS",bg='white', fg='black', font = ('Courier',16),command=QCSu)
                qcsBtn.place(relx=0.07,rely=0.66, relwidth=0.38,relheight=0.18)
                
                #Profile
                pBtn = Button(labelFrame,text="PROFILE",bg='white', fg='black', font = ('Courier',16),command=prof)
                pBtn.place(relx=0.55,rely=0.66, relwidth=0.38,relheight=0.18)
                
            else:
                messagebox.showerror('Wrong Details','Username Password combination NOT FOUND!\nTry Again')
                        
                        
        
        
        elif spbu.get().lower()=='admin':


            #Username and password
            global adminlog,adpsli
            cur1.execute("SELECT*FROM admin")
            adminlog=cur1.fetchall()
            adpsli={}
            for p in adminlog:
                adpsli[p[1]]= p[2]
            
##            cur.execute('SELECT uname FROM admin WHERE uname= %s AND passwd= %s', (unbu.get(), psbu.get(),))
##            aname = cur.fetchone()
                  
            if unbu.get() in adpsli and psbu.get()== adpsli[unbu.get()]:  #if (str(aname) != "None"):
                global ab
                ab=unbu.get()

                root.withdraw()
                
                def Admin():

                    #Book Database
                    def Bookdat():

                        global booklog
                        cur1.execute("SELECT*FROM books")
                        booklog=cur1.fetchall()
                        
                        #Adding Books
                        def addb():
                    
                            global booklog
##                                for ch in bid.get():
##                                    if ch.isdigit()== False:
##                                        messagebox.showinfo('Book Id',"Book ID to be written in digits.\nTry again")
##                                        break
                            if bid.get().isdigit()== True:
                                
                                bookid = int(bid.get())
                                title = bname.get()
                                author = bauth.get()
                                genre = bgen.get()
                                price = bstat.get()

                                bokidic=[]
                                for r in booklog:
                                    bokidic.append(r[0])

                                if bookid not in bokidic:
                                    print (title, author)
            ##                        cur.execute("INSERT INTO books(title,author,genre,status) VALUES(%(title)s, %(author)s, %(genre)s, %(status)s)")
                                    cur1.execute("INSERT INTO books(b_id,title,author,genre,price) VALUES (%s, %s ,%s ,%s,%s)", (bookid,title,author,genre,price))
                                    db1.commit()
            ##                        booklog[bookid]=[title,author,genre,status,'00/00/00']
                                    messagebox.showinfo('Success',"Book Added Successfully")
                                    ab.destroy()
                                    Bookdat()

                                else:
                                    messagebox.showinfo('Book Id',"Book ID already exists.\nTry again")
                            else:
                                messagebox.showinfo('Book Id',"Book ID to be written in digits.\nTry again")
                                
                        
                        def addBook():
                            
                            global bid ,bname, bauth, bgen, bstat, Canvas1, root, ab
                            ab = Tk()
                            ab.title("Library")
                            ab.minsize(width=400,height=400)
                            ab.geometry("1000x650")

                            Canvas1 = Canvas(ab)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)
                            
                            headingFrame1 = Frame(ab,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.25,rely=0.1,relwidth=0.5,relheight=0.13)

                            headingLabel = Label(headingFrame1, text="ADD BOOK", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(ab,bg='black')
                            labelFrame.place(relx=0.1,rely=0.28,relwidth=0.8,relheight=0.55)
                            
                            # Book ID
                            lb1 = Label(labelFrame,text="Book ID : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb1.place(relx=0.05,rely=0.16, relwidth=0.25, relheight=0.08)
                       
                            bid = Entry(labelFrame)
                            bid.place(relx=0.33,rely=0.16, relwidth=0.62, relheight=0.08)
                            
                            # Title
                            lb2 = Label(labelFrame,text="Title : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb2.place(relx=0.05,rely=0.31, relwidth=0.25, relheight=0.08)
                            
                            bname = Entry(labelFrame)
                            bname.place(relx=0.33,rely=0.31, relwidth=0.62, relheight=0.08)
                            
                            # Book Author
                            lb3 = Label(labelFrame,text="Author : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb3.place(relx=0.05,rely=0.46, relwidth=0.25, relheight=0.08)
                            
                            bauth = Entry(labelFrame)
                            bauth.place(relx=0.33,rely=0.46, relwidth=0.62, relheight=0.08)

                            # Book Genre
                            lb3 = Label(labelFrame,text="Genre : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb3.place(relx=0.05,rely=0.61, relwidth=0.25, relheight=0.08)
                            
                            bgen = Entry(labelFrame)
                            bgen.place(relx=0.33,rely=0.61, relwidth=0.62, relheight=0.08)
                            
                            # Book Status
                            lb4 = Label(labelFrame,text="Price : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb4.place(relx=0.05,rely=0.76, relwidth=0.25, relheight=0.08)

                            bstat=Entry(labelFrame)
                            bstat.place(relx=0.33,rely=0.76, relwidth=0.62, relheight=0.08)
                            
                            #Submit Button
                            SubmitBtn = Button(ab,text="ADD THIS BOOK TO DATABASE",font=('Courier',12),bg='#d1ccc0', fg='black',command=addb)
                            SubmitBtn.place(relx=0.2,rely=0.87, relwidth=0.35,relheight=0.08)

                            #Back Button
                            backBtn = Button(ab,text="BACK",font=('Courier',12),bg='#d1ccc0', fg='black',command=lambda:[ab.destroy(),Bookdat()])
                            backBtn.place(relx=0.62,rely=0.87, relwidth=0.16,relheight=0.08)

                        #Editing books

                        #Updating books
                        def updb():
                            
                            global booklog, bdid, ubid, ubn, uba, ubg, lb1, lb2, lb3, lb4, un, ua, ug,updid

        
                            #updid=bdid.get()                       
                            cur1.execute("SELECT title, author, genre FROM books WHERE b_id=%s", (updid,))
                            slct = cur1.fetchone()
                            print('updb',slct)
                            db1.commit()

                            un = ubx.get()
                            ua = uba.get()
                            ug = ubg.get()


                            #Entry Error Message
                            if ubid.get()!=updid:
                                messagebox.showerror('Book ID','Looks like you tried to change the Book ID, which is not possible! ')
                                ud.destroy()
                                db.destroy()
                                editBook()
                                
                            else:
##                                un=ubn.get()
##                                ua=uba.get()
##                                ug=ubg.get()
                                un = ubx.get()
                                ua = uba.get()
                                ug = ubg.get()
    ##                            booklog[updid][0]=un
    ##                            booklog[updid][1]=ua
    ##                            booklog[updid][2]=ug
                                
                                #Updating
                                cur1.execute("UPDATE books SET title= %s, author= %s, genre= %s WHERE b_id= %s", (un,ua,ug,updid))
                                db1.commit() 
                                #Delete Previous
                                '''lb2.destroy()
                                lb3.destroy()
                                lb4.destroy()'''
                                #Message of Update
                                cur1.execute("SELECT  title, author, genre FROM books WHERE b_id=%s", (updid,))
                                ez1 = cur1.fetchone()
                                print(ez1)
                                if ez1[0]==un and ez1[1]==ua and ez1[2]==ug:
                                    cur1.execute("SELECT*FROM books")
                                    booklog=cur1.fetchall()
                                    messagebox.showinfo('Edited Book Details','Changes Saved')
                                    ud.destroy()
                                    db.destroy()
                                    Bookdat()

                        def updBook():

                            global booklog, bdid, ubid, ubx, uba, ubg, lb1, lb2, lb3, lb4, ud, bdn, bda, bdg,updid

                            updid = bdid.get()
                            cur1.execute("SELECT title, author, genre FROM books WHERE b_id= %s", (updid,))
                            y = cur1.fetchone()
                            print(y)

                            ud=Tk()
                            ud.title("Edit Book Details")
                            ud.geometry('1000x650')

                            Canvas1 = Canvas(ud) 
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)

                            headingFrame1 = Frame(ud,bg='#FFBB00',bd=5)
                            headingFrame1.place(relx=0.24,rely=0.1,relwidth=0.5,relheight=0.11)

                            headingLabel = Label(headingFrame1, text="BOOK DETAILS", bg='black', fg='white', font = ('Courier',18))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(ud,bg='black')
                            labelFrame.place(relx=0.1,rely=0.3,relwidth=0.8,relheight=0.46)
                            yf=Label(labelFrame, text='Would you like to edit these details?', bg='#FFBB00', fg='black', font = ('Courier',17), padx=150)
                            yf.place(relx=0,rely=0)

                            tab=Label(labelFrame, text="%-10s%-20s%-18s%-20s"%('BID','Title','Author','Genre'),font = ('Courier',14),bg='black',fg='white')
                            tab.place(relx=0.08,rely=0.17)
                            line=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                            line.place (relx=0.06,rely=0.24)
                            dis1=Label(labelFrame,text="%-10s%-24s%-18s%-20s"%(updid,y[0],y[1],y[2]),font = ('Courier',12), bg='black', fg='white')
                            dis1.place(relx=0.06,rely=0.32)

                            #Book id
                            lb1 = Label(labelFrame,text="Book ID: ", bg='black', fg='white',font=('Courier',14))
                            lb1.place(relx=0.07,rely=0.47, relheight=0.07)
                            ubid = Entry(labelFrame,bg='grey98',state='disabled')
                            ubid.place(relx=0.07,rely=0.55, relwidth=0.35, relheight=0.07)
                            ubid.insert(0,updid)

                            #Book name
                            lb2 = Label(labelFrame,text="Book Name: ", bg='black', fg='white',font=('Courier',14))
                            lb2.place(relx=0.57,rely=0.47, relheight=0.07)
                            ubx = Entry(labelFrame,bg='grey98')
                            ubx.place(relx=0.57,rely=0.55, relwidth=0.35, relheight=0.07)
                            ubx.insert(0,y[0])

                            #Book author
                            lb3 = Label(labelFrame,text="Book Author: ", bg='black', fg='white',font=('Courier',14))
                            lb3.place(relx=0.07,rely=0.69, relheight=0.07)
                            uba = Entry(labelFrame,bg='grey98')
                            uba.place(relx=0.07,rely=0.77, relwidth=0.35, relheight=0.07)
                            uba.insert(0,y[1])

                             #Book genre
                            lb4 = Label(labelFrame,text="Book Genre: ", bg='black', fg='white',font=('Courier',14))
                            lb4.place(relx=0.57,rely=0.69, relheight=0.07)
                            ubg = Entry(labelFrame,bg='grey98')
                            ubg.place(relx=0.57,rely=0.77, relwidth=0.35, relheight=0.07)
                            ubg.insert(0,y[2])

                            sBtn = Button(ud,text="SAVE CHANGES",bg='#f7f1e3', fg='black', font = ('Courier',14),command=updb)
                            sBtn.place(relx=0.4,rely=0.82, relwidth=0.2,relheight=0.09)

                        #Deleteing books
                        def delb():

                            global booklog
                            cur1.execute("SELECT*FROM books WHERE b_id =%s", (bdid.get(),))
                            b = cur1.fetchone()
                            print(b,booklog)
                            if b in booklog:
                                if b[5]=="Issued":
                                    messagebox.showinfo('Oops!',"This book cannot be deleted as it is currently being read by a user. Try deleteing it once it has be returned. :)")
                                    db.destroy()
                                    Bookdat()    
                                else:
                                    cur1.execute("DELETE FROM books WHERE b_id=%s", (bdid.get(),))
                                    db1.commit()
                                    cur1.execute("SELECT*FROM books")
                                    booklog=cur1.fetchall()
                                    messagebox.showinfo('Success',"Book Deleted Successfully")
                                    db.destroy()
                                    Bookdat()
                            else:
                                messagebox.showinfo('Deletion',"This book does not exist in library")
                                db.destroy()
                                Bookdat()
                            
                        def editBook():
                            
                            global bdid,Canvas1,root,db

                            db = Tk()
                            db.title("Library")
                            db.minsize(width=400,height=400)
                            db.geometry("1000x650")

                            Canvas1 = Canvas(db)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)
                            
                            headingFrame1 = Frame(db,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.25,rely=0.08,relwidth=0.5,relheight=0.13)
                            
                            headingLabel = Label(headingFrame1, text="DATABASE FUNCTIONS", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(db,bg='black')
                            labelFrame.place(relx=0.1,rely=0.27,relwidth=0.8,relheight=0.6)

                            
    ##                        db1 = mysql.connector.connect(host='localhost', user='aashu', password='art#1234', database='db')
    ##                        cur1= db1.cursor()

                            global booklog ##- aashu
                            # Book ID to Delete
                            lb2 = Label(labelFrame,text="Enter the ID of the book : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb2.place(relx=0.08,rely=0.12, relwidth=0.45, relheight=0.1)
                            bdid = Entry(labelFrame)
                            bdid.place(relx=0.55,rely=0.12, relwidth=0.25, relheight=0.1)
     

                              
                            def disb():
                                global cur ##aashu
                                cur1.execute("SELECT title, author, genre FROM books WHERE b_id = %s", (bdid.get(),))
                                x = cur1.fetchone()                            

                                if x!= None :
                                    sid= bdid.get() ##- aashu
                                                                    
                                    lb3 = Label(labelFrame,text="Book Details: ", bg='black', fg='white', font=('Courier',13))
                                    lb3.place(relx=0.26,rely=0.24, relwidth=0.45, relheight=0.1)

                                    tab=Label(labelFrame, text="%-10s%-25s%-18s%-20s"%('BID','Title','Author','Genre'),font = ('Courier',14),bg='black',fg='white')
                                    tab.place(relx=0.06,rely=0.35)
                                    line=Label(labelFrame, text = "----------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                    line.place (relx=0.06,rely=0.40)
                                    dis1=Label(labelFrame,text="%-10s%-26s%-18s%-20s"%(sid,x[0],x[1],x[2]),font = ('Courier',12), bg='black', fg='white')
                                    dis1.place(relx=0.06,rely=0.45)

                                    lb4 = Label(labelFrame,text="How would you like to proceed?", bg='white', fg='black', font=('Courier',13))
                                    lb4.place(relx=0.25,rely=0.57, relwidth=0.45, relheight=0.1)
                                
                                    delBtn = Button(labelFrame,text="DELETE BOOK",bg='#d1ccc0', fg='black',font=('Courier',13), command=delb)
                                    delBtn.place(relx=0.18,rely=0.72, relwidth=0.25,relheight=0.15)

                                    updBtn = Button(labelFrame,text="UPDATE DETAILS",bg='#d1ccc0', fg='black',font=('Courier',13),command=updBook)
                                    updBtn.place(relx=0.52,rely=0.72, relwidth=0.25,relheight=0.15)

                                else:
                                    messagebox.showinfo('Book ID not found',"This book does not exist in library")
                                    db.destroy()
                                    editBook()
                            
                            #Submit Button
                            sbtn = Button(labelFrame,text="Search",bg='#d1ccc0', fg='black',command=disb)
                            sbtn.place(relx=0.82,rely=0.12, relwidth=0.1,relheight=0.1,)

                            db.mainloop()
                        

                        vb = Tk()
                        vb.title("Library")
                        vb.minsize(width=400,height=400)
                        vb.geometry("1250x700")

                        Canvas1 = Canvas(vb) 
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(vb,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.24,rely=0.07,relwidth=0.5,relheight=0.1)

                        headingLabel = Label(headingFrame1, text="BOOK DATABASE", bg='black', fg='white', font = ('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelF = Frame(vb,bg='black')
                        labelF.place(relx=0.08,rely=0.24,relwidth=0.84,relheight=0.63)
                        y = 0.2

                        aca= Canvas(labelF, bg='black')
                        aca.pack(side= LEFT, fill= BOTH, expand=True)

                        mscrbr= ttk.Scrollbar(labelF,orient=VERTICAL,command=aca.yview)
                        mscrbr.pack(side=RIGHT,fill=Y)

                        aca.configure(yscrollcommand=mscrbr.set)
                        aca.bind("<Configure>", lambda e:aca.configure(scrollregion=aca.bbox('all')))

                        labelFrame= Frame(aca,bg='black')
                        aca.create_window((0,0),window=labelFrame,anchor='nw')
                                    
                        Label(labelFrame, text='',font = ('Courier',13),bg='black',fg='white').pack(padx=0,pady=0,anchor='nw')
                        Label(labelFrame, text="%-11s%-33s%-22s%-22s%-20s"%('   BID','Title','Author','Genre','Status'),font = ('Courier',13),bg='black',fg='white').pack(anchor='nw',padx=0.07,pady=0.07)#.place(relx=0.07,rely=0.07)
                        line=Label(labelFrame, text = "   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                        line.pack(padx=0.07,pady=0.15,anchor='nw')#.place (relx=0.07,rely=0.15)

                        disli=[]  
                        for i in booklog:
                            disli.append(i)

                            for bkdb in disli:
                                Label(labelFrame,text="%-10s%-38s%-25s%-25s%-20s"%('    '+str(bkdb[0]),bkdb[1],bkdb[2],bkdb[3],bkdb[5]),font = ('Courier',11), bg='black', fg='white').pack(padx=0.07,pady=y,anchor='nw')#.place(relx=0.07,rely=y)
                                y += 0.05
                                disli=[]
                        
                        adBtn = Button(vb,text="ADD BOOK",bg='#f7f1e3', fg='black', font = ('Courier',12), command=lambda:[vb.destroy(),addBook()])
                        adBtn.place(relx=0.15,rely=0.9, relwidth=0.2,relheight=0.08)

                        delBtn = Button(vb,text="BOOK FUNCTIONS",bg='#f7f1e3', fg='black', font = ('Courier',12), command=lambda:[vb.destroy(),editBook()])
                        delBtn.place(relx=0.40,rely=0.9, relwidth=0.2,relheight=0.08)

                        BackBtn = Button(vb,text="RETURN TO ADMIN",bg='#f7f1e3', fg='black', font = ('Courier',12),command=lambda:[vb.destroy(), Admin()])
                        BackBtn.place(relx=0.65,rely=0.9, relwidth=0.2,relheight=0.08)

                        vb.mainloop()

                    #UserDatabase                        
                    def Userdat():
                        
                        #Adding User
                        def addu():
                            
                            usid = uid.get()
                            #uside= ufname.get()

                            usname = uname.get()
                            usdob = udob.get()
                            usemal = uemal.get()
                            usmobn = umob.get()

                            global dblist,uentri
                            uentri=[usid,usname,usdob,usemal,usmobn]#[uside,usid,usname,usdob,usemal,usmobn]
                            cur1.execute("SELECT username,user_id FROM user")
                            userlo = cur1.fetchall()
                            print(userlo,uentri)
                            global amu
                            amu='y'
                            while amu=='y':
                                
                                def aeche():
                                    global amu,uentri
                                    for q in uentri:
                                        if len(q)==0:
                                            messagebox.showerror('Account Details','All Entries are Mandatory!\nFill in All the Details')
                                            amu='h'
                                            break
                                aeche()

                                if '.com' not in usemal or '@' not in usemal:
                                    messagebox.showerror('Email Id','Write in correct format\nabc@xyz.com')
                                    amu='n'
                                    break

                                def auche():
                                    global amu
                                    for c in userlo:
                                        if usid== c[0]:
                                            messagebox.showerror('Username','Username already exists\nTry Again')
                                            amu='h'
                                            print('after us',amu)
                                            break
                                                      
                                def amche():
                                    global amu
                                    for k in usmobn:
                                        if k.isdigit()== False:
                                            messagebox.showerror('Mobile Number','Invalid Entry\nTry Again')
                                            amu='h'
                                            break
                                        
                                def abche():
                                    global amu
                                    dblist=['1','2','3','4','5','6','7','8','9','0','-']
                                    if '-' not in usdob:
                                        messagebox.showerror('Date of Birth','Write in correct format\nyyyy-mm-dd')
                                        amu='n'
                                    for nob in usdob:
                                        if nob not in dblist:
                                            messagebox.showerror('Date of Birth','Write in digits with correct format\nyyyy-mm-dd')
                                            amu='n'
                                            break

                                abche()

                                dobl=usdob.split('-')
                                if len(dobl[0])!=4:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    amu='n'
                                    break
                                elif int(dobl[1])>12:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    amu='n'
                                    break
                                elif int(dobl[2])>31:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    amu='n'
                                    break
                                
                                auche()
                                amche()
                                break
                                            
                            if amu=='y':
                                amu=0
                            print(amu)
                                                
                            while amu==0:
                                uside=str( int(userlo[-1][1]) + 1 )
                                defm="bronze"
                                print(uside)
                                cur1.execute("INSERT INTO user(user_id, username, name, dob,email_id, mobile_no, membership) VALUES (%s,%s,%s,%s,%s,%s,%s)", (uside,usid,usname,dt.datetime.strptime(usdob,'%Y-%m-%d').date(),usemal,usmobn,defm))
                                db1.commit()
                                ab.destroy()

                                global userlog
                                cur1.execute("SELECT*FROM user")
                                userlog= cur1.fetchall()

                                rec=userlog[-1]
                                if rec[1]==usid and rec[2]==usname and rec[3]==usemal and rec[4]==usmobn and rec[6]==dt.datetime.strptime(usdob,'%Y-%m-%d').date():
                                    messagebox.showinfo('Add User','User Added Successfully!\nDefault Password- tlib123\nUser can Change Password after Login')
                                
                                Userdat()
                                break

                        def addUser():
                            
                            global uid ,uname, udob, uemal, umob, Canvas1, root, ab
                            ab = Tk()
                            ab.title("Library")
                            ab.minsize(width=400,height=400)
                            ab.geometry("1000x650")

                            Canvas1 = Canvas(ab)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)
                            
                            headingFrame1 = Frame(ab,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.25,rely=0.1,relwidth=0.5,relheight=0.13)

                            headingLabel = Label(headingFrame1, text="ADD USER", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(ab,bg='black')
                            labelFrame.place(relx=0.1,rely=0.28,relwidth=0.8,relheight=0.55)

                            
                            
                            # User NAME
                            lb2 = Label(labelFrame,text="User Name : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb2.place(relx=0.05,rely=0.16, relwidth=0.25, relheight=0.08)
                            
                            uid = Entry(labelFrame)
                            uid.place(relx=0.33,rely=0.16, relwidth=0.62, relheight=0.08)
                            
                            # Name
                            lb3 = Label(labelFrame,text="Name : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb3.place(relx=0.05,rely=0.31, relwidth=0.25, relheight=0.08)
                            
                            uname = Entry(labelFrame)
                            uname.place(relx=0.33,rely=0.31, relwidth=0.62, relheight=0.08)
                            
                            
                            # User DOB
                            lb4 = Label(labelFrame,text="Date of Birth : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb4.place(relx=0.05,rely=0.46, relwidth=0.25, relheight=0.08)
                            
                            udob = Entry(labelFrame)
                            udob.place(relx=0.33,rely=0.46, relwidth=0.62, relheight=0.08)
                            udob.insert(0,'yyyy-mm-dd')

                            # User Email Id
                            lb4 = Label(labelFrame,text="Email Id : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb4.place(relx=0.05,rely=0.61, relwidth=0.25, relheight=0.08)
                            
                            uemal = Entry(labelFrame)
                            uemal.place(relx=0.33,rely=0.61, relwidth=0.62, relheight=0.08)
                            uemal.insert(0, 'abcd@xyz.com')
                            
                            # User Mobile Number
                            lb5 = Label(labelFrame,text="Mobile Number : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb5.place(relx=0.05,rely=0.76, relwidth=0.25, relheight=0.08)

                            umob = Entry(labelFrame)
                            umob.place(relx=0.33,rely=0.76, relwidth=0.62, relheight=0.08)
                            umob.insert(0, 'xxxxxxxxxx')

##                            #USERID
##
##                            lb1= Label(labelFrame,text="UserID : ", bg="#FFBB00", fg='black', font=('Courier',13))
##                            lb1.place(relx=0.05,rely=0.76, relwidth=0.25, relheight=0.08)
##
##                            ufname = Entry(labelFrame)
##                            ufname.place(relx=0.33,rely=0.76, relwidth=0.62, relheight=0.08)
                            
                            #Submit Button
                            SubmitBtn = Button(ab,text="ADD THIS USER TO DATABASE",font=('Courier',12),bg='#d1ccc0', fg='black',command=addu)
                            SubmitBtn.place(relx=0.2,rely=0.87, relwidth=0.35,relheight=0.08)

                            #Back Button
                            backBtn = Button(ab,text="BACK",font=('Courier',12),bg='#d1ccc0', fg='black',command=lambda:[ab.destroy(),Userdat()])
                            backBtn.place(relx=0.62,rely=0.87, relwidth=0.16,relheight=0.08)
                                    

                        #Updating User
                        def updu():
                            
                            global userlog, updid, bdid, ubd, ubn, ube, ubm, n, lb1, lb2, lb3, lb4, lb5, unme

                            updid=bdid.get()
                            print(updid,unme)
                            ubn1=ubn.get()
                            ubd1=ubd.get()
                            ube1=ube.get()
                            ubm1=ubm.get()
                            n1 = n.get()

                            cur1.execute("SELECT username FROM user")
                            userlo = cur1.fetchall()
                            global aem
                            aem='y'
                            while aem=='y':  
                                if '-' not in ubd1:
                                    messagebox.showerror('Date of Birth','Write in correct format\nyyyy-mm-dd')
                                    aem='n'
                                    break
                                    
                                if '.com' not in ube1 or '@' not in ube1:
                                    messagebox.showerror('Email Id','Write in correct format\nabc@xyz.com')
                                    aem='n'
                                    break

                                def unche():
                                    global aem
                                    for c in userlo:
                                        if n1 == c[0] and n1!= unme:
                                            messagebox.showerror('Username','Username already exists\nTry Again')
                                            aem='h'
                                            break

                                def mnche():
                                    global aem
                                    for k in ubm1:
                                        if k.isdigit()== False:
                                            messagebox.showerror('Mobile Number','Invalid Entry\nTry Again')
                                            aem='h'
                                            break

                                global dobl
                                dobl=ubd1.split('-')
                                if len(dobl[0])!=4:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    aem='n'
                                    break
                                elif int(dobl[1])>12:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    aem='n'
                                    break
                                elif int(dobl[2])>31:
                                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                                    aem='n'
                                    break

                                def bnche():
                                    global aem,dobl
                                    for k in dobl:
                                        if k.isdigit()== False:
                                            messagebox.showerror('Date of Birth','Date of Birth is NOT in Digits')
                                            aem='h'
                                            break
                                        
                                bnche()        
                                unche()
                                mnche()
                                break
                            
                            if aem=='y':
                                aem=0

                            print(aem)
                                
                            while aem==0:
                                auepdt=dt.datetime.strptime(ubd1,'%Y-%m-%d').date()
                                cur1.execute("UPDATE user SET email_id= %s, mobile_no= %s, dob= %s, username= %s, name= %s WHERE user_id= %s", (ube1,ubm1,auepdt,n1,ubn1,updid))
                                db1.commit()
                                
                                
                                #Delete Previous
                                '''lb1.destroy()
                                lb2.destroy()
                                lb3.destroy()
                                lb4.destroy()'''

                                
                                #Message of Update
                                cur1.execute("SELECT  username,name, email_id, mobile_no, dob FROM user WHERE user_id=%s", (updid,))
                                ez1 = cur1.fetchone()
                                if ez1[0]==n1 and ez1[1]==ubn1 and ez1[2]==ube1 and ez1[3]==ubm1 and ez1[4]==auepdt:
                                    messagebox.showinfo('Updated User','Update Changes Saved')
                                    ud.destroy()
                                    db.destroy()
                                    Userdat()
                                    break

                        def updUser():

                            global userlog, bdid, ubd, ubn, ube, ubm, n, lb1, lb2, lb3, lb4, lb5, ud, bdn, bda, bdg, unme
                         
                            updid=bdid.get()
                            cur1.execute("SELECT name, username, dob, email_id, mobile_no FROM user WHERE user_id = %s", (updid,))
                            x = cur1.fetchone()

                            nme = x[0]
                            unme = x[1]
                            dob = x[2]
                            eme = x[3]
                            mbn = x[4]
       
                            
                            ud=Tk()
                            ud.title("Edit User Details")
                            ud.geometry('1000x650')

                            Canvas1 = Canvas(ud) 
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)

                            headingFrame1 = Frame(ud,bg='#FFBB00',bd=5)
                            headingFrame1.place(relx=0.24,rely=0.1,relwidth=0.5,relheight=0.11)

                            headingLabel = Label(headingFrame1, text="USER DETAILS", bg='black', fg='white', font = ('Courier',18))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            

                            labelFrame = Frame(ud,bg='black')
                            labelFrame.place(relx=0.1,rely=0.3,relwidth=0.8,relheight=0.46)
                            yf=Label(labelFrame, text='Would you like to edit these details?', bg='#FFBB00', fg='black', font = ('Courier',17), padx=150)
                            yf.place(relx=0,rely=0)


                            #User name
                            lb1 = Label(labelFrame,text="User Name: ", bg='black', fg='white',font=('Courier',14))
                            lb1.place(relx=0.07,rely=0.25, relheight=0.07)
                            n = Entry(labelFrame,bg='grey98',)
                            n.place(relx=0.07,rely=0.33, relwidth=0.35, relheight=0.07)
                            n.insert(0,unme)

                            #User 
                            lb2 = Label(labelFrame,text="Name: ", bg='black', fg='white',font=('Courier',14))
                            lb2.place(relx=0.07,rely=0.47, relheight=0.07)
                            ubn = Entry(labelFrame,bg='grey98',)
                            ubn.place(relx=0.07,rely=0.55, relwidth=0.35, relheight=0.07)
                            ubn.insert(0, nme)

                            #User mobnum
                            lb3 = Label(labelFrame,text="MobNum: ", bg='black', fg='white',font=('Courier',14))
                            lb3.place(relx=0.57,rely=0.36, relheight=0.07)
                            ubm = Entry(labelFrame,bg='grey98')
                            ubm.place(relx=0.57,rely=0.44, relwidth=0.35, relheight=0.07)
                            ubm.insert(0,mbn)

                            #User DOB
                            lb4 = Label(labelFrame,text="DOB: ", bg='black', fg='white',font=('Courier',14))
                            lb4.place(relx=0.07,rely=0.69, relheight=0.07)
                            ubd = Entry(labelFrame,bg='grey98')
                            ubd.place(relx=0.07,rely=0.77, relwidth=0.35, relheight=0.07)
                            ubd.insert(0,dob)

                            #User Email Id
                            lb5 = Label(labelFrame,text="Email Id: ", bg='black', fg='white',font=('Courier',14))
                            lb5.place(relx=0.57,rely=0.58, relheight=0.07)
                            ube = Entry(labelFrame,bg='grey98')
                            ube.place(relx=0.57,rely=0.66, relwidth=0.35, relheight=0.07)
                            ube.insert(0,eme)


                            sBtn = Button(ud,text="SAVE CHANGES",bg='#f7f1e3', fg='black', font = ('Courier',14),command=updu)
                            sBtn.place(relx=0.4,rely=0.82, relwidth=0.2,relheight=0.09)

                        #Deleteing USER
                        def delbu():
                            cur1.execute("SELECT*FROM user WHERE user_id=%s", (bdid.get(),))
                            c = cur1.fetchone()
                            print(c)
                        
    ##                        delbid = bdid.get()
                            if c in userlog:
    ##                            del userlog[delbid]
                                cur1.execute("DELETE FROM user WHERE user_id=%s", (bdid.get(),))
                                db1.commit()
                                messagebox.showinfo('Success',"User Deleted Successfully")
                                db.destroy()
                                Userdat()
                            else:
                                messagebox.showinfo('Failed to Delete',"This user does not exist in library")
                                db.destroy()
                                Userdat()
                            
                        def editUser():
                            
                            global bdid,Canvas1,root,db,userlog

                            db = Tk()
                            db.title("Library")
                            db.minsize(width=400,height=400)
                            db.geometry("1000x650")

                            Canvas1 = Canvas(db)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)
                            
                            headingFrame1 = Frame(db,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.25,rely=0.08,relwidth=0.5,relheight=0.13)
                            
                            headingLabel = Label(headingFrame1, text="USER FUNCTIONS", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(db,bg='black')
                            labelFrame.place(relx=0.1,rely=0.27,relwidth=0.8,relheight=0.6)   
                            
                            # USERID to Update
                            lb2 = Label(labelFrame,text="Enter the ID of the user : ", bg="#FFBB00", fg='black', font=('Courier',13))
                            lb2.place(relx=0.08,rely=0.12, relwidth=0.45, relheight=0.1)
                            bdid = Entry(labelFrame)
                            bdid.place(relx=0.55,rely=0.12, relwidth=0.25, relheight=0.1)
                            
                            def disu():

                                global userlog
                                cur1.execute("SELECT name, username, dob, email_id, mobile_no FROM user WHERE user_id = %s", (bdid.get(),))
                                x = cur1.fetchone()
                                

                                if x!= None :
                                    usd= bdid.get() ##- aashu

                                    lb3 = Label(labelFrame,text="User Details: ", bg='black', fg='white', font=('Courier',13))
                                    lb3.place(relx=0.26,rely=0.24, relwidth=0.45, relheight=0.1)

                                    tab=Label(labelFrame, text="%-5s%-10s%-15s%-17s%-13s%-13s"%('UID','Username','Name','Email Id','MobNum','DOB',),font = ('Courier',13),bg='black',fg='white')
                                    tab.place(relx=0.06,rely=0.35)
                                    line=Label(labelFrame, text = "-----------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                    line.place (relx=0.06,rely=0.40)

                                    #usd = disli.append(i)
                                    dis1=Label(labelFrame,text="%-5s%-10s%-15s%-17s%-13s%-13s"%(usd,x[1],x[0],x[3],x[4], x[2]),font = ('Courier',12), bg='black', fg='white')
                                    dis1.place(relx=0.06,rely=0.45)

                                    lb4 = Label(labelFrame,text="How would you like to proceed?", bg='white', fg='black', font=('Courier',13))
                                    lb4.place(relx=0.25,rely=0.57, relwidth=0.45, relheight=0.1)
                    
                                    delBtn = Button(labelFrame,text="DELETE USER",bg='#d1ccc0', fg='black',font=('Courier',13), command=delbu)
                                    delBtn.place(relx=0.18,rely=0.72, relwidth=0.25,relheight=0.15)

                                    updBtn = Button(labelFrame,text="UPDATE DETAILS",bg='#d1ccc0', fg='black',font=('Courier',13),command=updUser)
                                    updBtn.place(relx=0.52,rely=0.72, relwidth=0.25,relheight=0.15)

                                else:
                                    messagebox.showinfo('User ID not found',"This user does not exist in library")
                                    db.destroy()
                                    editUser()
                                                            
                            #Submit Button
                            sbtn = Button(labelFrame,text="Search",bg='#d1ccc0', fg='black',command=disu)
                            sbtn.place(relx=0.82,rely=0.12, relwidth=0.1,relheight=0.1,)

                            db.mainloop()
                        

                        vb = Tk()
                        vb.title("Library")
                        vb.minsize(width=400,height=400)
                        vb.geometry("1250x660")

                        Canvas1 = Canvas(vb) 
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(vb,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.24,rely=0.07,relwidth=0.5,relheight=0.1)

                        headingLabel = Label(headingFrame1, text="USER DATABASE", bg='black', fg='white', font = ('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        labelF = Frame(vb,bg='black')
                        labelF.place(relx=0.08,rely=0.24,relwidth=0.84,relheight=0.63)
                        y = 0.2

                        aca= Canvas(labelF, bg='black')
                        aca.pack(side= LEFT, fill= BOTH, expand=True)

                        mscrbr= ttk.Scrollbar(labelF,orient=VERTICAL,command=aca.yview)
                        mscrbr.pack(side=RIGHT,fill=Y)

                        aca.configure(yscrollcommand=mscrbr.set)
                        aca.bind("<Configure>", lambda e:aca.configure(scrollregion=aca.bbox('all')))

                        labelFrame= Frame(aca,bg='black')
                        aca.create_window((0,0),window=labelFrame,anchor='nw')

                        Label(labelFrame, text='',font = ('Courier',13),bg='black',fg='white').pack(padx=0,pady=0,anchor='nw')
                        Label(labelFrame, text="%-10s%-16s%-22s%-23s%-19s%-14s"%('  UID','User Name','Name','Email Id','MobNum', 'DOB'),font = ('Courier',13),bg='black',fg='white').pack(padx=0.07,pady=0.07,anchor='nw')#.place(relx=0.07,rely=0.07)
                        line=Label(labelFrame, text = "  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                        line.pack(padx=0.07,pady=0.15,anchor='nw')#.place (relx=0.07,rely=0.15)

                        global userlog
                        cur1.execute("SELECT*FROM user")
                        userlog= cur1.fetchall()

                        disli=[]  
                        for i in userlog:
                            disli.append(i)

                            for udb in disli:
                                Label(labelFrame,text="%-12s%-16s%-25s%-25s%-20s%-14s"%('  '+str(udb[0]),udb[1],udb[2],udb[3],udb[4], udb[6]),font = ('Courier',11), bg='black', fg='white').pack(padx=0.07,pady=y,anchor='nw')#.place(relx=0.07,rely=y)
                                y += 0.05
                                disli=[]
                        
    ##                    for i in userlog:
    ##                        Label(labelFrame,text="%-10s%-19s%-14s%-19s%-17s"%(i,userlog[i]['Name'],userlog[i]['DOB'],userlog[i]['Email_Id'],userlog[i]['MobNum']),font = ('Courier',11), bg='black', fg='white').place(relx=0.07,rely=y)
    ##                        y += 0.05
                        
                        adBtn = Button(vb,text="ADD USER",bg='#f7f1e3', fg='black', font = ('Courier',12), command=lambda:[vb.destroy(),addUser()])
                        adBtn.place(relx=0.15,rely=0.9, relwidth=0.2,relheight=0.08)

                        delBtn = Button(vb,text="EDIT USER",bg='#f7f1e3', fg='black', font = ('Courier',12), command=lambda:[vb.destroy(), editUser()])
                        delBtn.place(relx=0.40,rely=0.9, relwidth=0.2,relheight=0.08)

                        BackBtn = Button(vb,text="RETURN TO ADMIN",bg='#f7f1e3', fg='black', font = ('Courier',12),command=lambda:[vb.destroy(), Admin()])
                        BackBtn.place(relx=0.65,rely=0.9, relwidth=0.2,relheight=0.08)

                        vb.mainloop()

                    #Queries Complaints and Suggestions
                    def QCSa():

                        def QACa():

                            def ans(yv):

                                def saveans(n):
                                    global qcs,abox
                                    ansq=abox.get(1.0,'end')
                                    qcs[n][3]=ansq
                                    aqac.append(qcs.pop(n))
                                    messagebox.showinfo('Answered',"Your answer has been entered. :)")
                                    a.destroy()
                                    QACa()
                                    
                                    
                                global qcs,abox
                                
                                a = Tk()
                                a.title("Library")
                                a.minsize(width=400,height=400)
                                a.geometry("600x400")

                                Canvas1 = Canvas(a)
                                Canvas1.config(bg="#12a4d9")
                                Canvas1.pack(expand=True,fill=BOTH)

                                qn=int((yv-0.24)/0.06)
                                que=qcs[qn][2]

                                headingFrame1 = Frame(a,bg="#FFBB00",bd=5)
                                headingFrame1.place(relx=0.08,rely=0.08,relwidth=0.3,relheight=0.12)
                                headingLabel1 = Label(headingFrame1, text="  Question:", bg='black', fg='white', font=('Courier',13),anchor='w')
                                headingLabel1.place(relx=0,rely=0, relwidth=1, relheight=1)
                                qbox = Text(a, bg='#f7f1e3', fg='black',font=('Courier',10))
                                qbox.place(relx=0.08,rely=0.22, relwidth=0.8, relheight=0.2)
                                qbox.insert('end',que)
                                qbox.configure(state="disabled")

                                headingFrame2 = Frame(a,bg="#FFBB00",bd=5)
                                headingFrame2.place(relx=0.08,rely=0.48,relwidth=0.3,relheight=0.12)
                                headingLabel2= Label(headingFrame2, text="  Answer:", bg='black', fg='white', font=('Courier',13),anchor='w')
                                headingLabel2.place(relx=0,rely=0, relwidth=1, relheight=1)
                                abox = Text(a,bg='#f7f1e3', fg='black',font=('Courier',10))
                                abox.place(relx=0.08,rely=0.63, relwidth=0.8, relheight=0.2)

                                b=Button(a,text="SUBMIT AMSWER",bg='black', fg='white', font = ('Courier',12),command=lambda :[saveans(qn)])
                                b.place(relx=0.66,rely=0.88, relwidth=0.3,relheight=0.1)

                            bf = Tk()
                            bf.title("Library")
                            bf.minsize(width=400,height=400)
                            bf.geometry("1000x650")

                            Canvas1 = Canvas(bf)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)

                            headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                            headingLabel = Label(headingFrame1, text="QUERIES AND COMPLAINTS", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(bf,bg='black')
                            labelFrame.place(relx=0.08,rely=0.3,relwidth=0.84,relheight=0.56)
                            lb2 = Label(labelFrame, text='  Unanswered queries and complaints     ', bg='#FFBB00', fg='black', font = ('Courier',17), padx=150)
                            lb2.place(relx=0,rely=0)

                            tab=Label(labelFrame, text="%-10s%-15s%-30s%-13s"%('UID','Type','Brief','Button'),font = ('Courier',14),bg='black',fg='white')
                            tab.place(relx=0.05,rely=0.12)
                            line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                            line.place (relx=0.03,rely=0.18)
                            global y
                            y=0.24
                            for i in range(0,len(qcs)):
                                if qcs[i][1]in ["Query","Complaint"] and qcs[i][3]=="":
                                    d=Label(labelFrame,text="%-10s%-15s%-30s%-13s"%(qcs[i][0],qcs[i][1],qcs[i][2],qcs[i][3]),font = ('Courier',11), bg='black', fg='white')
                                    d.place(relx=0.05,rely=y)
                                    b=Button(labelFrame,text="Answer",bg='#f7f1e3', fg='black', font = ('Courier',11),command=lambda y=y :[bf.destroy(),ans(y)])
                                    b.place(relx=0.72,rely=y, relwidth=0.2,relheight=0.05)
                                    y += 0.06

                            b=Button(bf,text="RETURN", bg='#f7f1e3', fg='black', font = ('Courier',12),command=lambda :[bf.destroy(),QCSa()])
                            b.place(relx=0.43,rely=0.88, relwidth=0.16,relheight=0.08)

                        #previously answered
                        def prevans():
                    
                            global userlog, booklog, aqac, uid

                            def vans(iv):
                                a = Tk()
                                a.title("Library")
                                a.minsize(width=400,height=400)
                                a.geometry("600x400")

                                Canvas1 = Canvas(a)
                                Canvas1.config(bg="#12a4d9")
                                Canvas1.pack(expand=True,fill=BOTH)

                                qn=iv
                                ques=aqac[qn][2]
                                answ=aqac[qn][3]

                                headingFrame1 = Frame(a,bg="#FFBB00",bd=5)
                                headingFrame1.place(relx=0.08,rely=0.08,relwidth=0.3,relheight=0.12)
                                headingLabel1 = Label(headingFrame1, text="  Question:", bg='black', fg='white', font=('Courier',13),anchor='w')
                                headingLabel1.place(relx=0,rely=0, relwidth=1, relheight=1)
                                qbox = Text(a, bg='#f7f1e3', fg='black',font=('Courier',10))
                                qbox.place(relx=0.08,rely=0.22, relwidth=0.8, relheight=0.2)
                                qbox.insert('end',ques)
                                qbox.configure(state="disabled")

                                headingFrame2 = Frame(a,bg="#FFBB00",bd=5)
                                headingFrame2.place(relx=0.08,rely=0.48,relwidth=0.3,relheight=0.12)
                                headingLabel2= Label(headingFrame2, text="  Answer:", bg='black', fg='white', font=('Courier',13),anchor='w')
                                headingLabel2.place(relx=0,rely=0, relwidth=1, relheight=1)
                                abox = Text(a, bg='#f7f1e3', fg='black',font=('Courier',10))
                                abox.place(relx=0.08,rely=0.63, relwidth=0.8, relheight=0.2)
                                abox.insert('end',answ)
                                abox.configure(state="disabled")

                                b=Button(a,text="RETURN",bg='black', fg='white', font = ('Courier',12),command=lambda :[a.destroy(),prevans()])
                                b.place(relx=0.66,rely=0.88, relwidth=0.3,relheight=0.1)

                            bf = Tk()
                            bf.title("Library")
                            bf.minsize(width=400,height=400)
                            bf.geometry("1000x650")

                            Canvas1 = Canvas(bf)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)

                            headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                            headingLabel = Label(headingFrame1, text="QUERIES AND COMPLAINTS", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(bf,bg='black')
                            labelFrame.place(relx=0.08,rely=0.3,relwidth=0.84,relheight=0.55)

                            lb2 = Label(labelFrame,text="   Previously Answered Queries and Complaints   ", bg="#FFBB00", fg='black', font=('Courier',17))
                            lb2.place(relx=0,rely=0,relwidth=1)

                            tab=Label(labelFrame, text="%-10s%-15s%-20s%-15s"%('UID','Type','Brief','Button'),font = ('Courier',14),bg='black',fg='white')
                            tab.place(relx=0.05,rely=0.12)
                            line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                            line.place (relx=0.03,rely=0.18)
                            global y
                            y=0.24
                            for i in range(0,len(aqac)):
                                d=Label(labelFrame,text="%-10s%-15s%-20s"%(aqac[i][0],aqac[i][1],aqac[i][2]),font = ('Courier',11), bg='black', fg='white')
                                d.place(relx=0.05,rely=y)
                                b=Button(labelFrame,text="View Answer",bg='#f7f1e3', fg='black', font = ('Courier',11),command=lambda i=i :[bf.destroy(),vans(i)])
                                b.place(relx=0.72,rely=y, relwidth=0.24,relheight=0.05)
                                y += 0.06

                            b=Button(bf,text="RETURN", bg='#f7f1e3', fg='black', font = ('Courier',12),command=lambda :[bf.destroy(),QCSa()])
                            b.place(relx=0.43,rely=0.88, relwidth=0.16,relheight=0.08)
                            
                        #Suggestions
                        def SUGs():
                            
                            bf = Tk()
                            bf.title("Library")
                            bf.minsize(width=400,height=400)
                            bf.geometry("1000x650")

                            Canvas1 = Canvas(bf)
                            Canvas1.config(bg="#12a4d9")
                            Canvas1.pack(expand=True,fill=BOTH)

                            headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                            headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                            headingLabel = Label(headingFrame1, text="SUGGESTIONS", bg='black', fg='white', font=('Courier',15))
                            headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                            labelFrame = Frame(bf,bg='black')
                            labelFrame.place(relx=0.08,rely=0.3,relwidth=0.84,relheight=0.5)
                            lb2 = Label(labelFrame, text='  Here are some suggestions from our users   ', bg='#FFBB00', fg='black', font = ('Courier',17), padx=150)
                            lb2.place(relx=0,rely=0)

                            tab=Label(labelFrame, text="%-10s%-45s%-20s"%('UID','Brief',"Status"),font = ('Courier',14),bg='black',fg='white')
                            tab.place(relx=0.05,rely=0.12)
                            line=Label(labelFrame, text = "--------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                            line.place (relx=0.03,rely=0.18)
                            global y
                            y=0.24
                            for i in range(0,len(sug)):
                                d=Label(labelFrame,text="%-10s%-30s"%(sug[i][0],sug[i][1]),font = ('Courier',11), bg='black', fg='white')
                                d.place(relx=0.05,rely=y)
                                b=Button(labelFrame,text="Working on",bg='#f7f1e3', fg='black', font = ('Courier',11),state= DISABLED)
                                b.place(relx=0.72,rely=y, relwidth=0.2,relheight=0.05)
                                y += 0.06

                            b=Button(bf,text="RETURN", bg='#f7f1e3', fg='black', font = ('Courier',12),command=lambda :[bf.destroy(),QCSa()])
                            b.place(relx=0.43,rely=0.88, relwidth=0.16,relheight=0.08)
                        
                        f = Tk()
                        f.title("Library")
                        f.minsize(width=400,height=400)
                        f.geometry("1000x650")

                        Canvas1 = Canvas(f)
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(f,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                        headingLabel = Label(headingFrame1, text="QUERIES, COMPLAINTS AND SUGGESTIONS", bg='black', fg='white', font=('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                        btn1 = Button(f,text="UNANSWERED QUERIES/COMPLAINTS",bg='black', fg='white',font = ('Courier',14),command=lambda:[f.destroy(), QACa()])
                        btn1.place(relx=0.225,rely=0.4, relwidth=0.55,relheight=0.1)

                        btn2 = Button(f,text="PREVIOUSLY ANSWERED QUERIES/COMPLAINTS",bg='black', fg='white',font = ('Courier',14), command=lambda:[f.destroy(),prevans()])
                        btn2.place(relx=0.225,rely=0.57, relwidth=0.55,relheight=0.1)

                        btn3 = Button(f,text="SUGGESTIONS",bg='black', fg='white',font = ('Courier',14), command=lambda:[f.destroy(), SUGs()])
                        btn3.place(relx=0.225,rely=0.74, relwidth=0.55,relheight=0.1)

                        btn4 = Button(f,text="RETURN TO ADMIN",font=('Courier',11),bg='#d1ccc0', fg='black', command=lambda:[f.destroy(), Admin()])
                        btn4.place(relx=0.36,rely=0.9, relwidth=0.25,relheight=0.07)

                        f.mainloop()

                    #Fines and Misplaced books
                    global Fine
                    def Fine():
                        
                        global booklog, userlog, eb
                        
                        fb = Tk()
                        fb.title("Library")
                        fb.minsize(width=400,height=400)
                        fb.geometry("1220x650")

                        Canvas1 = Canvas(fb) 
                        Canvas1.config(bg="#12a4d9")
                        Canvas1.pack(expand=True,fill=BOTH)

                        headingFrame1 = Frame(fb,bg="#FFBB00",bd=5)
                        headingFrame1.place(relx=0.24,rely=0.07,relwidth=0.5,relheight=0.1)

                        headingLabel = Label(headingFrame1, text="PENDING FINES", bg='black', fg='white', font = ('Courier',15))
                        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)
                            
                        labelFrame = Frame(fb,bg='black')
                        labelFrame.place(relx=0.08,rely=0.24,relwidth=0.84,relheight=0.57)

                        Label(labelFrame, text='Fines display by :',font = ('Courier',13),bg='black',fg='white').place(relx=0.15,rely=0.05)
                        eb=Combobox(labelFrame, values=('Books','User'),font = ('Courier',12))
                        eb.place(relx=0.35,rely=0.05,relwidth=0.3)

                        def checkf():
                            global eb
                            if eb.get()=='Books':
                                
                                labelFrame1 = Frame(labelFrame,bg='black')
                                labelFrame1.place(relx=0.03,rely=0.35,relheight=0.55)#,relwidth=0.84,relheight=0.57)

                                Label(labelFrame, text="%-12s%-25s%-10s%-9s%-14s%-12s%-10s"%('BID','Title','Fine','User','Issued on','Due on','Days Delayed'),font = ('Courier',13),bg='black',fg='white').place(relx=0.03,rely=0.17)
                                line=Label(labelFrame, text = "-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                line.place (relx=0.02,rely=0.25)

                                scrollb=Scrollbar(labelFrame1,orient=VERTICAL)

                                global bslt,dailfines
                                bslt=Listbox(labelFrame1,width=95,height=48,yscrollcommand=scrollb.set,bg='black',fg='white',font=('Courier',12),disabledforeground='white')

                                scrollb.config(command=bslt.yview)
                                scrollb.pack(side=RIGHT,fill=Y)

                                tdate=dt.date.today()
                                cur1.execute('SELECT bk_id,title,fine,borrowed_by,issued_on,due_on,returned_on,sl_no FROM borrowed_books WHERE (%s > due_on) AND (status=%s)',(tdate,'Pending'))
                                finst=cur1.fetchall()
                                for fr in finst:
                                    f=list(fr)
                                    if f[6]== None:
                                        f[6]= tdate
                                    dn=(f[6]-f[5]).days

                                    bslt.insert(END,"%-5s%-32s%-10s%-9s%-14s%-18s%-10s"%(str(f[0]),f[1],f[2],f[3],f[4],f[5],dn))

                                bslt.configure(state=DISABLED)
                                bslt.pack()
                                
                            elif eb.get()=='User':
                                
                                global userfine
                                def userfine():
                                
                                    labelFrame2 = Frame(labelFrame,bg='black')
                                    labelFrame2.place(relx=0.03,rely=0.35,relheight=0.55)#,relwidth=0.84,relheight=0.57)

                                    Label(labelFrame, text="%-15s%-20s%-15s%-20s%-15s"%('\tUID','Username','Fine','No.of Books','Membership\t\t'),font = ('Courier',13),bg='black',fg='white').place(relx=0.03,rely=0.17)
                                    line=Label(labelFrame, text = "-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",bg='black',fg='white')
                                    line.place (relx=0.02,rely=0.25)

                                    scrollb2=Scrollbar(labelFrame2,orient=VERTICAL)
                                    #global bslt2

                                    connect()
                                    
                                    global bslt2
                                    bslt2=Listbox(labelFrame2,width=95,height=48,yscrollcommand=scrollb2.set,bg='black',fg='white',font=('Courier',12))

                                    scrollb2.config(command=bslt2.yview)
                                    scrollb2.pack(side=RIGHT,fill=Y)

                                    connect()

                                    cur1.execute('SELECT * FROM user WHERE due_amount != %s',(0.00,))
                                    ubls=cur1.fetchall()

                                    tdate=dt.date.today()

                                    dailfines()
                                    connect()

                                    cur1.execute("SELECT * FROM borrowed_books WHERE (%s > due_on) AND (returned_on = %s OR fine != %s) AND (status!='Paid')",(tdate,0000-00-00,0.00))
                                    fnst=cur1.fetchall()

                                    bcot={}
                                    for us in userlog:
                                        bcot[us[1]]=0
                                    print(bcot,'\n')

                                    for g in fnst:
                                        x=bcot[g[4]]
                                        bcot[g[4]]=x+1
                                        print(x)
                                    print(bcot,'\n',ubls)

                                    for i in ubls:
                                        bslt2.insert(END,"%-25s%-20s%-20s%-15s%-15s"%('\t\t        '+str(i[0]),i[1],i[7],bcot[i[1]],i[8]))

                                    bslt2.pack()

                                userfine()
                                
                            else:
                                messagebox.showinfo('Fines display error','Please select among Books or User')
                                    
                        def updpay():
                            global bslt,bslt2,userfine,labelFrame2,eb
                            val=bslt2.get(ANCHOR)
                            if val=='':
                                messagebox.showerror('Selection','Please Select User to Update Fine.')
                            else:
                                l=val.split()[0];print(l)
                                cur1.execute("SELECT username, fines FROM user WHERE user_id=%s", (l,))
                                bdet= cur1.fetchone()
                                cur1.execute("SELECT fine,sl_no,title,issued_on FROM borrowed_books WHERE borrowed_by=%s AND returned_on!=%s AND status!='Paid' AND fine!=0.00",(bdet[0],0000-00-00))
                                recs=cur1.fetchall();paf=0;lno=recs[0][0]
                                for r in recs:
                                    paf+=float(r[0])
                                    if r[0]<lno:
                                        lno=r[0]
                                resp=messagebox.askyesno('Update Fine','Do you want to Update fine for this User?\n\n  User Name: %s\n  Payable Pending fine: %s\n  Minimum Amount: %s'%(bdet[0],paf,lno))
                                if resp==1:
                                    fineamt=float(askstring('Fine Payment', 'Enter the fine paid by the user:\t\t\t'))
                                    print(fineamt,type(fineamt),'\n',resp);str1=''
                                    if fineamt>=paf:
                                        connect()
                                        ba=fineamt-paf
                                        for r in recs:
                                            cur1.execute("UPDATE borrowed_books SET status=%s WHERE sl_no=%s",('Paid',r[1]))
                                            db1.commit()
                                            str1=str1+'\n\t'+r[2]+'  '+r[3].strftime('%d-%m-%Y')
                                        da=float(bdet[1])-paf
                                        cur1.execute("UPDATE user set due_amount=%s where username=%s;", (da,bdet[0]))
                                        db1.commit()
                                        messagebox.showinfo('Fine Updated','You have updated Fine Amount: %s Rs\nFrom User: %s\nBalance Amount: %s\n\nPlease return fined books to clear any pending fines\nFine on thses books have been cleared:%s'%(fineamt,bdet[0],ba,str1))

                                        connect()
                                        bslt2.delete(0,END)
                                        try:
                                            bslt2.remove()
                                        except:
                                            bslt2.destroy()
                                        userfine()
                                    else:
                                        connect()
                                        rmt=fineamt;str2=''
                                        for r in recs:
                                            if rmt>=float(r[0]):
                                                rmt-=float(r[0])
                                                cur1.execute("UPDATE borrowed_books SET status=%s WHERE sl_no=%s",('Paid',r[1]))
                                                db1.commit()
                                                str2=str2+'\n\t'+r[2]+'  '+r[3].strftime('%d-%m-%Y')
                                        pat=fineamt-rmt
                                        da=paf-pat
                                        cur1.execute("UPDATE user set due_amount=%s where username=%s;", (da,bdet[0]))
                                        db1.commit()
                                        messagebox.showinfo('Fine Updated','You have updated Fine Amount: %s / %s Rs\nFrom User: %s\nBalance Amount: %s\n\nPlease return fined books to clear any pending fines\nFine on thses books have been cleared:%s'%(pat,paf,bdet[0],rmt,str2))

                                        connect()
                                        bslt2.delete(0,END)
                                        try:
                                            bslt2.remove()
                                        except:
                                            bslt2.destroy()
                                        userfine()
                                    userfine()
                                    checkf()
                                    

                                else:
                                    #messagebox.showinfo('Update Fine','Fine is already updated')
                                    pass

                        BackBtn = Button(fb,text="RETURN TO ADMIN",font=('Courier',13),bg='#d1ccc0', fg='black', command=lambda:[fb.destroy(), Admin()])
                        BackBtn.place(relx=0.15,rely=0.87, relwidth=0.3,relheight=0.1)

                        BackBtn1 = Button(fb,text="UPDATE PAYMENT",font=('Courier',13),bg='#d1ccc0', fg='black',command=updpay)
                        BackBtn1.place(relx=0.55,rely=0.87, relwidth=0.3,relheight=0.1)

                        BackBtn2 = Button(labelFrame,text="CHECK",font=('Courier',13),bg='#d1ccc0', fg='black',command=checkf)
                        BackBtn2.place(relx=0.68,rely=0.04,relwidth=0.1)

                        fb.mainloop()

                    bf = Tk()
                    bf.title("Library")
                    bf.minsize(width=400,height=400)
                    bf.geometry("1000x650")

                    Canvas1 = Canvas(bf)
                    Canvas1.config(bg="#12a4d9")
                    Canvas1.pack(expand=True,fill=BOTH)

                    headingFrame1 = Frame(bf,bg="#FFBB00",bd=5)
                    headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.16)
                    headingLabel = Label(headingFrame1, text="WELCOME TO ADMINISTRATION FUNCTIONS", bg='black', fg='white', font=('Courier',15))
                    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

                    btn1 = Button(bf,text="Book Database",bg='black', fg='white',font = ('Courier',14),command=lambda:[bf.destroy(), Bookdat()])
                    btn1.place(relx=0.27,rely=0.35, relwidth=0.45,relheight=0.1)

                    btn2 = Button(bf,text="User Database",bg='black', fg='white',font = ('Courier',14), command=lambda:[bf.destroy(), Userdat()])
                    btn2.place(relx=0.27,rely=0.47, relwidth=0.45,relheight=0.1)

                    btn3 = Button(bf,text="Fines and Book upkeep",bg='black', fg='white', font = ('Courier',14),command=lambda:[bf.destroy(), Fine()])
                    btn3.place(relx=0.27,rely=0.59, relwidth=0.45,relheight=0.1)

                    btn4 = Button(bf,text="Queries and Complaints",bg='black', fg='white', font = ('Courier',14),command=lambda:[bf.destroy(), QCSa()])
                    btn4.place(relx=0.27,rely=0.72, relwidth=0.45,relheight=0.1)

                    btn5 = Button(bf,text="LOGOUT",bg='Grey', fg='white', font = ('Courier',14),command=lambda:[bf.destroy(), root.destroy(), main()])
                    btn5.place(relx=0.3,rely=0.84, relwidth=0.38,relheight=0.08)

                    bf.mainloop()
                    
                Admin()

            else:
                messagebox.showerror('Wrong Details','Admin Password combination NOT FOUND!\nTry Again')
        else:
            messagebox.showerror('Profile Error','Invalid Profile Entry\nTry Again')


    global forgotp
    def forgotp():
        if spbu.get().lower()=='user':
            rootfp=Tk()
            rootfp.title('Forgot Password')
            rootfp.geometry('500x400')
            
            Canvasf = Canvas(rootfp) 
            Canvasf.config(bg="#12a4d9")
            Canvasf.pack(expand=True,fill=BOTH)

            headingFrame1f = Frame(rootfp,bg="#FFBB00",bd=5)
            headingFrame1f.place(relx=0.1,rely=0.07,relwidth=0.8,relheight=0.13)

            headingLabelf = Label(headingFrame1f, text=" SUBMIT YOUR REGISTERED EMAIL ID\nTO GENERATE NEW PASSWORD .", bg='black', fg='white',font = ('Courier',13))
            headingLabelf.place(relx=0,rely=0, relwidth=1, relheight=1)
            Label(rootfp,bg='lightblue',padx=1200,pady=0.5).place(relx=0,rely=0.24)

            global ue1,cue1,ue2,cue2
            
            labelFramef = Frame(rootfp,bg='black')
            labelFramef.place(relx=0.1,rely=0.33,relwidth=0.8,relheight=0.6)
            
            ue1=Label(labelFramef,text='Username:',font=('',15),bg='black',fg='white')
            ue1.place(relx=0.115,rely=0.16, relheight=0.07)
            
            cue1=Entry(labelFramef)
            cue1.place(relx=0.49,rely=0.16, relwidth=0.35, relheight=0.078)
            
            ue2=Label(labelFramef,text='Email Id:',font=('',15),bg='black',fg='white')
            ue2.place(relx=0.12,rely=0.45, relheight=0.07)
            
            cue2=Entry(labelFramef)
            cue2.place(relx=0.49,rely=0.45, relwidth=0.35, relheight=0.078)

            def npswd():
                global ue1,cue1,ue2,cue2,userlog,ab
                ab=cue1.get()
                usli={}
                for p in userlog:
                    usli[p[1]]= [p[3],p[5]]
                while True:
                    if ab in usli:
                        if ('@' not in cue2.get()) or ('.com' not in cue2.get()):
                            messagebox.showerror('Email Id','Invalid Entry. Write in correct format\nabc@xyz.com')
                            break
                        if cue2.get() == usli[ab][0]:
                            headingLabelf.destroy()
                            ue1.destroy()
                            cue1.destroy()
                            ue2.destroy()
                            cue2.destroy()

                            #ue1=Label(labelFramef,text='Username:',font=('',15),bg='lavender')
                            #cue1=Entry(labelFramef)
                            #ue2=Label(labelFramef,text='Email Id:',font=('',15),bg='lavender')
                            #cue2=Entry(labelFramef)
                            
                            headlabf = Label(headingFrame1f, text=" CHANGING PASSWORD\nCREATE A STRONG NEW PASSWORD .", bg='black', fg='white',font = ('Courier',15))
                            headlabf.place(relx=0,rely=0, relwidth=1, relheight=1)
                            
                            ue3=Label(labelFramef,text='Create New Password',font=('Roman',15),bg='black',fg='white')
                            ue3.place(relx=0.17,rely=0.11, relheight=0.07)

                            global cue3
                            cue3=Entry(labelFramef)
                            cue3.place(relx=0.17,rely=0.21, relwidth=0.7, relheight=0.07)
            
                            ue4=Label(labelFramef,text='Confirm Password',font=('Roman',15),bg='black',fg='white')
                            ue4.place(relx=0.17,rely=0.40, relheight=0.07)

                            global cue4
                            cue4=Entry(labelFramef)
                            cue4.place(relx=0.17,rely=0.50, relwidth=0.7, relheight=0.07)

                            def donfp():
                                global ab,usli,cp1,cp2
                                cp1=cue3.get()
                                cp2=cue4.get()

                                print(cp1,cp2)

                                if len(cp1)==0 or len(cp2)==0:
                                    messagebox.showerror('Password Entry','All Entries are Mandatory!\nFill in all the Details')
                                    
                                elif cp1 != cp2:
                                    messagebox.showerror('New Password','Passwords Do Not Match!')
                                    
                                elif cp1 == cp2:
                                    cur.execute("UPDATE user SET password= %s WHERE username= %s", (cue3.get(),ab))
                                    db.commit()
                                        
    ##                                Ud[ab]['Password']=cue4.get()
    ##                                ufpad={ab:cue3.get()}
    ##                                U.update(ufpad)
    ##                                del ufpad
    ##                              if (ab in U and U[ab]==cue3.get()) and (cue4.get()==Ud[ab]['Password']):
    ##                                messagebox.showinfo('New Password','New Password Created')
    ##                                rootf.destroy()

                                global userlog
                                cur.execute("SELECT*FROM user")
                                userlog= cur.fetchall()

                                cur.execute("SELECT password FROM user WHERE username=%s", (ab,))
                                nps = cur.fetchone()[0]
                                if (nps==cp1) and (nps==cp2): #if(ab in U and U[ab]==cue3.get()) and (cue2.get()==Ud[ab]['Password']):
                                    messagebox.showinfo('New Password','New Password Created')
                                    rootfp.destroy()

                            rootfp.update()

                            global lwcse,upcse,numbe,spchr,score
                            lwcse=False
                            upcse=False
                            numbe=False
                            spchr=False
                            score=0
                            
                            global pscheck
                            def pscheck():
                                global lwcse,upcse,numbe,spchr,score,cue3
                                for evchr in cue3.get():
                                    if evchr in 'abcdefghijklmnopqrstuvwxyz':
                                        lwcse=True
                                    elif evchr in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                                        upcse=True
                                    elif evchr in '1234567890':
                                        numbe=True
                                    else:
                                        spchr=True
                                if lwcse==True and upcse==True:
                                    score+=10
                                if numbe==True and (lwcse==True or upcse==True):
                                    score+=10
                                if spchr==True:
                                    score+=5
                                if len(cue3.get())>=8:
                                    score+=5

                                if lwcse!=True or upcse!=True:
                                    score-=15
                                if numbe!=True and (lwcse!=True or upcse!=True):
                                    score-=15
                                if spchr!=True:
                                    score-=10
                                if len(cue3.get())<8:
                                    score-=10
                                rootfp.update()
                                
                                '''if score<=10:
                                    shwlab=Label(labelFramef,text='Password Strength is weak',font=('',11),bg='lavender',fg='red')
                                    shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                elif score>10 and score<=20:
                                    shwlab=Label(labelFramef,text='Password Strength is medium',font=('',11),bg='lavender',fg='red')
                                    shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                elif score>=25:
                                    shwlab=Label(labelFramef,text='Password Strength is strong',font=('',11),bg='lavender',fg='red')
                                    shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                else:
                                    pass'''
                            nbl=Button(labelFramef,text="Done",bg='lightgrey',font=('Times',14),command=donfp)
                            nbl.place(relx=0.36,rely=0.7, relwidth=0.27,relheight=0.13)
                            rootfp.update()
                            def wlo():
                                global lwcse,upcse,numbe,spchr,score,cue3,pscheck
                                #q=0
                                while True: #q<=15:
                                    try:
                                        score=score*0
        ##                                if rootfp.quit()==True:
        ##                                    break
                                        cue3.get()
                                        pscheck()
                                        if score<=10:
                                            shwlab=Label(labelFramef,text='Password Strength is weak     ',font=('',11),bg='black',fg='lightblue')
                                            shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                            score=score*0
                                            cue3.get()
                                            continue
                                        if score>10 and score<=25:
                                            shwlab=Label(labelFramef,text='Password Strength is medium',font=('',11),bg='black',fg='lightblue')
                                            shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                            score=score*0
                                            cue3.get()
                                            continue
                                        if score>25 and score<=40:
                                            shwlab=Label(labelFramef,text='Password Strength is strong   ',font=('',11),bg='black',fg='lightblue')
                                            shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                            score=score*0
                                            cue3.get()
                                            continue
                                        else:
                                            score=0
                                            rootfp.update()
                                            continue
                                        score=0
                                        rootfp.update()
                                    except:
                                        break
                                    #q+=1
                            wlo()

                            #nbl=Button(labelFramef,text="Done",bg='lightgrey',font=('Times',12))
                            #nbl.place(relx=0.36,rely=0.7, relwidth=0.25,relheight=0.1)

                            break
                    
                        else:
                            messagebox.showerror('Email Id','Email Id does NOT MATCH\n Email-id Not Found')
                            break
                    
                    else:
                        messagebox.showerror('User Name','Invalid Entry. Username NOT FOUND!')
                        break

            npsbu=Button(labelFramef,text="Next",bg='lightgrey',font=('Times',14),command=npswd)
            npsbu.place(relx=0.36,rely=0.7,relwidth=0.27,relheight=0.13)
            rootfp.mainloop()

        elif spbu.get().lower()=='admin':
            
            rootfp=Tk()
            rootfp.title('Forgot Password')
            rootfp.geometry('500x400')
            
            Canvasf = Canvas(rootfp) 
            Canvasf.config(bg="#12a4d9")
            Canvasf.pack(expand=True,fill=BOTH)

            headingFrame1f = Frame(rootfp,bg="#FFBB00",bd=5)
            headingFrame1f.place(relx=0.1,rely=0.07,relwidth=0.8,relheight=0.13)

            headingLabelf = Label(headingFrame1f, text=" SU ID\nTO GENERATE NEW PASSWORD .", bg='black', fg='white',font = ('Courier',13))
            headingLabelf.place(relx=0,rely=0, relwidth=1, relheight=1)
            Label(rootfp,bg='lightblue',padx=1200,pady=0.5).place(relx=0,rely=0.24)

            global aue1,acue1,aue2,acue2
            
            labelFramef = Frame(rootfp,bg='black')
            labelFramef.place(relx=0.1,rely=0.33,relwidth=0.8,relheight=0.6)
            
            aue1=Label(labelFramef,text='Admin Id:',font=('',15),bg='black',fg='white')
            aue1.place(relx=0.115,rely=0.16, relheight=0.07)
            
            acue1=Entry(labelFramef)
            acue1.place(relx=0.49,rely=0.16, relwidth=0.35, relheight=0.078)
            
            aue2=Label(labelFramef,text='Admin No.:',font=('',15),bg='black',fg='white')
            aue2.place(relx=0.12,rely=0.45, relheight=0.07)
            
            acue2=Entry(labelFramef)
            acue2.place(relx=0.49,rely=0.45, relwidth=0.35, relheight=0.078)

            def anpswd():
                global aue1,acue1,aue2,acue2,adminlog,ab
                ab=acue1.get()
                cur.execute("SELECT*FROM admin")
                adminlog=cur.fetchall()
                asli={}
                for p in adminlog:
                    asli[p[1]]= str(p[0])
                print(adminlog,asli)
                while True:
                    if ab in asli:
                        if acue2.get() == asli[ab]:
                            headingLabelf.destroy()
                            aue1.destroy()
                            acue1.destroy()
                            aue2.destroy()
                            acue2.destroy()

                            #ue1=Label(labelFramef,text='Username:',font=('',15),bg='lavender')
                            #cue1=Entry(labelFramef)
                            #ue2=Label(labelFramef,text='Email Id:',font=('',15),bg='lavender')
                            #cue2=Entry(labelFramef)
                            
                            headlabf = Label(headingFrame1f, text=" CHANGING PASSWORD\nCREATE A NEW PASSWORD .", bg='black', fg='white',font = ('Courier',15))
                            headlabf.place(relx=0,rely=0, relwidth=1, relheight=1)
                            
                            ue3=Label(labelFramef,text='Create New Password',font=('Roman',15),bg='black',fg='white')
                            ue3.place(relx=0.17,rely=0.11, relheight=0.07)

                            global cue3
                            cue3=Entry(labelFramef)
                            cue3.place(relx=0.17,rely=0.21, relwidth=0.7, relheight=0.07)
            
                            ue4=Label(labelFramef,text='Confirm Password',font=('Roman',15),bg='black',fg='white')
                            ue4.place(relx=0.17,rely=0.40, relheight=0.07)

                            global cue4
                            cue4=Entry(labelFramef)
                            cue4.place(relx=0.17,rely=0.50, relwidth=0.7, relheight=0.07)

                            def adonfp():
                                global ab,asli,cp1,cp2
                                cp1=cue3.get()
                                cp2=cue4.get()

                                print(cp1,cp2)

                                if len(cp1)==0 or len(cp2)==0:
                                    messagebox.showerror('Password Entry','All Entries are Mandatory!\nFill in all the Details')
                                    
                                elif cp1 != cp2:
                                    messagebox.showerror('New Password','Passwords Do Not Match!')
                                    
                                elif cp1 == cp2:
                                    cur.execute("UPDATE admin SET passwd= %s WHERE uname= %s", (cue3.get(),ab))
                                    db.commit()
                                        
    ##                                Ud[ab]['Password']=cue4.get()
    ##                                ufpad={ab:cue3.get()}
    ##                                U.update(ufpad)
    ##                                del ufpad
    ##                              if (ab in U and U[ab]==cue3.get()) and (cue4.get()==Ud[ab]['Password']):
    ##                                messagebox.showinfo('New Password','New Password Created')
    ##                                rootf.destroy()

                                global adminlog
                                cur.execute("SELECT*FROM admin")
                                adminlog=cur.fetchall()

                                cur.execute("SELECT passwd FROM admin WHERE uname=%s", (ab,))
                                nps = cur.fetchone()[0]
                                if (nps==cp1) and (nps==cp2): #if(ab in U and U[ab]==cue3.get()) and (cue2.get()==Ud[ab]['Password']):
                                    messagebox.showinfo('New Password','New Password Created')
                                    rootfp.destroy()

                            rootfp.update()

                            global lwcse,upcse,numbe,spchr,score
                            lwcse=False
                            upcse=False
                            numbe=False
                            spchr=False
                            score=0
                            
                            global apscheck
                            def apscheck():
                                global lwcse,upcse,numbe,spchr,score,cue3
                                for evchr in cue3.get():
                                    if evchr in 'abcdefghijklmnopqrstuvwxyz':
                                        lwcse=True
                                    elif evchr in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                                        upcse=True
                                    elif evchr in '1234567890':
                                        numbe=True
                                    else:
                                        spchr=True
                                if lwcse==True and upcse==True:
                                    score+=10
                                if numbe==True and (lwcse==True or upcse==True):
                                    score+=10
                                if spchr==True:
                                    score+=5
                                if len(cue3.get())>=8:
                                    score+=5

                                if lwcse!=True or upcse!=True:
                                    score-=15
                                if numbe!=True and (lwcse!=True or upcse!=True):
                                    score-=15
                                if spchr!=True:
                                    score-=10
                                if len(cue3.get())<8:
                                    score-=10
                                rootfp.update()
                                
                                '''if score<=10:
                                    shwlab=Label(labelFramef,text='Password Strength is weak',font=('',11),bg='lavender',fg='red')
                                    shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                elif score>10 and score<=20:
                                    shwlab=Label(labelFramef,text='Password Strength is medium',font=('',11),bg='lavender',fg='red')
                                    shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                elif score>=25:
                                    shwlab=Label(labelFramef,text='Password Strength is strong',font=('',11),bg='lavender',fg='red')
                                    shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                else:
                                    pass'''
                            nbl=Button(labelFramef,text="Done",bg='lightgrey',font=('Times',14),command=adonfp)
                            nbl.place(relx=0.36,rely=0.7, relwidth=0.27,relheight=0.13)
                            rootfp.update()
                            def awlo():
                                global lwcse,upcse,numbe,spchr,score,cue3,apscheck
                                #q=0
                                while True: #q<=15:
                                    try:
                                        score=score*0
        ##                                if rootfp.quit()==True:
        ##                                    break
                                        cue3.get()
                                        apscheck()
                                        if score<=10:
                                            shwlab=Label(labelFramef,text='Password Strength is weak     ',font=('',11),bg='black',fg='lightblue')
                                            shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                            score=score*0
                                            cue3.get()
                                            continue
                                        if score>10 and score<=25:
                                            shwlab=Label(labelFramef,text='Password Strength is medium',font=('',11),bg='black',fg='lightblue')
                                            shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                            score=score*0
                                            cue3.get()
                                            continue
                                        if score>25 and score<=40:
                                            shwlab=Label(labelFramef,text='Password Strength is strong   ',font=('',11),bg='black',fg='lightblue')
                                            shwlab.place(relx=0.27,rely=0.85, relheight=0.07)
                                            score=score*0
                                            cue3.get()
                                            continue
                                        else:
                                            score=0
                                            rootfp.update()
                                            continue
                                        score=0
                                        rootfp.update()
                                    except:
                                        break
                                    #q+=1
                            awlo()

                            #nbl=Button(labelFramef,text="Done",bg='lightgrey',font=('Times',12))
                            #nbl.place(relx=0.36,rely=0.7, relwidth=0.25,relheight=0.1)

                            break
                    
                        else:
                            messagebox.showerror('Admin No.','Admin No. does NOT MATCH\n Admin no. Not Found')
                            break
                    
                    else:
                        messagebox.showerror('Admin ID','Invalid Entry. Admin name NOT FOUND!')
                        break

            npsbu=Button(labelFramef,text="Next",bg='lightgrey',font=('Times',14),command=anpswd)
            npsbu.place(relx=0.36,rely=0.7,relwidth=0.27,relheight=0.13)
            rootfp.mainloop()
            
        else:
            messagebox.showerror('Forgot Password','Sorry! Please Select PROFILE in Login Page')
        
    global signup
    def signup():

        root.withdraw()
        
        sroot=Tk()
        sroot.title('Sign Up')
        sroot.geometry('1000x650')

        Canvas1 = Canvas(sroot) 
        Canvas1.config(bg="#12a4d9")
        Canvas1.pack(expand=True,fill=BOTH)

        headingFrame1 = Frame(sroot,bg='#FFBB00',bd=5)
        headingFrame1.place(relx=0.25,rely=0.07,relwidth=0.5,relheight=0.13)

        headingLabel = Label(headingFrame1, text="LIBLIGHT Library", bg='black', fg='white', font = ('Courier',18))
        headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

        labelFrame = Frame(sroot,bg='black')
        labelFrame.place(relx=0.1,rely=0.3,relwidth=0.8,relheight=0.6)
        Label(labelFrame, text='Fill in Details', bg='#FFBB00', fg='black', font = ('Courier',18), padx=500).place(relx=0,rely=0,)
        
        #Name
        lb1 = Label(labelFrame,text="Name ", bg='black', fg='white',font=('Courier',15))
        lb1.place(relx=0.05,rely=0.13, relheight=0.07)
        bid = Entry(labelFrame,bg='grey98')
        bid.place(relx=0.05,rely=0.20, relwidth=0.35, relheight=0.07)
        
        #DOB
        lb2 = Label(labelFrame,text="Date of Birth ", bg='black', fg='white',font=('Courier',15))
        lb2.place(relx=0.05,rely=0.33, relheight=0.07)
        bid2 = Entry(labelFrame,bg='grey98')
        bid2.place(relx=0.05,rely=0.40, relwidth=0.35, relheight=0.07)
        bid2.insert(0,'yyyy-mm-dd')
        
        #Email Id
        lb3 = Label(labelFrame,text="Email Id ", bg='black', fg='white',font=('Courier',15))
        lb3.place(relx=0.05,rely=0.53, relheight=0.07)
        bid3 = Entry(labelFrame,bg='grey98')
        bid3.place(relx=0.05,rely=0.60, relwidth=0.35, relheight=0.07)
        bid3.insert(0,'abcd@xyz.com')
        
        #Mobile Number
        lb4 = Label(labelFrame,text="Mobile Number ", bg='black', fg='white',font=('Courier',15))
        lb4.place(relx=0.05,rely=0.73, relheight=0.07)
        bid4 = Entry(labelFrame,bg='grey98')
        bid4.place(relx=0.05,rely=0.80, relwidth=0.35, relheight=0.07)
        bid4.insert(0,'xxxxxxxxxx')
        
        #Username
        lb5 = Label(labelFrame,text="Username ", bg='black', fg='white',font=('Courier',15))
        lb5.place(relx=0.55,rely=0.13, relheight=0.07)
        bid5 = Entry(labelFrame,bg='grey98')
        bid5.place(relx=0.55,rely=0.20, relwidth=0.35, relheight=0.07)
        
        #Password
        lb6 = Label(labelFrame,text="Password ", bg='black', fg='white',font=('Courier',15))
        lb6.place(relx=0.55,rely=0.33, relheight=0.07)
        bid6 = Entry(labelFrame,bg='grey98')
        bid6.place(relx=0.55,rely=0.40, relwidth=0.35, relheight=0.07)
        
        #Confirm Password
        lb7 = Label(labelFrame,text="Confirm Password ", bg='black', fg='white',font=('Courier',15))
        lb7.place(relx=0.55,rely=0.53, relheight=0.07)
        bid7 = Entry(labelFrame,bg='grey98')
        bid7.place(relx=0.55,rely=0.60, relwidth=0.35, relheight=0.07)
        
        #Create Account
        global U,userlog,nlist,dblist
        nlist=['1','2','3','4','5','6','7','8','9','0',' ']
        dblist=['1','2','3','4','5','6','7','8','9','0','-']
        def sclick():
            global userlo,nlist,dblist,sentri
            sentri=[bid5.get(),bid.get(),bid2.get(),bid3.get(),bid4.get(),bid6.get(),bid7.get()]
            cur.execute("SELECT username,user_id FROM user")
            userlo = cur.fetchall()
            print(userlo)
            global smu
            smu='y'
            while smu=='y':
                
                if '.com' not in bid3.get() or '@' not in bid3.get():
                    messagebox.showerror('Email Id','Write in correct format\nabc@xyz.com')
                    smu='n'
                    break

                if bid7.get() != bid6.get():
                    messagebox.showerror('Password Error','Passwords Do Not Match')
                    smu='n'
                    break

                def uche():
                    global smu
                    for c in userlo:
                        if bid5.get()== c[0]:
                            messagebox.showerror('User Name','Username already exists\nTry Again')
                            smu='h'
                            print('after us',smu)
                            break
                                      
                def mche():
                    global smu
                    for k in bid4.get():
                        if k.isdigit()== False:
                            messagebox.showerror('Mobile Number','Invalid Entry\nTry Again')
                            smu='h'
                            break
                        
                def eche():
                    global smu,sentri
                    for q in sentri:
                        if len(q)==0:
                            messagebox.showerror('Account Details','All Entries are Mandatory!\nFill in All the Details')
                            smu='h'
                            break

                def bche():
                    global smu
                    if '-' not in bid2.get():
                        messagebox.showerror('Date of Birth','Write in correct format\nyyyy-mm-dd')
                        smu='n'
                    for nob in bid2.get():
                        if nob not in dblist:
                            messagebox.showerror('Date of Birth','Write in digits with correct format\nyyyy-mm-dd')
                            smu='n'
                            break

                eche()
                bche()

                dobl=bid2.get().split('-')
                if len(dobl[0])!=4:
                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                    smu='n'
                    break
                elif int(dobl[1])>12:
                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                    smu='n'
                    break
                elif int(dobl[2])>31:
                    messagebox.showerror('Date of Birth','Invalid Date\nTry again')
                    smu='n'
                    break
                
                uche()
                mche()
                break
                            
            if smu=='y':
                smu=0
            print(smu)
                                
            while smu==0:
                global userlog
                suid= str( int(userlo[-1][1]) + 1 )
                sudt= dt.datetime.strptime(bid2.get(),'%Y-%m-%d').date()
                print(suid,sudt)
                cur.execute("INSERT into user (user_id,username,name,email_id,mobile_no,dob,password,fines) values (%s,%s,%s,%s,%s,%s,%s,%s)",( suid,bid5.get(),bid.get(),bid3.get(),bid4.get(),sudt,bid7.get(),'' ))
                db.commit()
                
                cur.execute("SELECT*FROM user")
                userlog= cur.fetchall()
                rec=userlog[-1]
                print(rec)
                if rec[1]==bid5.get() and rec[2]==bid.get() and rec[3]==bid3.get() and rec[4]==bid4.get() and rec[5]==bid7.get() and rec[6]==sudt:
                    messagebox.showinfo('Profile- Sign Up','User Account Created Successfully!')
                    sroot.destroy()
                    root.deiconify()
                    break
                
##            if bid5.get() in userlog and bid5.get() in U:
##                messagebox.showinfo('Profile- Sign Up','User Account Created Successfully!')
##                sroot.destroy()

        lbu = Button(labelFrame,text="SIGN UP ",bg='#f7f1e3', fg='black',command=sclick)
        lbu.place(relx=0.75,rely=0.8,relwidth=0.18, relheight=0.08)

        sroot.mainloop()

    #Entry buttons
    login=Button(root,text='LOGIN',bg='#f7f1e3', fg='black',font=('Courier',13),command=login)
    login.place(relx=0.1,rely=0.83, relwidth=0.16,relheight=0.08)
    forgb=Button(root,text=' FORGOT PASSWORD? ',bg='#f7f1e3', fg='black',font=('Courier',13),padx=25,command=forgotp)
    forgb.place(relx=0.28,rely=0.83, relwidth=0.24,relheight=0.08 )
    sup=Button(root,text='Not Registered? SIGN UP',bg='#f7f1e3', fg='black',font=('Courier',13), padx=35, command=signup)
    sup.place(relx=0.55,rely=0.83, relwidth=0.36,relheight=0.08)
    
    root.mainloop()
    
main()
