# VELODYNE-VLP-16

LiDARからデータを取得・可視化するスクリプト群

対応モデル

- Velodyne VLP-16
- Velodyne VLP-32c
- Ouster OS1-32

## LiDARから直接データを取得・保存する

直接のデータ取得は`make_xxx_from_stream.py`を使うことができる

### VelodyneからCSV保存

LiDARをPCにつないだ状態で実行(機種は自動認識)

```
> python make_csv_velodyne_from_stream.py [out_dir]
```

`[out_dir]/YYMMDD-HHmm/csv/xxx.csv`に一周分ずつ点群データが保存される

### VelodyneからPCD保存

LiDARをPCにつないだ状態で実行(機種は自動認識)

```
> python make_pcd_velodyne_from_stream.py [out_dir]
```

`[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`に一周分ずつ点群データが保存される

### OusterからPCD保存

`make_pcd_ouster_from_stream.py`中の以下の行にLiDARのhostnameを記述

```
HOST_NAME = "os-122201001516.local"
```

LiDARをPCにつないだ状態で実行

```
> python make_pcd_ouster_from_stream.py [out_dir]
```

`[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`に一周分ずつ点群データが保存される

## PCAPからPCDに変換

PCAPはパケットキャプチャしたデータを保存するファイルで、VeloViewなどのGUIで録画するとこの形式になる。

`pcap_to_pcd.py`内の関数を使う

## 可視化

### CSVの可視化

`file_path`にcsvを指定

```
> python visualize_csv.py [file_path]
```

### PCDの可視化

`file_path`にpcdを指定

```
> python visualize_pcd.py [file_path]
```
