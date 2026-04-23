import ui
import csv
import os
from datetime import datetime

class AdvancedTicTacToe(ui.View):
    """
    3手制限ルールを採用した◯×ゲーム
    4手目を打つと自分の最も古い印が消える。
    """
    def __init__(self):
        # 画面設定
        self.name = '3-Move Limit Tic-Tac-Toe'
        self.background_color = '#fdfdfd'
        
        # ゲーム状態の初期化
        self.current_player_mark = '◯' 
        self.move_history = {'◯': [], '✖': []} 
        self.buttons = []
        
        # フォルダとファイル名の設定
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, '../data')
        
        # 起動時の日時でログファイル名を生成
        file_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.log_file = os.path.join(self.data_dir, f'game_log_{file_timestamp}.csv')
        
        # 準備
        self._setup_directory()
        self._create_board_ui()
        
    def _setup_directory(self):
        """保存用ディレクトリの作成"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def _create_board_ui(self):
        """3x3のゲームボードUIを作成"""
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

    def cell_tapped(self, sender):
        """マスがタップされた時の処理"""
        # すでに印があるマスは無効
        if sender.title:
            return 

        # 1. 座標とプレイヤー情報の特定
        index = int(sender.name)
        y, x = divmod(index, 3)
        player_id = '0' if self.current_player_mark == '◯' else '1'
        
        # 2. ログの保存 (player, hand, timestamp, x, y)
        self.save_log(player_id, self.current_player_mark, x, y)

        # 3. 印を配置し、履歴に追加
        sender.title = self.current_player_mark
        self.move_history[self.current_player_mark].append(sender)
        
        # 4. 【特殊ルール】4手目を打った場合、自分の1手目を消去
        if len(self.move_history[self.current_player_mark]) > 3:
            oldest_btn = self.move_history[self.current_player_mark].pop(0)
            oldest_btn.title = ''
            
        # 5. 勝利判定
        if self.check_winner():
            ui.hud_alert(f'Player {player_id} Wins!')
            self.reset_game()
            return

        # 6. ターン交代
        self.current_player_mark = '✖' if self.current_player_mark == '◯' else '◯'

    def check_winner(self):
        """勝利条件（縦・横・斜め）のチェック"""
        b = [btn.title for btn in self.buttons]
        win_patterns = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # 横
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # 縦
            (0, 4, 8), (2, 4, 6)             # 斜め
        ]
        for p in win_patterns:
            if b[p[0]] == b[p[1]] == b[p[2]] != '':
                return True
        return False

    def save_log(self, player_id, hand, x, y):
        """プレイログをCSVに書き込み"""
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_exists = os.path.isfile(self.log_file)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['player', 'hand', 'timestamp', 'x', 'y'])
                writer.writerow([player_id, hand, now, x, y])
        except IOError as e:
            print(f"Log save error: {e}")

    def reset_game(self):
        """ゲーム盤面のリセット"""
        for btn in self.buttons:
            btn.title = ''
        self.move_history = {'◯': [], '✖': []}
        self.current_player_mark = '◯'

if __name__ == '__main__':
    view = AdvancedTicTacToe()
    view.present('sheet')
