
#isam job for 20180404~8, 6 AirQualityForecastZone(AQFS), only GR1~4 and PTA are taken into account
#sum up aerosol results using python program, to be PM10, see SA_PM10.py
in $(ls CCTM*nc);do python ../SA_PM10.py $nc;done >& /dev/null
for z in FWS JJZ NEC NWC SCH YZD;do 
  for d in {4..8};do
    #only GR13、GR24、PTA results(_[GP]*) are summed, see addNC, the python program
    ncs='';for nc in $(ls PM10${z}_2018040${d}_[GP]*.nc);do ncs=${ncs}" "$nc;done;
    python ~/bin/addNC $ncs PM10${z}_2018040${d}.nc
  done
done
# combine all days for each zone
for z in FWS JJZ NEC NWC SCH YZD;do ncrcat -O PM10${z}_2018040?.nc PM10${z}.nc;done
