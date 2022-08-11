# drum-pattern-markov-chain
ドラムパターンMIDIファイルからマルコフ連鎖を活用して新たなドラムパターンを作ります<br>
[この動画](https://www.youtube.com/watch?v=nUJiKVWmrdk)で用いたソースコード]です。


# ドラムパターン⇔MIDI対応表
ドラムパターンをMIDIに変換する際は以下表の通りに作成してください。


## 音の種類

| MIDI(ノード番号) | 情報 | 文字列 |
| --- | ---| --- |
| 36(C1) | Kick      | "C" |
| 38(D1) | Snare     | "D" |
| 40(E1) | Percussion| "E" |
| 41(F1) | Clap      | "F" |
| 43(G1) | Ride      | "G" |
| 45(A1) | Close HH  | "A" |
| 47(B1) | Open HH   | "B" |
| 48(C2) | FX        | "X" |
| 0(C-2) | None      | "N" |

## 音の長さ

| MIDI(Ticks per Beat) | 情報 | 文字列 |
| --- | ---| --- |
| 480 | 1/4  | "4" |
| 240 | 1/8  | "8" |
| 120 | 1/16 | "16" |

## 音の強さ

| MIDI(Velocity) | 情報 | 文字列 |
| --- | ---| --- |
| 127 | 強い  | "h" |
| 0~126 | 普通  | "m" |

## その他

| 情報 | 内容 | 文字列 |
| --- | ---| --- |
| 同時押し | ドラムパターンの文字列同士が同時押しする場合、間に用いる | "+" |
| 連打 | ドラムパターンの文字列が同時押しせず次につながる場合、間に用いる | "_" |
| 区切り部分 | ドラムパターンの文字列が同時押しせず次につながり、かつマルコフ連鎖の区切り単位に該当する場合間に用いる | " " |

## 変換例
以下のように打ち込んだMIDIファイルは、区切り間隔が`separate_time=480`設定の場合`C4h D8h_D8m C4h D4h`となります。

![](https://user-images.githubusercontent.com/65853436/184064986-32e34a2e-862a-4825-81f6-3629e383c2da.png)

## MIDIデータ作成時の注意
同時押しが発生する場合、互いのノードの長さをどちらか一番短いノードに合わせる必要があります。

【Before】<br>
<img src="https://user-images.githubusercontent.com/65853436/184065632-ce047002-11a7-4a0e-bb92-82bab6079082.png" width="600">

【After】<br>
<img src="https://user-images.githubusercontent.com/65853436/184065682-e8578b0f-a71d-41c3-a643-adbef95e2ac6.png" width="600">


# 実行環境
[poetry](https://github.com/python-poetry/poetry)を用いて環境を用意しています。

```
git clone git@github.com:nijigen-plot/drum-pattern-markov-chain.git
poetry install
```