rd /s /q build\
rd /s /q dist\
pyinstaller --hidden-import=queue -F -w "login.py"
md dist\platforms
xcopy platforms dist\platforms /s
xcopy sqldrivers dist\sqldrivers /s
copy *.ui dist\
copy *.db dist\
cd /d dist
ren login.exe erp.exe