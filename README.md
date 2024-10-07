# VELODYNE-VLP-16

Scripts for acquiring and visualizing data from LiDAR  
LiDARからデータを取得・可視化するスクリプト群

Supported models / 対応モデル:
- Velodyne VLP-16
- Velodyne VLP-32c
- Ouster OS1-32

## Acquiring and saving data directly from LiDAR / LiDARから直接データを取得・保存する

Direct data acquisition can be done using `make_xxx_from_stream.py`  
直接のデータ取得は`make_xxx_from_stream.py`を使うことができる

### Saving CSV from Velodyne / Velodyneから CSV 保存

Execute with LiDAR connected to PC (model is automatically recognized)  
LiDARをPCにつないだ状態で実行(機種は自動認識)

```
> python make_csv_velodyne_from_stream.py [out_dir]
```

Point cloud data for each revolution is saved in `[out_dir]/YYMMDD-HHmm/csv/xxx.csv`  
`[out_dir]/YYMMDD-HHmm/csv/xxx.csv`に一周分ずつ点群データが保存される

### Saving PCD from Velodyne / VelodyneからPCD保存

Execute with LiDAR connected to PC (model is automatically recognized)  
LiDARをPCにつないだ状態で実行(機種は自動認識)

```
> python make_pcd_velodyne_from_stream.py [out_dir]
```

Point cloud data for each revolution is saved in `[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`  
`[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`に一周分ずつ点群データが保存される

### Saving PCD from Ouster / OusterからPCD保存

Specify the LiDAR's hostname in the following line in `make_pcd_ouster_from_stream.py`  
`make_pcd_ouster_from_stream.py`中の以下の行にLiDARのhostnameを記述

```
HOST_NAME = "os-122201001516.local"
```

Execute with LiDAR connected to PC  
LiDARをPCにつないだ状態で実行

```
> python make_pcd_ouster_from_stream.py [out_dir]
```

Point cloud data for each revolution is saved in `[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`  
`[out_dir]/YYMMDD-HHmm/pcd/xxx.pcd`に一周分ずつ点群データが保存される

## Converting PCAP to PCD / PCAPからPCDに変換

PCAP is a file format for saving packet capture data, which is the format used when recording with GUI tools like VeloView.  
PCAPはパケットキャプチャしたデータを保存するファイルで、VeloViewなどのGUIで録画するとこの形式になる。

Use the functions in `pcap_to_pcd.py`  
`pcap_to_pcd.py`内の関数を使う

### For Velodyne (VeloView) / Velodyne(VeloView)からの場合

Specify `pcap_file_path` for pcap and `out_dir` for save destination  
`pcap_file_path`にpcap、`out_dir`に保存先を指定

`model` supports ['HDL-32E', 'HDL-64E', 'HDL-64E_S2', 'HDL-64E_S3', 'VLP-16', 'VLP-32C', 'Alpha Prime']  
`model`は['HDL-32E', 'HDL-64E', 'HDL-64E_S2', 'HDL-64E_S3', 'VLP-16', 'VLP-32C', 'Alpha Prime']に対応

```
> python pcap_to_pcd.py [velodyne or v] [pcap_file_path] [model] [out_dir]
```

Changing `rpm` (default 600) and setting dual mode can be done with the following settings:  
`rpm`の変更(デフォルト600)とdualモードの設定は以下のセッティングで変更可能:

```
optional arguments:
  -h, --help            show this help message and exit
  --rpm RPM, -r RPM     rpm setting
  --dual, -d            dual setting (True if included)
```

### For Ouster (Ouster Studio) / Ouster(Ouster Studio)からの場合

Specify `pcap_file_path` for pcap, `metadata_file_path` for metadata (.json), and `out_dir` for save destination  
`pcap_file_path`にpcap、`metadata_file_path`にmetadata(.json)、`out_dir`に保存先を指定

```
> python pcap_to_pcd.py [ouster or o] [pcap_file_path] [metadata_file_path] [out_dir]
```

## Visualization / 可視化

### Visualizing CSV / CSVの可視化

Specify `file_path` for csv  
`file_path`にcsvを指定

```
> python visualize_csv.py [file_path]
```

### Visualizing PCD / PCDの可視化

Specify `file_path` for pcd  
`file_path`にpcdを指定

```
> python visualize_pcd.py [file_path]
```

# Troubleshooting / トラブルシューティング

Security software like Eset may block LiDAR data. Disabling the Firewall feature allows data reception.  
Eset等のセキュリティソフトが入っているとLiDARデータを弾いてしまう。Firewall機能を無効化することでデータ受信が可能となる。
