# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.


init python:



    from pyphonetics import RefinedSoundex

    import socket

    rs = RefinedSoundex()


    req = "REQ INPUT"
    req = req.encode("utf-8")

    ratName = ""

    kw_list = ["Cool", "Groovy", "Sweet", "Lovely", "Adorable", "Radical", "Gnarly", "Sucky", "Sloppy", "Boring", "Love", "Hate", "Meh", "Okay", "Nope"]
    kw_n = [1, 2, 2, 1, 2, 2, -2, -3, -3, -2, 2, -5, -5, -2, -1]
    guide_img = ["guide_1_1.png", "guide_1_2.png", "guide_1_3.png", "guide_1_4.png", "guide_1_5.png", "guide_2.png"]
    roses_nb_round = [5, 4, 3, 2, 1]

    response = ["theres nothing"]

    def valid(k):
        return k.isalpha()

    def valid_string(k):
        return not ':' in k

    

    class Rat:

        def __init__(self, name, affection, keywords, taste, lines, pos, sprite_name):
            self.c = Character(name)
            self.name = name
            self.affection = affection
            self.keywords_taste = dict()
            self.lines = lines
            self.pos = pos
            self.idle_img = sprite_name
            for k in range(len(keywords)):
                self.keywords_taste[keywords[k]] = taste[k]


        def process_input_date(self, n_keywords):
            kws = dict()
            nb = 0
            for k in n_keywords:
                print(kw_list)
                for kw_n in range(len(kw_list)):
                    rat_k = kw_list[kw_n]
                    print(rat_k, kw_n)
                    dist = rs.distance(k, rat_k)
                    if(dist < 2):
                        nb += 1
                        if rat_k not in kws.keys():
                            kws[rat_k] = 0
                        kws[rat_k] += self.keywords_taste[rat_k]
                            


            for kw_k in kws.keys():
                aff_val = kws[kw_k]
                if nb >= 5:
                    aff_val *= 5 / nb
                self.affection += aff_val
            return (self.affection >= 0, kws)

        def getLine(self, date_number):
            return self.lines[date_number]

        def get_response(self):
            res = "Cool"
            if self.affection > 5 :
                res = "Groovy"
            elif self.affection > 0:
                res = "Meh"
            else :
                res = "No."
            return res

        def react_sprite(self):
            if self.affection > 5 :
                return self.idle_img + "_happy"
            elif self.affection > 0:
                return self.idle_sprite()
            else :
                return self.idle_img + "_angry"

        def idle_sprite(self): 
            print(self.idle_img)
            return self.idle_img + "_idle"  

        def in_love(self):
            return True    


    class Game:    
        def __init__(self, rats, rats_pos):
            self.rats = rats
            self.round = 0
            self.rats_pos = rats_pos
            self.amnt_rats = len(rats)
            self.rats_rose = list()
            self.response = list()
            self.textBoxDim = (0.15, 0.75, 1250, 200)
            for i in range(self.amnt_rats):
                self.rats_rose.append(False)
            self.final_verdict = False

        def prepareForRemoval(self, rat):
            index_rat = self.rats.index(rat)
            self.rats_rose[index_rat] = True

        def game_over(self):
            return self.amnt_rats <= 1     

        def processAudio(self):
            
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.connect(("", 7777))
            s.send(req)
            data = s.recv(1500).decode("utf-8")
            s.close() 

            if not valid_string(data):
                self.error = "Audio error"
                return self.processAudio()
            return data

        def get_rats_names(self):
            return map(lambda rat: rat.name, self.rats) 

        def processAudioRose(self):
            nb_rose = 0
            self.error = False
            for r in self.rats_rose:
                if r:
                    nb_rose += 1
            data = self.processAudio()

            print(data)
            
            words_data = data.split()

            if(self.is_final_verdict(words_data)):
                self.finish_rose_ceremony()




            rats_chosen = list()
            for i in range(len(self.rats)):
                rats_chosen.append(False)

            

            for w in words_data:
                if valid(w):
                    rats_names_dist = list(map(lambda rat_name: rs.distance(w, rat_name), self.get_rats_names()))

                    for i in range(len(rats_chosen)):
                        choice = rats_chosen[i] or rats_names_dist[i] < 1
                        rats_chosen[i] = choice
                        if (not self.rats_rose[i]) and choice:
                            nb_rose += 1
                    if(nb_rose > roses_nb_round[self.round]):
                        return 
                
            for r in range(len(self.rats_rose)):
                self.rats_rose[r] = bool(self.rats_rose[r]) ^ bool(rats_chosen[r])
                
            self.error = True

        def process_input_date(self, rat):
            data = self.processAudio()  
            words_data = data.split()
            
            (is_rat_satisfied, kws) = rat.process_input_date(words_data)
            print(kws)
            self.response = kws
            response = self.response
            rat_line = rat.get_response() 
            if not is_rat_satisfied:
                self.prepareForRemoval(rat)
            return is_rat_satisfied

        def update_rats(self):
            new_rats = list()
            for i in range(self.amnt_rats):
                if not self.rats_rose[i]:
                    new_rats.append(self.rats[i])
            self.rats = new_rats
            self.amnt_rats = len(self.rats)

        def start_rose_ceremony(self): 
            self.update_rats()
            if self.game_over():
                return self.game_over_seq()
            self.rats_rose = list() 
            for i in range(len(self.rats)):
                self.rats_rose.append(False)
            self.final_verdict = False  
            renpy.hide_screen("date_screen")

        def game_over_seq(self):

            if self.amnt_rats < 1:
                renpy.call("bad_end")
            else:
                renpy.call("ending_sequence")

        def finish_rose_ceremony(self):
            new_rats = list()
            for ri in range(len(self.rats_rose)):
                if self.rats_rose[ri]:
                    new_rats.append(self.rats[ri])
            self.rats = new_rats
            self.amnt_rats = len(self.rats)

            self.rats_rose = list() 
            for i in range(len(self.rats)):
                self.rats_rose.append(False)

            print("new_round")

            self.round += 1
            renpy.hide_screen("rose_ceremony")
            if self.game_over():
                self.game_over_seq()
            else:
                renpy.call("date")

        def is_rat_chosen(self, index):
            return self.rats_rose[index]

        def rat_name(self, index):    
            return self.get_rats_names()[index]

        def is_final_verdict(self, words_data):
            for w in range(len(words_data)):
                if words_data[w] != ":" and rs.distance(words_data[w], "final") < 2:
                    self.final_verdict = True
                    return True
            if len(words_data) < 2:
                self.final_verdict = False
                return 
            for w in range(len(words_data) - 1):
                if rs.distance(words_data[w], "final") < 2 & rs.distance(words_data[w], "verdict"):
                    self.final_verdict = True
            

        def is_rose_ceremony_over(self):
            print(self.final_verdict)
            return self.final_verdict

        def pause(self, duration):
            # Source : https://lemmasoft.renai.us/forums/viewtopic.php?t=71040
            if duration > 0:
                renpy.pause(duration, hard=True)

        def winning_rat(self):
            if self.game_over():
                rat = self.rats[0]
                if rat.in_love():
                    return rat
            return Null    



    rat1 = Rat("Rattle", 6, list(kw_list), list(kw_n), ["Hello ! It's me. The Ratle Chuu-Ann. You may know me from my hit songs such as 'Pink Ratty Club'", "'God, What have you done ? You're a Pink Ratty Girl, and you dance in the tub. Oh mama, I'm just having fun, on the cheese in my heels, it's where I belong, down at the Pink Ratty Club'", "line3", "line4", "line5", "line6", "line7"], (0.2, 0.2), "rattle")  
    rat2 = Rat("Blue", 6, list(kw_list), list(kw_n), ["Hi ! I'm G4mer_R0ddent_441. It's kinda weird going on a date irl, you know ? But I'm really glad to have met you.", "Have you ever watched Sewers Moon ? I'm actually in a cosplay of The Guardian of Pipes. Do you know what cosplay is ? I love it ! I'd really like to match with someone at a con.", "line3", "line4", "line5", "line6", "line7"], (0.2, 0.2), "rod")  
    rat3 = Rat("Kiki", 6, list(kw_list), list(kw_n), ["line1", "line2", "line3", "line4", "line5", "line6", "line7"], (0.2, 0.2), "rattle")  
    rat4 = Rat("Runner", 6, list(kw_list), list(kw_n), ["line1", "line2", "line3", "line4", "line5", "line6", "line7"], (0.2, 0.2), "rod")  
    rat5 = Rat("Chew", 6, list(kw_list), list(kw_n), ["line1", "line2", "line3", "line4", "line5", "line6", "line7"], (0.2, 0.2), "rattle")

    rats_pos_list = [
    ( 600, 200, 50, 50),
    ( 1200, 200, 50, 50),
    (400, 300, 50, 50),
    (1400, 300, 50, 50),
    (800, 350, 50, 50)
    ]  

    rats_list = [rat1, rat2, rat3, rat4, rat5]
    #rats_list = [rat1, rat2]

    game = Game(rats_list, rats_pos_list)

    


screen rose_ceremony():
    image "rose_bg.png"
    for r in range(game.amnt_rats):
        # For every mushroom in the list, show it as imagebutton
        imagebutton :
            if game.is_rat_chosen(r):
                idle "Rat_rose.png"
            else:
                idle "Rat_roseless.png"
            area game.rats_pos[r]

        #image roses_n if error rose then red  

    imagebutton :
        idle "roses.png"  
        at mic_hover(0.8)
        action Function(game.processAudioRose)
        pos (600, 600)    


style response_box_style:
    background Frame("nope.jpeg", 0,0)
    xmaximum 100
    ymaximum 100

style response_text_style:
    color "#b92e47"

screen response_box():
    vbox:
        xpos 1600
        ypos 100
        for response_kws in game.response:
            textbutton response_kws xalign 0.05 text_style "response_text_style"
           







        





screen satisfaction_popup(satisfaction_indicator):
    if satisfaction_indicator :
        image "yay.png" at yay_anim
    else :
        image "nope.png" at nope_anim

            


transform mic_hover(amnt):
    on hover:
        additive amnt
    on idle:
        additive 0.0

transform guide_appear:
    alpha 0.0
    easein 1 alpha 1.0      
    


screen date_screen():

    dismiss action NullAction()
    imagebutton :
        align (0.95, 0.70)
        idle "mic_button" 
        at mic_hover(0.8)
        hovered [Function(renpy.notify, "mic")]
        action [Return()]

        

        

screen guide_screen(id):  

    image "guide_bg"

    for i in range(id):
        imagebutton :
            idle guide_img[i]
            at guide_appear

    

    if id < 6:
        key ["K_KP_ENTER", "mousedown_1"] action [Show("guide_screen", None, id+1)]
    else :
        key ["K_KP_ENTER", "mousedown_1"] action [Hide("guide_screen"), Call("date")]   





screen ending_screen(lover_rat, id):   
    image "end_bg.png"

    if id > 0 and lover_rat != Null:
        image "end_you.png"

    

    if id < 1:
        key ["K_KP_ENTER", "mousedown_1"] action [Show("ending_screen", None, lover_rat, id+1)]
    else :
        key ["K_KP_ENTER", "mousedown_1"] action [Return]   

   


# The game starts here.

label start:
    
    call screen guide_screen(1)
    
        

    pause

    return


transform yay_anim:
    pos(100, 100)
    zoom 0.0
    easein 2 zoom 0.35 rotate 30.0
    easein 1 zoom 0.0 rotate 0.0

transform nope_anim:
    pos(100, -50)
    zoom 0.45
    easein 1 ypos 200
    easein 1 ypos 1000 rotate 45.0

transform rat_move_anim(start, finish, yp, speed):
    xpos start
    ypos yp
    easein speed xpos finish  

transform rat_leave_anim(start, finish, speed):
    pause 1
    xpos start
    easein speed xpos finish 




label date:

    
    show screen date_screen


    $ ite = 0

    image lounge = "bg lounge.png"
    show lounge

    image you  = "you_rat.png"
    show you at rat_move_anim(1.2, 0.55, 0.15, 2)

    

    while ite < game.amnt_rats:

        hide screen response_box

        python : 
            current_rat = game.rats[ite]
            idle_sprite = current_rat.idle_sprite()
            
            ratName = current_rat.name
        
        image rat idle = "[idle_sprite].png"


        show rat idle at rat_move_anim(-0.50, 0.20, 0.15, 2)

        

        $ l = current_rat.getLine(game.round)

        current_rat.c "[l]"

        

        python:
                
            #TODO CHANGE SATIS TO RAT    
            satisfaction_indicator = game.process_input_date(current_rat)

         

        $ react_sprite = current_rat.react_sprite()

        image rat react = "[react_sprite].png"

        show screen response_box

        show screen satisfaction_popup(satisfaction_indicator) 

        show rat react at rat_leave_anim(0.20, -0.5, 1)

    
        pause 2

        hide screen satisfaction_popup



        




        $ ite += 1



    $ game.start_rose_ceremony()

    show you at rat_move_anim(0.55, 1.2, 0.15, 2)
    hide you
    hide rat  
    hide screen response_box
    hide lounge

    call screen rose_ceremony
        

label ending_sequence:
    $ lover = game.winning_rat()

    call screen ending_screen(lover, 0)
    return 

label bad_end:
    image bg_end = "end_bg.png"
    show bg_end
    call screen ending_screen(Null, 0)

    return    