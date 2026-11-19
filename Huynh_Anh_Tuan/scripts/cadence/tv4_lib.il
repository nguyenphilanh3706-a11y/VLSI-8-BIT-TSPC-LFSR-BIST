;; tv4_lib.il - TV4 (Huynh Anh Tuan): tao thu vien Virtuoso "tv4" gan cong nghe gpdk090.
;; Chay trong CIW:  load("<thu muc>/scripts/cadence/tv4_lib.il")
;; Thu vien dat tai /home/buet/pjck_tv4/tv4 (dia may ao, KHONG dat trong /mnt/hgfs).
;; Neu thu vien da co thi chi in vi tri, khong tao lai, khong xoa gi.
let((path lib cdslib ip line found op)
  path = "/home/buet/pjck_tv4/tv4"
  lib = ddGetObj("tv4")
  if(lib then
    printf("TV4: thu vien tv4 DA CO tai %s - khong tao lai\n" lib~>readPath)
  else
    system("mkdir -p /home/buet/pjck_tv4")
    lib = ddCreateLib("tv4" path)
    if(lib then
      printf("TV4: techBindTechFile -> %L\n" techBindTechFile(lib "gpdk090"))
      printf("TV4: da tao thu vien tv4 tai %s\n" lib~>readPath)
    else
      printf("TV4: !! ddCreateLib loi - tao bang Library Manager > File > New > Library (ten tv4, Attach gpdk090)\n")))
  ;; dam bao cds.lib (thu muc khoi dong Virtuoso) co dong DEFINE tv4
  cdslib = strcat(getWorkingDir() "/cds.lib")
  found = nil
  when(isFile(cdslib)
    ip = infile(cdslib)
    while(gets(line ip) when(rexMatchp("^ *DEFINE +tv4 " line) found = t))
    close(ip))
  if(found then
    printf("TV4: %s da co dong DEFINE tv4\n" cdslib)
  else when(lib
    op = outfile(cdslib "a")
    fprintf(op "DEFINE tv4 %s\n" path)
    close(op)
    printf("TV4: da them 'DEFINE tv4 %s' vao %s\n" path cdslib)))
  printf("TV4: ket qua ddGetObj(\"tv4\")~>readPath = %L ; tech = %L\n" ddGetObj("tv4")~>readPath
         techGetTechFile(ddGetObj("tv4"))~>libName)
  t)
