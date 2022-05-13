# VELODYNE-VLP-16

LiDAR からデータを取得・可視化するスクリプト群

対応モデル

- Velodyne VLP-16
- Velodyne VLP-32c
- Ouster OS1-32

## LiDAR から直接データを取得・保存する

直接のデータ取得は`make_xxx_from_stream.py`を使うことができる

### Velodyne から CSV 保存

LiDAR を PC につないだ状態で実行(機種は自動認識)

```
> python make_csv_velodyne_from_stream.py [out_dir]
```

`[out_dir]/YYMMDD-HHmm/csv/xxx.csv`に一周分ずつ点群データが保存される

### Velodyne から PCD 保存

LiDAR を PC につないだ状態で実行(機種は自動認識)

```
> python make_pcd_velodyne_from_stream.py [out_dir]
```

`[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`に一周分ずつ点群データが保存される

### Ouster から PCD 保存

`make_pcd_ouster_from_stream.py`中の以下の行に LiDAR の hostname を記述

```
HOST_NAME = "os-122201001516.local"
```

LiDAR を PC につないだ状態で実行

```
> python make_pcd_ouster_from_stream.py [out_dir]
```

`[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`に一周分ずつ点群データが保存される

## PCAP から PCD に変換

PCAP はパケットキャプチャしたデータを保存するファイルで、VeloView などの GUI で録画するとこの形式になる。

`pcap_to_pcd.py`内の関数を使う

### Velodyne(VeloView)からの場合

`pcap_file_path`に pcap、`out_dir`に保存先を指定<br>
`model`は['VLP16', '32C', '32E', 'VLS128']に対応

```
> python pcap_to_pcd.py [velodyne or v] [pcap_file_path] [model] [out_dir]
```

`rpm`の変更(デフォルト 600)と dual モードの設定は以下のセッティングで変更可能

```
optional arguments:
  -h, --help            show this help message and exit
  --rpm RPM, -r RPM     rpm setting
  --dual, -d            dual setting
```

### Ouster(Ouster Studio)からの場合

`pcap_file_path`に pcap、`metadata_file_path`に metadata(.json)、
`out_dir`に保存先を指定

```
> python pcap_to_pcd.py [ouster or o] [pcap_file_path] [metadata_file_path] [out_dir]
```

## 可視化

### CSV の可視化

`file_path`に csv を指定

```
> python visualize_csv.py [file_path]
```

### PCD の可視化

`file_path`に pcd を指定

```
> python visualize_pcd.py [file_path]
```

# Troubleshooting

Eset等のセキュリティソフトが入っているとLiDARデータを弾いてしまう。

Firewall機能を無効化することでデータ受信が可能となる。
