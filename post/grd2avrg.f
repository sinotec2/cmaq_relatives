      CHARACTER*4 MAQ(10), MSPEC(10,50) !CAMX4.01
      INTEGER MFID(60)
      character*10 names
      parameter(ni=65,nj=65)
      dimension a(ni,nj)
      parameter(PHIC=23.60785)!   ; CENTRAL LATITUDE (minus for southern hemesphere)
      parameter(XLONC=120.9908)

      DATA NUEM3/46/
      DATA MAQ /1HA, 1HI, 1HR, 1HQ, 1HU, 1HA, 1HL, 1HI, 1HT, 1HY /

      open(1,file='dict.grd')
      nii=ni
      njj=nj
      call readsurf(1,nii,njj,a)

      call readIn(2,NX,NY,NZ,XORG,YORG,DELTAX,DELTAY)
      OPEN(NUEM3, FILE='pm2_5.avrg',FORM='UNFORMATTED'
     +  ,convert='BIG_ENDIAN',STATUS='UNKNOWN')

      data NSG, NOSPEC, NBD, TBEG, NED, TEND/1,1,17281,0,17281,1/
        XUTM=XLONC
        YUTM=PHIC
        NZONE=(180+XLONC)/6+1
        XORG=XORG*1000.
        YORG=YORG*1000.
        DELTAX=DELTAX*1000.
        DELTAY=DELTAY*1000.

      WRITE(NUEM3) MAQ, MFID, NSG, NOSPEC, NBD, TBEG, NED, TEND
      WRITE(NUEM3) XUTM,YUTM,NZONE,XORG,YORG,DELTAX,DELTAY,     !FINE
     +             NX,NY,NZ, NVLOW,NVUP,DZSURF,DZMINL,DZMINU    !FINE
      WRITE (NUEM3)1,1,NX,NY
      names='PM2_5'
      do J=1,NOSPEC
        do I=1,10
              MSPEC(I,J)=names(i:i)
        enddo
        enddo
      WRITE (NUEM3)((MSPEC(I,J),I=1,10),J=1,NOSPEC)
      WRITE (NUEM3)NBD, TBEG,NED, TEND
      do L=1,NOSPEC
      do K=1,NZ
      WRITE(NUEM3)NSG,(MSPEC(J,L),J=1,10),((a(I,J),I=1,NX),J=1,NY)
      ENDDO        !L
      ENDDO        !L

      stop
      end
      subroutine readIn(igrd,NX,NY,NZ,XORG,YORG,DELTAX,DELTAY)
      character fname*100,project*10 ,A1*1
      write(A1,'(I1)')igrd
      open(1,file='./d'//A1//'.in'
     +,status='unknown')
      do i=1,2
      read(1,*)
      enddo
      read(1,'(20x,a10)') project
      write(*,'(a,1x,a10)') '                     Projection:',project
      do i=4,7
      read(1,*)
      enddo
      read(1,'(20x,a)') fname !line 8th
      read(fname,*) NX,NY,NZ
      write(*,'(a,3i10)')'                 CAMx grid size:',NX,NY,NZ
      read(1,'(20x,a)') fname
      read(fname,*)DELTAX,DELTAY
       write(*,'(a,2f10.3)')
     &                  '              CAMx grid spacing:',DELTAX,DELTAY
       if (project.eq.'LCP       ') then
        iproj = 2
        read(1,'(20x,a)') fname
        read(fname,*) XORG,YORG,clonin,clatin,tlat1in,tlat2in
        write(*,'(a,2f10.3)')
     &                  '    CAMx LCP Origin (SW corner):',XORG,YORG
        write(*,'(a,4f10.3,/)')
     &  '    CAMx LCP Projection Params :',clonin,clatin,tlat1in,tlat2in
        endif
        close(1)
        return
        end

