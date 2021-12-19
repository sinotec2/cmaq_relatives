YY=`echo $1|cut -c1-2`
MM=`echo $1|cut -c3-4`
begd=$(date -d "20${YY}-${MM}-15 -1 month" +%Y-%m-%d)
prem=$YY$(date -d "20${YY}-${MM}-15 -1 month" +%m)
nexm=$YY$(date -d "20${YY}-${MM}-15 +1 month" +%m)
mkdir -p $1
ROOT=$(echo $PWD|cut -d'/' -f 2)
cd $1
for r in {5..12};do 
  mkdir -p run$r
  cd run$r
  for d in {0..6};do 
    ds=$(( ( $r - 1 ) * 4 + $d -1 ))
    dd=$(date -d "$begd +${ds} day" +%Y-%m-%d )
    ft=20$1
#    if [ $r -eq 5 ] && [ $d -eq 1 ];then ft=20$prem;fi
#    if [ $r -eq 12 ] && [ $d -ge 5 ];then ft=20$nexm;fi
    for DM in 1 2 4;do 
      f=/$ROOT/WRF4.1/WRFv4.1.3/$ft/wrfout/wrfout_d0${DM}_${dd}_00\:00\:00
      ln -sf $f wrfout_d0${DM}_$d
      ln -sf $f ..
    done
  done
  cd ..
done
cd ..
