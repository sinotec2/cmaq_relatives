# 執行**CMAQ-ISAM**

## 背景
- 與CAMx-OSAT/PSAT類似，**Integrated Source Apportionment Method (ISAM)**是**CMAQ**內設之污染來源分配模式，可以針對模擬範圍內的污染區域、類別進行追蹤計算，分別輸出該分區(分類)之污染濃度，以進行來源追蹤，以便完成：
1. 敏感性分析
1. 排放量設定方式修正、校正
1. 地形遮蔽、滯留現象之探討研究
1. 污染防制、減量、空氣品質管理
相關研究發表不少，詳見下列參考文獻。使用範例、手冊等請參考[官網](https://www.epa.gov/cmaq/integrated-source-apportionment-method-cmaq-isam)。

- 執行**CMAQ-ISAM**的腳本與執行`CCTM`是同一個。然實際全年、全月的模擬還有許多設定需要修改。
- **CMAQ-ISAM**不必特別處理排放量，EPA設計讓所有的排放開關控制對照，都些在`EmissCtrl`檔案內，藉該檔案來控制特定地區污染排放的開啟或關閉。


## `EmissCtrl`檔案
- 這個namelist的目的原本是給程式控制排放量的。為了分區進行管制，因此會需要設定(**CMAQ**程式內應用)分區的名稱、[網格遮罩]()`gridmask`檔案與該檔案內定義的名稱之對照關係。各變數說明如下：
  - `ISAM_REGIONS`：檔案標籤，就是在`csh`中所指定的[gridmask遮罩檔案]()。
  - `Region Label`：在nml檔案內應用的分區名稱
  - `Variable on File`：在gridmask檔案內的分區名稱。
- 中國大陸的[空氣質量預報](http://big5.mee.gov.cn/gate/big5/www.mee.gov.cn/hjzl/dqhj/kqzlyb/)分區為例  

```python
!------------------------------------------------------------------------------!
&RegionsRegistry
!| Region Label   | File_Label  | Variable on File
 RGN_NML  =
  'AQFZ0', 'ISAM_REGIONS','AQFZ0',
  'AQFZ1', 'ISAM_REGIONS','AQFZ1',
  'AQFZ2', 'ISAM_REGIONS','AQFZ2',
  'AQFZ3', 'ISAM_REGIONS','AQFZ3',
  'AQFZ4', 'ISAM_REGIONS','AQFZ4',
  'AQFZ5', 'ISAM_REGIONS','AQFZ5',
  'AQFZ6', 'ISAM_REGIONS','AQFZ6',
  'AQFZ7', 'ISAM_REGIONS','AQFZ7',
  'ALL',   'ISAM_REGIONS','ALL',
  'EVERYWHERE'  ,'N/A'        ,'N/A',
/
```
- 臺灣地區縣市代碼為例

```python
!------------------------------------------------------------------------------!
&RegionsRegistry
!| Region Label   | File_Label  | Variable on File
 RGN_NML  =
  'CNTY_01', 'ISAM_REGIONS','CNTY_01',
  'CNTY_02', 'ISAM_REGIONS','CNTY_02',
  'CNTY_11', 'ISAM_REGIONS','CNTY_11',
  'CNTY_12', 'ISAM_REGIONS','CNTY_12',
  'CNTY_17', 'ISAM_REGIONS','CNTY_17',
  'CNTY_21', 'ISAM_REGIONS','CNTY_21',
  'CNTY_22', 'ISAM_REGIONS','CNTY_22',
  'CNTY_31', 'ISAM_REGIONS','CNTY_31',
  'CNTY_32', 'ISAM_REGIONS','CNTY_32',
  'CNTY_33', 'ISAM_REGIONS','CNTY_33',
  'CNTY_34', 'ISAM_REGIONS','CNTY_34',
  'CNTY_35', 'ISAM_REGIONS','CNTY_35',
  'CNTY_36', 'ISAM_REGIONS','CNTY_36',
  'CNTY_37', 'ISAM_REGIONS','CNTY_37',
  'CNTY_38', 'ISAM_REGIONS','CNTY_38',
  'CNTY_39', 'ISAM_REGIONS','CNTY_39',
  'CNTY_40', 'ISAM_REGIONS','CNTY_40',
  'CNTY_41', 'ISAM_REGIONS','CNTY_41',
  'CNTY_42', 'ISAM_REGIONS','CNTY_42',
  'CNTY_43', 'ISAM_REGIONS','CNTY_43',
  'CNTY_44', 'ISAM_REGIONS','CNTY_44',
  'CNTY_45', 'ISAM_REGIONS','CNTY_45',
  'CNTY_46', 'ISAM_REGIONS','CNTY_46',
  'WATER',   'ISAM_REGIONS','CNTY_53',
  'ALL',   'ISAM_REGIONS','ALL',
  'EVERYWHERE'  ,'N/A'        ,'N/A',
/
```
- 
## Reference
- USEPA, **Integrated Source Apportionment Method (CMAQ-ISAM)**, CMAQ User's Guide (c) 2021, [github](https://github.com/USEPA/CMAQ/blob/main/DOCS/Users_Guide/CMAQ_UG_ch11_ISAM.md)