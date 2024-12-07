import random
import json
import os
import MGE

MGE.init()

window = MGE.Window("LibMGE 2048", resolution=(400, 500), flags=0)
window.set_TitleBarColor(MGE.Color((30, 34, 38)))
window.set_BorderColor(None)

material_hover = MGE.Material(color=MGE.Color(90, 90, 240))

class _temp:
    multiplier = 11
    difficulty = 1
    score = 0
    maxScore = 0
    language = {}

class MenuScene:
    def __init__(self):
        self.TitleText = MGE.ObjectText((MGE.AutoCalcs2D.Center(), 100), font_size=30, text="LibMGE 2048")
        self.TitleText.pivot = MGE.Pivot2D.Center

        self.MaxScoreText = MGE.ObjectText((10, 200), text=f"{_temp.language['maxScore']} {_temp.maxScore}")

        self.numVitText = MGE.ObjectText((10, 230), text=f"{_temp.language['numVit']} ")

        self.input = MGE.ObjectInputTextLine((self.numVitText.surfaceSize[0] + 10, 231), (50, 10), text=f"{_temp.multiplier}")
        self.input.setNumericFilter()

        self.difficultyText = MGE.ObjectText((10, 260), text=f"{_temp.language['difficulty']} ")

        self.easyButton = MGE.Button((10, 290), 0, (80, 20))
        self.easyText = MGE.ObjectText((30, 290), font_size=15, text=_temp.language['easy'])
        self.normalButton = MGE.Button((10, 310), 0, (80, 20))
        self.normalText = MGE.ObjectText((30, 310), font_size=15, text=_temp.language['normal'])

        self.StartButton = MGE.ButtonText((MGE.AutoCalcs2D.Center(), 470), 0, (MGE.AutoCalcs2D.Percent(100), 60), (1, 1), 20, _temp.language['startGame'], material_hover=material_hover)
        self.StartButton.pivot = MGE.Pivot2D.Center

    def logicScene(self, program):

        self.input.update(window)

        if self.easyButton.button(1, window, window.camera):
            _temp.difficulty = 0

        if self.normalButton.button(1, window, window.camera):
            _temp.difficulty = 1

        if self.StartButton.button(1, window, window.camera):
            _temp.multiplier = int(self.input.text)
            data = {"language": "pt-BR",
                    "multiplier": _temp.multiplier,
                    "difficulty": _temp.difficulty}
            with open('Data/config.json', 'w') as file:
                json.dump(data, file, indent=4)
            program.scene = GameScene(4 if _temp.difficulty == 1 else 5)

    def drawScene(self):
        window.clear(color=(20, 20, 26, 255))
        self.TitleText.drawObject(window, render=True)

        self.MaxScoreText.drawObject(window, render=True)

        self.numVitText.drawObject(window, render=True)
        self.input.drawObject(window)

        self.difficultyText.drawObject(window, render=True)

        self.easyText.drawObject(window, render=True)
        self.normalText.drawObject(window, render=True)

        if "difficulty" not in window.drawnObjects:
            window.drawnObjects.append("difficulty")
            window.drawSquare((10, 313 if _temp.difficulty == 1 else 293), (15, 15), 0, 0, MGE.Colors.StandardColor)

        self.StartButton.drawObject(window)

    def close(self):
        self.StartButton.close()
        del self.StartButton, self

class GameScene:
    def __init__(self, board_size=4):
        self._board_size = board_size

        _temp.score = 0

        self.ScoreText = MGE.ObjectText((10, 10))
        self.ScoreText._text_render_type = 1

        self.MaxScoreText = MGE.ObjectText((10, 40), text=f"{_temp.language['maxScore']} {_temp.maxScore}")
        self.MaxScoreText._text_render_type = 1

        self.Text = MGE.ObjectText((10, 70), 0, 15, f"{_temp.language['addNumbers']} {2 ** _temp.multiplier}!")
        self.Text._text_render_type = 1

        self.color = MGE.Color(32, 32, 38)

        self.matrix = [[0 for _ in range(self._board_size)] for _ in range(self._board_size)]
        self.text_matrix = [[MGE.ObjectText(font_size=25) for _ in range(self._board_size)] for _ in range(self._board_size)]

        zero_positions = [(i, j) for i, row in enumerate(self.matrix) for j, val in enumerate(row) if val == 0]
        positions_to_change = random.sample(zero_positions, 2)
        for i, j in positions_to_change:
            self.matrix[i][j] = 2

        self.window_game = MGE.InternalWindow((0, 100), 0, (400, 400), resolution=(400, 400))

    def logicScene(self, program):
        if MGE.keyboard(MGE.KeyboardButton.Esc):
            program.scene = MenuScene()

        def _add():
            zero_positions = [(i, j) for i, row in enumerate(self.matrix) for j, val in enumerate(row) if val == 0]
            if not zero_positions:
                program.scene = GameEndScene(_temp.language['gameOver'])
                return
            i, j = random.choice(zero_positions)
            self.matrix[i][j] = 2

        def merge_line(line):
            merged = []
            previous = None
            line_points = 0
            for num in line:
                if num != 0:
                    if previous is None:
                        previous = num
                    elif previous == num:
                        combined_value = previous * 2
                        merged.append(combined_value)
                        line_points += combined_value
                        previous = None
                    else:
                        merged.append(previous)
                        previous = num
            if previous is not None:
                merged.append(previous)
            return merged + [0] * (len(line) - len(merged)), line_points

        def rotate_matrix(mat, times):
            for _ in range(times):
                mat = [list(row) for row in zip(*mat[::-1])]
            return mat

        def move(direction):
            rotated = self.matrix
            if direction[0] != 0:
                rotated = rotate_matrix(self.matrix, direction[0])

            new_matrix = []
            total_points = 0
            for row in rotated:
                merged_row, points = merge_line(row)
                new_matrix.append(merged_row)
                total_points += points

            if direction[1] != 0:
                self.matrix = rotate_matrix(new_matrix, direction[1])
            else:
                self.matrix = new_matrix

            _temp.score += total_points

            if max(max(row) for row in self.matrix) == 2 ** _temp.multiplier:
                program.scene = GameEndScene(_temp.language['youWin'])
                return

        if MGE.keyboard(MGE.KeyboardButton.KeyW) or MGE.keyboard(MGE.KeyboardButton.Up):
            move((0, 0))
            _add()
        if MGE.keyboard(MGE.KeyboardButton.KeyA) or MGE.keyboard(MGE.KeyboardButton.Left):
            move((3, 1))
            _add()
        if MGE.keyboard(MGE.KeyboardButton.KeyS) or MGE.keyboard(MGE.KeyboardButton.Down):
            move((2, 2))
            _add()
        if MGE.keyboard(MGE.KeyboardButton.KeyD) or MGE.keyboard(MGE.KeyboardButton.Right):
            move((1, 3))
            _add()

        if _temp.score > _temp.maxScore:
            _temp.maxScore = _temp.score

        self.ScoreText.text = f"{_temp.language['score']} {_temp.score}"
        self.MaxScoreText.text = f"{_temp.language['maxScore']} {_temp.maxScore}"

    def drawScene(self):
        window.clear(color=(20, 20, 26, 255))
        self.ScoreText.drawObject(window, render=True)
        self.MaxScoreText.drawObject(window, render=True)
        self.Text.drawObject(window, render=True)

        self.window_game.clear(color=(26, 26, 32, 255))

        for num, col in enumerate(self.matrix):
            _size = (400 - 10 * (self._board_size + 1)) // self._board_size
            for num2, c in enumerate(col):
                loc_x = 10 + _size * num + 10 * num
                loc_y = 10 + _size * num2 + 10 * num2
                if f"{num}/{num2}" not in self.window_game.drawnObjects:
                    self.window_game.drawnObjects.append(f"{num}/{num2}")
                    self.window_game.drawSquare((loc_x, loc_y), (_size, _size), 0, 5, self.color if c == 0 else MGE.Colors.Blue)
                if c != 0:
                    self.text_matrix[num][num2].text = f"{c}"
                    self.text_matrix[num][num2].location = loc_x + 5, loc_y + 5
                    self.text_matrix[num][num2].drawObject(self.window_game, render=True)

        self.window_game.drawObject(window)

    def close(self):
        del self

class GameEndScene:
    def __init__(self, result):

        if _temp.score > _temp.maxScore:
            _temp.maxScore = _temp.score

        with open('Data/save.json', 'w') as file:
            json.dump({'maxScore': _temp.maxScore}, file, indent=4)

        self.TitleText = MGE.ObjectText((MGE.AutoCalcs2D.Center(), 100), font_size=30, text=result)
        self.TitleText.pivot = MGE.Pivot2D.Center
        self.TitleText._text_render_type = 1

        self.ScoreText = MGE.ObjectText((10, 190), text=f"{_temp.language['score']} {_temp.score}")
        self.ScoreText._text_render_type = 1

        self.MaxScoreText = MGE.ObjectText((10, 220), text=f"{_temp.language['maxScore']} {_temp.maxScore}")
        self.MaxScoreText._text_render_type = 1

        self.BackButton = MGE.ButtonText((MGE.AutoCalcs2D.Center(), 408), 0, (MGE.AutoCalcs2D.Percent(100), 60), (1, 1), 20, _temp.language['return'], material_hover=material_hover)
        self.BackButton.pivot = MGE.Pivot2D.Center

        self.RestartButton = MGE.ButtonText((MGE.AutoCalcs2D.Center(), 470), 0, (MGE.AutoCalcs2D.Percent(100), 60), (1, 1), 20, _temp.language['restart'], material_hover=material_hover)
        self.RestartButton.pivot = MGE.Pivot2D.Center

    def logicScene(self, program):
        if self.BackButton.button(1, window, window.camera):
            program.scene = MenuScene()
        elif self.RestartButton.button(1, window, window.camera):
            program.scene = GameScene(4 if _temp.difficulty == 1 else 5)

    def drawScene(self):
        window.clear(color=(20, 20, 26, 255))
        self.TitleText.drawObject(window, render=True)
        self.ScoreText.drawObject(window, render=True)
        self.MaxScoreText.drawObject(window, render=True)

        self.BackButton.drawObject(window)
        self.RestartButton.drawObject(window)

    def close(self):
        del self

class Program:
    def __init__(self):
        save_path = "Data/save.json"
        if os.path.exists(save_path):
            with open(save_path, 'r') as file:
                _temp.maxScore = json.load(file).get('maxScore', 0)

        with open('Data/config.json', 'r', encoding='utf8') as file:
            config_data = json.load(file)
        _temp.multiplier = config_data.get('multiplier', 1)
        _temp.difficulty = config_data.get('difficulty', 'normal')

        language_file = f"Data/languages/{config_data.get('language', 'en-US')}.json"
        with open(language_file, 'r', encoding='utf8') as file:
            _temp.language = json.load(file)

        self._scene = MenuScene()

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, scene):
        if self._scene:
            self._scene.close()
        self._scene = scene

    def BaseLogic(self):
        MGE.update()
        window.update()
        window.title = f"LibMGE 2048 | FPS: {int(window.frameRate)}"

        if MGE.QuitEvent() or MGE.keyboard(MGE.KeyboardButton.F1):
            exit()

    def run(self):
        while True:
            self.BaseLogic()
            if self._scene:
                self._scene.logicScene(self)
                self._scene.drawScene()

if __name__ == "__main__":
    _program = Program()
    _program.run()
