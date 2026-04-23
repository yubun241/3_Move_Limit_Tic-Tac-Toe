import ui
import csv
import os
import sound
from datetime import datetime

class AdvancedTicTacToe(ui.View):
    def __init__(self):
        self.name = '3-Move Limit Tic-Tac-Toe'
        self.background_color = '#fdfdfd'
        
        # ゲームデータの管理
        self.current_player_mark = '◯'
        self.move_history = {'◯': [], '✖': []}
        self.session_log = [] # 1試合分のデータを一時保存するリスト
        self.buttons = []
        
        # ディレクトリ設定
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, '../data')
        self._setup_directory()
        
        # UI作成
        self._create_ui()
        
    def _setup_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def _create_ui(self):
        # 3x3のゲームボード作成
        cell_size = 90
        margin = 5
        start_x = 45
        start_y = 100

        for i in range(9):
            row, col = divmod(i, 3)
            btn = ui.Button(name=str(i))
            btn.frame = (col * (cell_size + margin) + start_x, 
                         row * (cell_size + margin) + start_y, 
                         cell_size, cell_size)
            btn.background_color = 'white'
            btn.tint_color = '#333333'
            btn.font = ('<System-Bold>', 40)
            btn.border_width = 1
            btn.border_color = '#dddddd'
            btn.corner_radius = 10
            btn.action = self.cell_tapped
            self.add_subview(btn)
            self.buttons.append(btn)
            
        # クリアボタンの設置
        clear_btn = ui.Button(title='Clear / Save Game')
        clear_btn.frame = (start_x, start_y + 300, cell_size * 3 + margin * 2, 44)
        clear_btn.background_color = '#ff9500'
        clear_btn.tint_color = 'white'
        clear_btn.font = ('<System-Bold>', 18)
        clear_btn.corner_radius = 8
        clear_btn.action = self.clear_button_tapped
        self.add_subview(clear_btn)

    def cell_tapped(self, sender):
        if sender.title: return 

        sound.play_effect('ui:click_1')
        
        # 1. 指し手情報の記録
        index = int(sender.name)
        y, x = divmod(index, 3)
        player_id = '0' if self.current_player_mark == '◯' else '1'
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # リストに一時保存 (CSV書き出し用)
        self.session_log.append([player_id, self.current_player_mark, now, x, y])

        # 2. 盤面への反映
        sender.title = self.current_player_mark
        self.move_history[self.current_player_mark].append(sender)
        
        # 3. 特殊ルール（4手前を消す）
        if len(self.move_history[self.current_player_mark]) > 3:
            oldest_btn = self.move_history[self.current_player_mark].pop(0)
            oldest_btn.title = ''
            
        # 4. 勝利判定
        if self.check_winner():
            sound.play_effect('arcade:Powerup_1')
            ui.hud_alert(f'Player {player_id} Wins!')
            self.save_and_reset() # 保存してリセット
            return

        # 5. ターン交代
        self.current_player_mark = '✖' if self.current_player_mark == '◯' else '◯'

    def check_winner(self):
        b = [btn.title for btn in self.buttons]
        win_patterns = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for p in win_patterns:
            if b[p[0]] == b[p[1]] == b[p[2]] != '':
                return True
        return False

    def clear_button_tapped(self, sender):
        """クリアボタンが押された時の処理"""
        if self.session_log:
            sound.play_effect('ui:click_2')
            self.save_and_reset()
            ui.hud_alert('Game Saved & Reset')
        else:
            ui.hud_alert('No moves to save')

    def save_and_reset(self):
        """現在のセッションログをCSVに保存し、ゲームをリセットする"""
        if not self.session_log:
            return

        # 保存時の時間でファイル名を生成
        save_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = os.path.join(self.data_dir, f'game_log_{save_timestamp}.csv')
        
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['player', 'hand', 'timestamp', 'x', 'y'])
                writer.writerows(self.session_log)
        except Exception as e:
            print(f"Save error: {e}")

        # 状態リセット
        for btn in self.buttons:
            btn.title = ''
        self.move_history = {'◯': [], '✖': []}
        self.session_log = []
        self.current_player_mark = '◯'

if __name__ == '__main__':
    AdvancedTicTacToe().present('sheet')
