import PySimpleGUI as sg
from random import randint


class GUI:

    def __init__(self):
        self.selected_difficulty = "NONE"
        self.bg_color = '#0EFFE9'
        self.btn_bg_color = '#FF0E83'
        self.btn_text_color = '#ffffff'
        self.font = 'Terminal'
        self.text_color = '#000000'
        self.user_score = 0
        self.user_score_key = 'User_Score'
        self.update = {'update': False, 'selected_difficulty': False, 'bg_color': False, 'btn_bg_color': False,
                       'btn_text_color': False, 'font': False, 'text_color': False, 'user_score': False,
                       'user_score_key': False}

    def set_difficulty(self, new_difficulty):
        self.update['update'] = True
        self.update['selected_difficulty'] = True
        if new_difficulty == "Easy":
            self.selected_difficulty = "EASY"
            print('Difficulty Selected: Easy')
        elif new_difficulty == "Intermediate":
            self.selected_difficulty = "INTERMEDIATE"
            print('Difficulty Selected: Intermediate')
        elif new_difficulty == "Insane":
            self.selected_difficulty = "INSANE"
            print('Difficulty Selected: INSANE')
        else:
            print('Invalid Selection, current difficulty: ' + self.selected_difficulty)

    def get_difficulty(self):
        return self.selected_difficulty

    def set_bg_color(self, new_color):
        self.update['update'] = True
        self.update['bg_color'] = True
        self.bg_color = new_color
        print('Background Color: ' + new_color)

    def set_btn_bg_color(self, new_color):
        self.update['update'] = True
        self.update['btn_bg_color'] = True
        self.btn_bg_color = new_color
        print('Button Background Color: ' + new_color)

    def set_btn_text_color(self, new_color):
        self.update['update'] = True
        self.update['btn_text_color'] = True
        self.btn_text_color = new_color
        print('Button Text Color: ' + new_color)

    def set_font(self, new_font):
        self.update['update'] = True
        self.update['font'] = True
        self.font = new_font
        print('Font: ' + new_color)

    def set_text_color(self, new_color):
        self.update['update'] = True
        self.update['text_color'] = True
        self.text_color = new_color
        print('Text Color: ' + new_color)

    def set_user_score(self, new_score):
        self.update['update'] = True
        self.update['user_score'] = True
        if type(new_score) == int or type(new_score) == float or type(new_score) == str:
            self.user_score = int(new_score)
            print('User Score: ' + str(self.user_score))

    def get_user_score(self):
        return self.user_score

    def set_user_score_key(self, new_key):
        self.update['update'] = True
        self.update['user_score_key'] = True
        self.user_score_key = new_key

    def get_user_score_key(self):
        return self.user_score_key

    def setup_theme(self):
        sg.theme_background_color(color=self.bg_color)  # Background Colour
        sg.set_options(element_padding=(5, 9), font=(self.font,))  # Set font
        return None

    def make_initial_window(self):
        # Create the layout
        self.setup_theme()

        layout_initial = [
            [sg.Text("WELCOME TO QIX", justification='center', size=(1280, 3), pad=((0, 0), (200, 0)),
                     text_color=self.text_color, background_color=self.bg_color)],
            [sg.Text("Select Difficulty", justification='center', size=(1280, 3),
                     text_color=self.text_color, background_color=self.bg_color)],
            [sg.Button("Easy", size=(15, 2), pad=((260, 45), (10, 10)),
                       button_color=(self.btn_text_color, self.btn_bg_color)),
             sg.Button("Intermediate", size=(15, 2), pad=((45, 45), (10, 10)),
                       button_color=(self.btn_text_color, self.btn_bg_color)),
             sg.Button("Insane", size=(15, 2), pad=((45, 45), (10, 10)),
                       button_color=(self.btn_text_color, self.btn_bg_color))],
            [sg.Button("Exit", size=(15, 2), pad=((538, 0), (50, 50)),
                       button_color=(self.btn_text_color, self.btn_bg_color))],

        ]

        # Create the window
        window_initial = sg.Window("QIX", layout_initial, size=(1280, 800), grab_anywhere=True, finalize=True)

        # Return the window
        return window_initial

    def update_initial_window(self, window):
        new_window = window

        if self.update['update']:
            self.update['update'] = False

        if self.update['selected_difficulty']:
            self.update['selected_difficulty'] = False
        elif self.update['user_score']:
            self.update['user_score'] = False
        elif self.update['user_score_key']:
            self.update['user_score_key'] = False
        elif (self.update['bg_color'] or self.update['btn_bg_color'] or self.update['btn_text_color']
              or self.update['font'] or self.update['text_color']):
            self.update['bg_color'] = False
            self.update['btn_bg_color'] = False
            self.update['btn_text_color'] = False
            self.update['font'] = False
            self.update['text_color'] = False
            window.close()
            new_window = self.make_initial_window()

        return new_window

    def render_initial_screen(self):
        initial_window = self.make_initial_window()

        # Create an event loop
        while True:
            if self.update['update']:
                initial_window = self.update_initial_window(initial_window)

            event, values = initial_window.read()

            # End program if user closes window or
            # presses the EXIT button
            if event == "Exit" or event == sg.WIN_CLOSED:
                print('Exiting')
                break
            elif event == "Easy":
                self.set_difficulty("Easy")
                break
            elif event == "Intermediate":
                self.set_difficulty("Intermediate")
                break
            elif event == "Insane":
                self.set_difficulty("Insane")
                break

        initial_window.close()
        return self.selected_difficulty

    def make_game_over_window(self):
        self.setup_theme()

        # Create the layout
        layout_game_over = [
            [sg.Text("GAME OVER", justification='center', size=(1280, 3), pad=((0, 0), (200, 0)),
                     text_color=self.text_color, background_color=self.bg_color)],
            [sg.Text("Area Captured: " + str(self.user_score), justification='center', size=(1280, 3),
                     text_color=self.text_color, background_color=self.bg_color, key=self.user_score_key)],
            [sg.Button("Restart", size=(15, 2), pad=((538, 0), (0, 0)),
                       button_color=(self.btn_text_color, self.btn_bg_color))],
            [sg.Button("Exit", size=(15, 2), pad=((538, 0), (50, 50)),
                       button_color=(self.btn_text_color, self.btn_bg_color))],

        ]

        # Create the window
        window_game_over = sg.Window("QIX", layout_game_over, size=(1280, 800), grab_anywhere=True, finalize=True)

        # Return the window
        return window_game_over

    def update_game_over_window(self, window):
        new_window = window

        if self.update['update']:
            self.update['update'] = False

        if self.update['selected_difficulty']:
            self.update['selected_difficulty'] = False
        elif self.update['user_score']:
            self.update['user_score'] = False
            window[self.user_score_key].update("Area Captured: " + str(self.user_score))
        elif (self.update['bg_color'] or self.update['btn_bg_color'] or self.update['btn_text_color']
              or self.update['font'] or self.update['text_color'] or self.update['user_score_key']):
            self.update['bg_color'] = False
            self.update['btn_bg_color'] = False
            self.update['btn_text_color'] = False
            self.update['font'] = False
            self.update['text_color'] = False
            self.update['user_score_key'] = False
            window.close()
            new_window = self.make_game_over_window()

        return new_window

    def render_game_over_screen(self):
        # Boolean which checks whether to restart game or not
        restart = False
        game_over_window = self.make_game_over_window()

        # Create an event loop
        while True:
            if self.update['update']:
                game_over_window = self.update_game_over_window(game_over_window)

            event, values = game_over_window.read()

            # End program if user closes window or
            # presses the EXIT button
            if event == "Exit" or event == sg.WIN_CLOSED:
                print('Exiting')
                break
            elif event == "Restart":
                print('Restarting Game')
                restart = True
                break

        game_over_window.close()

        if restart:
            self.render_initial_screen()

    def create_screen(self, choice):
        if choice == "START":
            self.render_initial_screen()
        elif choice == "GAME_OVER":
            self.render_game_over_screen()


if __name__ == "__main__":
    the_GUI = GUI()
    choices = {'Start': 'START', 'Game Over': 'GAME_OVER'}
    chosen = 'Game Over'
    the_GUI.create_screen(choices[chosen])

    Colors_light = ['#33cc33', '#0EFFE9', '#cc99ff', '#ffff66', '#ffb384', '#c2cbb8']
    Colors_dark = ['#ff0000', '#990000', '#552b00', '#660033', '#552b00', '#FF0E83']
    Difficulties = ['Easy', 'Intermediate', 'Insane', 'False Alarm', 'Not working', 'Useless indeed']
    line = {'Start': "Type CD & press enter to change selected difficulty.\n",
            'Game Over': "Type CS & press enter to change user score.\n"}

    user_input = "NONE"
    while user_input.lower().strip() != "exit":
        user_input = input("Type CBGT & press enter to change background and text color.\n"
                           "Type CBTN & press enter to button background and its text color.\n"
                           + line[chosen] +
                           "Type exit & press enter to to stop program.\n")
        if user_input.lower().strip() == "cbgt":
            the_GUI.set_bg_color(Colors_light[randint(0, 5)])
            the_GUI.set_text_color(Colors_dark[randint(0, 5)])
        elif user_input.lower().strip() == "cbtn":
            the_GUI.set_btn_bg_color(Colors_light[randint(0, 5)])
            the_GUI.set_btn_text_color(Colors_dark[randint(0, 5)])
        elif user_input.lower().strip() == "cd":
            the_GUI.set_difficulty(Difficulties[randint(0, 5)])
        elif user_input.lower().strip() == "cs":
            the_GUI.set_user_score(randint(1, 100))
        elif user_input.lower().strip() == "exit":
            break
        the_GUI.create_screen(choices[chosen])
