	SUBROUTINE readsurf(n,ni,nj,a)
      include '/home/kuang/bin/CNTROL.CMD'
      real a(ni,nj)
      read (n,*,end=999)
      read (n,*)NOXG,NOYG
      read(n,*)XORG,XUTM
      read(n,*)YORG,YUTM
      read (n,*)cmin,cmax
      if(XORG.lt.1000) then
        XORG=XORG*1000
        YORG=YORG*1000
        XUTM=XUTM*1000
        YUTM=YUTM*1000
      endif
        print*,noxg,noyg
        NI=NOXG
        NJ=NOYG
!       allocate(a(ni,nj))
        DELTAX=(XUTM-XORG)/(NI-1)
        DELTAY=(YUTM-YORG)/(NJ-1)
        I1=NI/10+1
        I2=MOD(NI,10)
        IF(I2.EQ.0)I1=I1-1
C         do 42 j=1,nj
             read(n,*) ((a( k,j),K=1,ni),j=1,nj)
 42      continue
	do i=1,NI
	do j=1,NJ
	  if(a(i,j).gt.cmax)a(i,j)=0
	enddo
	enddo
999     return
        end
      subroutine surfer(ni,nj,n,a)
      include '/home/kuang/bin/CNTROL.CMD'
      real a(400,400)
      DIMENSION SCR(ni*nj)
        CMIN=99999
        CMAX=-99999
        J1=1
        J2=ni*nj
        JJ=1
        DO 221 J=1,nj
        DO 221 I=1,ni
          SCR(JJ)=a(i,j)
          CMIN=AMIN1(CMIN,SCR(JJ))
          CMAX=AMAX1(CMAX,SCR(JJ))
          JJ=JJ+1
221     CONTINUE
        WRITE(n,'(a4)')'DSAA'
        WRITE(n,*)NOXG,NOYG
        WRITE(n,*)XORG,XUTM !dot in grid
        WRITE(n,*)YORG,YUTM
        WRITE(n,*)CMIN,CMAX
        I1=NI/10+1
        I2=MOD(NI,10)
        IF(I2.EQ.0)I1=I1-1
C--MAKE THE BOUNDARY BLANK
        goto 102
        DO 30 I=1,NI
         SCR(I)=1.70141E+38
30      CONTINUE
        DO 31 I=J2-NI+1,J2
         SCR(I)=1.70141E+38
31      CONTINUE
        DO 32 I=J1,J2,NI
         SCR(I)=1.70141E+38
32      CONTINUE
        DO 33 I=J1+NI-1,J2,NI
         SCR(I)=1.70141E+38
33      CONTINUE
102     K1=J1
        DO 2 J=1,NJ
          DO 3 KK=1,I1
            K2=K1+9
            IF(KK.EQ.I1.AND.I2.NE.0) K2=K1+I2-1
            WRITE(N,101)(SCR(I),I=K1,K2)
4           K1=K2+1
3         CONTINUE
          WRITE(N,*)
2       CONTINUE
101   FORMAT(1x,10(1PG13.5E3))
      RETURN
      END
