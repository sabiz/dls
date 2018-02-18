#! /bin/sh

head suumo_conv.csv -n1
read -p "カラム番号をカンマ区切りで入力> " cul

cat suumo_conv.csv | cut -f $cul -d ',' > suumo_pick.csv
