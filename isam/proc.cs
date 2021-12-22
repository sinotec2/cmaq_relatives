
#isam job for 20180404~8, 6 AirQualityForecastZone(AQFS), only GR1~4 and PTA are taken into account
#sum up aerosol results using python program, to be PM25_IONS, see SA_PM25_IONS.py
for nc in $(ls CCTM*nc);do python ../SA_PM25_IONS.py $nc;done >& /dev/null
for z in FWS JJZ NEC NWC SCH YZD;do 
  for d in {4..8};do
    #only GR13、GR24、PTA results(_[GP]*) are summed, see addNC, the python program
    ncs='';for nc in $(ls PM25_IONS${z}_2018040${d}_[GP]*.nc);do ncs=${ncs}" "$nc;done;
    python ~/bin/addNC $ncs PM25_IONS${z}_2018040${d}.nc
  done
done
# combine all days for each zone
for z in FWS JJZ NEC NWC SCH YZD;do ncrcat -O PM25_IONS${z}_2018040?.nc PM25_IONS${z}.nc;done
