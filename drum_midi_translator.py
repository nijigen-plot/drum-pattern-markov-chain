import re

import mido
import numpy as np
from mido import Message, MetaMessage, MidiFile, MidiTrack


class TextToMidi:
    def __init__(self):
        pass

    # 音色の文字列をMIDInote番号へ変更する
    def translate_note(self, sound_kind: str):
        if sound_kind == "C":
            return 36
        elif sound_kind == "D":
            return 38
        elif sound_kind == "E":
            return 40
        elif sound_kind == "F":
            return 41
        elif sound_kind == "G":
            return 43
        elif sound_kind == "A":
            return 45
        elif sound_kind == "B":
            return 47
        elif sound_kind == "X":
            return 48
        else:
            return False  # Nに対応

    # 音色の長さ文字列をMIDI timeへ変更する
    def translate_length(self, sound_length: str):
        return int(int(sound_length) ** -1 * 1920)

    # 音色の強さ文字列尾をMIDI velocityへ変更する
    def translate_velocity(self, sound_velocity: str):
        if sound_velocity == "h":
            return 127
        else:
            return 80  # mに対応

    # 文字列を連結記号とMIDIデータを示す文字列に分けて判別する
    def split_midi_text(self, t: str):
        # C8h A16h 等のMIDIデータを示す文字列をlistで格納
        midi_data = re.split("[_+]{1,1}", t)
        # + _ 等のデータ連結方法を示す文字列をlistで格納
        linking = re.findall("[_+]{1,1}", t)
        # midi_dataの長さ
        midi_data_length = len(midi_data)
        # 同時押しの場合のnote_off Messageを保存しておく配列
        self.note_off_messages = []
        for i in range(midi_data_length):
            # midi_dataの最後の要素の場合は連結文字列を_としてcreate_note_element関数へデータを渡す
            if i + 1 == midi_data_length:
                self.create_note_element(midi_data[i], "_")
            # それ以外の場合は連結文字列を共に渡す
            else:
                self.create_note_element(midi_data[i], linking[i])

    # 文字列を各要素に分解しMIDIの情報へ変換する
    def create_note_element(self, midi_text: str, linking: str):
        try:
            # 大文字のアルファベットを抜き出す。複数見つかった場合は最初を正とする
            sound_kind = re.findall("[CDEFGABXN]{1,1}", midi_text)[0]
            # 数字を抜き出す。複数見つかった場合は最初を正とする
            sound_length = re.findall("[0-9]{1,2}", midi_text)[0]
            # アルファベットh or mを抜き出す
            sound_velocity = re.findall("[hm]{1,1}", midi_text)[0]
        except IndexError:
            raise IndexError(f"{midi_text} 文字列に入れるべきデータが入っていませんでした。文字列が間違っていないか再確認してください。")
        else:
            if linking == "_":
                self.create_mido_message(
                    [
                        self.translate_note(sound_kind),
                        self.translate_length(sound_length),
                        self.translate_velocity(sound_velocity),
                    ]
                )
            else:  # linkingが+の場合に対応
                self.on_hold_mido_message(
                    [
                        self.translate_note(sound_kind),
                        self.translate_length(sound_length),
                        self.translate_velocity(sound_velocity),
                    ]
                )

    # MIDI情報を用いてMido Messageを作成する
    def create_mido_message(self, midi_info_list: list):
        note = midi_info_list[0]
        time = midi_info_list[1]
        velo = midi_info_list[2]
        self.track.append(Message("note_on", note=note, velocity=velo, time=0))
        self.track.append(Message("note_off", note=note, time=time))
        # 最後に+で溜まったnote_offがあればそれらもappendし、リセットする
        [self.track.append(no) for no in self.note_off_messages]
        self.note_off_messages = []

    # MIDI情報を用いてMido Messageを作成する（同時押し版）
    def on_hold_mido_message(self, midi_info_list: list):
        note = midi_info_list[0]
        velo = midi_info_list[2]
        self.track.append(Message("note_on", note=note, velocity=velo, time=0))
        # note_offのMessageだけnote_off_messages関数へ格納する
        self.note_off_messages.append(Message("note_off", note=note, time=False))

    # テキストをMIDIに変換する
    def save_transform(self, parse_text: str, save_directory: str, bpm=175):
        text_list = parse_text.split(" ")

        # MIDIファイルの作成
        self.mid = MidiFile()
        self.track = MidiTrack()
        self.mid.tracks.append(self.track)
        self.track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm)))
        for tl in text_list:
            self.split_midi_text(tl)

        # 保存
        self.mid.save(save_directory)
        print(f"create MIDI file to {save_directory}.")


class MidiToText:
    def __init__(self):
        pass

    # noteから音色文字へ変換する
    def rev_translate_note(self, note: int):
        if note == 36:
            return "C"
        elif note == 38:
            return "D"
        elif note == 40:
            return "E"
        elif note == 41:
            return "F"
        elif note == 43:
            return "G"
        elif note == 45:
            return "A"
        elif note == 47:
            return "B"
        elif note == 48:
            return "X"
        elif note == 0:
            return "N"
        else:
            raise KeyError(f"{note} : 対応外の音程がMIDIデータに打ち込まれています。")

    # timeから長さを表す文字へ変換する
    def rev_translate_length(self, time: int):
        # timeはint型で返す
        return int(1 / (time * self.time_multiply / 1920))

    # velocityから強さを表す文字へ変換する
    def rev_translate_velocity(self, velo: int):
        if velo == 127:
            return "h"
        else:
            return "m"  # 127以外はすべてmとして逆変換する

    # dictのkeyとitemsを文字列としてそれぞれ連結する
    def dict_to_str(self, d: dict, k: str):
        # {'C' : [16, 'h']} は 'C16h'と変換される
        return k + "".join([str(i) for i in d[k]])

    def create_text(self, md: mido.messages.messages.Message):
        # 情報毎に分解する
        _type = md.type
        note = md.note
        time = md.time
        velo = md.velocity
        if _type == "note_on":
            self.total_time += time
            # 辞書に音程をキーとして情報を追加する
            self.md_dict[self.rev_translate_note(note)] = [
                self.total_time,
                self.rev_translate_velocity(velo),
            ]
        elif _type == "note_off":
            # 累積time情報を更新する
            self.total_time += time
            append_target_note = self.rev_translate_note(note)
            # onと紐づけるデータを取得する
            result = {k: v for k, v in self.md_dict.items() if k == append_target_note}
            # note_offとなったノードのon時累積時間を格納する
            self.on_time_list.append(result[append_target_note][0])
            # offを記録した際の累積時間からonを記録した際の累積時間を引き上書き(これがnoteの長さとなる)
            result[append_target_note][0] = self.rev_translate_length(self.total_time - result[append_target_note][0])
            # 紐づけたデータは辞書から削除する
            self.md_dict = {k: v for k, v in self.md_dict.items() if k != append_target_note}
            # dictの情報から文字列を作成する
            self.translate_results.append(self.dict_to_str(result, append_target_note))
        else:
            raise KeyError(f"type={_type} 予期していないtypeを発見しました。")

    # _ or + or ' ' の連結情報を付与する
    def texts_join(self):
        # self.on_time_listの時間間隔を補正する
        fix_on_time_list = [int(self.time_multiply * t) for t in self.on_time_list]
        # on_time_listが小さい順に並び変える
        sort_fix_on_time_list = [fix_on_time_list[i] for i in np.argsort(fix_on_time_list)]
        sort_translate_results = [self.translate_results[i] for i in np.argsort(fix_on_time_list)]
        # _か+かを判定する
        bridge_text_list = []
        for i in range(len(sort_fix_on_time_list)):
            try:
                if sort_fix_on_time_list[i] == sort_fix_on_time_list[i + 1]:
                    bridge_text_list.append("+")
                else:
                    bridge_text_list.append("_")
            except IndexError:  # 最後の配列参照のエラーをスルーする
                pass
        # ' 'かどうかを判定する
        for i in range(len(sort_fix_on_time_list)):
            try:
                if (sort_fix_on_time_list[i] != sort_fix_on_time_list[i + 1]) and (
                    sort_fix_on_time_list[i + 1] % self.separate_time == 0
                ):
                    bridge_text_list[i] = " "
                else:
                    pass
            except IndexError:
                pass
        # 変換した文字列と結合する
        create_text = []
        for i in range(len(sort_translate_results)):
            create_text.append(sort_translate_results[i])
            try:
                create_text.append(bridge_text_list[i])
            except IndexError:
                return "".join(create_text)

    # MIDIをテキストに変換する separate_time 240は1/8毎に文字列に空白を打ちこむ設定。
    # 480で1/4毎、120で1/16毎に空白を打ちこむ。マルコフ連鎖させる際の遷移先をふやしたり減らしたりするために使用。
    def transform(self, midi_data: mido.midifiles.midifiles.MidiFile, separate_time=240):
        self.separate_time = separate_time
        self.time_multiply = int(480 / midi_data.ticks_per_beat)
        # tracks0のMIDI情報(SMF0のMIDIファイルを読む想定)
        midi_track = midi_data.tracks[0]
        # Messageの情報のみを抜き出す
        message_data = list(filter(lambda x: type(x) == mido.messages.messages.Message, midi_track))
        # note_onとnote_off情報を紐づけるための辞書
        self.md_dict = {}
        # 累積時間情報
        self.total_time = 0
        # 同時押しかどうかを判定するためのonノード時累積時間配列
        self.on_time_list = []
        # 変換したテキスト
        self.translate_results = []
        for md in message_data:
            self.create_text(md)
        result_text = self.texts_join()
        # return self.translate_results, self.on_time_list
        return result_text
